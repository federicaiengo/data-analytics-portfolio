"""Read-only identity gate for the approved static HR dashboard template.

A byte-identical template is required before a style-sensitive workbook rebuild.
This is a source-integrity check, not an Excel desktop or visual QA result.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

APPROVED_TEMPLATE_BLOB_SHA = "2db1b794d86792fb2b12bac1d72b394eb6807d7b"


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def require_approved_template(template: Path, expected_sha: str = APPROVED_TEMPLATE_BLOB_SHA) -> str:
    template = Path(template)
    if not template.is_file():
        raise ValueError("Approved HR workbook template not found")
    digest = git_blob_sha(template.read_bytes())
    if digest != expected_sha:
        raise ValueError(
            "HR workbook template differs from the audited Git version; "
            "do not rebuild until template identity and styling are reviewed"
        )
    return digest
