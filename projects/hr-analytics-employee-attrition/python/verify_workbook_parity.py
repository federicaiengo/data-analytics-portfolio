#!/usr/bin/env python3
"""Read-only cell-level parity of the static HR workbook against source aggregates.

No external dependencies. The workbook, source CSV and raw dataset are NEVER edited.
This validates the 28 source rows represented in the XLSX and selected Dashboard
repeat views; it does not validate Microsoft Excel desktop rendering.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import posixpath
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
OFFICE = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PACKAGE = "http://schemas.openxmlformats.org/package/2006/relationships"

BLOCKS = {
    "OverTime": ("Overtime", range(5, 7)),
    "JobRole": ("Job Roles", range(5, 14)),
    "Department": ("Departments", range(5, 8)),
    "JobSatisfaction": ("Satisfaction", range(5, 9)),
    "WorkLifeBalance": ("Satisfaction", range(12, 16)),
    "YearsAtCompanyBand": ("Tenure", range(5, 10)),
}
SHEET_NAMES = {"Dashboard", "Overtime", "Job Roles", "Departments", "Satisfaction", "Tenure", "Method"}
RATE_TOLERANCE_PCT_POINTS = 0.0000501  # CSV rounds percentage points to four decimals.


def tag(uri: str, local: str) -> str:
    return "{" + uri + "}" + local


def normalize_label(value: object) -> str:
    # Workbook stores 1-4 satisfaction categories as numeric cells, CSV as text.
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    # Workbook typography uses Unicode en dashes in tenure bands; CSV uses hyphens.
    return str(value).strip().replace("–", "-").replace("—", "-").replace("−", "-")


def read_cells(xlsx: Path) -> dict[str, dict[str, str | float]]:
    with zipfile.ZipFile(xlsx) as arc:
        names = set(arc.namelist())
        for required in ("xl/workbook.xml", "xl/_rels/workbook.xml.rels"):
            if required not in names:
                raise ValueError("Missing XLSX component " + required)
        workbook = ET.fromstring(arc.read("xl/workbook.xml"))
        relationships = ET.fromstring(arc.read("xl/_rels/workbook.xml.rels"))
        refs = {
            e.get("Id"): (e.get("Target"), e.get("TargetMode", ""))
            for e in relationships.findall(tag(PACKAGE, "Relationship"))
        }
        shared_strings = []
        if "xl/sharedStrings.xml" in names:
            shared_root = ET.fromstring(arc.read("xl/sharedStrings.xml"))
            for item in shared_root.findall(tag(MAIN, "si")):
                shared_strings.append("".join(t.text or "" for t in item.iter(tag(MAIN, "t"))))
        worksheets = {}
        for sheet in workbook.findall("./" + tag(MAIN, "sheets") + "/" + tag(MAIN, "sheet")):
            name, rel = sheet.get("name"), sheet.get(tag(OFFICE, "id"))
            if rel not in refs:
                raise ValueError("Missing worksheet relationship for " + str(name))
            target, mode = refs[rel]
            if mode == "External" or not target:
                raise ValueError("Unsafe external/missing worksheet relationship for " + str(name))
            part = target.lstrip("/") if target.startswith("/") else posixpath.normpath(posixpath.join("xl", target))
            if part not in names:
                raise ValueError("Missing worksheet part " + part)
            root = ET.fromstring(arc.read(part))
            cells = {}
            for cell in root.findall(".//" + tag(MAIN, "sheetData") + "/" + tag(MAIN, "row") + "/" + tag(MAIN, "c")):
                address, celltype = cell.get("r"), cell.get("t", "n")
                if celltype == "e":
                    raise ValueError(f"Excel error cell {name}!{address}")
                formula = cell.find(tag(MAIN, "f"))
                if formula is not None:
                    raise ValueError(f"Unexpected formula in static workbook at {name}!{address}")
                value = cell.find(tag(MAIN, "v"))
                if celltype == "inlineStr":
                    string = cell.find(tag(MAIN, "is"))
                    content = "".join(t.text or "" for t in string.iter(tag(MAIN, "t"))) if string is not None else ""
                    cells[address] = content
                elif celltype == "s":
                    if value is None or value.text is None:
                        raise ValueError(f"Missing shared-string index {name}!{address}")
                    cells[address] = shared_strings[int(value.text)]
                elif celltype in ("n", ""):
                    if value is not None and value.text is not None:
                        cells[address] = float(value.text)
                elif celltype == "b":
                    if value is not None and value.text is not None:
                        cells[address] = value.text == "1"
                elif value is not None:
                    cells[address] = value.text or ""
            worksheets[name] = cells
        if set(worksheets) != SHEET_NAMES:
            raise ValueError(f"Unexpected workbook sheets {set(worksheets) ^ SHEET_NAMES}")
        return worksheets


def load_aggregates(path: Path) -> dict[tuple[str, str], tuple[int, int, float]]:
    with path.open(encoding="utf-8-sig", newline="") as inp:
        reader = csv.DictReader(inp)
        if set(reader.fieldnames or ()) != {
            "dimension", "group", "employee_count", "attrition_count", "attrition_rate_pct"
        }:
            raise ValueError("Unexpected aggregate CSV columns")
        result = {}
        for row in reader:
            key = (row["dimension"], normalize_label(row["group"]))
            if key in result:
                raise ValueError("Duplicate aggregate row " + str(key))
            result[key] = (
                int(row["employee_count"]), int(row["attrition_count"]),
                float(row["attrition_rate_pct"])
            )
    if len(result) != 28:
        raise ValueError(f"Expected 28 aggregate rows, got {len(result)}")
    return result


def expect_number(cells: dict, address: str, expected: int | float, description: str,
                  tolerance: float = 0) -> None:
    actual = cells.get(address)
    if not isinstance(actual, (int, float)) or isinstance(actual, bool):
        raise ValueError(f"{description} {address}: missing/nonnumeric value {actual!r}")
    if abs(actual - expected) > tolerance:
        raise ValueError(f"{description} {address}: expected {expected}, found {actual}")


def compare_group(cells: dict, r: int, expected: tuple[int, int, float], context: str) -> None:
    count, attritions, percentage_points = expected
    expect_number(cells, "B" + str(r), count, context + " count")
    expect_number(cells, "C" + str(r), attritions, context + " attritions")
    expect_number(
        cells, "D" + str(r), percentage_points / 100, context + " rate",
        RATE_TOLERANCE_PCT_POINTS / 100,
    )


def git_blob_hash(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def compare_parity(worksheets: dict, aggregates: dict,
                   raw_csv: bytes) -> int:
    remaining = dict(aggregates)
    total = remaining.pop(("Overall", "All employees"), None)
    if total is None:
        raise ValueError("Missing Overall aggregate")
    dashboard = worksheets["Dashboard"]
    expect_number(dashboard, "B5", total[0], "Dashboard total records")
    expect_number(dashboard, "B6", total[1], "Dashboard attritions")
    expect_number(dashboard, "B7", total[2] / 100, "Dashboard rate",
                  RATE_TOLERANCE_PCT_POINTS / 100)
    expect_number(dashboard, "B8", len(BLOCKS), "Dashboard dimension groups")
    nchecks = 1

    for dim, (sheetname, rowrange) in BLOCKS.items():
        cells = worksheets[sheetname]
        seen = set()
        for r in rowrange:
            label = normalize_label(cells.get("A" + str(r), ""))
            key = (dim, label)
            if key not in remaining:
                raise ValueError(f"Unrecognized workbook group {sheetname}!A{r}: {label!r}")
            if key in seen:
                raise ValueError(f"Repeated workbook group {key}")
            compare_group(cells, r, remaining[key], f"{dim}/{label}")
            seen.add(key)
            nchecks += 1
        for key in seen:
            remaining.pop(key)
    if remaining:
        raise ValueError(f"Aggregate groups missing from workbook: {list(remaining)}")

    # Dashboard repeats two overtime groups and five of the roles: verify both mirrors.
    by_dim = dict(aggregates)
    for row in (13, 14):
        label = normalize_label(dashboard.get("A" + str(row), ""))
        key = ("OverTime", label)
        if key not in by_dim:
            raise ValueError("Unknown Dashboard overtime label " + label)
        compare_group(dashboard, row, by_dim[key], "Dashboard overtime/" + label)
    for row in range(18, 23):
        label = normalize_label(dashboard.get("A" + str(row), ""))
        key = ("JobRole", label)
        if key not in by_dim:
            raise ValueError("Unknown Dashboard role " + label)
        compare_group(dashboard, row, by_dim[key], "Dashboard role/" + label)

    # Provenance is checked against raw bytes and raw schema, not just a stale string.
    with_raw = list(csv.reader(raw_csv.decode("utf-8-sig").splitlines()))
    if not with_raw:
        raise ValueError("Empty raw data")
    headers, employees = with_raw[0], with_raw[1:]
    meth = worksheets["Method"]
    if meth.get("B5") != "WA_Fn-UseC_-HR-Employee-Attrition.csv":
        raise ValueError("Unexpected workbook source filename")
    if meth.get("B6") != git_blob_hash(raw_csv):
        raise ValueError("Workbook source Git blob SHA differs from actual raw CSV")
    expect_number(meth, "B7", len(employees), "Method raw employee count")
    expect_number(meth, "B8", len(headers), "Method raw column count")
    if len(employees) != total[0]:
        raise ValueError("Raw employee count does not match Overall aggregate")
    print(f"PASS: {nchecks}/28 distinct aggregate groups, 7 Dashboard mirrors, "
          f"source Git SHA, raw shape, count/attritions/rates checked.")
    print("Limits: this is a static XLSX parity audit, NOT Excel desktop-rendering QA "
          "or automated workbook regeneration.")
    return nchecks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workbook", type=Path, default=Path("excel/HR_Attrition_Evidence_Dashboard.xlsx"))
    parser.add_argument("--aggregates", type=Path, default=Path("excel/hr_dashboard_group_metrics.csv"))
    parser.add_argument("--raw", type=Path, default=Path("data/raw/WA_Fn-UseC_-HR-Employee-Attrition.csv"))
    args = parser.parse_args()
    try:
        compare_parity(read_cells(args.workbook), load_aggregates(args.aggregates), args.raw.read_bytes())
    except (ValueError, OSError, KeyError, IndexError, ET.ParseError, zipfile.BadZipFile) as exc:
        print("FAIL:", exc, file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
