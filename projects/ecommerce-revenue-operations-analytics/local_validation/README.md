# Local SQL validation — DuckDB (optional, no Snowflake account)

**Status: CI-VERIFIED ON SYNTHETIC DATA (2 November 2026).** This is an optional, independent local test harness. It is **not** a Snowflake benchmark, a dbt/Snowflake integration test, or evidence that all 28 models pass on DuckDB.

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

## Original mart SQL validation (CI-verified on synthetic data)

`check_original_mart.py` reads the **actual repository SQL** for `mart_revenue_financial_reconciliation`, substitutes its one dbt `ref('fct_orders')` with an in-memory synthetic relation, and adapts only `TO_CHAR(..., 'YYYY-MM')` to DuckDB `STRFTIME`. It asserts counts, delivered orders, missing items, mismatch rate and absolute mismatch metrics across two months.

From the repository's E-Commerce project directory (with DuckDB installed in its existing `.venv`):

```powershell
& .\.venv\Scripts\python.exe .\local_validation\check_original_mart.py
```

**Verified on GitHub Actions:** [E-Commerce synthetic SQL validation — run 41484382346](https://github.com/federicaiengo/data-analytics-portfolio/actions/runs/41484382346), completed successfully on **2 November 2026** at source commit `9bdd1cee1156b8de2eef648bac83fd1fe66a4a83`. Both steps passed: `check_monthly_reconciliation.py` and `check_original_mart.py`. The preceding attempt failed before the synthetic fixture columns were aligned; the subsequent commit corrected that fixture and the complete run passed. This is CI execution on a small, synthetic four-order/two-month dataset, **not** a Snowflake query, a full dbt regression, a rerun of the 249-test historical baseline, or a performance benchmark. Upstream `fct_orders` and intermediate models were not executed by this harness. The original mart SQL was not modified.
