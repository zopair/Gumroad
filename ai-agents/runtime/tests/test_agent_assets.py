"""SEO and original product-asset generation tests."""
import json
import pathlib
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))
from scripts.build_agent_assets import build

SEO_PATH = REPO_ROOT / "ai-agents" / "runtime" / "seo-listings.json"

class AgentAssetTests(unittest.TestCase):
    def test_ten_distinct_seo_listing_briefs_meet_quality_bounds(self):
        listings = json.loads(SEO_PATH.read_text(encoding="utf-8"))["listings"]
        self.assertEqual(len(listings), 10)
        self.assertEqual(len({item["slug"] for item in listings}), 10)
        self.assertEqual(len({item["primary_keyword"] for item in listings}), 10)
        for item in listings:
            with self.subTest(product=item["slug"]):
                self.assertLessEqual(len(item["seo_title"]), 70)
                self.assertGreaterEqual(len(item["meta_description"]), 100)
                self.assertLessEqual(len(item["meta_description"]), 160)
                self.assertGreaterEqual(len(item["tags"]), 4)
                self.assertGreaterEqual(len(item["faq"]), 3)
                self.assertTrue(item["problem"])
                self.assertTrue(item["solution"])

    def test_asset_builder_generates_valid_product_specific_vector_art(self):
        with tempfile.TemporaryDirectory() as temp:
            output = pathlib.Path(temp)
            self.assertEqual(build(output), 10)
            for product in json.loads(SEO_PATH.read_text(encoding="utf-8"))["listings"]:
                folder = output / product["slug"]
                listing, cover = folder / "listing.md", folder / "assets" / "cover.svg"
                thumb = folder / "assets" / "thumbnail.svg"
                with self.subTest(product=product["slug"]):
                    self.assertTrue(listing.is_file())
                    self.assertIn(product["name"], listing.read_text(encoding="utf-8"))
                    ET.parse(cover)
                    ET.parse(thumb)

if __name__ == "__main__":
    unittest.main()
