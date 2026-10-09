"""Read-only independent KPI cross-check for the raw public insurance dataset.

Outputs aggregate summaries only. In particular, this script must never print
customer names, addresses, account, routing or SSN values.
No SQL/DB connection or additional packages are required.
"""
from __future__ import annotations

import csv
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / "data" / "raw" / "insurance_data.csv"
EXPECTED_TOTAL_ROWS = 10_000
EXPECTED_TOTAL_VALUE = Decimal("165638300.00")
EXPECTED_LIFE_ROWS = 1_682
EXPECTED_LIFE_VALUE = Decimal("91478000.00")
EXPECTED_HIGH_VALUE = 103
THRESHOLD = Decimal("95000")
PERSONAL_LOOKING_COLUMNS = (
    "CUSTOMER_NAME", "ADDRESS_LINE1", "ADDRESS_LINE2",
    "SSN", "ROUTING_NUMBER", "ACCT_NUMBER"
)


def summarize(path: Path) -> dict:
    totals = defaultdict(lambda: {"claims": 0, "total": Decimal(0), "high": 0})
    ids = set()
    count = high_count = 0
    total = Decimal(0)
    with Path(path).open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        columns = reader.fieldnames or []
        missing = {"CLAIM_AMOUNT", "INSURANCE_TYPE", "TRANSACTION_ID"} - set(columns)
        if missing:
            raise ValueError(f"Missing required columns: {sorted(missing)}")
        for line, row in enumerate(reader, 2):
            if None in row:
                raise ValueError(f"Malformed CSV at source line {line}")
            identifier = row["TRANSACTION_ID"]
            if not identifier or identifier in ids:
                raise ValueError(f"Missing/duplicate transaction identifier at line {line}")
            ids.add(identifier)
            try:
                amount = Decimal(row["CLAIM_AMOUNT"])
            except (InvalidOperation, TypeError):
                raise ValueError(f"Invalid claim amount at source line {line}") from None
            if not amount.is_finite():
                raise ValueError(f"Non-finite claim amount at source line {line}")
            category = row["INSURANCE_TYPE"]
            count += 1
            total += amount
            totals[category]["claims"] += 1
            totals[category]["total"] += amount
            if amount >= THRESHOLD:
                high_count += 1
                totals[category]["high"] += 1
    return {
        "records": count,
        "claim_value": total,
        "high_value_claims": high_count,
        "insurance_types": dict(sorted(totals.items())),
        "personal_looking_fields": sorted(set(PERSONAL_LOOKING_COLUMNS) & set(columns)),
    }


def baseline_matches(summary: dict) -> bool:
    life = summary["insurance_types"].get("Life", {})
    return (
        summary["records"] == EXPECTED_TOTAL_ROWS
        and summary["claim_value"] == EXPECTED_TOTAL_VALUE
        and summary["high_value_claims"] == EXPECTED_HIGH_VALUE
        and life.get("claims") == EXPECTED_LIFE_ROWS
        and life.get("total") == EXPECTED_LIFE_VALUE
        and life.get("high") == EXPECTED_HIGH_VALUE
    )


if __name__ == "__main__":
    summary = summarize(SOURCE)
    print("Records:", summary["records"])
    print("Total recorded claim value (dataset units):", summary["claim_value"])
    print("High-value claims:", summary["high_value_claims"])
    for category, values in summary["insurance_types"].items():
        print(category, values["claims"], values["total"], values["high"])
    print("Personal-identifier-like source columns detected:", len(summary["personal_looking_fields"]))
    print("Baseline cross-check:", "PASS" if baseline_matches(summary) else "FAIL")
    if not baseline_matches(summary):
        raise SystemExit(1)
