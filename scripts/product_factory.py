#!/usr/bin/env python3
"""Zero-dependency product manifest intake and validation for the Zubair Product Factory."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

CHANNELS = {"kdp-paperback", "kdp-kindle", "gumroad-kit"}
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
REQUIRED = ("slug", "channel", "idea", "language", "theme", "audience", "price_usd", "status")


def validate_manifest(data: dict) -> list[str]:
    errors = [f"missing required field: {key}" for key in REQUIRED if key not in data]
    if data.get("channel") not in CHANNELS:
        errors.append("channel must be one of: " + ", ".join(sorted(CHANNELS)))
    slug = data.get("slug", "")
    if not isinstance(slug, str) or not SLUG_RE.fullmatch(slug):
        errors.append("slug must contain lowercase letters, numbers, and single hyphens only")
    if not isinstance(data.get("idea"), str) or not data["idea"].strip():
        errors.append("idea must be a non-empty string")
    if not isinstance(data.get("language"), list) or not data["language"] or any(x not in {"en", "ar"} for x in data["language"]):
        errors.append("language must be a non-empty list containing only en and/or ar")
    price = data.get("price_usd")
    if isinstance(price, bool) or not isinstance(price, (int, float)) or price <= 0:
        errors.append("price_usd must be a positive number")
    if data.get("status") not in {"draft", "produced", "approved", "published"}:
        errors.append("status must be draft, produced, approved, or published")
    if data.get("status") in {"approved", "published"} and not data.get("approval_issue"):
        errors.append("approved/published manifests require an approval_issue")
    return errors


def version_fingerprint(data: dict) -> str:
    """Hash product-defining inputs; workflow metadata does not change the product version."""
    stable = {k: v for k, v in data.items() if k not in {"approval_issue", "status", "outputs", "published", "version_sha256"}}
    encoded = json.dumps(stable, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def create_manifest(args: argparse.Namespace) -> Path:
    data = {
        "slug": args.slug,
        "channel": args.channel,
        "idea": args.idea.strip(),
        "language": [x.strip() for x in args.language.split(",") if x.strip()],
        "theme": args.theme,
        "audience": args.audience,
        "trim": args.trim or None,
        "pages": args.pages,
        "illustrations_required": args.illustrations_required,
        "price_usd": args.price,
        "status": "draft",
        "approval_issue": None,
        "version_sha256": None,
        "outputs": {"interior_pdf": None, "cover_pdf": None, "listing": None},
        "published": {"kdp_url": None, "gumroad_url": None},
    }
    errors = validate_manifest(data)
    if errors:
        raise SystemExit("\n".join(errors))
    data["version_sha256"] = version_fingerprint(data)
    path = Path(args.out) / f"{args.slug}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise SystemExit(f"refusing to overwrite existing manifest: {path}")
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    create = sub.add_parser("create")
    create.add_argument("--slug", required=True)
    create.add_argument("--channel", required=True, choices=sorted(CHANNELS))
    create.add_argument("--idea", required=True)
    create.add_argument("--language", default="en")
    create.add_argument("--theme", default="general")
    create.add_argument("--audience", default="general")
    create.add_argument("--trim")
    create.add_argument("--pages", type=int)
    create.add_argument("--illustrations-required", type=int)
    create.add_argument("--price", type=float, default=9.0)
    create.add_argument("--out", default="manifests")
    args = parser.parse_args()
    if args.command == "create":
        print(create_manifest(args))


if __name__ == "__main__":
    main()
