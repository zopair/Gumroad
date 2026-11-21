#!/usr/bin/env python3
"""RelayMind orchestrator.

Environment:
  TOPIC         idea text (or pre-enhanced script JSON from the web app)   [required]
  LANG_CODE     en | ar  (LANG is also accepted; locale strings like en_US.UTF-8 are ignored)
  VOICE         optional edge-tts voice override
  GITHUB_TOKEN  workflow token with `models: read` (free GitHub Models)
  TG_TOKEN      optional Telegram bot token
  TG_CHAT_ID    optional Telegram numeric chat id
  RELAYMIND_OFFLINE=1   force fully-local generation (dry-run / tests)

Usage:  python runner.py            (reads env)
        python runner.py --dry-run  (offline, short local render for verification)
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from engine import media_factory, prompt_enhancer, resolver  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("relaymind")


def detect_lang(env_lang: str, topic: str) -> str:
    v = (env_lang or "").strip().lower()
    if v in ("ar", "arabic", "عربي"):
        return "ar"
    if v in ("en", "english"):
        return "en"
    arabic = sum(1 for ch in topic if "\u0600" <= ch <= "\u06ff")
    return "ar" if arabic > len(topic) * 0.3 else "en"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="offline local render test")
    ap.add_argument("--out", default="output")
    args = ap.parse_args()
    if args.dry_run:
        os.environ["RELAYMIND_OFFLINE"] = "1"

    t0 = time.time()
    topic = os.environ.get("TOPIC", "").strip() or ("3 habits that make you smarter" if args.dry_run else "")
    if not topic:
        log.error("TOPIC is empty")
        return 2
    lang = detect_lang(os.environ.get("LANG_CODE") or os.environ.get("LANG", ""), topic)
    token = os.environ.get("GITHUB_TOKEN", "")
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    report: dict = {"topic": topic[:300], "lang": lang, "ok": False}

    try:
        report["health"] = resolver.health_check()
        script = prompt_enhancer.enhance(topic, lang, token)
        if args.dry_run:
            script["scenes"] = script["scenes"][:3]
        report["script"] = script
        (out / "script.json").write_text(json.dumps(script, ensure_ascii=False, indent=2), encoding="utf-8")
        log.info("script source=%s scenes=%d", script.get("source"), len(script["scenes"]))

        result = media_factory.build_video(script, str(out), voice=os.environ.get("VOICE") or None)
        report.update(result)
        report["ok"] = True

        caption = f"{script['title']}\n\n{script.get('caption', '')}\n{' '.join(script.get('hashtags', []))}"
        tg_tok, tg_chat = os.environ.get("TG_TOKEN", ""), os.environ.get("TG_CHAT_ID", "")
        if tg_tok and tg_chat and not resolver.offline():
            report["telegram"] = resolver.telegram_send_video(tg_tok, tg_chat, result["video"], caption)
    except Exception as exc:  # noqa: BLE001
        report["error"] = f"{type(exc).__name__}: {exc}"
        report["trace"] = traceback.format_exc()[-2000:]
        log.error("render failed: %s", exc)
    finally:
        report["total_seconds"] = round(time.time() - t0, 1)
        resolver.dump_report(str(out / "report.json"), report)

    if report["ok"]:
        log.info("DONE %s (%.1fs, %.2f MB, %.1fs video)", report["video"], report["total_seconds"],
                 report["size_mb"], report["duration"])
        summary = os.environ.get("GITHUB_STEP_SUMMARY")
        if summary:
            with open(summary, "a", encoding="utf-8") as fh:
                fh.write(f"### RelayMind\n- Title: {report['script']['title']}\n"
                         f"- Duration: {report['duration']}s, size {report['size_mb']} MB\n"
                         f"- Render: {report['render_seconds']}s\n")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
