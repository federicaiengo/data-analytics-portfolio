"""Safety regression tests for the optional HR workbook refresh command.

Fixture-only tests: they never modify the committed workbook, rebuild an XLSX
or claim desktop Excel/visual QA.
"""
import tempfile
import unittest
from pathlib import Path

from python.refresh_workbook_snapshot import rebuild


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

    def test_existing_output_is_not_replaced(self):
        self.output.write_bytes(b"retain existing output")
        with self.assertRaisesRegex(ValueError, "already exists"):
            rebuild(self.template, self.aggregates, self.raw, self.output)
        self.assertEqual(self.output.read_bytes(), b"retain existing output")

    def test_missing_input_is_reported_without_new_output(self):
        self.aggregates.unlink()
        with self.assertRaisesRegex(ValueError, "Missing input"):
            rebuild(self.template, self.aggregates, self.raw, self.output)
        self.assertFalse(self.output.exists())


if __name__ == "__main__":
    unittest.main()
