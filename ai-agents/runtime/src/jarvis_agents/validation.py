"""Input validation and text helpers shared by product workflows."""
from __future__ import annotations
import re
from collections.abc import Mapping
from typing import Any

def required_text(data: Mapping[str, Any], key: str, *, label: str | None = None) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"'{label or key}' is required and must be non-empty text.")
    return value.strip()

def optional_text(data: Mapping[str, Any], key: str, default: str = "") -> str:
    value = data.get(key, default)
    if value is None:
        return default
    if not isinstance(value, str):
        raise ValueError(f"'{key}' must be text.")
    return value.strip()

def text_list(value: Any, field: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise ValueError(f"'{field}' must be a list of text values.")
    return [item.strip() for item in value if item.strip()]

def report(title: str, summary: str, sections: list[dict[str, Any]], warnings: list[str] | None = None) -> dict[str, Any]:
    return {"title": title, "summary": summary, "sections": sections, "warnings": warnings or [], "actions": []}

def section(heading: str, content: Any) -> dict[str, Any]:
    return {"heading": heading, "content": content}

def words(text: str) -> list[str]:
    return re.findall(r"[\w'-]+", text.casefold(), flags=re.UNICODE)

def sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?؟])\s+", text.strip())
    return [part.strip() for part in parts if part.strip()]
