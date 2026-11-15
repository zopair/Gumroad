"""Build deterministic, isolated ZIP previews for the ten JARVIS products."""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import zipfile
from pathlib import Path
from typing import Any

EXAMPLES = {
    "rankmaster-ai": "rankmaster.json", "leadscout-bot": "leadscout.json",
    "tradetrend-analyst": "tradetrend.json", "docusense-support": "docusense.json",
    "socialsync-ai": "socialsync.json", "mailforge-pro": "mailforge.json",
    "contentflip-ai": "contentflip.json", "estateguard-ai": "estateguard.json",
    "codesentinel": "codesentinel.json", "marketmind-ai": "marketmind.json",
}

FUNCTIONS = {
    "rankmaster-ai": "rankmaster",
    "leadscout-bot": "leadscout",
    "tradetrend-analyst": "tradetrend",
    "docusense-support": "docusense",
    "socialsync-ai": "socialsync",
    "mailforge-pro": "mailforge",
    "contentflip-ai": "contentflip",
    "estateguard-ai": "estateguard",
    "codesentinel": "codesentinel",
    "marketmind-ai": "marketmind",
}
ZIP_TIME = (2020, 1, 1, 0, 0, 0)

LICENSE = """JARVIS PRODUCT LICENSE — DRAFT FOR SELLER REVIEW

Copyright © 2026 Zubair Digital Kits. All rights reserved.

IMPORTANT: This is a proposed commercial license draft. It must be reviewed and
approved by the seller before the product is offered for sale. No sale or
distribution authorization is implied by the presence of this file.

Proposed grant: after purchase and subject to the final seller-approved terms,
the purchaser receives a non-exclusive, non-transferable license to install
and use this product for the purchaser's own internal personal or business
workflows. The purchaser may provide access to employees or contractors only
as reasonably necessary for that internal use.

The purchaser may not resell, sublicense, publish, redistribute, or make the
source code or product files available to unrelated third parties; remove
copyright or legal notices; or use the product in violation of applicable law.

The product is supplied without a promise of uninterrupted operation, fitness
for a particular purpose, business results, ranking improvements, investment
returns, legal conclusions, or complete security detection. The purchaser is
responsible for reviewing outputs and maintaining appropriate backups and
security controls.

This draft does not replace a final agreement adapted to the seller's
jurisdiction, buyer locations, consumer law, privacy requirements, and refund
policy. If it has not been approved, do not represent it as the final license.
"""

NOTICES = """# Third-party notices and source provenance

This product bundle contains an original, product-specific workflow authored
for Zubair Digital Kits and uses only the Python standard library at runtime.
No source code from the upstream repositories listed in the internal research
register is included in this archive. Those repositories were research
references only and are not dependencies of this bundle.

No third-party model weights, datasets, fonts, icon packs, or external binaries
are bundled. Product artwork is original JARVIS family artwork. The Python
standard library is distributed under its respective PSF license; consult
https://docs.python.org/3/license.html for details.

Do not add upstream source, assets, models, or datasets to this bundle without
a separate pinned-commit, dependency, attribution, and license audit.
"""

def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))

def _workflow_module(source: str, function_name: str) -> str:
    tree = ast.parse(source)
    imports = []
    selected = None
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            imports.append(ast.get_source_segment(source, node))
        elif isinstance(node, ast.FunctionDef) and node.name == function_name:
            selected = ast.get_source_segment(source, node)
    if not selected:
        raise ValueError(f"Workflow function '{function_name}' was not found.")
    return (
        '"""Isolated workflow module generated from the reviewed JARVIS runtime."""\n'
        + "\n".join(item for item in imports if item)
        + "\n\n"
        + selected
        + "\n"
    )

