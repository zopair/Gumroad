"""Stable public registry and report contract for the JARVIS agent family."""
from __future__ import annotations
from collections.abc import Callable, Mapping
from typing import Any
from .workflows import codesentinel, contentflip, docusense, estateguard, leadscout, mailforge, marketmind, rankmaster, socialsync, tradetrend

AGENT_SLUGS = ("rankmaster-ai", "leadscout-bot", "tradetrend-analyst", "docusense-support", "socialsync-ai", "mailforge-pro", "contentflip-ai", "estateguard-ai", "codesentinel", "marketmind-ai")
_HANDLERS: dict[str, Callable[[Mapping[str, Any]], dict[str, Any]]] = {
    "rankmaster-ai": rankmaster, "leadscout-bot": leadscout, "tradetrend-analyst": tradetrend,
    "docusense-support": docusense, "socialsync-ai": socialsync, "mailforge-pro": mailforge,
    "contentflip-ai": contentflip, "estateguard-ai": estateguard, "codesentinel": codesentinel, "marketmind-ai": marketmind,
}

def run_agent(slug: str, payload: Mapping[str, Any]) -> dict[str, Any]:
    """Run a deterministic, side-effect-free workflow and return a report."""
    if slug not in _HANDLERS:
        raise ValueError(f"Unknown agent '{slug}'. Choose one of: {', '.join(AGENT_SLUGS)}")
    if not isinstance(payload, Mapping):
        raise ValueError("Input must be a JSON object.")
    result = _HANDLERS[slug](payload)
    if not isinstance(result, dict):
        raise TypeError(f"Agent '{slug}' returned an invalid report.")
    result.update({"schema_version": "1.0", "agent": slug, "actions": []})
    return result
