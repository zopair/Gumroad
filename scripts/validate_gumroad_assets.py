#!/usr/bin/env python3
"""Validate repository PNG assets against Gumroad and brand export standards."""

from __future__ import annotations

import argparse
import struct
from dataclasses import dataclass
from pathlib import Path

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
MIB = 1024 * 1024
GUMROAD_COVER_MAX_BYTES = 50 * MIB


@dataclass(frozen=True)
class PngMetadata:
    width: int
    height: int
    dpi_x: float | None
    dpi_y: float | None


def parse_png_metadata(path: Path) -> PngMetadata:
    """Read PNG dimensions and optional physical pixel density without Pillow."""
    with path.open("rb") as stream:
        if stream.read(8) != PNG_SIGNATURE:
            raise ValueError(f"Not a PNG file: {path}")

        width = height = None
        dpi_x = dpi_y = None
        while True:
            header = stream.read(8)
            if len(header) != 8:
                raise ValueError(f"PNG is truncated before IEND: {path}")
            length, chunk_type = struct.unpack(">I4s", header)
            payload = stream.read(length)
            crc = stream.read(4)
            if len(payload) != length or len(crc) != 4:
                raise ValueError(f"PNG has a truncated chunk: {path}")

            if chunk_type == b"IHDR":
                if length != 13:
                    raise ValueError(f"Invalid PNG IHDR chunk: {path}")
                width, height = struct.unpack(">II", payload[:8])
            elif chunk_type == b"pHYs":
                if length == 9:
                    x_ppm, y_ppm, unit = struct.unpack(">IIB", payload)
                    if unit == 1:
                        dpi_x = x_ppm * 0.0254
                        dpi_y = y_ppm * 0.0254
            elif chunk_type == b"IEND":
                break

        if not width or not height:
            raise ValueError(f"PNG is missing valid dimensions: {path}")
        return PngMetadata(width, height, dpi_x, dpi_y)


def validate_asset(path: Path, root: Path) -> list[str]:
    """Return policy violations for one PNG asset."""
    relative = path.relative_to(root).as_posix()
    errors: list[str] = []
    size = path.stat().st_size

    try:
        info = parse_png_metadata(path)
    except (OSError, ValueError, struct.error) as exc:
        return [f"{relative}: {exc}"]

    if size == 0:
        errors.append(f"{relative}: file is empty")

    is_product_asset = relative.startswith("products/")
    is_thumbnail = is_product_asset and path.stem.lower() == "thumbnail"

    if is_product_asset:
        if size >= GUMROAD_COVER_MAX_BYTES:
            errors.append(f"{relative}: Gumroad image covers must be under 50 MiB")
        if info.dpi_x is None or info.dpi_y is None or info.dpi_x < 72 or info.dpi_y < 72:
            errors.append(f"{relative}: Gumroad image assets require at least 72 DPI metadata")
        if max(info.width, info.height) > 4096:
            errors.append(f"{relative}: longest side exceeds Gumroad's 4096 px image threshold")

        if is_thumbnail:
            if info.width < 600 or info.height < 600 or info.width != info.height:
                errors.append(f"{relative}: thumbnail must be square and at least 600x600 px")
        elif info.width < 1280 or info.height < 720:
            errors.append(f"{relative}: Gumroad cover must be at least 1280x720 px")

    expected = {
        "storefront/brand-avatar.png": (1024, 1024),
        "storefront/favicon.png": (128, 128),
        "storefront/brand-wordmark.png": (1600, 400),
    }.get(relative)
    if expected and (info.width, info.height) != expected:
        errors.append(
            f"{relative}: expected {expected[0]}x{expected[1]} px, "
            f"got {info.width}x{info.height} px"
        )

    if relative.startswith("marketing/") and (info.width, info.height) != (1000, 1500):
        errors.append(
            f"{relative}: campaign artwork must be 1000x1500 px, "
            f"got {info.width}x{info.height} px"
        )

    return errors


def validate_tree(root: Path) -> list[str]:
    errors: list[str] = []
    for folder in ("products", "storefront", "marketing"):
        base = root / folder
        if base.exists():
            for path in sorted(base.rglob("*.png")):
                errors.extend(validate_asset(path, root))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()

    errors = validate_tree(args.root.resolve())
    if errors:
        print("Asset validation failed:")
        for error in errors:
            print(f" - {error}")
        return 1

    print("Asset validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
