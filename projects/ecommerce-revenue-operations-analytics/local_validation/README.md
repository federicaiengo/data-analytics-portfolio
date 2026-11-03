# Local SQL validation — DuckDB (optional, no Snowflake account)

**Status: CI-VERIFIED ON SYNTHETIC DATA (2–3 November 2026).** This is an optional, independent local test harness. It is **not** a Snowflake benchmark, a dbt/Snowflake integration test, or evidence that all 28 models pass on DuckDB.

## Scope

Use **small, deliberately constructed synthetic datasets** to validate individual original SQL models and a connected **11-model original-SQL subset**, from synthetic RAW strings through four staging views and seven downstream views to the monthly financial mart. The original Snowflake/dbt SQL and its materializations remain unchanged. Never upload local `profiles.yml`, credentials, raw business datasets, query history, or private checkpoints.

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

**Limits:** This is an isolated synthetic, in-memory SQL model check. It is **not** execution of original staging transformations, `int_orders_lifecycle`, `fct_orders`, the review models, the full 28-model dbt DAG, Snowflake workloads, actual raw Olist rows, or Snowflake-vs-DuckDB performance. The original 249/249 dbt result remains a separate historical Snowflake-era result. No working Snowflake warehouse is required for these tests.

## Original lifecycle SQL SELECT (CI-verified, 3 November 2026)

`check_original_lifecycle.py` exercises the SQL SELECT of the **original** `int_orders_lifecycle.sql` against eight deliberately constructed synthetic orders in DuckDB. To run a full-refresh-style SELECT independently of Snowflake/dbt, the harness explicitly strips the original dbt materialization `config()` and the conditional `is_incremental()` filter, then substitutes one verified `ref('stg_orders')`. Unrecognized Jinja fails closed instead of being silently rewritten. The underlying original dbt SQL file is not modified.

Checks cover order-level uniqueness, normal order lifecycle timings, approval before purchase, carrier before approval, delivery before carrier or purchase, estimated delivery before purchase, missing approval and missing delivery timestamps, and the distinction between an unavailable timestamp and a temporal-sequence anomaly. Negative intervals remain NULL where defined by the original SQL.