def _readme(product: dict[str, Any], seo: dict[str, Any]) -> str:
    features = "\n".join(f"- {item}" for item in product.get("features", []))
    limits = "\n".join(f"- {item}" for item in product.get("limitations", []))
    return f"""# {product['name']}

**JARVIS by Zubair Digital Kits** — {product['buyer']}

{product['short_description']}

## Included
{features}

## Requirements
- Python 3.11 or newer
- No third-party runtime dependencies
- No account, API key, database, browser, or network connection required

## Quick start
1. Extract this ZIP to a folder.
2. Install Python 3.11+ if it is not already installed.
3. Open a terminal in this folder.
4. Run: `python run.py examples/input.json`
5. The JSON report is printed to the terminal. To save it, run:
   `python run.py examples/input.json --output report.json`

## Input format
Edit `examples/input.json` with your own information while preserving the JSON structure. The output is a structured JSON report. All work is performed locally; this package does not send input to an external service.

## Product limitations
{limits}

## SEO listing draft
- SEO title: {seo['seo_title']}
- Primary keyword: {seo['primary_keyword']}
- Meta description: {seo['meta_description']}

## Important
Review all generated material before relying on or publishing it. This tool does not guarantee business, financial, legal, security, search-ranking, or marketing outcomes. See `LICENSE.txt` (seller-review draft) and `THIRD_PARTY_NOTICES.md`.
"""

def _add_sbom_and_checksums(files: dict[str, str | bytes], slug: str, product_name: str) -> None:
    file_records = []
    for name, content in sorted(files.items()):
        raw = content.encode("utf-8") if isinstance(content, str) else content
        digest = hashlib.sha256(raw).hexdigest()
        file_records.append({
            "fileName": f"./{name}",
            "SPDXID": f"SPDXRef-File-{hashlib.sha256(name.encode('utf-8')).hexdigest()[:16]}",
            "checksums": [{"algorithm": "SHA256", "checksumValue": digest}],
            "licenseConcluded": "NOASSERTION",
            "licenseInfoInFiles": ["NOASSERTION"],
            "copyrightText": "NOASSERTION",
        })
    namespace_seed = json.dumps(file_records, sort_keys=True, separators=(",", ":")).encode("utf-8")
    namespace_hash = hashlib.sha256(namespace_seed).hexdigest()
    sbom = {
        "spdxVersion": "SPDX-2.3",
        "dataLicense": "CC0-1.0",
        "SPDXID": "SPDXRef-DOCUMENT",
        "name": f"JARVIS {product_name} preview",
        "documentNamespace": f"https://spdx.org/spdxdocs/jarvis-{slug}-{namespace_hash}",
        "creationInfo": {
            "creators": ["Tool: JARVIS isolated bundle builder"],
            "created": "2026-11-15T00:00:00Z",
            "comment": "Generated inventory for this preview archive. License conclusions are intentionally NOASSERTION; the included commercial license is a draft requiring seller approval.",
        },
        "packages": [{
            "name": slug,
            "SPDXID": "SPDXRef-Package",
            "versionInfo": "0.1.0-preview",
            "downloadLocation": "NOASSERTION",
            "filesAnalyzed": True,
            "licenseConcluded": "NOASSERTION",
            "licenseDeclared": "NOASSERTION",
            "copyrightText": "Copyright (c) 2026 Zubair Digital Kits",
            "primaryPackagePurpose": "APPLICATION",
            "packageComment": "Original local workflow package. No upstream repository source or third-party runtime package is included. Commercial terms remain subject to seller approval.",
        }],
        "files": file_records,
        "relationships": [{
            "spdxElementId": "SPDXRef-DOCUMENT",
            "relationshipType": "DESCRIBES",
            "relatedSpdxElement": "SPDXRef-Package",
        }],
    }
    files["SBOM.spdx.json"] = json.dumps(sbom, ensure_ascii=False, indent=2) + "\n"
    manifest = []
    for name, content in sorted(files.items()):
        raw = content.encode("utf-8") if isinstance(content, str) else content
        manifest.append(f"{hashlib.sha256(raw).hexdigest()}  {name}")
    files["FILE_MANIFEST.sha256"] = "\n".join(manifest) + "\n"

