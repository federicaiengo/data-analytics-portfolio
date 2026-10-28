"""Safety regression tests for the optional HR workbook refresh command.

Fixture-only tests: they never modify the committed workbook, rebuild an XLSX
or claim desktop Excel/visual QA.
"""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from python.refresh_workbook_snapshot import rebuild, export_verified_snapshot


class WorkbookRefreshSafetyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.template = self.root / "template.xlsx"
        self.aggregates = self.root / "aggregates.csv"
        self.raw = self.root / "raw.csv"
        self.output = self.root / "generated.xlsx"
        self.template.write_bytes(b"intentionally unapproved synthetic workbook bytes")
        self.aggregates.write_text("synthetic,not,real\n", encoding="utf-8")
        self.raw.write_text("not a valid HR data source\n", encoding="utf-8")

    def test_unapproved_template_fails_before_csv_parsing_or_output(self):
        original = self.template.read_bytes()
        with self.assertRaisesRegex(ValueError, "differs from the audited Git version"):
            rebuild(self.template, self.aggregates, self.raw, self.output)
        self.assertEqual(self.template.read_bytes(), original)
        self.assertFalse(self.output.exists())

    def test_output_must_not_overwrite_template(self):
        with self.assertRaisesRegex(ValueError, "must not overwrite"):
            rebuild(self.template, self.aggregates, self.raw, self.template)

    def test_output_must_not_overwrite_csv_input(self):
        with self.assertRaisesRegex(ValueError, "must not overwrite"):
            rebuild(self.template, self.aggregates, self.raw, self.raw)

    def test_output_must_not_overwrite_aggregate_input(self):
        original = self.aggregates.read_bytes()
        with self.assertRaisesRegex(ValueError, "must not overwrite"):
            rebuild(self.template, self.aggregates, self.raw, self.aggregates)
        self.assertEqual(self.aggregates.read_bytes(), original)

    def test_output_symlink_to_template_is_rejected(self):
        try:
            self.output.symlink_to(self.template)
        except (OSError, NotImplementedError):
            self.skipTest("Symlinks unavailable")
        original = self.template.read_bytes()
        with self.assertRaisesRegex(ValueError, "must not overwrite|symbolic link"):
            rebuild(self.template, self.aggregates, self.raw, self.output)
        self.assertEqual(self.template.read_bytes(), original)

    def test_existing_output_is_not_replaced(self):
        self.output.write_bytes(b"retain existing output")
        with self.assertRaisesRegex(ValueError, "already exists"):
            rebuild(self.template, self.aggregates, self.raw, self.output)
        self.assertEqual(self.output.read_bytes(), b"retain existing output")

    def test_dangling_symlink_output_is_rejected(self):
        redirected = self.root / "uncreated.xlsx"
        try:
            self.output.symlink_to(redirected)
        except (OSError, NotImplementedError):
            self.skipTest("Symlinks unavailable")
        with self.assertRaisesRegex(ValueError, "symbolic link"):
            rebuild(self.template, self.aggregates, self.raw, self.output)
        self.assertFalse(redirected.exists())

    def test_partial_export_is_removed_when_save_raises(self):
        output = self.output

        class BrokenExport:
            def save(self, path):
                Path(path).write_bytes(b"partial XLSX")
                raise OSError("simulated export failure")

        class BrokenSpreadsheetFile:
            @staticmethod
            def export_xlsx(_book):
                return BrokenExport()

        with self.assertRaisesRegex(OSError, "simulated export failure"):
            export_verified_snapshot(object(), output, {}, b"", BrokenSpreadsheetFile)
        self.assertFalse(output.exists())

    def test_failed_parity_removes_exported_workbook(self):
        output = self.output

        class Export:
            def save(self, path):
                Path(path).write_bytes(b"synthetic XLSX bytes")

        class SpreadsheetFile:
            @staticmethod
            def export_xlsx(_book):
                return Export()

        with patch("python.refresh_workbook_snapshot.read_cells", return_value={}):
            with patch("python.refresh_workbook_snapshot.compare_parity", side_effect=ValueError("parity mismatch")):
                with self.assertRaisesRegex(ValueError, "parity mismatch"):
                    export_verified_snapshot(object(), output, {}, b"", SpreadsheetFile)
        self.assertFalse(output.exists())

    def test_incomplete_reconciliation_removes_exported_workbook(self):
        output = self.output

        class Export:
            def save(self, path):
                Path(path).write_bytes(b"synthetic XLSX bytes")

        class SpreadsheetFile:
            @staticmethod
            def export_xlsx(_book):
                return Export()

        with patch("python.refresh_workbook_snapshot.read_cells", return_value={}):
            with patch("python.refresh_workbook_snapshot.compare_parity", return_value=27):
                with self.assertRaisesRegex(ValueError, "Fewer than 28"):
                    export_verified_snapshot(object(), output, {}, b"", SpreadsheetFile)
        self.assertFalse(output.exists())

    def test_missing_input_is_reported_without_new_output(self):
        self.aggregates.unlink()
        with self.assertRaisesRegex(ValueError, "Missing input"):
            rebuild(self.template, self.aggregates, self.raw, self.output)
        self.assertFalse(self.output.exists())


if __name__ == "__main__":
    unittest.main()
