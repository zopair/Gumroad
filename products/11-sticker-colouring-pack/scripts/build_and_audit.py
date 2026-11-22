#!/usr/bin/env python3
"""Validate source assets and build the customer ZIP and print-ready colouring PDF."""
from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path

from PIL import Image
from reportlab.lib.units import inch
from reportlab.platypus import BaseDocTemplate, Frame, Image as PDFImage, PageBreak, PageTemplate

ROOT = Path(__file__).resolve().parents[3]
PRODUCT = ROOT / "products" / "11-sticker-colouring-pack"
SOURCE = PRODUCT / "source"
MANIFEST = PRODUCT / "manifest.json"
DELIVERY = PRODUCT / "delivery"
REPORT = PRODUCT / "quality-report.md"


def git_blob_sha1(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def validate() -> tuple[list[str], list[str], dict]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    errors: list[str] = []
    warnings: list[str] = []
    seen: dict[str, str] = {}
    counts = {"stickers_png": 0, "colouring_pages_jpg": 0, "original_renders_jpg": 0}
    for item in manifest["files"]:
        path = SOURCE / item["path"]
        if not path.is_file():
            errors.append(f"Missing: {item['path']}")
            continue
        data = path.read_bytes()
        if len(data) != item["size_bytes"]:
            errors.append(f"Size mismatch: {item['path']}")
        if git_blob_sha1(data) != item["git_blob_sha1"]:
            errors.append(f"Git blob SHA-1 mismatch: {item['path']}")
        digest = hashlib.sha256(data).hexdigest()
        if digest in seen:
            warnings.append(f"Duplicate content: {item['path']} = {seen[digest]}")
        else:
            seen[digest] = item["path"]
        if item["path"].endswith(".png") and item["path"].startswith("stickers-transparent/"):
            counts["stickers_png"] += 1
            try:
                with Image.open(path) as image:
                    image.verify()
                with Image.open(path) as image:
                    if image.format != "PNG":
                        errors.append(f"Not PNG: {item['path']}")
                    if image.mode not in ("RGBA", "LA") and "transparency" not in image.info:
                        errors.append(f"No transparency channel: {item['path']}")
            except Exception as exc:
                errors.append(f"Unreadable image {item['path']}: {exc}")
        elif item["path"].startswith("colouring-pages/"):
            counts["colouring_pages_jpg"] += 1
            try:
                with Image.open(path) as image:
                    image.verify()
                with Image.open(path) as image:
                    if image.format != "JPEG" or image.size != (1600, 1600):
                        errors.append(f"Unexpected colouring page format/dimensions: {item['path']} {image.format} {image.size}")
            except Exception as exc:
                errors.append(f"Unreadable image {item['path']}: {exc}")
        elif item["path"].startswith("original-renders-400px/"):
            counts["original_renders_jpg"] += 1
            try:
                with Image.open(path) as image:
                    image.verify()
                with Image.open(path) as image:
                    if image.format != "JPEG" or image.size != (400, 400):
                        errors.append(f"Unexpected original render format/dimensions: {item['path']} {image.format} {image.size}")
            except Exception as exc:
                errors.append(f"Unreadable image {item['path']}: {exc}")
    expected = {"stickers_png": 18, "colouring_pages_jpg": 13, "original_renders_jpg": 31}
    for key, value in expected.items():
        if counts[key] != value:
            errors.append(f"Count mismatch {key}: expected {value}, got {counts[key]}")
    for relative_path, expected_size, _kind in json.loads((SOURCE / "spec.json").read_text(encoding="utf-8")):
        path = SOURCE / relative_path
        if not path.is_file():
            errors.append(f"Missing from spec: {relative_path}")
            continue
        try:
            with Image.open(path) as image:
                if list(image.size) != expected_size:
                    errors.append(f"Spec dimension mismatch: {relative_path}; expected {expected_size}, got {list(image.size)}")
        except Exception as exc:
            errors.append(f"Cannot inspect spec image {relative_path}: {exc}")
    cover = SOURCE / "cover.png"
    try:
        with Image.open(cover) as image:
            if image.format != "PNG" or image.size != (1429, 804):
                errors.append(f"Unexpected cover format/dimensions: {image.format} {image.size}")
    except Exception as exc:
        errors.append(f"Unreadable cover: {exc}")
    if len(manifest["files"]) != 67:
        errors.append(f"Manifest file count expected 67, got {len(manifest['files'])}")
    return errors, warnings, counts


def build_pdf() -> Path:
    output = DELIVERY / "colouring-pages.pdf"
    DELIVERY.mkdir(parents=True, exist_ok=True)
    pages = sorted((SOURCE / "colouring-pages").glob("*.jpg"))
    page_size = 5.333333 * inch
    document = BaseDocTemplate(str(output), pagesize=(page_size, page_size))
    frame = Frame(0, 0, page_size, page_size, leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    document.addPageTemplates([PageTemplate(id="colouring-pages", frames=[frame])])
    story = []
    for index, path in enumerate(pages):
        story.append(PDFImage(str(path), width=page_size, height=page_size))
        if index < len(pages) - 1:
            story.append(PageBreak())
    document.build(story)
    return output


def build_zip(pdf_path: Path) -> Path:
    output = DELIVERY / "sticker-colouring-pack.zip"
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for path in sorted(SOURCE.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(SOURCE).as_posix())
        archive.write(pdf_path, "delivery/colouring-pages.pdf")
    return output


def main() -> int:
    errors, warnings, counts = validate()
    if errors:
        REPORT.write_text("# Sticker Pack QA — FAILED\n\n" + "\n".join(f"- {x}" for x in errors), encoding="utf-8")
        print("\n".join(errors))
        return 1
    pdf_path = build_pdf()
    zip_path = build_zip(pdf_path)
    lines = [
        "# Sticker & Colouring Pack — Quality Report",
        "",
        "**Result: PASS** — source files match the committed manifest and image checks.",
        "",
        f"- Stickers: {counts['stickers_png']}",
        f"- Colouring pages: {counts['colouring_pages_jpg']}",
        f"- Original 400px renders: {counts['original_renders_jpg']}",
        f"- Print PDF: {pdf_path.stat().st_size:,} bytes; 13 square pages at approximately 5.33 in.",
        f"- Delivery ZIP: {zip_path.stat().st_size:,} bytes.",
        "- PNGs: readable, PNG format, transparency channel present.",
        "- Colouring pages: readable 1600 × 1600 JPEG.",
        "- Original renders: readable 400 × 400 JPEG.",
        "- Git blob SHA-1 and byte-size checks: all passed.",
        "",
        "## Warnings",
        *([f"- {warning}" for warning in warnings] if warnings else ["- None."]),
        "",
        "## Limitations",
        "- Visual/artistic review and legal ownership review are not automated.",
        "- The seller license remains a candidate and requires final seller approval.",
        "- AI-generated/upscaled source disclosures are retained; no professional print guarantee is made.",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
