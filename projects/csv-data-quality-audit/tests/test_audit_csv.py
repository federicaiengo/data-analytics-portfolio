"""Regression tests use invented records only, never real customer data."""
from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from audit_csv import AuditError, audit_csv, main, write_json_report  # noqa: E402

SAMPLE = (
    "customer_id,email,signup_date,country\n"
    "C-001,alex@example.test,2026-11-01,IT\n"
    " c-001 ,alex@example.test,2026-11-01,IT\n"
    "C-002,,2026-02-30,FR\n"
    ",invalid@@example.test,2026-10-03,DE\n"
    "C-004,marie@example.test,2026-10-04,IT\n"
    "C-005,extra@example.test,2026-10-05,IT,extra\n"
)


class DataQualityAuditTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def make_csv(self, text: str = SAMPLE) -> Path:
        source = self.root / "customers.csv"
        source.write_text(text, encoding="utf-8")
        return source

    def scan(self, source: Path) -> dict:
        return audit_csv(
            source,
            key_column="customer_id",
            required_columns=("customer_id", "email", "signup_date"),
            email_column="email",
            date_column="signup_date",
        )

    def test_synthetic_counts_and_overlapping_issues(self):
        report = self.scan(self.make_csv())
        self.assertEqual(report["statistics"]["rows_read"], 6)
        self.assertEqual(report["statistics"]["rows_analyzed"], 5)
        self.assertEqual(report["statistics"]["distinct_nonempty_keys"], 3)
        checks = report["checks"]
        self.assertEqual(checks["duplicate_keys"], 1)
        self.assertEqual(checks["missing_keys"], 1)
        self.assertEqual(checks["missing_required_by_column"], {
            "customer_id": 1, "email": 1, "signup_date": 0
        })
        self.assertEqual(checks["invalid_email_shape"], 1)
        self.assertEqual(checks["invalid_iso_dates"], 1)
        self.assertEqual(checks["inconsistent_column_count_rows"], 1)
        self.assertEqual(checks["outer_whitespace_cells"], 1)
        self.assertEqual(report["statistics"]["issue_observations"], 8)

    def test_report_contains_no_source_cell_values(self):
        report = self.scan(self.make_csv())
        blob = json.dumps(report)
        for private in ("alex@example.test", "marie@example.test", "C-001", "C-002"):
            self.assertNotIn(private, blob)
        self.assertFalse(report["source_modified"])

    def test_input_csv_is_never_modified(self):
        source = self.make_csv()
        before = source.read_bytes()
        self.scan(source)
        self.assertEqual(source.read_bytes(), before)

    def test_valid_file_has_zero_issues(self):
        source = self.make_csv(
            "customer_id,email,signup_date,country\n"
            "C-1,clean@example.test,2026-02-28,IT\n"
            "C-2,other@example.test,2024-02-29,DE\n"
        )
        report = self.scan(source)
        self.assertFalse(report["statistics"]["has_issues"])
        self.assertEqual(report["statistics"]["issue_observations"], 0)

    def test_duplicate_keys_casefold_and_trimmed(self):
        source = self.make_csv(
            "customer_id,email,signup_date,country\n"
            "ABC,valid@example.test,2026-11-01,IT\n"
            " abc ,valid@example.test,2026-11-02,IT\n"
        )
        self.assertEqual(self.scan(source)["checks"]["duplicate_keys"], 1)

    def test_date_rejects_invalid_or_noniso_dates(self):
        source = self.make_csv(
            "customer_id,email,signup_date,country\n"
            "1,a@example.test,2026-02-30,IT\n"
            "2,b@example.test,11/08/2026,FR\n"
            "3,c@example.test,2024-02-29,DE\n"
        )
        self.assertEqual(self.scan(source)["checks"]["invalid_iso_dates"], 2)

    def test_missing_selected_column_fails_closed(self):
        source = self.make_csv("customer_id,email\n1,a@example.test\n")
        with self.assertRaisesRegex(AuditError, "absent"):
            self.scan(source)

    def test_casefold_colliding_headers_are_rejected(self):
        source = self.make_csv("customer_id,EMAIL,email,signup_date\n1,a@b.test,x@b.test,2026-11-01\n")
        with self.assertRaisesRegex(AuditError, "Duplicate CSV"):
            self.scan(source)

    def test_empty_and_untrimmed_headers_are_rejected(self):
        for header in ("customer_id, email,signup_date\n", "customer_id,,signup_date\n"):
            with self.subTest(header=header):
                with self.assertRaisesRegex(AuditError, "headers"):
                    self.scan(self.make_csv(header + "1,a@example.test,2026-11-01\n"))

    def test_inconsistent_row_width_is_counted_not_ignored(self):
        source = self.make_csv(
            "customer_id,email,signup_date,country\n"
            "1,a@example.test,2026-11-01,IT\n"
            "2,missing@example.test\n"
        )
        report = self.scan(source)
        self.assertEqual(report["checks"]["inconsistent_column_count_rows"], 1)
        self.assertEqual(report["statistics"]["rows_analyzed"], 1)

    def test_malformed_quoted_input_is_rejected(self):
        source = self.make_csv(
            'customer_id,email,signup_date,country\n"not-closed,a@example.test,2026-11-01,IT\n'
        )
        with self.assertRaisesRegex(AuditError, "Invalid CSV"):
            self.scan(source)

    def test_report_write_is_deterministic_and_atomic(self):
        report = self.scan(self.make_csv())
        target = self.root / "report.json"
        write_json_report(report, target)
        first = target.read_bytes()
        write_json_report(report, target)
        self.assertEqual(target.read_bytes(), first)
        self.assertEqual(json.loads(first), report)
        self.assertEqual(list(self.root.glob(".csv-quality-*.tmp")), [])

    def test_cli_fail_on_issues_still_writes_report(self):
        source = self.make_csv()
        target = self.root / "report.json"
        with contextlib.redirect_stdout(io.StringIO()):
            exit_code = main([
                "--input", str(source),
                "--report", str(target),
                "--key", "customer_id",
                "--required", "customer_id,email,signup_date",
                "--email-column", "email",
                "--date-column", "signup_date",
                "--fail-on-issues",
            ])
        self.assertEqual(exit_code, 2)
        self.assertTrue(target.is_file())
        self.assertTrue(json.loads(target.read_text())["statistics"]["has_issues"])

    def test_cli_refuses_to_overwrite_source_csv(self):
        source = self.make_csv()
        before = source.read_bytes()
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as ctx:
                main(["--input", str(source), "--report", str(source), "--key", "customer_id"])
        self.assertEqual(ctx.exception.code, 2)
        self.assertEqual(source.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
