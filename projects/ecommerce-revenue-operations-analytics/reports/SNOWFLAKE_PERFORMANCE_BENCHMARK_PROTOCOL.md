# Snowflake query performance — controlled benchmark protocol

**Status: NOT EXECUTED. No Snowflake timing, speedup or cost result is claimed here.**
This runbook prepares a reproducible measurement on the existing E-Commerce data models; it does **not** change them.

## Scope and prerequisite

Compare on-demand monthly KPIs computed from `FCT_ORDERS` against equivalent stored pre-aggregated KPIs from `MART_REVENUE_FINANCIAL_RECONCILIATION`. This measures the effect of **reading an already materialized business mart**, not a hypothetical SQL optimizer improvement, nor an end-to-end dbt pipeline acceleration. Additional dbt mart-build time/storage must be accounted for before claiming system-level efficiency.

Verify first that both objects exist and reflect the same completed dbt run. The expected Snowflake database/schema is `ECOMMERCE_ANALYTICS.ANALYTICS`; if your actual dbt target differs, use that deployed schema. Run only in an authorized Snowflake account. These queries are read-only except for reversible session settings.

## 1. Reproducible session

```sql
USE WAREHOUSE ECOMMERCE_WH;
USE DATABASE ECOMMERCE_ANALYTICS;
USE SCHEMA ANALYTICS;

-- Disable the persisted RESULT cache. This does not disable warehouse local data caches.
ALTER SESSION SET USE_CACHED_RESULT = FALSE;

SELECT CURRENT_WAREHOUSE(), CURRENT_DATABASE(), CURRENT_SCHEMA(), CURRENT_ROLE();
```

Record UTC timestamp, warehouse size/state, role, schema, source table and mart row counts, and the dbt run used. Keep the same warehouse and session for both variants. Avoid changing warehouse size, adding clustering keys or using external query accelerators during the trial.

## 2. Correctness gate — must return zero discrepancies

```sql
WITH baseline AS (
    SELECT
        DATE_TRUNC('month', order_purchase_timestamp)::DATE AS month_start_date,
        COUNT(*) AS order_count,
        COUNT_IF(financial_values_match IS NOT NULL) AS comparable_order_count,
        COUNT_IF(financial_values_match = FALSE) AS mismatching_order_count
    FROM FCT_ORDERS
    GROUP BY 1
), mart AS (
    SELECT
        month_start_date, order_count, comparable_order_count, mismatching_order_count
    FROM MART_REVENUE_FINANCIAL_RECONCILIATION
)
SELECT
    b.month_start_date AS baseline_month, m.month_start_date AS mart_month,
    b.order_count AS baseline_orders, m.order_count AS mart_orders,
    b.comparable_order_count AS baseline_comparable, m.comparable_order_count AS mart_comparable,
    b.mismatching_order_count AS baseline_mismatches, m.mismatching_order_count AS mart_mismatches
FROM baseline b
FULL OUTER JOIN mart m
    ON EQUAL_NULL(b.month_start_date, m.month_start_date)
WHERE NOT EQUAL_NULL(b.order_count, m.order_count)
   OR NOT EQUAL_NULL(b.comparable_order_count, m.comparable_order_count)
   OR NOT EQUAL_NULL(b.mismatching_order_count, m.mismatching_order_count);
```

Do not compare elapsed times as interchangeable business outputs if this query returns rows. Resolve stale marts, missing values or semantic differences first.

## 3. Run paired timed queries

Execute the two tagged statements once each for warm-up, then at least three alternating pairs (`baseline → mart → mart → baseline` when practical to reduce order bias). Do not aggregate the warm-up with measured results. Copy the exact statements rather than changing projection or filters between runs.

```sql
ALTER SESSION SET QUERY_TAG = 'FI_ECOM_BASELINE_V1';
-- Baseline: compute the grouped KPI on demand from the order fact.
SELECT
    DATE_TRUNC('month', order_purchase_timestamp)::DATE AS month_start_date,
    COUNT(*) AS order_count,
    COUNT_IF(financial_values_match IS NOT NULL) AS comparable_order_count,
    COUNT_IF(financial_values_match = FALSE) AS mismatching_order_count
FROM FCT_ORDERS
GROUP BY 1
ORDER BY 1;

ALTER SESSION SET QUERY_TAG = 'FI_ECOM_MART_V1';
-- Mart: retrieve the same previously materialized KPI fields.
SELECT
    month_start_date, order_count, comparable_order_count, mismatching_order_count
FROM MART_REVENUE_FINANCIAL_RECONCILIATION
ORDER BY 1;
```

## 4. Collect actual evidence from Snowflake

Set a third tag for the history query. Retrieve actual query IDs and query text, inspect query profiles if surprising, and exclude failures, warm-ups and concurrent heavy warehouse activity. Snowflake statistics are in milliseconds; output rows and bytes scanned are **not** alone a valid speedup measure.

```sql
ALTER SESSION SET QUERY_TAG = 'FI_ECOM_AUDIT_V1';
SELECT
    query_id, start_time, query_tag, warehouse_name, warehouse_size,
    execution_status, total_elapsed_time, execution_time, compilation_time,
    queued_provisioning_time, queued_overload_time,
    bytes_scanned, partitions_scanned, partitions_total
FROM TABLE(INFORMATION_SCHEMA.QUERY_HISTORY_BY_SESSION(RESULT_LIMIT => 1000))
WHERE query_tag IN ('FI_ECOM_BASELINE_V1', 'FI_ECOM_MART_V1')
  AND execution_status = 'success'
ORDER BY start_time;
```

Record three or more **measured** times for each variant, their median and spread, number of rows returned, cold/warm cache notes and all query IDs. Do not turn small-dataset timing noise into a claim of cost reduction. For total cost assessment, the extra dbt materialization work and storage matter.

## 5. Stop conditions / publication policy

- If result sets do not reconcile: **FAIL**, no benchmark claim.
- If the Snowflake warehouse cannot be accessed: **NOT EXECUTED**, retain this protocol only.
- If measured performance overlaps within noise: report **no demonstrated speed advantage**.
- If times differ: report measured milliseconds and conditions, never imply causality beyond this controlled setup.
- Never publish connection credentials, tenant-specific business data, private query URLs or raw account identifiers.

**Documentation references:** [Snowflake ALTER SESSION](https://docs.snowflake.com/sql-reference/sql/alter-session) · [QUERY_HISTORY_BY_SESSION](https://docs.snowflake.com/en/sql-reference/functions/query_history).
