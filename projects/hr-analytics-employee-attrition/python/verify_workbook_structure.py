#!/usr/bin/env python3
"""Read-only XLSX package QA; does NOT validate Microsoft Excel rendering.

Standard library only. The committed workbook is never modified.
"""
import argparse
import csv
import posixpath
import sys
import zipfile
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET

S = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
O = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
P = "http://schemas.openxmlformats.org/package/2006/relationships"


def q(ns, part):
    return "{" + ns + "}" + part


def inspect_xlsx(path, expected_sheets, aggregate_path):
    errors = []
    with zipfile.ZipFile(path) as z:
        corrupt = z.testzip()
        if corrupt:
            raise ValueError("Damaged ZIP member: " + corrupt)
        members = set(z.namelist())
        for part in ("[Content_Types].xml", "xl/workbook.xml", "xl/_rels/workbook.xml.rels"):
            if part not in members:
                raise ValueError("Missing required XLSX part: " + part)
        wb = ET.fromstring(z.read("xl/workbook.xml"))
        relroot = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
        rels = {
            rel.get("Id"): (rel.get("Target", ""), rel.get("TargetMode", ""))
            for rel in relroot.findall(q(P, "Relationship"))
        }
        collection = wb.find(q(S, "sheets"))
        if collection is None:
            raise ValueError("Workbook has no sheets collection")
        sheets = collection.findall(q(S, "sheet"))
        sheet_names = [s.get("name", "") for s in sheets]
        print("Sheet names:", ", ".join(sheet_names))
        if len(sheets) != expected_sheets:
            errors.append(f"Expected {expected_sheets} sheets, found {len(sheets)}")
        if any(not name for name in sheet_names) or len(set(sheet_names)) != len(sheet_names):
            errors.append("Blank or duplicate worksheet name")
        numeric = Counter()
        formula_count = cached_count = total_rows = 0
        for entry in sheets:
            rid = entry.get(q(O, "id"))
            if rid not in rels:
                errors.append("Missing sheet relationship for " + entry.get("name", "?"))
                continue
            target, mode = rels[rid]
            if mode == "External":
                errors.append("External worksheet relationship for " + entry.get("name", "?"))
                continue
            sheet_path = (
                target.lstrip("/")
                if target.startswith("/")
                else posixpath.normpath(posixpath.join("xl", target))
            )
            if sheet_path not in members:
                errors.append("Missing worksheet XML: " + sheet_path)
                continue
            root = ET.fromstring(z.read(sheet_path))
            row_path = ".//" + q(S, "sheetData") + "/" + q(S, "row")
            cell_path = row_path + "/" + q(S, "c")
            rows = root.findall(row_path)
            cells = root.findall(cell_path)
            total_rows += len(rows)
            for cell in cells:
                value = cell.find(q(S, "v"))
                formula = cell.find(q(S, "f"))
                if formula is not None:
                    formula_count += 1
                    if value is not None and value.text:
                        cached_count += 1
                if cell.get("t") == "e":
                    errors.append(
                        f"Cached Excel error at {entry.get('name')}!{cell.get('r')}: "
                        + (value.text if value is not None and value.text else "?")
                    )
                if value is not None and value.text and cell.get("t", "n") in ("n", ""):
                    try:
                        number = float(value.text)
                    except ValueError:
                        continue
                    if number.is_integer():
                        numeric[int(number)] += 1
            print(f"- {entry.get('name')}: {len(rows)} stored rows, {len(cells)} stored cells")
        if aggregate_path:
            with open(aggregate_path, newline="", encoding="utf-8-sig") as stream:
                reader = csv.DictReader(stream)
                fields = reader.fieldnames or []
                records = list(reader)
            if len(records) != 28:
                errors.append(f"Expected 28 aggregate rows, found {len(records)}")
            print("Aggregate source:", len(records), "rows; columns:", ", ".join(fields))
            print("Advisory numeric presence: 1470:", numeric[1470], "237:", numeric[237])
            print("Numeric presence does NOT prove workbook-to-CSV reconciliation.")
        print(f"Stored worksheet rows: {total_rows}; formulas: {formula_count}; cached formulas: {cached_count}")
        print("Valid XLSX package does NOT prove compatibility with desktop Microsoft Excel.")
        if errors:
            raise ValueError("; ".join(errors))
        print("PASS: XLSX package readable; worksheet relationships valid; no cached error cells.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workbook", type=Path, default=Path("excel/HR_Attrition_Evidence_Dashboard.xlsx"))
    parser.add_argument("--aggregate", type=Path, default=Path("excel/hr_dashboard_group_metrics.csv"))
    parser.add_argument("--expected-sheets", type=int, default=7)
    args = parser.parse_args()
    try:
        inspect_xlsx(args.workbook, args.expected_sheets, args.aggregate)
    except (ValueError, OSError, ET.ParseError, zipfile.BadZipFile) as exc:
        print("FAIL:", exc, file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
