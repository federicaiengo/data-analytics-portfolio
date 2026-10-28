#!/usr/bin/env python3
"""Rebuild an HR workbook snapshot using the original styled XLSX as template.

Uses artifact_tool for workbook edits. Sources and original template remain
unchanged. The new output is checked against all 28 source aggregate groups.
This does not prove visual fidelity or Microsoft Excel desktop compatibility.
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_dashboard_source import aggregate_rows
from workbook_template_guard import require_approved_template
from verify_workbook_parity import (
    BLOCKS, compare_parity, git_blob_hash, load_aggregates, normalize_label, read_cells,
)


def write_group(book, sheet_name, row, record):
    count, attritions, _csv_pct = record
    if count == 0:
        raise ValueError(f"Empty group in {sheet_name}, row {row}")
    sheet = book.worksheets.get_item(sheet_name)
    sheet.get_range(f"B{row}:D{row}").values = [[count, attritions, attritions / count]]


def rebuild(template: Path, aggregate: Path, raw: Path, output: Path) -> int:
    for filename in (template, aggregate, raw):
        if not filename.is_file():
            raise ValueError("Missing input: " + str(filename))
    if output.resolve() in {f.resolve() for f in (template, aggregate, raw)}:
        raise ValueError("Output must not overwrite source or original XLSX")
    if output.is_symlink():
        raise ValueError("Output cannot be a symbolic link: " + str(output))
    if output.exists():
        raise ValueError("Output already exists: " + str(output))

    # Reject an unknown template before importing or exporting any workbook.
    require_approved_template(template)

    raw_bytes = raw.read_bytes()
    records = list(csv.DictReader(raw_bytes.decode("utf-8-sig").splitlines()))
    regenerated = aggregate_rows(records)  # In memory: never overwrites CSV.
    reference = load_aggregates(aggregate)
    recalculated = {
        (str(r["dimension"]), normalize_label(r["group"])): (
            int(r["employee_count"]), int(r["attrition_count"]), float(r["attrition_rate_pct"])
        )
        for r in regenerated
    }
    if recalculated != reference:
        raise ValueError("Aggregate CSV differs from the deterministic source rebuild")

    try:
        from artifact_tool import Blob, SpreadsheetFile
    except ImportError as exc:
        raise RuntimeError('Optional workbook renderer is not installed') from exc
    workbook = SpreadsheetFile.import_xlsx(Blob.load(str(template)))
    for dim, (sheet_name, row_numbers) in BLOCKS.items():
        sheet = workbook.worksheets.get_item(sheet_name)
        for row in row_numbers:
            label = normalize_label(sheet.get_range(f"A{row}").values[0][0])
            key = (dim, label)
            if key not in reference:
                raise ValueError(f"Template label mismatch at {sheet_name}!A{row}: {label}")
            write_group(workbook, sheet_name, row, reference[key])

    overall = reference[("Overall", "All employees")]
    dashboard = workbook.worksheets.get_item("Dashboard")
    dashboard.get_range("B5:B8").values = [
        [overall[0]], [overall[1]], [overall[1] / overall[0]], [len(BLOCKS)]
    ]
    for row in (13, 14):
        label = normalize_label(dashboard.get_range(f"A{row}").values[0][0])
        write_group(workbook, "Dashboard", row, reference[("OverTime", label)])
    for row in range(18, 23):
        label = normalize_label(dashboard.get_range(f"A{row}").values[0][0])
        write_group(workbook, "Dashboard", row, reference[("JobRole", label)])

    method = workbook.worksheets.get_item("Method")
    method.get_range("B5:B8").values = [
        [raw.name], [git_blob_hash(raw_bytes)], [len(records)],
        [len(records[0]) if records else 0],
    ]
    output.parent.mkdir(parents=True, exist_ok=True)
    try:
        # A failed exporter may leave a partial XLSX; remove it on any failure.
        SpreadsheetFile.export_xlsx(workbook).save(str(output))
        checked = compare_parity(read_cells(output), reference, raw_bytes)
        if checked != 28:
            raise ValueError("Fewer than 28 aggregate rows reconciled")
    except Exception:
        output.unlink(missing_ok=True)
        raise
    print(f"PASS: New workbook created, 28/28 rows reconciled: {output}")
    print("Warning: desktop Excel rendering and precise design fidelity still require review.")
    return checked


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--template", type=Path, default=ROOT / "excel" / "HR_Attrition_Evidence_Dashboard.xlsx")
    p.add_argument("--aggregate", type=Path, default=ROOT / "excel" / "hr_dashboard_group_metrics.csv")
    p.add_argument("--raw", type=Path, default=ROOT / "data" / "raw" / "WA_Fn-UseC_-HR-Employee-Attrition.csv")
    p.add_argument("--output", type=Path, required=True, help="New XLSX path: never the original template")
    args = p.parse_args()
    try:
        rebuild(args.template, args.aggregate, args.raw, args.output)
    except (ValueError, OSError, RuntimeError) as exc:
        print("FAIL:", exc, file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
