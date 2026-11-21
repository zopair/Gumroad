"""Self-healing layer: endpoint health checks, retry/rotation, discovery, Telegram delivery.

Every external call in RelayMind goes through this module so that a single
429 / 5xx / timeout never breaks a render. When a chain is exhausted the caller
falls back to a fully local generator (Pillow / FFmpeg / espeak-ng).
"""
from __future__ import annotations

import json
import logging
import os
import random
import re
import time
from typing import Any, Callable, Iterable, Optional, Sequence

import requests

log = logging.getLogger("relaymind.resolver")

USER_AGENT = "RelayMind/1.0 (+https://github.com/zopair/Gumroad)"
RETRYABLE = {408, 409, 425, 429, 500, 502, 503, 504, 522, 524}

# --------------------------------------------------------------------------- #
# Endpoint registry (verified November 2026)
# --------------------------------------------------------------------------- #
# NOTE: GitHub Models (models.github.ai) was retired on 2026-07-30
# (https://docs.github.com/en/rest/models/inference). It is kept as a quick last
# attempt only; keyless Pollinations text endpoints are the primary free LLMs.
LLM_PROVIDERS: list[dict] = [
    {"name": "pollinations-text", "url": "https://text.pollinations.ai/openai", "model": "openai", "auth": "pollinations"},
    {"name": "pollinations-gen", "url": "https://gen.pollinations.ai/v1/chat/completions", "model": "openai", "auth": "pollinations-key"},
    {"name": "custom", "url": os.environ.get("LLM_BASE_URL", ""), "model": os.environ.get("LLM_MODEL", "gpt-4o-mini"), "auth": "custom"},
    {"name": "github-models", "url": "https://models.github.ai/inference/chat/completions", "model": "openai/gpt-4o-mini", "auth": "github"},
]
IMAGE_ENDPOINTS: list[str] = [
    # {prompt} {w} {h} {seed} are formatted at call time
    "https://image.pollinations.ai/prompt/{prompt}?width={w}&height={h}&seed={seed}&nologo=true&model=flux",
    "https://image.pollinations.ai/prompt/{prompt}?width={w}&height={h}&seed={seed}&nologo=true",
]
WIKIMEDIA_API = "https://commons.wikimedia.org/w/api.php"
OPENVERSE_API = "https://api.openverse.org/v1/images/"
GITHUB_SEARCH_API = "https://api.github.com/search/repositories"
TELEGRAM_API = "https://api.telegram.org/bot{token}/{method}"

HEALTH_TARGETS = {
    "pollinations_text": "https://text.pollinations.ai",
    "pollinations": "https://image.pollinations.ai",
    "wikimedia": "https://commons.wikimedia.org",
    "openverse": "https://api.openverse.org/v1/",
    "telegram": "https://api.telegram.org",
}


# Pollinations anonymous tier (Nov 2026): 1 image / 45 s / IP -> HTTP 402 FREE_LIMIT.
# A tiny circuit breaker reserves slots so we never waste time on guaranteed 402s.
import threading  # noqa: E402

_POLL_LOCK = threading.Lock()
_POLL_NEXT = 0.0
POLL_INTERVAL = 0 if os.environ.get("POLLINATIONS_TOKEN") else 46.0


def pollinations_slot() -> bool:
    """Reserve the next Pollinations slot if it is available right now."""
    global _POLL_NEXT
    with _POLL_LOCK:
        now = time.time()
        if now < _POLL_NEXT:
            return False
        _POLL_NEXT = now + POLL_INTERVAL
        return True


def pollinations_backoff(seconds: float) -> None:
    global _POLL_NEXT
    with _POLL_LOCK:
        _POLL_NEXT = max(_POLL_NEXT, time.time() + seconds)


class ChainExhausted(RuntimeError):
    """Raised when every provider in a fallback chain failed."""


def _session() -> requests.Session:
    s = requests.Session()
    s.headers["User-Agent"] = USER_AGENT
    return s


SESSION = _session()


def offline() -> bool:
    """RELAYMIND_OFFLINE=1 forces the fully-local path (used by dry-run tests)."""
    return os.environ.get("RELAYMIND_OFFLINE", "").strip() in {"1", "true", "yes"}


