"""Tests for isolated, self-contained per-product release archives."""
import hashlib
import http.client
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
                        self.assertIn("web.py", names)
                        self.assertIn("index.html", names)
                        self.assertIn("app.js", names)
                        self.assertIn("styles.css", names)
                        self.assertIn("jarvis_agent/workflow.py", names)
                        self.assertIn("jarvis_agent/providers.py", names)
                        self.assertIn("examples/input.json", names)
                        self.assertIn("SBOM.spdx.json", names)
                        self.assertIn("FILE_MANIFEST.sha256", names)
                        sbom = json.loads(bundle.read("SBOM.spdx.json"))
                        self.assertEqual(sbom["spdxVersion"], "SPDX-2.3")
                        self.assertEqual(sbom["packages"][0]["name"], archive.stem)
                        manifest_lines = bundle.read("FILE_MANIFEST.sha256").decode().splitlines()
                        for line in manifest_lines:
                            expected, filename = line.split("  ", 1)
                            self.assertEqual(hashlib.sha256(bundle.read(filename)).hexdigest(), expected)
                        run_script = bundle.read("run.py").decode()
                        readme = bundle.read("README.md").decode()
                        self.assertIn("--ai", run_script)
                        self.assertIn("JARVIS_API_KEY", run_script)
                        self.assertIn("third-party", readme.lower())
                        manifest = json.loads(bundle.read("manifest.json"))
                        self.assertEqual(manifest["slug"], archive.stem)
                        self.assertEqual(manifest["runtime_dependencies"], [])
                        source = bundle.read("jarvis_agent/workflow.py").decode()
                        self.assertEqual(source.count("\ndef "), 1, "Bundle must contain exactly one product workflow.")

    def test_each_bundle_has_a_loopback_web_ui_that_runs_locally(self):
        with tempfile.TemporaryDirectory() as temp:
            archives = build_all(ROOT, pathlib.Path(temp))
            for archive in archives:
                with self.subTest(archive=archive.name):
                    target = pathlib.Path(temp) / (archive.stem + "-web")
                    target.mkdir()
                    with zipfile.ZipFile(archive) as bundle:
                        bundle.extractall(target)
                    process = subprocess.Popen(
                        [sys.executable, "web.py", "--port", "0"],
                        cwd=target,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                    )
                    try:
                        ready = process.stdout.readline().strip()
                        self.assertTrue(ready.startswith("JARVIS_UI_URL="), ready)
                        port = int(ready.rsplit(":", 1)[1])
                        connection = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
                        connection.request("GET", "/")
                        page = connection.getresponse()
                        self.assertEqual(page.status, 200)
                        self.assertIn(archive.stem, page.read().decode().lower())
                        sample = (target / "examples/input.json").read_text(encoding="utf-8")
                        connection.request("POST", "/api/run", body=sample, headers={"Content-Type": "application/json"})
                        response = connection.getresponse()
                        self.assertEqual(response.status, 200)
                        report = json.loads(response.read())
                        self.assertEqual(report["agent"], archive.stem)
                        connection.close()
                    finally:
                        process.terminate()
                        process.wait(timeout=5)

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
                    missing_key = subprocess.run([sys.executable, "run.py", "examples/input.json", "--ai"], cwd=target, capture_output=True, text=True, timeout=10)
                    self.assertNotEqual(missing_key.returncode, 0)
                    self.assertIn("JARVIS_API_KEY", missing_key.stderr)
                    self.assertEqual(output["agent"], archive.stem)
                    self.assertTrue(output["title"])
                    self.assertEqual(output["actions"], [])

if __name__ == "__main__":
    unittest.main()
