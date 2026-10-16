"""Template identity checks; never rely on a substitute workbook for real QA."""
import tempfile
import unittest
from pathlib import Path
from python.workbook_template_guard import (
    APPROVED_TEMPLATE_BLOB_SHA, git_blob_sha, require_approved_template,
)


class WorkbookIdentityTests(unittest.TestCase):
    def test_documented_template_hash_is_pinned(self):
        self.assertEqual(APPROVED_TEMPLATE_BLOB_SHA, "2db1b794d86792fb2b12bac1d72b394eb6807d7b")

    def test_matching_fake_template_accepted_under_supplied_test_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "tiny-test-only.xlsx"
            path.write_bytes(b"synthetic fixture, not a real workbook")
            self.assertEqual(
                require_approved_template(path, expected_sha=git_blob_sha(path.read_bytes())),
                git_blob_sha(path.read_bytes()),
            )

    def test_unapproved_file_rejected_without_modification(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "wrong.xlsx"
            source = b"not the approved source"
            path.write_bytes(source)
            with self.assertRaisesRegex(ValueError, "differs from the audited"):
                require_approved_template(path)
            self.assertEqual(path.read_bytes(), source)

    def test_missing_file_explained(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "not found"):
                require_approved_template(Path(tmp) / "missing.xlsx")


if __name__ == "__main__":
    unittest.main()
