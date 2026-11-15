"""Tests for isolated, self-contained per-product release archives."""
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from build_bundles import build_all

class ProductBundleTests(unittest.TestCase):
    def test_builds_ten_isolated_archives_with_required_contents(self):
        with tempfile.TemporaryDirectory() as temp:
            paths = build_all(ROOT, pathlib.Path(temp))
            self.assertEqual(len(paths), 10)
            for archive in paths:
                with self.subTest(archive=archive.name):
                    with zipfile.ZipFile(archive) as bundle:
                        names = set(bundle.namelist())
                        self.assertIn("README.md", names)
                        self.assertIn("manifest.json", names)
                        self.assertIn("SEO_LISTING.json", names)
                        self.assertIn("LICENSE.txt", names)
                        self.assertIn("THIRD_PARTY_NOTICES.md", names)
                        self.assertIn("run.py", names)
                        self.assertIn("jarvis_agent/workflow.py", names)
                        self.assertIn("examples/input.json", names)
                        manifest = json.loads(bundle.read("manifest.json"))
                        self.assertEqual(manifest["slug"], archive.stem)
                        self.assertEqual(manifest["runtime_dependencies"], [])
                        source = bundle.read("jarvis_agent/workflow.py").decode()
                        self.assertEqual(source.count("\ndef "), 1, "Bundle must contain exactly one product workflow.")

    def test_each_bundle_runs_its_sample_without_network_or_install(self):
        with tempfile.TemporaryDirectory() as temp:
            archives = build_all(ROOT, pathlib.Path(temp))
            for archive in archives:
                with self.subTest(archive=archive.name):
                    target = pathlib.Path(temp) / archive.stem
                    target.mkdir()
                    with zipfile.ZipFile(archive) as bundle:
                        bundle.extractall(target)
                    result = subprocess.run([sys.executable, "run.py", "examples/input.json"], cwd=target, capture_output=True, text=True, timeout=10)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    output = json.loads(result.stdout)
                    self.assertEqual(output["agent"], archive.stem)
                    self.assertTrue(output["title"])
                    self.assertEqual(output["actions"], [])

if __name__ == "__main__":
    unittest.main()
