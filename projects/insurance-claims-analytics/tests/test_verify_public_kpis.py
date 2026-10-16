"""Independent fixture tests; intentionally no real customer identifiers."""
import csv
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from decimal import Decimal
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "python"))
from verify_public_kpis import summarize, baseline_matches, main

FIELDS = ("TRANSACTION_ID", "INSURANCE_TYPE", "CLAIM_AMOUNT",
          "SSN", "ROUTING_NUMBER", "ACCT_NUMBER", "CUSTOMER_NAME",
          "ADDRESS_LINE1", "ADDRESS_LINE2")


def claim(id, category="Life", amount="95000"):
    return {
        "TRANSACTION_ID": str(id),
        "INSURANCE_TYPE": category, "CLAIM_AMOUNT": amount,
        "SSN": "NONREAL-PRIVATE-TEST-VALUE",
        "ROUTING_NUMBER": "NONREAL-ROUTING",
        "ACCT_NUMBER": "NONREAL-ACCOUNT",
        "CUSTOMER_NAME": "NONREAL-CUSTOMER",
        "ADDRESS_LINE1": "NONREAL-ADDRESS",
        "ADDRESS_LINE2": "",
    }


class InsuranceRawKpiTests(unittest.TestCase):
    def run_csv(self, records, fields=FIELDS):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "test.csv"
            with path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=fields)
                writer.writeheader()
                writer.writerows(records)
            return summarize(path)

    def test_aggregate_totals_and_high_value_threshold(self):
        result = self.run_csv([
            claim("T1", "Life", "95000"),
            claim("T2", "Life", "94999.99"),
            claim("T3", "Motor", "400"),
        ])
        self.assertEqual(result["records"], 3)
        self.assertEqual(result["claim_value"], Decimal("190399.99"))
        self.assertEqual(result["high_value_claims"], 1)
        self.assertEqual(result["insurance_types"]["Life"]["high"], 1)
        self.assertFalse(baseline_matches(result))

    def test_identifier_values_not_returned_in_report(self):
        result = self.run_csv([claim("T1")])
        serialized = repr(result)
        for secret in ("NONREAL-CUSTOMER", "NONREAL-PRIVATE-TEST-VALUE",
                       "NONREAL-ROUTING", "NONREAL-ACCOUNT", "NONREAL-ADDRESS"):
            self.assertNotIn(secret, serialized)
        self.assertIn("SSN", result["personal_looking_fields"])

    def test_duplicate_claim_key_rejected(self):
        with self.assertRaises(ValueError):
            self.run_csv([claim("T1"), claim("T1")])

    def test_missing_claim_key_rejected(self):
        with self.assertRaises(ValueError):
            self.run_csv([claim("")])

    def test_non_numeric_claim_amount_rejected(self):
        with self.assertRaises(ValueError):
            self.run_csv([claim("T1", amount="not-money")])

    def test_non_finite_claim_amount_rejected(self):
        for value in ("NaN", "Infinity", "-Infinity"):
            with self.assertRaises(ValueError):
                self.run_csv([claim("T1", amount=value)])

    def test_missing_required_field_rejected(self):
        with self.assertRaises(ValueError):
            self.run_csv([{"TRANSACTION_ID":"T1","INSURANCE_TYPE":"Life"}],
                         fields=("TRANSACTION_ID", "INSURANCE_TYPE"))

    def test_source_encoding_bom_accepted(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bom.csv"
            with path.open("w", newline="", encoding="utf-8-sig") as handle:
                writer = csv.DictWriter(handle, fieldnames=FIELDS)
                writer.writeheader()
                writer.writerow(claim("T1", amount="100"))
            self.assertEqual(summarize(path)["claim_value"], Decimal("100"))


    def test_cli_synthetic_fixture_succeeds_without_claiming_historical_validation(self):
        fixture = PROJECT / "tests" / "fixtures" / "synthetic_insurance_claims.csv"
        out = io.StringIO()
        with redirect_stdout(out):
            status = main(["--input", str(fixture)])
        self.assertEqual(status, 0)
        self.assertIn("Records: 3", out.getvalue())
        self.assertIn("190399.99", out.getvalue())
        self.assertIn("NOT_RUN", out.getvalue())
        self.assertNotIn("PASS", out.getvalue())

    def test_cli_historical_baseline_is_explicit_and_rejects_fixture(self):
        fixture = PROJECT / "tests" / "fixtures" / "synthetic_insurance_claims.csv"
        out = io.StringIO()
        with redirect_stdout(out):
            status = main(["--input", str(fixture), "--check-historical-baseline"])
        self.assertEqual(status, 1)
        self.assertIn("Historical baseline cross-check: FAIL", out.getvalue())

    def test_cli_missing_source_explained_without_traceback(self):
        with tempfile.TemporaryDirectory() as tmp:
            absent = Path(tmp) / "not-shipped.csv"
            err = io.StringIO()
            with redirect_stderr(err):
                status = main(["--input", str(absent)])
        self.assertEqual(status, 2)
        self.assertIn("SOURCE UNAVAILABLE", err.getvalue())
        self.assertIn("--input", err.getvalue())
        self.assertNotIn("Traceback", err.getvalue())

if __name__ == "__main__":
    unittest.main()
