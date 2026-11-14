import sys
import tempfile
import unittest
from pathlib import Path

from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_product_workbooks import build_all


class ProductWorkbookTests(unittest.TestCase):
    def test_generates_ten_valid_workbooks(self):
        with tempfile.TemporaryDirectory() as tmp:
            files = build_all(ROOT, Path(tmp))
            self.assertEqual(len(files), 10)
            for path in files:
                self.assertGreater(path.stat().st_size, 5000)
                wb = load_workbook(path, read_only=False, data_only=False)
                self.assertIn("START HERE", wb.sheetnames)
                self.assertGreaterEqual(len(wb.sheetnames), 2)
                wb.close()

    def test_content_calendar_has_thirty_days(self):
        with tempfile.TemporaryDirectory() as tmp:
            build_all(ROOT, Path(tmp))
            wb = load_workbook(Path(tmp) / "30-day-content-calendar.xlsx", data_only=False)
            ws = wb["Content Calendar"]
            self.assertEqual(ws.max_row, 31)
            self.assertEqual(ws["A31"].value, 30)
            self.assertTrue(ws.data_validations.dataValidation)
            wb.close()

    def test_hook_library_contains_one_hundred_original_hooks(self):
        with tempfile.TemporaryDirectory() as tmp:
            build_all(ROOT, Path(tmp))
            wb = load_workbook(Path(tmp) / "100-content-hooks.xlsx", data_only=False)
            ws = wb["Hook Library"]
            self.assertEqual(ws.max_row, 101)
            self.assertTrue(ws["C2"].value)
            self.assertTrue(ws["C101"].value)
            wb.close()

    def test_crm_and_pricing_contain_live_formulas(self):
        with tempfile.TemporaryDirectory() as tmp:
            build_all(ROOT, Path(tmp))
            crm = load_workbook(Path(tmp) / "simple-crm-lead-tracker.xlsx", data_only=False)
            self.assertTrue(str(crm["Dashboard"]["B2"].value).startswith("="))
            self.assertTrue(crm["Leads"].data_validations.dataValidation)
            crm.close()
            pricing = load_workbook(Path(tmp) / "service-pricing-calculator.xlsx", data_only=False)
            self.assertTrue(str(pricing["Inputs"]["B11"].value).startswith("="))
            self.assertTrue(str(pricing["Quote Builder"]["G7"].value).startswith("="))
            pricing.close()


if __name__ == "__main__":
    unittest.main()