**Observed CI:** [run 41546194247](https://github.com/federicaiengo/data-analytics-portfolio/actions/runs/41546194247) on commit `e7b0a826747be117e1d77b957f13791311adbbbf` completed **SUCCESS**. All **four** workflow steps passed, including the original intermediate reconciliation models, the original monthly mart, and this original lifecycle SELECT. Future modifications to `int_orders_lifecycle.sql` also trigger this workflow.

To run the lifecycle check locally from this project's directory:

```powershell
& .\\.venv\\Scripts\\python.exe .\\local_validation\\check_original_lifecycle.py
```

**Not demonstrated:** dbt incremental `MERGE`, watermark/resume behavior, Snowflake SQL execution or warehouse performance, the original staging models, the real Olist dataset, the fact-table join, and a full-project 28-model regression. This harness extends low-cost regression coverage while Snowflake is unavailable; it is **not** a complete warehouse migration.

## Original fact and review SQL checks (CI-verified, 3 November 2026)

**Fact-layer test:** `check_original_fact_orders.py` executes the **unchanged original** `fct_orders.sql` using exact substitutions for three upstream `ref()` calls. Its pre-aggregated lifecycle, financial and review relations are **independently constructed synthetic fixtures**; it does not execute those upstream models as one connected dbt DAG. Five synthetic lifecycle orders test order-level grain, preservation of orders with missing finance or review summaries, exact propagation of amounts, reconciliation states, review fields and temporal flags, and exclusion of orphan upstream records.

The test also deliberately duplicates a review-summary row to **demonstrate a limitation**: the fact's left join would multiply rows when an upstream `order_id` is not unique. The source model assumes upstream grain/uniqueness rather than independently enforcing it. A passing test of this adversarial case does **not** mean the fact model itself protects against duplicate keys.

**Review-layer test:** `check_original_reviews_summary.py` executes the **unchanged original** `int_order_reviews_summary.sql`, substituting only its exact staging `ref()` with six fabricated review rows. It checks per-order grouping, total vs distinct review IDs, average/min/max scores, differing and NULL scores, first/last timestamps, and title/message presence.

**Verified CI:** [E-Commerce synthetic SQL validation run 41558348936](https://github.com/federicaiengo/data-analytics-portfolio/actions/runs/41558348936) on commit `d8060f509299a312e4527bcd1ef8d2e219f10327` completed **SUCCESS** with **six validation scripts passing**, including both new tests. Workflow path filters also cover modifications to the original `fct_orders.sql` and `int_order_reviews_summary.sql`.

Run from the E-Commerce project directory with DuckDB installed:

```powershell
& .\\.venv\\Scripts\\python.exe .\\local_validation\\check_original_fact_orders.py
& .\\.venv\\Scripts\\python.exe .\\local_validation\\check_original_reviews_summary.py
```

**Coverage accounting:** These six scripts exercise SQL from **seven original dbt models in isolated synthetic fixtures** (three financial intermediates, order lifecycle, order reviews, `fct_orders`, and the monthly reconciliation mart). They **do not** compile or execute the connected 28-model dbt project, original Snowflake staging models, any real Snowflake dataset, incremental `MERGE`, or a cross-platform performance benchmark. Snowflake-origin historical results are preserved as historical evidence, not presented as current DuckDB measurements.

## Initial seven-model subset — historical validation (CI-verified, 3 November 2026)

The initial version of `check_integrated_financial_pipeline.py` ran a **single connected DuckDB pipeline** using the original repository SQL for these seven dbt models:

1. `int_order_items_summary`
2. `int_order_payments_summary`
3. `int_order_financial_reconciliation`
4. `int_order_reviews_summary`
5. `int_orders_lifecycle`
6. `fct_orders`
7. `mart_revenue_financial_reconciliation`

In this initial stage, the models read the **same four typed, deliberately synthetic staging tables** (`stg_orders`, `stg_order_items`, `stg_order_payments`, `stg_order_reviews`). The script creates the seven views in dependency order, validates the grain at intermediate, fact and monthly levels, and checks independently specified monthly financial figures.

Eight fabricated orders across January–February exercise two-item/two-payment JOIN multiplication, source orphans, missing both finance summaries, missing reviews, score aggregation, event-order anomaly, exact 0.01 vs 0.02 mismatch tolerance, and month-level totals. Verified expected monthly results: January **4 orders, 2 comparable, 1 mismatching, 50% mismatch rate, 195.00 item+freight, 220.00 payments, 5.00 absolute mismatch**; February **4 orders, 3 comparable, 1 mismatching, approximately 33.33% mismatch rate, 105.00 item+freight, 50.03 payments, 0.02 absolute mismatch**. Currency units are not implied by the synthetic amounts.

**Verified CI:** [GitHub Actions run 41560038307](https://github.com/federicaiengo/data-analytics-portfolio/actions/runs/41560038307) on source commit `5afcb397673012fb848f64e5bfe51026b977dba4`, **COMPLETED / SUCCESS**: seven validation scripts PASS, including the new integrated chain. The previous six isolated tests remain in the workflow.

Run locally from the E-Commerce project directory with DuckDB installed:

```powershell
& .\\.venv\\Scripts\\python.exe .\\local_validation\\check_integrated_financial_pipeline.py
```

**Initial-stage limits:** This was a connected **seven-model SQL subset**, not the full 28-model dbt project. Its four input tables are **typed synthetic staging fixtures** rather than original staging-model SQL or actual Olist/Snowflake data. The `int_orders_lifecycle` SELECT is executed in **full-refresh style**, with an explicitly guarded removal of its dbt `config()` and `is_incremental()` Jinja block. The original monthly mart requires **one explicit `TO_CHAR` → `STRFTIME` substitution** for DuckDB. Other SQL is reused with strictly verified `ref()` substitutions. No incremental `MERGE` / watermark state, dbt compilation, historical 249-check rerun, production deployment, or Snowflake-vs-DuckDB performance comparison is demonstrated. No Snowflake credentials or stored Snowflake data are read.

## Expanded RAW-to-mart 11-model chain (CI-verified, 3 November 2026)

The **current** `check_integrated_financial_pipeline.py` uses four deliberately fabricated RAW text tables to run an **integrated 11-model SQL subset**, consisting of four original staging models plus the seven original models documented above:

- `stg_orders`, `stg_order_items`, `stg_order_payments`, `stg_order_reviews` — **actual original staging SQL** using the narrow, fail-closed `original_staging_duckdb.py` bridge.
- `int_order_items_summary`, `int_order_payments_summary`, `int_order_financial_reconciliation`, `int_order_reviews_summary`, `int_orders_lifecycle`, `fct_orders`, `mart_revenue_financial_reconciliation` — seven downstream original SQL models chained from the staging views.

The original Snowflake/dbt SQL source files remain **unchanged**. Four `source('olist_raw', ...)` calls are substituted with explicit local RAW fixture tables; the stage adapter converts only explicitly counted `TRY_TO_TIMESTAMP_NTZ`, `TRY_TO_NUMBER(...,38,0)`, and `TRY_TO_DECIMAL(...,12,2)` expressions into DuckDB `TRY_CAST` expressions. It rejects unrecognized conversions or templating instead of silently relaxing the SQL. This is **dialect adaptation**, not demonstrated equivalence between all Snowflake and DuckDB conversion behavior.

The eight synthetic orders and previously hand-specified January/February financial expectations remain unchanged. Additional negative fixtures exercise conversion of **malformed raw price, payment amount, review score, and review timestamp to NULL** in staging without contaminating fact-level data, because those malformed records are synthetic source orphans. The workflow still checks JOIN grain, source orphan exclusion, financial thresholds, review and lifecycle flags, and exact monthly aggregates.

**Verified CI:** [GitHub Actions run 41561089884](https://github.com/federicaiengo/data-analytics-portfolio/actions/runs/41561089884) on source commit `bbeea3138a4ef707fb53b47e167ef3793a7f569b` completed **SUCCESS**. **Seven Python validation scripts pass**, including the 11-model connected chain. Four original staging SQL paths are monitored by the workflow on push/PR.

```powershell
& .\\.venv\\Scripts\\python.exe .\\local_validation\\check_integrated_financial_pipeline.py
```

**Scope boundary:** This is **11/28 original-model SQL expressions covered by a connected synthetic subset**, with documented Snowflake-to-DuckDB syntax substitutions. It does **not** run the real Olist/Snowflake records, the original Snowflake warehouse, actual dbt compilation, any dbt incremental `MERGE`/watermark, the 17 other dbt models, all 249 historical dbt regression checks, or a representative performance benchmark. Existing Snowflake access details and data are retained by the owner but the warehouse is currently unavailable; this script does not access them.

## Local incremental MERGE semantics experiment (CI-verified, 3 November 2026)

`check_local_incremental_semantics.py` tests the **original** `int_orders_lifecycle.sql` full-refresh and incremental-selection SQL, under guarded removal of the dbt `config()` and conditional Jinja tags. The original **`>= MAX(_loaded_at)` predicate**, `unique_key='order_id'` and `incremental_strategy='merge'` are checked against repository source. A separate **locally constructed DuckDB `MERGE` statement** applies matching updates and nonmatching inserts to a synthetic target table. This statement is **not dbt-compiled SQL** and does not test the Snowflake dbt adapter or its generated MERGE.

Synthetic batch scenarios and expectations include:

- Repeat a batch with no source changes: full row snapshot identical (**idempotent**).
- Update an existing order with the *same* watermark as the latest batch: the change is merged.
- Add a new order with a later watermark: it is inserted with no duplicate `order_id`.
- Repeat the last batch and insert another order **tied to the maximum watermark**: reprocessing remains idempotent and the new key appears.
- Modify an older source row **without advancing its old `_loaded_at`**: the change is deliberately **not** picked up by the watermark filter. This is a documented limitation of the source design and an important operational risk, **not a passing guarantee that late corrections will be ingested**.

**Verified CI:** [E-Commerce synthetic SQL validation run 41561443051](https://github.com/federicaiengo/data-analytics-portfolio/actions/runs/41561443051), source commit `24b52035d5d5f72bbf1b81b0739545f6a02ff296`, **COMPLETED / SUCCESS**; **eight Python validation scripts passed**, including the 11-model integrated subset and this separate local incremental experiment.

```powershell
& .\\.venv\\Scripts\\python.exe .\\local_validation\\check_local_incremental_semantics.py
```

**Boundary:** This verifies a **DuckDB local emulation** of the documented incremental contract. It does **not** compile or execute dbt incremental models, test Snowflake's real `MERGE`, prove end-to-end production idempotence, replay actual source history, or solve the backdated-correction limitation. The retained Snowflake access details and data are neither loaded nor accessed.
