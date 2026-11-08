"""Read-only, deterministic CSV data-quality audit.

No cell values are included in reports or error messages. No source CSV is
overwritten, cleaned, or silently corrected. Python standard library only.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import tempfile
from datetime import date
from pathlib import Path

EMAIL_SHAPE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class AuditError(ValueError):
    """Expected input/schema validation failure with no row-level disclosure."""


def audit_csv(
    input_path: Path,
    *,
    key_column: str,
    required_columns: tuple[str, ...] = (),
    email_column: str | None = None,
    date_column: str | None = None,
) -> dict:
    """Return only aggregate validation statistics.

    Duplicate keys are compared after stripping outer whitespace and case
    folding. Email formatting is a basic syntax heuristic, not verification
    of deliverability. Dates must be valid YYYY-MM-DD calendar dates.
    Overlapping issue observations do not represent unique affected rows.
    """
    input_path = Path(input_path)
    fields = [key_column, *required_columns]
    if email_column:
        fields.append(email_column)
    if date_column:
        fields.append(date_column)
    if not all(name and name.strip() == name for name in fields):
        raise AuditError("Configured column names must be nonempty and trimmed")

    try:
        handle = input_path.open("r", encoding="utf-8-sig", newline="")
    except OSError as exc:
        raise AuditError("Cannot read the input CSV") from exc

    try:
        with handle:
            reader = csv.reader(handle, strict=True)
            try:
                headers = next(reader)
            except StopIteration as exc:
                raise AuditError("CSV is empty") from exc
            if not headers or any(not h or h != h.strip() for h in headers):
                raise AuditError("CSV headers must be nonempty and trimmed")
            if len({h.casefold() for h in headers}) != len(headers):
                raise AuditError("Duplicate CSV column names are not supported")
            missing_configuration = set(fields) - set(headers)
            if missing_configuration:
                raise AuditError("One or more configured columns are absent from CSV headers")

            pos = {h: i for i, h in enumerate(headers)}
            required = tuple(dict.fromkeys(required_columns))
            missing_required = {field: 0 for field in required}
            seen_keys: set[str] = set()
            rows_read = rows_analyzed = duplicates = missing_keys = 0
            malformed = invalid_email = invalid_date = outer_whitespace = 0

            for record in reader:
                rows_read += 1
                if len(record) != len(headers):
                    malformed += 1
                    continue
                rows_analyzed += 1
                trimmed = {h: record[i].strip() for h, i in pos.items()}
                outer_whitespace += sum(
                    value != value.strip() for value in record
                )

                key = trimmed[key_column].casefold()
                if not key:
                    missing_keys += 1
                elif key in seen_keys:
                    duplicates += 1
                else:
                    seen_keys.add(key)

                for field in required:
                    if not trimmed[field]:
                        missing_required[field] += 1

                if email_column and trimmed[email_column]:
                    if EMAIL_SHAPE.fullmatch(trimmed[email_column]) is None:
                        invalid_email += 1

                if date_column and trimmed[date_column]:
                    value = trimmed[date_column]
                    if ISO_DATE.fullmatch(value) is None:
                        invalid_date += 1
                    else:
                        try:
                            date.fromisoformat(value)
                        except ValueError:
                            invalid_date += 1
    except (csv.Error, UnicodeError) as exc:
        raise AuditError("Invalid CSV encoding or quoting") from exc

    checks = {
        "duplicate_keys": duplicates,
        "missing_keys": missing_keys,
        "missing_required_by_column": missing_required,
        "invalid_email_shape": invalid_email,
        "invalid_iso_dates": invalid_date,
        "inconsistent_column_count_rows": malformed,
        "outer_whitespace_cells": outer_whitespace,
    }
    issue_observations = sum((
        duplicates, missing_keys, sum(missing_required.values()),
        invalid_email, invalid_date, malformed, outer_whitespace
    ))
    return {
        "schema_version": "1.0",
        "provenance": "operator-supplied CSV; values not independently verified",
        "source_modified": False,
        "configuration": {
            "key_column": key_column,
            "required_columns": list(required),
            "email_column": email_column,
            "date_column": date_column,
        },
        "statistics": {
            "rows_read": rows_read,
            "rows_analyzed": rows_analyzed,
            "distinct_nonempty_keys": len(seen_keys),
            "issue_observations": issue_observations,
            "has_issues": issue_observations > 0,
        },
        "checks": checks,
        "limitations": (
            "Counts may overlap across checks and are not unique affected rows. "
            "Email checks are syntactic only. No values were corrected or verified "
            "against external authoritative sources."
        ),
    }


def write_json_report(report: dict, output_path: Path) -> None:
    """Atomically replace only the explicitly designated JSON report."""
    path = Path(output_path)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="\n", suffix=".tmp",
            prefix=".csv-quality-", dir=path.parent, delete=False
        ) as handle:
            temporary = Path(handle.name)
            json.dump(report, handle, sort_keys=True, indent=2, ensure_ascii=False)
            handle.write("\n")
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Existing CSV input")
    parser.add_argument("--report", required=True, type=Path, help="Output JSON report")
    parser.add_argument("--key", required=True, help="CSV column used as record key")
    parser.add_argument("--required", default="", help="Comma-separated required columns")
    parser.add_argument("--email-column", default=None, help="Optional syntax-only email column")
    parser.add_argument("--date-column", default=None, help="Optional YYYY-MM-DD date column")
    parser.add_argument(
        "--fail-on-issues", action="store_true",
        help="Return exit code 2 if validation finds any issue (report still written)"
    )
    args = parser.parse_args(argv)
    if args.input.resolve() == args.report.resolve():
        parser.error("CSV input and JSON report paths must differ")
    required = tuple(x.strip() for x in args.required.split(",") if x.strip())
    try:
        report = audit_csv(
            args.input,
            key_column=args.key,
            required_columns=required,
            email_column=args.email_column,
            date_column=args.date_column,
        )
        write_json_report(report, args.report)
    except (AuditError, OSError) as exc:
        # Print diagnostics without source paths, rows, or raw field values.
        message = str(exc) if isinstance(exc, AuditError) else "Cannot write JSON report"
        print(f"AUDIT ERROR: {message}", file=sys.stderr)
        return 1

    stats = report["statistics"]
    print(
        f"CSV audit complete: {stats['rows_read']} rows read, "
        f"{stats['issue_observations']} issue observations; "
        "no source data modified."
    )
    return 2 if args.fail_on_issues and stats["has_issues"] else 0


if __name__ == "__main__":
    sys.exit(main())