def request_with_retry(
    method: str,
    url: str,
    *,
    attempts: int = 3,
    timeout: float = 25,
    backoff: float = 1.5,
    **kwargs: Any,
) -> requests.Response:
    """HTTP call with exponential backoff + jitter that honours Retry-After."""
    if offline():
        raise ConnectionError("offline mode")
    last_exc: Optional[Exception] = None
    for i in range(attempts):
        try:
            r = SESSION.request(method, url, timeout=timeout, **kwargs)
            if r.status_code in RETRYABLE:
                wait = backoff * (2 ** i) + random.uniform(0, 0.5)
                ra = r.headers.get("Retry-After")
                if ra and ra.isdigit():
                    wait = min(float(ra), 20.0)
                log.warning("HTTP %s from %s (try %d/%d), waiting %.1fs",
                            r.status_code, url.split("?")[0], i + 1, attempts, wait)
                last_exc = requests.HTTPError(f"HTTP {r.status_code}", response=r)
                if i < attempts - 1:
                    time.sleep(wait)
                continue
            return r
        except (requests.Timeout, requests.ConnectionError) as exc:
            last_exc = exc
            log.warning("network error %s (try %d/%d): %s", url.split("?")[0], i + 1, attempts, exc)
            if i < attempts - 1:
                time.sleep(backoff * (2 ** i))
    raise last_exc or RuntimeError("request failed")


def run_chain(name: str, providers: Sequence[tuple[str, Callable[[], Any]]],
              validate: Callable[[Any], bool] = bool) -> tuple[str, Any]:
    """Try providers in order; return (provider_name, result) of the first valid one."""
    errors = []
    for pname, fn in providers:
        try:
            result = fn()
            if validate(result):
                log.info("[%s] provider ok: %s", name, pname)
                return pname, result
            errors.append(f"{pname}: invalid result")
        except Exception as exc:  # noqa: BLE001 - self-healing must never crash
            errors.append(f"{pname}: {type(exc).__name__}: {exc}")
            log.warning("[%s] provider %s failed: %s", name, pname, exc)
    raise ChainExhausted(f"{name}: " + " | ".join(errors))


# --------------------------------------------------------------------------- #
# Health checks
# --------------------------------------------------------------------------- #
def health_check(timeout: float = 6) -> dict[str, bool]:
    """Fast reachability probe so we can skip dead providers instead of waiting on them."""
    status: dict[str, bool] = {}
    for key, url in HEALTH_TARGETS.items():
        if offline():
            status[key] = False
            continue
        try:
            r = SESSION.head(url, timeout=timeout, allow_redirects=True)
            status[key] = r.status_code < 500
        except Exception:  # noqa: BLE001
            status[key] = False
    log.info("health: %s", status)
    return status


