"""Deterministic, non-destructive cleaning of the IBM HR educational CSV.

The raw file is immutable. Cleaning removes *only* independently identified
constant fields; it does not invent missing values, drop employees, normalize
outcomes after seeing results, or infer causal relationships.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw/WA_Fn-UseC_-HR-Employee-Attrition.csv"
CLEAN = ROOT / "data/clean/employee_attrition_clean.csv"
REPORT = ROOT / "data/clean/source_quality_report.json"

RAW_FIELDS = (
    "Age", "Attrition", "BusinessTravel", "DailyRate", "Department",
    "DistanceFromHome", "Education", "EducationField", "EmployeeCount",
    "EmployeeNumber", "EnvironmentSatisfaction", "Gender", "HourlyRate",
    "JobInvolvement", "JobLevel", "JobRole", "JobSatisfaction",
    "MaritalStatus", "MonthlyIncome", "MonthlyRate", "NumCompaniesWorked",
    "Over18", "OverTime", "PercentSalaryHike", "PerformanceRating",
    "RelationshipSatisfaction", "StandardHours", "StockOptionLevel",
    "TotalWorkingYears", "TrainingTimesLastYear", "WorkLifeBalance",
    "YearsAtCompany", "YearsInCurrentRole", "YearsSinceLastPromotion",
    "YearsWithCurrManager",
)
CONSTANTS = {
    "EmployeeCount": "1", "Over18": "Y", "StandardHours": "80",
}
CLEAN_FIELDS = tuple(k for k in RAW_FIELDS if k not in CONSTANTS)
ENUMS = {
    "Attrition": {"Yes", "No"},
    "OverTime": {"Yes", "No"},
    "Gender": {"Male", "Female"},
    "Department": {"Sales", "Research & Development", "Human Resources"},
    "BusinessTravel": {"Travel_Rarely", "Travel_Frequently", "Non-Travel"},
    "EducationField": {"Life Sciences", "Other", "Medical", "Marketing",
                       "Technical Degree", "Human Resources"},
    "MaritalStatus": {"Single", "Married", "Divorced"},
    "JobRole": {"Sales Representative", "Sales Executive", "Research Scientist",
                "Research Director", "Healthcare Representative", "Human Resources",
                "Manager", "Laboratory Technician", "Manufacturing Director"},
}
INTEGER_FIELDS = frozenset(RAW_FIELDS) - set(ENUMS) - {"Over18"}
FOUR_POINT = (
    "EnvironmentSatisfaction", "JobInvolvement", "JobSatisfaction",
    "RelationshipSatisfaction", "WorkLifeBalance",
)


def validate_and_clean(source: Path, expected_rows: int | None = None,
                       expected_attritions: int | None = None) -> tuple[list[dict[str, str]], dict]:
    source = Path(source)
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    with source.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != RAW_FIELDS:
            raise ValueError("Raw CSV schema drift: expected exact 35-column field order")
        raw = list(reader)

    if not raw:
        raise ValueError("Empty employee dataset")
    if expected_rows is not None and len(raw) != expected_rows:
        raise ValueError(f"Expected {expected_rows} source rows, found {len(raw)}")
    seen: set[str] = set()
    distinct_rows: set[tuple[str, ...]] = set()
    missing = 0
    rows: list[dict[str, str]] = []
    yes_count = 0
    categories: dict[str, Counter] = {k: Counter() for k in ENUMS}
    numeric_ranges: dict[str, list[int]] = {}

    for n, row in enumerate(raw, 2):
        if None in row or any(v is None for v in row.values()):
            raise ValueError(f"Malformed source row at line {n}")
        if any(not v.strip() for v in row.values()):
            missing += 1
            raise ValueError(f"Blank value at source line {n}; no silent imputation")
        current = tuple(row[k] for k in RAW_FIELDS)
        if current in distinct_rows:
            raise ValueError(f"Duplicate complete employee row at source line {n}")
        distinct_rows.add(current)
        employee = row["EmployeeNumber"]
        if employee in seen:
            raise ValueError(f"Duplicate EmployeeNumber at source line {n}")
        seen.add(employee)

        for field, actual in CONSTANTS.items():
            if row[field] != actual:
                raise ValueError(f"Expected constant {field}={actual!r}, line {n}")
        for field, allowed in ENUMS.items():
            value = row[field]
            if value not in allowed:
                raise ValueError(f"Unexpected {field} category on line {n}: {value!r}")
            categories[field][value] += 1

        nums: dict[str, int] = {}
        for field in INTEGER_FIELDS:
            try:
                number = int(row[field])
            except ValueError as exc:
                raise ValueError(f"Non-integer {field} on line {n}") from exc
            if str(number) != row[field] or number < 0:
                raise ValueError(f"Invalid nonnegative integer {field} on line {n}")
            nums[field] = number
            bounds = numeric_ranges.setdefault(field, [number, number])
            bounds[0] = min(bounds[0], number)
            bounds[1] = max(bounds[1], number)

        if not 18 <= nums["Age"] <= 100:
            raise ValueError(f"Implausible Age on line {n}")
        if not all(1 <= nums[k] <= 4 for k in FOUR_POINT):
            raise ValueError(f"Satisfaction/involvement scale outside 1-4 on line {n}")
        if not 1 <= nums["Education"] <= 5 or not 1 <= nums["JobLevel"] <= 5:
            raise ValueError(f"Education or job level outside 1-5 on line {n}")
        if not 1 <= nums["PerformanceRating"] <= 4:
            raise ValueError(f"PerformanceRating outside 1-4 on line {n}")
        if not 0 <= nums["PercentSalaryHike"] <= 100:
            raise ValueError(f"Invalid salary hike percentage on line {n}")
        for f in ("DailyRate", "HourlyRate", "MonthlyIncome", "MonthlyRate"):
            if nums[f] <= 0:
                raise ValueError(f"Non-positive {f} on line {n}")
        for field, limit in (
            ("YearsAtCompany", "TotalWorkingYears"),
            ("YearsInCurrentRole", "YearsAtCompany"),
            ("YearsWithCurrManager", "YearsAtCompany"),
            ("YearsSinceLastPromotion", "YearsAtCompany"),
        ):
            if nums[field] > nums[limit]:
                raise ValueError(f"{field} exceeds {limit} on line {n}")

        yes_count += row["Attrition"] == "Yes"
        rows.append({k: row[k] for k in CLEAN_FIELDS})

    if expected_attritions is not None and yes_count != expected_attritions:
        raise ValueError(f"Unexpected attritions: expected {expected_attritions}, got {yes_count}")
    report = {
        "data_status": "public educational dataset; observational, not causal",
        "source_file": source.name,
        "source_sha256": digest,
        "source_rows": len(raw),
        "source_columns": len(RAW_FIELDS),
        "clean_rows": len(rows),
        "clean_columns": len(CLEAN_FIELDS),
        "recorded_attritions": yes_count,
        "null_or_blank_fields": missing,
        "duplicate_employee_ids": 0,
        "duplicate_rows": 0,
        "removed_constant_columns": list(CONSTANTS),
        "transformations": ["Remove three verified constant columns; preserve all other values and row order"],
        "categorical_frequencies": {k: dict(sorted(v.items())) for k, v in sorted(categories.items())},
        "numeric_observed_ranges": dict(sorted(numeric_ranges.items())),
        "validation_status": "PASS",
        "interpretation_limit": "Source-derived snapshot; not evidence of causal turnover drivers",
    }
    return rows, report


def write_outputs(source: Path = RAW, clean: Path = CLEAN, report_file: Path = REPORT,
                  expected_rows: int | None = 1470,
                  expected_attritions: int | None = 237) -> dict:
    rows, report = validate_and_clean(source, expected_rows, expected_attritions)
    clean.parent.mkdir(parents=True, exist_ok=True)
    report_file.parent.mkdir(parents=True, exist_ok=True)
    with clean.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CLEAN_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    report_file.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n",
                           encoding="utf-8")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=RAW)
    parser.add_argument("--output", type=Path, default=CLEAN)
    parser.add_argument("--report", type=Path, default=REPORT)
    args = parser.parse_args()
    result = write_outputs(args.source, args.output, args.report)
    print(f"PASS: {result['clean_rows']} rows, {result['clean_columns']} columns; "
          f"removed constants={','.join(result['removed_constant_columns'])}")
