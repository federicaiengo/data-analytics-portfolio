"""Prevent confusing synthetic demonstrations with operator-supplied AI observations."""
import json
import tempfile
import unittest
from pathlib import Path

from src.generate_report import DEMO_SOURCE, build_report

ROOT = Path(__file__).resolve().parents[1]


class ReportDataStatusTests(unittest.TestCase):
    def test_packaged_demo_keeps_previous_json_payload(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "report.json"
            build_report(str(DEMO_SOURCE), str(output))
            generated = json.loads(output.read_text(encoding="utf-8"))
        expected = json.loads(
            (ROOT / "results" / "demo_metrics.json").read_text(encoding="utf-8")
        )
        self.assertEqual(generated, expected)
        self.assertEqual(generated["data_status"], "synthetic demonstration data")

    def test_unreviewed_copy_cannot_be_silently_labelled_synthetic(self):
        with tempfile.TemporaryDirectory() as tmp:
            csv_file = Path(tmp) / "unreviewed.csv"
            csv_file.write_bytes(DEMO_SOURCE.read_bytes())
            output = Path(tmp) / "report.json"
            with self.assertRaisesRegex(ValueError, "Input status is unknown"):
                build_report(str(csv_file), str(output))
            self.assertFalse(output.exists())

    def test_observational_status_never_claims_independent_verification(self):
        with tempfile.TemporaryDirectory() as tmp:
            csv_file = Path(tmp) / "operator_observations.csv"
            csv_file.write_bytes(DEMO_SOURCE.read_bytes())
            output = Path(tmp) / "report.json"
            build_report(str(csv_file), str(output), input_kind="observational")
            result = json.loads(output.read_text(encoding="utf-8"))
        self.assertIn("not independently verified", result["data_status"])
        self.assertNotIn("synthetic demonstration data", result["data_status"])

    def test_unknown_kind_rejected_without_creating_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "report.json"
            with self.assertRaisesRegex(ValueError, "input_kind must be"):
                build_report(str(DEMO_SOURCE), str(output), input_kind="verified")
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
