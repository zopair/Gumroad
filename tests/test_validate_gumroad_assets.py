import struct
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT / "scripts"))

from validate_gumroad_assets import parse_png_metadata, validate_asset


def make_png(width, height, dpi=96):
    ppm = round(dpi / 0.0254)
    chunks = []
    def chunk(kind, payload):
        return struct.pack(">I", len(payload)) + kind + payload + b"\x00\x00\x00\x00"
    chunks.append(chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)))
    chunks.append(chunk(b"pHYs", struct.pack(">IIB", ppm, ppm, 1)))
    chunks.append(chunk(b"IEND", b""))
    return b"\x89PNG\r\n\x1a\n" + b"".join(chunks)


class GumroadAssetValidationTests(unittest.TestCase):
    def test_reads_png_dimensions_and_dpi(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "cover.png"
            path.write_bytes(make_png(1600, 1000, 96))
            info = parse_png_metadata(path)
            self.assertEqual((info.width, info.height), (1600, 1000))
            self.assertGreaterEqual(info.dpi_x, 72)
            self.assertGreaterEqual(info.dpi_y, 72)

    def test_accepts_valid_product_cover(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "products" / "demo" / "assets" / "cover.png"
            path.parent.mkdir(parents=True)
            path.write_bytes(make_png(1600, 1000, 96))
            self.assertEqual(validate_asset(path, root), [])

    def test_rejects_product_cover_below_gumroad_minimum(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "products" / "demo" / "assets" / "cover.png"
            path.parent.mkdir(parents=True)
            path.write_bytes(make_png(1200, 700, 96))
            errors = validate_asset(path, root)
            self.assertTrue(any("1280x720" in error for error in errors))

    def test_rejects_cover_without_72_dpi_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "products" / "demo" / "assets" / "cover.png"
            path.parent.mkdir(parents=True)
            path.write_bytes(make_png(1600, 1000, 60))
            errors = validate_asset(path, root)
            self.assertTrue(any("72 DPI" in error for error in errors))

    def test_thumbnail_is_square_and_at_least_600_pixels(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "products" / "demo" / "assets" / "thumbnail.png"
            path.parent.mkdir(parents=True)
            path.write_bytes(make_png(600, 600, 96))
            self.assertEqual(validate_asset(path, root), [])
            path.write_bytes(make_png(600, 580, 96))
            errors = validate_asset(path, root)
            self.assertTrue(any("600x600" in error for error in errors))

    def test_rejects_cover_at_or_above_50_mib(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "products" / "demo" / "assets" / "cover.png"
            path.parent.mkdir(parents=True)
            path.write_bytes(make_png(1600, 1000, 96))
            with path.open("ab") as stream:
                stream.truncate(50 * 1024 * 1024)
            errors = validate_asset(path, root)
            self.assertTrue(any("under 50 MiB" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
