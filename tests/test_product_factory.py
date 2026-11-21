import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from argparse import Namespace

from scripts.product_factory import create_manifest, validate_manifest, version_fingerprint


class ProductFactoryTests(unittest.TestCase):
    def manifest(self):
        return {
            "slug": "fruit-friends", "channel": "kdp-paperback",
            "idea": "Fruit coloring book", "language": ["en"], "theme": "fruits",
            "audience": "ages 4-8", "price_usd": 7.99, "status": "draft",
            "approval_issue": None,
        }

    def test_rejects_unsafe_slug(self):
        data = self.manifest()
        data["slug"] = "../outside"
        self.assertTrue(any("slug" in error for error in validate_manifest(data)))

    def test_rejects_unknown_channel(self):
        data = self.manifest()
        data["channel"] = "automatic-publish"
        self.assertTrue(any("channel" in error for error in validate_manifest(data)))

    def test_approved_manifest_requires_issue(self):
        data = self.manifest()
        data["status"] = "approved"
        self.assertTrue(any("approval_issue" in error for error in validate_manifest(data)))

    def test_version_fingerprint_ignores_workflow_metadata(self):
        first = self.manifest()
        second = {**first, "status": "approved", "approval_issue": 12}
        self.assertEqual(version_fingerprint(first), version_fingerprint(second))

    def test_version_fingerprint_matches_workflow_with_stored_hash(self):
        data = self.manifest()
        data["version_sha256"] = version_fingerprint(data)
        workflow_fields = {"approval_issue", "status", "outputs", "published", "version_sha256"}
        stable = {key: value for key, value in data.items() if key not in workflow_fields}
        workflow_hash = hashlib.sha256(json.dumps(
            stable, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode()).hexdigest()
        self.assertEqual(data["version_sha256"], workflow_hash)
        self.assertEqual(version_fingerprint(data), workflow_hash)

    def test_creates_manifest_without_overwriting(self):
        with tempfile.TemporaryDirectory() as tmp:
            args = Namespace(slug="sample-kit", channel="gumroad-kit", idea="A useful kit",
                language="en", theme="business", audience="freelancers", trim=None,
                pages=None, illustrations_required=None, price=9.0, out=tmp)
            path = create_manifest(args)
            self.assertTrue(path.exists())
            self.assertEqual(json.loads(path.read_text())["status"], "draft")
            with self.assertRaises(SystemExit):
                create_manifest(args)


if __name__ == "__main__":
    unittest.main()