def build_all(runtime_root: Path, output_dir: Path) -> list[Path]:
    runtime_root = Path(runtime_root).resolve()
    repo_root = runtime_root.parents[1]
    products = _read_json(runtime_root / "products.json")["products"]
    listings = _read_json(runtime_root / "seo-listings.json")["listings"]
    listing_by_slug = {item["slug"]: item for item in listings}
    workflow_source = (runtime_root / "src/jarvis_agents/workflows.py").read_text(encoding="utf-8")
    validation_source = (runtime_root / "src/jarvis_agents/validation.py").read_text(encoding="utf-8")
    output_dir.mkdir(parents=True, exist_ok=True)
    archives = []
    seen = set()

    for product in products:
        slug = product["slug"]
        if slug not in FUNCTIONS or slug in seen:
            raise ValueError(f"Unexpected or duplicate product slug: {slug}")
        seen.add(slug)
        if slug not in listing_by_slug:
            raise ValueError(f"Missing SEO listing for {slug}")
        sample_path = runtime_root / "examples" / EXAMPLES[slug]
        if not sample_path.is_file():
            raise FileNotFoundError(f"Missing sample input for {slug}")
        seo = listing_by_slug[slug]
        function_name = FUNCTIONS[slug]
        files = {
            "README.md": _readme(product, seo),
            "manifest.json": json.dumps({
                "schema_version": "1.0",
                "publisher": "Zubair Digital Kits",
                "family": "JARVIS",
                "slug": slug,
                "name": product["name"],
                "version": "0.1.0-preview",
                "runtime_dependencies": [],
                "python_requires": ">=3.11",
                "entrypoint": "python run.py examples/input.json",
                "network_access": False,
                "upstream_code_included": False,
                "release_status": "preview_not_release_approved",
                "limitations": product.get("limitations", []),
            }, ensure_ascii=False, indent=2) + "\n",
            "SEO_LISTING.json": json.dumps(seo, ensure_ascii=False, indent=2) + "\n",
            "LICENSE.txt": LICENSE,
            "THIRD_PARTY_NOTICES.md": NOTICES,
            "jarvis_agent/__init__.py": f'"""Isolated {product["name"]} workflow."""\nfrom .workflow import {function_name} as run_agent\n',
            "jarvis_agent/validation.py": validation_source,
            "jarvis_agent/workflow.py": _workflow_module(workflow_source, function_name),
            "run.py": """from __future__ import annotations
import argparse
import json
from pathlib import Path
from jarvis_agent import run_agent

def main() -> int:
    parser = argparse.ArgumentParser(description="Run this JARVIS product locally.")
    parser.add_argument("input", type=Path, help="UTF-8 JSON input file")
    parser.add_argument("--output", type=Path, help="Optional output JSON path")
    args = parser.parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        parser.error("Input JSON must be an object.")
    result = run_agent(payload)
    result.update({"schema_version": "1.0", "agent": PRODUCT_SLUG, "actions": []})
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0

PRODUCT_SLUG = __PRODUCT_SLUG__

if __name__ == "__main__":
    raise SystemExit(main())
""".replace("__PRODUCT_SLUG__", repr(slug)),
            "examples/input.json": sample_path.read_text(encoding="utf-8"),
        }
        art_root = repo_root / "ai-agents" / "products" / slug / "assets"
        for art_name in ("cover.png", "cover.svg", "thumbnail.png", "thumbnail.svg"):
            art_path = art_root / art_name
            if not art_path.is_file():
                raise FileNotFoundError(f"Missing product artwork: {art_path}")
            files[f"assets/{art_name}"] = art_path.read_bytes()

        _add_sbom_and_checksums(files, slug, product["name"])

        archive_path = output_dir / f"{slug}.zip"
        with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            for name, content in sorted(files.items()):
                info = zipfile.ZipInfo(name, date_time=ZIP_TIME)
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                if isinstance(content, str):
                    archive.writestr(info, content.encode("utf-8"))
                else:
                    archive.writestr(info, content)
        archives.append(archive_path)

    if seen != set(FUNCTIONS):
        raise ValueError(f"Product registry mismatch. Missing: {sorted(set(FUNCTIONS) - seen)}")
    return archives

def main() -> int:
    parser = argparse.ArgumentParser(description="Build isolated JARVIS product ZIP previews.")
    parser.add_argument("--output-dir", type=Path, default=Path("dist"))
    args = parser.parse_args()
    runtime_root = Path(__file__).resolve().parents[1]
    archives = build_all(runtime_root, args.output_dir)
    checksums = {}
    for archive in archives:
        checksums[archive.name] = hashlib.sha256(archive.read_bytes()).hexdigest()
    (args.output_dir / "SHA256SUMS.json").write_text(json.dumps(checksums, indent=2) + "\n", encoding="utf-8")
    print(f"Built {len(archives)} isolated product preview archives in {args.output_dir}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
