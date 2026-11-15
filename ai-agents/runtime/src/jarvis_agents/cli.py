"""Command-line interface for local JARVIS agent runs."""
from __future__ import annotations
import argparse
import json
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
    return parser

def main(argv: Sequence[str] | None = None) -> int:
    parser, args = build_parser(), None
    args = parser.parse_args(argv)
    if args.command == "list":
        print("\n".join(AGENT_SLUGS)); return 0
    try:
        payload = json.loads(args.input.read_text(encoding="utf-8"))
        result = run_agent(args.agent, payload)
        rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(rendered, encoding="utf-8")
        else: sys.stdout.write(rendered)
        return 0
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        parser.exit(2, f"error: {exc}\n")

if __name__ == "__main__":
    raise SystemExit(main())
