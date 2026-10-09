"""No employee-level data or external services are needed for these tests."""
import csv
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "python"))
from build_dashboard_source import aggregate_rows, tenure_band, write_summary, DIMENSIONS


def row(id, attrition="No", overtime="No", role="Analyst", department="Research",
        satisfaction="3", balance="3", years="2"):
    return {
        "EmployeeNumber": str(id), "Attrition": attrition,
        "OverTime": overtime, "JobRole": role, "Department": department,
        "JobSatisfaction": satisfaction, "WorkLifeBalance": balance,
        "YearsAtCompany": years,
    }


class HrDashboardAggregationTests(unittest.TestCase):
    def test_rates_and_denominators(self):
        results = aggregate_rows([
            row(1, "Yes", "Yes"), row(2, "No", "Yes"),
            row(3, "No", "No"), row(4, "Yes", "No"),
        ])
        overall = next(x for x in results if x["dimension"] == "Overall")
        self.assertEqual((overall["employee_count"], overall["attrition_count"]),
                         (4, 2))
        self.assertEqual(overall["attrition_rate_pct"], "50.0000")
        overtime = {x["group"]: x for x in results if x["dimension"] == "OverTime"}
        self.assertEqual(overtime["Yes"]["attrition_count"], 1)
        self.assertEqual(overtime["Yes"]["employee_count"], 2)
        for dimension in DIMENSIONS:
            self.assertEqual(sum(x["employee_count"] for x in results
                                 if x["dimension"] == dimension), 4)

    def test_zero_attrition_is_zero_percent(self):
        results = aggregate_rows([row(101), row(102)])
        self.assertEqual(results[0]["attrition_rate_pct"], "0.0000")

    def test_tenure_boundaries(self):
        for years, expected in {
            "0": "0-1 years", "1": "0-1 years", "2": "2-3 years",
            "3": "2-3 years", "4": "4-5 years", "5": "4-5 years",
            "6": "6-10 years", "10": "6-10 years", "11": "11+ years",
        }.items():
            self.assertEqual(tenure_band(years), expected)

    def test_invalid_tenure_raises(self):
        for value in ("-1", "NaN", "1.5", ""):
            with self.assertRaises(ValueError):
                tenure_band(value)

    def test_duplicate_ids_block_silent_double_counting(self):
        with self.assertRaises(ValueError):
            aggregate_rows([row(7), row(7)])

    def test_unknown_attrition_category_fails(self):
        with self.assertRaises(ValueError):
            aggregate_rows([row(7, attrition="Maybe")])

    def test_spreadsheet_formula_injection_category_fails(self):
        with self.assertRaises(ValueError):
            aggregate_rows([row(7, role="=HYPERLINK(...)")])

    def test_empty_input_fails(self):
        with self.assertRaises(ValueError):
            aggregate_rows([])

    def test_csv_output_has_only_aggregate_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "sample.csv"
            target = Path(tmp) / "summary.csv"
            rows = [row(123, "Yes", "Yes"), row(456, "No", "No")]
            with source.open("w", newline="", encoding="utf-8") as stream:
                writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
                writer.writeheader()
                writer.writerows(rows)
            result = write_summary(source, target)
            with target.open(newline="", encoding="utf-8") as stream:
                reader = csv.DictReader(stream)
                self.assertEqual(reader.fieldnames, [
                    "dimension", "group", "employee_count", "attrition_count",
                    "attrition_rate_pct",
                ])
                output = list(reader)
            self.assertEqual(len(output), len(result))
            contents = target.read_text(encoding="utf-8")
            self.assertNotIn("EmployeeNumber", contents)
            self.assertNotIn("123", contents)
            self.assertNotIn("456", contents)


if __name__ == "__main__":
    unittest.main()
