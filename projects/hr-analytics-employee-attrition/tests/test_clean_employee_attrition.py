"""Unit tests for the non-destructive source validation / cleaning contract."""
from __future__ import annotations

import csv
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "python"))
from clean_employee_attrition import (
    CLEAN_FIELDS, RAW_FIELDS, validate_and_clean, write_outputs,
)


def employee(identifier: str = "1", attrition: str = "No") -> dict[str, str]:
    defaults = {
        "Age": "35", "Attrition": attrition, "BusinessTravel": "Travel_Rarely",
        "DailyRate": "100", "Department": "Sales", "DistanceFromHome": "5",
        "Education": "3", "EducationField": "Life Sciences", "EmployeeCount": "1",
        "EmployeeNumber": identifier, "EnvironmentSatisfaction": "3",
        "Gender": "Female", "HourlyRate": "60", "JobInvolvement": "3",
        "JobLevel": "2", "JobRole": "Sales Executive", "JobSatisfaction": "3",
        "MaritalStatus": "Single", "MonthlyIncome": "4500",
        "MonthlyRate": "8000", "NumCompaniesWorked": "2", "Over18": "Y",
        "OverTime": "No", "PercentSalaryHike": "13", "PerformanceRating": "3",
        "RelationshipSatisfaction": "3", "StandardHours": "80",
        "StockOptionLevel": "0", "TotalWorkingYears": "12",
        "TrainingTimesLastYear": "2", "WorkLifeBalance": "3",
        "YearsAtCompany": "5", "YearsInCurrentRole": "3",
        "YearsSinceLastPromotion": "1", "YearsWithCurrManager": "3",
    }
    assert tuple(defaults) == RAW_FIELDS
    return defaults


class HrCleaningTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "raw.csv"

    def write(self, rows, columns=RAW_FIELDS):
        with self.path.open("w", encoding="utf-8", newline="") as h:
            writer = csv.DictWriter(h, fieldnames=columns, lineterminator="\n")
            writer.writeheader()
            for row in rows:
                writer.writerow({k: row[k] for k in columns})
        return self.path

    def test_only_three_verified_constants_are_removed(self):
        src = self.write([employee("1", "Yes"), employee("2", "No")])
        rows, report = validate_and_clean(src, expected_rows=2, expected_attritions=1)
        self.assertEqual(len(rows), 2)
        self.assertEqual(tuple(rows[0]), CLEAN_FIELDS)
        self.assertEqual(len(CLEAN_FIELDS), 32)
        self.assertEqual(rows[0]["EmployeeNumber"], "1")
        self.assertEqual(rows[0]["Attrition"], "Yes")
        self.assertEqual(report["removed_constant_columns"],
                         ["EmployeeCount", "Over18", "StandardHours"])
        self.assertEqual(report["validation_status"], "PASS")

    def test_cleaner_keeps_original_csv_unmodified(self):
        src = self.write([employee()])
        before = src.read_bytes()
        out = Path(self.temp.name) / "clean.csv"
        report = Path(self.temp.name) / "report.json"
        write_outputs(src, out, report, expected_rows=1, expected_attritions=0)
        self.assertEqual(src.read_bytes(), before)
        self.assertTrue(out.is_file())
        self.assertTrue(report.is_file())
        self.assertNotIn("Over18", out.read_text().splitlines()[0])

    def test_missing_data_does_not_get_silently_imputed(self):
        row = employee()
        row["JobRole"] = ""
        with self.assertRaisesRegex(ValueError, "Blank value"):
            validate_and_clean(self.write([row]))

    def test_duplicate_identifier_is_rejected(self):
        a, b = employee(), employee()
        b["Age"] = "41"
        with self.assertRaisesRegex(ValueError, "Duplicate EmployeeNumber"):
            validate_and_clean(self.write([a, b]))

    def test_duplicate_complete_row_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Duplicate complete"):
            validate_and_clean(self.write([employee(), employee()]))

    def test_unexpected_constant_value_is_blocking(self):
        row = employee()
        row["StandardHours"] = "40"
        with self.assertRaisesRegex(ValueError, "Expected constant"):
            validate_and_clean(self.write([row]))

    def test_unknown_category_is_rejected(self):
        row = employee()
        row["Attrition"] = "Possibly"
        with self.assertRaisesRegex(ValueError, "Unexpected Attrition"):
            validate_and_clean(self.write([row]))

    def test_implausible_numeric_range_is_rejected(self):
        row = employee()
        row["JobSatisfaction"] = "9"
        with self.assertRaisesRegex(ValueError, "1-4"):
            validate_and_clean(self.write([row]))

    def test_inconsistent_tenure_is_rejected(self):
        row = employee()
        row["YearsAtCompany"] = "13"
        with self.assertRaisesRegex(ValueError, "TotalWorkingYears"):
            validate_and_clean(self.write([row]))

    def test_non_integer_age_is_rejected(self):
        row = employee()
        row["Age"] = "35.5"
        with self.assertRaisesRegex(ValueError, "Non-integer Age"):
            validate_and_clean(self.write([row]))

    def test_schema_drift_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "schema drift"):
            validate_and_clean(self.write([employee()], RAW_FIELDS[:-1]))

    def test_empty_source_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Empty"):
            validate_and_clean(self.write([]))

    def test_expected_reference_totals_are_checked(self):
        with self.assertRaisesRegex(ValueError, "Expected 1470"):
            validate_and_clean(self.write([employee()]), expected_rows=1470)
        with self.assertRaisesRegex(ValueError, "Unexpected attritions"):
            validate_and_clean(self.write([employee()]), expected_attritions=237)


if __name__ == "__main__":
    unittest.main()
