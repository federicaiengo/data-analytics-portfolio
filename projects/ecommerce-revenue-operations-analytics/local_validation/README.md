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

## Original intermediate SQL validation (CI-verified, 3 November 2026)

`check_original_intermediate_reconciliation.py` loads the **unchanged repository SQL** for the original `int_order_items_summary`, `int_order_payments_summary` and `int_order_financial_reconciliation` models. It substitutes their exact dbt `ref()` dependencies with DuckDB in-memory relations, rejecting unexpected or unresolved templating. It does not implement or silently simplify the SQL transformations.

Seven synthetic order rows test the join grain when one order has **two items and three payments**, the NULL states for missing item/payment summaries, both directions of financial mismatch, exact-cent tolerance (`0.01` matching vs `0.02` mismatching), and exclusion of orphan staging rows. The deliberately naive raw JOIN produces six rows for the many-to-many example; the original aggregate-before-join models retain one row per modeled order.

**Observed CI:** [run 41545865668](https://github.com/federicaiengo/data-analytics-portfolio/actions/runs/41545865668) on source commit `eecdec7b0b21efac61b6c4df7283d01f33738f2f` completed **SUCCESS**, with all **three** validation steps passing: synthetic monthly counts, original monthly mart, and original intermediate models. The workflow is triggered again when the three original intermediate SQL files, the mart SQL, its harness or the workflow definition change.

Run from the E-Commerce project directory with DuckDB installed:

```powershell
& .\\.venv\\Scripts\\python.exe .\\local_validation\\check_original_intermediate_reconciliation.py
```

**Limits:** This is an isolated synthetic, in-memory SQL model check. It is **not** execution of original staging transformations, `int_orders_lifecycle`, `fct_orders`, the review models, the full 28-model dbt DAG, Snowflake workloads, actual raw Olist rows, or Snowflake-vs-DuckDB performance. The original 249/249 dbt result remains a separate historical Snowflake-era result. The expired Snowflake access is not required for this validation.

## Original lifecycle SQL SELECT (CI-verified, 3 November 2026)

`check_original_lifecycle.py` exercises the SQL SELECT of the **original** `int_orders_lifecycle.sql` against eight deliberately constructed synthetic orders in DuckDB. To run a full-refresh-style SELECT independently of Snowflake/dbt, the harness explicitly strips the original dbt materialization `config()` and the conditional `is_incremental()` filter, then substitutes one verified `ref('stg_orders')`. Unrecognized Jinja fails closed instead of being silently rewritten. The underlying original dbt SQL file is not modified.

Checks cover order-level uniqueness, normal order lifecycle timings, approval before purchase, carrier before approval, delivery before carrier or purchase, estimated delivery before purchase, missing approval and missing delivery timestamps, and the distinction between an unavailable timestamp and a temporal-sequence anomaly. Negative intervals remain NULL where defined by the original SQL.

**Observed CI:** [run 41546194247](https://github.com/federicaiengo/data-analytics-portfolio/actions/runs/41546194247) on commit `e7b0a826747be117e1d77b957f13791311adbbbf` completed **SUCCESS**. All **four** workflow steps passed, including the original intermediate reconciliation models, the original monthly mart, and this original lifecycle SELECT. Future modifications to `int_orders_lifecycle.sql` also trigger this workflow.

To run the lifecycle check locally from this project's directory:

```powershell
& .\\.venv\\Scripts\\python.exe .\\local_validation\\check_original_lifecycle.py
```

**Not demonstrated:** dbt incremental `MERGE`, watermark/resume behavior, Snowflake SQL execution or warehouse performance, the original staging models, the real Olist dataset, the fact-table join, and a full-project 28-model regression. This harness extends low-cost regression coverage after loss of Snowflake access; it is **not** a complete warehouse migration.
