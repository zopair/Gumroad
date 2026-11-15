"""Packaging contract tests for product metadata and legal provenance."""
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class PackagingContractTests(unittest.TestCase):
    def test_each_product_has_a_machine_readable_release_manifest(self):
        manifest = json.loads((ROOT / "products.json").read_text(encoding="utf-8"))
        self.assertEqual(len(manifest["products"]), 10)
        slugs = {item["slug"] for item in manifest["products"]}
        self.assertEqual(len(slugs), 10)
        for product in manifest["products"]:
            with self.subTest(product=product["slug"]):
                self.assertTrue(product["name"])
                self.assertTrue(product["primary_keyword"])
                self.assertTrue(product["short_description"])
                self.assertTrue(product["upstream"]["url"])
                self.assertTrue(product["upstream"]["commit"])
                self.assertIn(product["upstream"]["license"], {"MIT", "Apache-2.0"})
                self.assertFalse(product["release_ready"])

    def test_no_product_manifest_contains_live_publishing_credentials(self):
        manifest_text = (ROOT / "products.json").read_text(encoding="utf-8").lower()
        for forbidden in ("gumroad_access_token", "api_secret", "private_key"):
            self.assertNotIn(forbidden, manifest_text)


if __name__ == "__main__":
    unittest.main()
