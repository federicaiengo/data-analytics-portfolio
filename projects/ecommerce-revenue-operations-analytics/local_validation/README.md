# Local SQL validation — DuckDB (optional, no Snowflake account)

**Status: PREPARED, NOT EXECUTED.** This is an optional, independent local test harness. It is **not** a Snowflake benchmark, a dbt/Snowflake integration test, or evidence that all 28 models pass on DuckDB.

## Scope

Use a **small synthetic dataset** to test the monthly financial reconciliation logic found in `fct_orders` and `mart_revenue_financial_reconciliation`. The original Snowflake/dbt SQL and its materializations remain unchanged. Never upload local `profiles.yml`, credentials, raw business datasets, query history, or private checkpoints.

## Run locally (PowerShell)

From this folder, create an isolated environment using an installed Python version compatible with DuckDB, then install DuckDB from PyPI:

```powershell
py -3.13 -m venv .venv
& .\.venv\Scripts\python.exe -m pip install duckdb
& .\.venv\Scripts\python.exe .\check_monthly_reconciliation.py
```

These commands require package-download access and install only into this folder's virtual environment. They do not contact Snowflake. The script itself uses an in-memory database and does not load user files.

## Interpretation

The script tests four deliberately constructed orders across two months, including a mismatch and a non-comparable null. It verifies that the aggregate count and the comparable/mismatching counts agree with independently stated expected values. A PASS establishes only the synthetic local checks. A FAIL requires investigation. Neither result measures Snowflake performance or proves production data quality.