# --------------------------------------------------------------------------- #
# Free LLM rotation (Pollinations keyless -> custom OpenAI-compatible -> GitHub Models)
# --------------------------------------------------------------------------- #
def chat_completion(messages: list[dict], token: str = "", *, temperature: float = 0.8,
                    max_tokens: int = 1200, json_mode: bool = True) -> tuple[str, str]:
    """Rotate across free OpenAI-compatible endpoints. Returns (provider, content)."""

    def make(p: dict) -> Callable[[], str]:
        def call() -> str:
            headers = {"Content-Type": "application/json", "Accept": "application/json"}
            if p["auth"] == "pollinations-key" and not os.environ.get("POLLINATIONS_TOKEN"):
                raise RuntimeError("needs free POLLINATIONS_TOKEN")
            if p["auth"].startswith("pollinations") and os.environ.get("POLLINATIONS_TOKEN"):
                headers["Authorization"] = "Bearer " + os.environ["POLLINATIONS_TOKEN"]
            elif p["auth"] == "custom":
                if not p["url"]:
                    raise RuntimeError("LLM_BASE_URL not set")
                if os.environ.get("LLM_API_KEY"):
                    headers["Authorization"] = "Bearer " + os.environ["LLM_API_KEY"]
            elif p["auth"] == "github":
                if not token:
                    raise RuntimeError("no GITHUB_TOKEN")
                headers.update({"Authorization": f"Bearer {token}", "X-GitHub-Api-Version": "2022-11-28"})
            body: dict[str, Any] = {"model": p["model"], "messages": messages,
                                    "temperature": temperature, "max_tokens": max_tokens}
            if json_mode:
                body["response_format"] = {"type": "json_object"}
            r = request_with_retry("POST", p["url"], headers=headers, json=body, attempts=2,
                                   timeout=60 if p["auth"].startswith("pollinations") else 30)
            if r.status_code == 402 and p["auth"] == "pollinations":
                m = re.search(r"[Rr]etry after (\d+)s", r.text)
                wait = int(m.group(1)) + 1 if m else 46
                if wait <= 30:  # anonymous tier: 1 reply / 45 s / IP
                    log.info("pollinations text cooling down %ss", wait)
                    time.sleep(wait)
                    r = request_with_retry("POST", p["url"], headers=headers, json=body, attempts=1, timeout=60)
            if r.status_code != 200:
                raise RuntimeError(f"HTTP {r.status_code}: {r.text[:160]}")
            try:
                return r.json()["choices"][0]["message"]["content"]
            except Exception as exc:  # noqa: BLE001
                raise RuntimeError(f"non-JSON reply: {r.text[:80]!r}") from exc
        return call

    return run_chain("llm", [(p["name"], make(p)) for p in LLM_PROVIDERS],
                     validate=lambda s: isinstance(s, str) and len(s.strip()) > 20)


# Open-source discovery helper
# --------------------------------------------------------------------------- #
def discover_repos(query: str, token: str = "", limit: int = 5) -> list[dict]:
    """Search GitHub for open-source fallback resources (fonts, music, models...)."""
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        r = request_with_retry("GET", GITHUB_SEARCH_API, headers=headers, attempts=2, timeout=15,
                               params={"q": query, "sort": "stars", "order": "desc", "per_page": limit})
        if r.status_code != 200:
            return []
        return [{"full_name": i["full_name"], "url": i["html_url"], "stars": i["stargazers_count"],
                 "license": (i.get("license") or {}).get("spdx_id")} for i in r.json().get("items", [])]
    except Exception as exc:  # noqa: BLE001
        log.warning("discovery failed: %s", exc)
        return []


# --------------------------------------------------------------------------- #
# Telegram delivery
# --------------------------------------------------------------------------- #
def telegram_send_video(token: str, chat_id: str, video_path: str, caption: str = "") -> bool:
    """Upload the MP4 with sendVideo; falls back to sendDocument, then a text notice."""
    if not token or not chat_id or not os.path.exists(video_path):
        return False
    size_mb = os.path.getsize(video_path) / 1_048_576
    caption = caption[:1000]
    methods = ["sendVideo", "sendDocument"] if size_mb < 49 else []
    for method in methods:
        try:
            with open(video_path, "rb") as fh:
                field = "video" if method == "sendVideo" else "document"
                data = {"chat_id": chat_id, "caption": caption}
                if method == "sendVideo":
                    data.update({"supports_streaming": "true", "width": "1080", "height": "1920"})
                r = request_with_retry("POST", TELEGRAM_API.format(token=token, method=method),
                                       data=data, files={field: ("relaymind.mp4", fh, "video/mp4")},
                                       attempts=2, timeout=120)
            if r.ok and r.json().get("ok"):
                log.info("telegram %s delivered", method)
                return True
            log.warning("telegram %s failed: %s", method, r.text[:200])
        except Exception as exc:  # noqa: BLE001
            log.warning("telegram %s error: %s", method, exc)
    try:
        request_with_retry("POST", TELEGRAM_API.format(token=token, method="sendMessage"),
                           data={"chat_id": chat_id, "text": f"RelayMind video ready ({size_mb:.1f} MB). "
                                 "Open the RelayMind app to download it.\n\n" + caption[:300]},
                           attempts=2, timeout=20)
    except Exception:  # noqa: BLE001
        pass
    return False


def dump_report(path: str, report: dict) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=2)
