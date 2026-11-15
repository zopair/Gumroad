"""Command-line interface for local JARVIS agent runs."""
from __future__ import annotations
import argparse
import json
import os
import sys
from pathlib import Path
from typing import Sequence
from . import AGENT_SLUGS, run_agent

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="jarvis-agents", description="Run a local JARVIS analysis or drafting workflow.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("list", help="List available agents.")
    run_parser = subparsers.add_parser("run", help="Run an agent using a JSON input file.")
    run_parser.add_argument("agent", choices=AGENT_SLUGS)
    run_parser.add_argument("--input", required=True, type=Path, help="Path to a UTF-8 JSON object.")
    run_parser.add_argument("--output", type=Path, help="Optional report output path; stdout when omitted.")
    run_parser.add_argument("--ai", action="store_true", help="Explicitly send input to the configured AI provider for text enhancement.")
    return parser

def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "list":
        print("\n".join(AGENT_SLUGS))
        return 0
    try:
        payload = json.loads(args.input.read_text(encoding="utf-8"))
        provider = None
        if args.ai:
            from .providers import OpenAICompatibleProvider
            api_key, model = os.environ.get("JARVIS_API_KEY"), os.environ.get("JARVIS_MODEL")
            if not api_key or not model:
                parser.error("--ai requires JARVIS_API_KEY and JARVIS_MODEL environment variables.")
            provider = OpenAICompatibleProvider(api_key=api_key, model=model, base_url=os.environ.get("JARVIS_BASE_URL", "https://api.openai.com/v1/chat/completions"))
        result = run_agent(args.agent, payload, provider=provider)
        if provider is not None:
            result["warnings"].append("AI provider usage may incur charges under your provider account.")
        rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(rendered, encoding="utf-8")
        else:
            sys.stdout.write(rendered)
        return 0
    except (OSError, json.JSONDecodeError, ValueError, RuntimeError) as exc:
        parser.exit(2, f"error: {exc}\n")

if __name__ == "__main__":
    raise SystemExit(main())
