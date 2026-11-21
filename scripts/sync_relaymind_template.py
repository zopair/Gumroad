#!/usr/bin/env python3
"""Embed templates/client_workflow.yml into index.html (offline fallback copy).

Run after editing the workflow template:  python scripts/sync_relaymind_template.py
"""
import html
import re
from pathlib import Path

root = Path(__file__).resolve().parents[1]
tpl = (root / "templates" / "client_workflow.yml").read_text(encoding="utf-8").strip()
assert "</script" not in tpl.lower()
page = root / "index.html"
src = page.read_text(encoding="utf-8")
pattern = re.compile(r'(<script type="text/plain" id="workflowTemplate">\n)(.*?)(\n</script>)', re.S)
assert pattern.search(src), "workflowTemplate block not found"
page.write_text(pattern.sub(lambda m: m.group(1) + tpl + m.group(3), src, count=1), encoding="utf-8")
print("index.html synced with templates/client_workflow.yml")
