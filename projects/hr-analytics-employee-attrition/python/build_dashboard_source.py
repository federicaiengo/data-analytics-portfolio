"""Rebuild privacy-minimal HR dashboard aggregate tables from the original CSV.

This is a deterministic source table for the Excel evidence dashboard, not a
claim of a fully automatic Excel refresh or a cleaned employee-level dataset.
Standard-library only; no individual employee records are exported.
"""
from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "WA_Fn-UseC_-HR-Employee-Attrition.csv"
OUTPUT = ROOT / "excel" / "hr_dashboard_group_metrics.csv"
COLUMNS = ("dimension", "group", "employee_count", "attrition_count", "attrition_rate_pct")
DIMENSIONS = (
    "Overall", "OverTime", "JobRole", "Department",
    "JobSatisfaction", "WorkLifeBalance", "YearsAtCompanyBand",
)
TENURE_ORDER = ("0-1 years", "2-3 years", "4-5 years", "6-10 years", "11+ years")
REQUIRED = {
    "EmployeeNumber", "Attrition", "OverTime", "JobRole", "Department",
    "JobSatisfaction", "WorkLifeBalance", "YearsAtCompany",
}


def tenure_band(raw: str) -> str:
    try:
        years = int(raw)
    except (TypeError, ValueError):
        raise ValueError("YearsAtCompany must be a whole number") from None
    if years < 0:
        raise ValueError("YearsAtCompany cannot be negative")
    if years <= 1:
        return TENURE_ORDER[0]
    if years <= 3:
        return TENURE_ORDER[1]
    if years <= 5:
        return TENURE_ORDER[2]
    if years <= 10:
        return TENURE_ORDER[3]
    return TENURE_ORDER[4]


def safe_category(value: str, column: str) -> str:
    value = (value or "").strip()
    if not value:
        raise ValueError(f"Missing category: {column}")
    # Avoid CSV spreadsheet-formula injection even for future source datasets.
    if value.lstrip().startswith(("=", "+", "-", "@")):
        raise ValueError(f"Unsafe spreadsheet category in {column}")
    return value


def aggregate_rows(rows: list[dict[str, str]]) -> list[dict[str, str | int]]:
    if not rows:
        raise ValueError("Cannot summarize an empty source")
    seen_ids: set[str] = set()
    counts: dict[tuple[str, str], list[int]] = defaultdict(lambda: [0, 0])

    for line, row in enumerate(rows, 2):
        missing = REQUIRED - set(row)
        if missing:
            raise ValueError(f"Required source columns missing: {sorted(missing)}")
        identifier = (row["EmployeeNumber"] or "").strip()
        if not identifier or identifier in seen_ids:
            raise ValueError(f"Missing or duplicate employee ID at line {line}")
        seen_ids.add(identifier)
        event = (row["Attrition"] or "").strip()
        if event not in {"Yes", "No"}:
            raise ValueError(f"Unknown attrition category at line {line}")

        dims = {
            "Overall": "All employees",
            "OverTime": safe_category(row["OverTime"], "OverTime"),
            "JobRole": safe_category(row["JobRole"], "JobRole"),
            "Department": safe_category(row["Department"], "Department"),
            "JobSatisfaction": safe_category(row["JobSatisfaction"], "JobSatisfaction"),
            "WorkLifeBalance": safe_category(row["WorkLifeBalance"], "WorkLifeBalance"),
            "YearsAtCompanyBand": tenure_band(row["YearsAtCompany"]),
        }
        for dim, category in dims.items():
            group_count = counts[(dim, category)]
            group_count[0] += 1
            if event == "Yes":
                group_count[1] += 1

    output: list[dict[str, str | int]] = []
    n = len(rows)
    for dimension in DIMENSIONS:
        matched = [(label, v) for (dim, label), v in counts.items() if dim == dimension]
        if sum(v[0] for _, v in matched) != n:
            raise AssertionError(f"Missing or duplicated rows in {dimension}")
        if dimension == "YearsAtCompanyBand":
            matched.sort(key=lambda x: TENURE_ORDER.index(x[0]))
        elif dimension in ("JobSatisfaction", "WorkLifeBalance"):
            matched.sort(key=lambda x: int(x[0]))
        else:
            matched.sort(key=lambda x: x[0])
        for label, (group_n, attritions) in matched:
            output.append({
                "dimension": dimension,
                "group": label,
                "employee_count": group_n,
                "attrition_count": attritions,
                "attrition_rate_pct": f"{100 * attritions / group_n:.4f}",
            })
    return output


def write_summary(source: Path = RAW, destination: Path = OUTPUT) -> list[dict[str, str | int]]:
    with source.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if not REQUIRED.issubset(set(reader.fieldnames or [])):
            raise ValueError(f"Missing source columns: {sorted(REQUIRED - set(reader.fieldnames or []))}")
        groups = aggregate_rows(list(reader))

    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(groups)
    return groups


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=RAW)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    summary = write_summary(args.source, args.output)
    print(f"Wrote {len(summary)} privacy-minimal group rows to {args.output}")


if __name__ == "__main__":
    main()
