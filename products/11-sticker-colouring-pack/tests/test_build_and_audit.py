import hashlib
import json
import sys
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))
from build_and_audit import git_blob_sha1  # noqa: E402


class GitBlobSha1Tests(unittest.TestCase):
    def test_empty_file_matches_git_empty_blob(self):
        self.assertEqual(
            git_blob_sha1(b""),
            "e69de29bb2d1d6434b8b29ae775ad8c2e48c5391",
        )

    def test_blob_hash_includes_git_header_and_payload(self):
        payload = b"sticker pack"
        expected = hashlib.sha1(b"blob 12\0" + payload).hexdigest()
        self.assertEqual(git_blob_sha1(payload), expected)


class ManifestTests(unittest.TestCase):
    def test_manifest_inventory_has_expected_pack_counts(self):
        manifest_path = Path(__file__).resolve().parents[1] / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(manifest["total_files"], 67)
        self.assertEqual(manifest["counts"]["stickers_png"], 18)
        self.assertEqual(manifest["counts"]["colouring_pages_jpg"], 13)
        self.assertEqual(manifest["counts"]["original_renders_jpg"], 31)
        self.assertNotIn("pack-full.zip", [item["path"] for item in manifest["files"]])


if __name__ == "__main__":
    unittest.main()
