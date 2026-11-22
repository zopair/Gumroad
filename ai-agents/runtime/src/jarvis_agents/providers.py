"""Optional OpenAI-compatible provider and evidence-constrained report enhancement."""
from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


class OpenAICompatibleProvider:
    """Explicit opt-in chat-completions client; never instantiated implicitly."""

    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        base_url: str = "https://api.openai.com/v1/chat/completions",
        timeout: float = 30.0,
        max_tokens: int = 1200,
    ) -> None:
        if not api_key or not api_key.strip():
            raise ValueError("A provider API key is required.")
        if not model or not model.strip():
            raise ValueError("A provider model name is required.")
        parsed = urlparse(base_url)
        local_http = parsed.scheme == "http" and parsed.hostname in {"localhost", "127.0.0.1", "::1"}
        if parsed.scheme != "https" and not local_http:
            raise ValueError("Provider endpoint must use HTTPS (HTTP is allowed only for localhost tests).")
        if not parsed.netloc:
            raise ValueError("Provider endpoint must be an absolute URL.")
        if timeout <= 0 or timeout > 120:
            raise ValueError("Provider timeout must be between 0 and 120 seconds.")
        if max_tokens < 1 or max_tokens > 8192:
            raise ValueError("max_tokens must be between 1 and 8192.")
        self._api_key = api_key.strip()
        self.model = model.strip()
        self.base_url = base_url
        self.timeout = timeout
        self.max_tokens = max_tokens

    def complete(self, messages: list[dict[str, str]]) -> str:
        if not isinstance(messages, list) or not messages:
            raise ValueError("At least one chat message is required.")
        body = json.dumps({
            "model": self.model,
            "messages": messages,
            "temperature": 0.2,
            "max_tokens": self.max_tokens,
        }).encode("utf-8")
        request = Request(
            self.base_url,
            data=body,
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            method="POST",
        )
        try:
            with urlopen(request, timeout=self.timeout) as response:
                raw = response.read(2_000_001)
        except HTTPError as exc:
            raise RuntimeError(
                f"AI provider returned HTTP {exc.code}. Check endpoint, model, API key, and quota."
            ) from None
        except (URLError, TimeoutError) as exc:
            raise RuntimeError(
                f"AI provider connection failed: {getattr(exc, 'reason', 'request timed out')}"
            ) from None
        if len(raw) > 2_000_000:
            raise RuntimeError("AI provider response exceeded the 2 MB safety limit.")
        try:
            content = json.loads(raw.decode("utf-8"))["choices"][0]["message"]["content"]
        except (UnicodeDecodeError, json.JSONDecodeError, KeyError, IndexError, TypeError):
            raise RuntimeError("AI provider returned an unexpected chat-completions response.") from None
        if not isinstance(content, str) or not content.strip():
            raise RuntimeError("AI provider returned an empty or non-text response.")
        return content.strip()


def enhance_report(
    slug: str,
    payload: Mapping[str, Any],
    result: dict[str, Any],
    provider: Any,
) -> dict[str, Any]:
    """Enhance report prose while preserving evidence and deterministic safety metadata."""
    if not callable(getattr(provider, "complete", None)):
        raise TypeError("Provider must expose a complete(messages) method.")
    messages = [
        {
            "role": "system",
            "content": (
                "You are an evidence-constrained editor. Return ONLY valid JSON with exactly these keys: "
                "title (string), summary (string), sections (array of objects with heading and content). "
                "Improve clarity using only facts in the input and baseline report. Do not invent data, "
                "sources, metrics, legal conclusions, financial advice, or personal details. Preserve "
                "uncertainty and every source excerpt exactly. Never propose external actions. "
                "Do not include warnings or actions."
            ),
        },
        {
            "role": "user",
            "content": json.dumps(
                {"agent": slug, "input": payload, "baseline_report": result},
                ensure_ascii=False,
                default=str,
            ),
        },
    ]
    try:
        enhanced = json.loads(provider.complete(messages))
    except (json.JSONDecodeError, TypeError):
        raise ValueError(
            "AI provider must return a valid JSON object; no partial AI output was applied."
        ) from None
    if (
        not isinstance(enhanced, dict)
        or not isinstance(enhanced.get("title"), str)
        or not isinstance(enhanced.get("summary"), str)
        or not isinstance(enhanced.get("sections"), list)
    ):
        raise ValueError("AI provider response does not match the required report schema.")
    if any(
        not isinstance(item, dict)
        or not isinstance(item.get("heading"), str)
        or "content" not in item
        for item in enhanced["sections"]
    ):
        raise ValueError("AI provider returned an invalid report section.")
    result["title"] = enhanced["title"]
    result["summary"] = enhanced["summary"]
    result["sections"] = enhanced["sections"]
    result.setdefault("warnings", []).extend([
        "AI-assisted text may contain errors. Verify every factual statement and source.",
        "Input content was sent to the configured third-party AI endpoint; do not submit confidential or regulated data unless authorized.",
    ])
    return result
