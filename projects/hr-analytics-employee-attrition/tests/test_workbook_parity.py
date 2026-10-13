"""Regression gates for XLSX-to-CSV parity; workbook is read-only."""
import csv
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
from verify_workbook_parity import (  # noqa: E402
    compare_parity, git_blob_hash, load_aggregates, normalize_label, read_cells,
)

BOOK = ROOT / "excel" / "HR_Attrition_Evidence_Dashboard.xlsx"
AGG = ROOT / "excel" / "hr_dashboard_group_metrics.csv"
RAW = ROOT / "data" / "raw" / "WA_Fn-UseC_-HR-Employee-Attrition.csv"


class WorkbookParityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base_sheets = read_cells(BOOK)
        cls.aggs = load_aggregates(AGG)
        cls.raw = RAW.read_bytes()

    def verify(self, sheets=None):
        return compare_parity(
            sheets if sheets is not None else self.base_sheets,
            self.aggs, self.raw
        )

    def test_real_workbook_reconciles_all_28_aggregates(self):
        self.assertEqual(self.verify(), 28)

    def test_github_blob_hash_provenance_matches_workbook(self):
        self.assertEqual(self.base_sheets["Method"]["B6"], git_blob_hash(self.raw))

    def test_mutated_employee_count_is_rejected(self):
        modified = deepcopy(self.base_sheets)
        modified["Overtime"]["B5"] += 1
        with self.assertRaisesRegex(ValueError, "count"):
            self.verify(modified)

    def test_mutated_attrition_rate_is_rejected(self):
        modified = deepcopy(self.base_sheets)
        modified["Job Roles"]["D5"] += 0.01
        with self.assertRaisesRegex(ValueError, "rate"):
            self.verify(modified)

    def test_mutated_dashboard_copy_is_rejected(self):
        modified = deepcopy(self.base_sheets)
        modified["Dashboard"]["C18"] += 1
        with self.assertRaisesRegex(ValueError, "Dashboard role"):
            self.verify(modified)

    def test_wrong_source_provenance_is_rejected(self):
        modified = deepcopy(self.base_sheets)
        modified["Method"]["B6"] = "wrong_sha"
        with self.assertRaisesRegex(ValueError, "Git blob SHA"):
            self.verify(modified)

    def test_numeric_categories_and_unicode_tenure_label(self):
        self.assertEqual(normalize_label(1.0), "1")
        self.assertEqual(normalize_label("0–1 years"), "0-1 years")

    def test_malformed_csv_duplicate_categories_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            csv_path = Path(tmp) / "source.csv"
            with csv_path.open("w", newline="", encoding="utf-8") as fh:
                writer = csv.writer(fh)
                writer.writerow(
                    ["dimension", "group", "employee_count", "attrition_count", "attrition_rate_pct"]
                )
                writer.writerow(["Overall", "All employees", 1470, 237, 16.1224])
                writer.writerow(["Overall", "All employees", 1470, 237, 16.1224])
            with self.assertRaisesRegex(ValueError, "Duplicate aggregate"):
                load_aggregates(csv_path)


if __name__ == "__main__":
    unittest.main()
