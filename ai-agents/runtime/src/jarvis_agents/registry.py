"""Stable public registry and report contract for the JARVIS agent family."""
from __future__ import annotations
import json
from collections.abc import Callable, Mapping
from typing import Any
from .workflows import codesentinel, contentflip, docusense, estateguard, leadscout, mailforge, marketmind, rankmaster, socialsync, tradetrend

AGENT_SLUGS = ("rankmaster-ai", "leadscout-bot", "tradetrend-analyst", "docusense-support", "socialsync-ai", "mailforge-pro", "contentflip-ai", "estateguard-ai", "codesentinel", "marketmind-ai")
_HANDLERS: dict[str, Callable[[Mapping[str, Any]], dict[str, Any]]] = {
    "rankmaster-ai": rankmaster, "leadscout-bot": leadscout, "tradetrend-analyst": tradetrend,
    "docusense-support": docusense, "socialsync-ai": socialsync, "mailforge-pro": mailforge,
    "contentflip-ai": contentflip, "estateguard-ai": estateguard, "codesentinel": codesentinel, "marketmind-ai": marketmind,
}

def run_agent(slug: str, payload: Mapping[str, Any], *, provider: Any | None = None) -> dict[str, Any]:
    """Run a local workflow, optionally using an explicitly supplied AI provider."""
    if slug not in _HANDLERS:
        raise ValueError(f"Unknown agent '{slug}'. Choose one of: {', '.join(AGENT_SLUGS)}")
    if not isinstance(payload, Mapping):
        raise ValueError("Input must be a JSON object.")
    result = _HANDLERS[slug](payload)
    if not isinstance(result, dict):
        raise TypeError(f"Agent '{slug}' returned an invalid report.")
    result.update({"schema_version": "1.0", "agent": slug, "actions": []})
    if provider is not None:
        if not callable(getattr(provider, "complete", None)):
            raise TypeError("Provider must expose a complete(messages) method.")
        messages = [
            {"role": "system", "content": "You are an evidence-constrained editor. Return ONLY valid JSON with exactly these keys: title (string), summary (string), sections (array of objects with heading and content). Improve clarity using only facts in the input and baseline report. Do not invent data, sources, metrics, legal conclusions, financial advice, or personal details. Preserve uncertainty and every source excerpt exactly. Never propose external actions. Do not include warnings or actions."},
            {"role": "user", "content": json.dumps({"agent": slug, "input": payload, "baseline_report": result}, ensure_ascii=False, default=str)},
        ]
        try:
            enhanced = json.loads(provider.complete(messages))
        except (json.JSONDecodeError, TypeError):
            raise ValueError("AI provider must return a valid JSON object; no partial AI output was applied.") from None
        if not isinstance(enhanced, dict) or not isinstance(enhanced.get("title"), str) or not isinstance(enhanced.get("summary"), str) or not isinstance(enhanced.get("sections"), list):
            raise ValueError("AI provider response does not match the required report schema.")
        if any(not isinstance(item, dict) or not isinstance(item.get("heading"), str) or "content" not in item for item in enhanced["sections"]):
            raise ValueError("AI provider returned an invalid report section.")
        result["title"], result["summary"], result["sections"] = enhanced["title"], enhanced["summary"], enhanced["sections"]
        result["warnings"].append("AI-assisted text may contain errors. Verify every factual statement and source.")
        result["warnings"].append("Input content was sent to the configured third-party AI endpoint; do not submit confidential or regulated data unless authorized.")
    return result
