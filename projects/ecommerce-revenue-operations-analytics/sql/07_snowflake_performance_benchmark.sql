-- ============================================================
-- 07_snowflake_performance_benchmark.sql
-- E-Commerce Revenue & Operations Analytics
-- Reproducible Snowflake query-performance benchmark
-- ============================================================
--
-- PURPOSE
-- Compare two logically equivalent financial-reconciliation queries:
--
--   BASELINE:
--     Re-aggregates order items and payments from staging tables
--     every time the analytical query is executed.
--
--   OPTIMIZED:
--     Reads a deliberately materialized session TEMPORARY TABLE,
--     created from the dbt intermediate VIEW. This explicitly measures
--     read-side materialization; the build has a separate, real cost.
--
-- IMPORTANT
-- Do not publish performance claims until this script has been run
-- in Snowflake and the observed metrics have been copied into
-- reports/snowflake_performance_results.md.
--
-- Run both queries in the SAME session and warehouse.
-- The dbt project config materializes intermediate models as VIEWS,
-- so comparing the view alone would NOT be a table-vs-reaggregation
-- benchmark. A temporary table is created explicitly below.
-- Persisted result reuse is disabled. Warehouse cache can still matter.
-- ============================================================


use database ECOMMERCE_ANALYTICS;
use schema ANALYTICS;

alter session set use_cached_result = false;


-- ------------------------------------------------------------
-- 0. SESSION / WAREHOUSE CONTEXT
-- ------------------------------------------------------------

select
    current_account() as account_name,
    current_region() as region,
    current_warehouse() as warehouse_name,
    current_database() as database_name,
    current_schema() as schema_name,
    current_timestamp() as benchmark_started_at;


-- ------------------------------------------------------------
-- A. ONE-TIME SESSION MATERIALIZATION (COST MUST BE RECORDED)
-- ------------------------------------------------------------
-- This is a session TEMPORARY TABLE, not a permanent production model.
-- Its creation scans/aggregates the dbt VIEW and has time/compute cost.
-- Only read-side queries benefit until the table needs rebuilding.
-- Comparing this against one baseline query WITHOUT accounting for
-- build cost would be misleading.
--
alter session set query_tag = 'portfolio_perf_build_temp_reconciliation';

create or replace temporary table BENCHMARK_ORDER_FINANCIAL_RECONCILIATION as
select
    order_id,
    financial_values_match,
    payment_minus_item_freight_value
from BENCHMARK_ORDER_FINANCIAL_RECONCILIATION;


-- ------------------------------------------------------------
-- 1. BASELINE QUERY
-- ------------------------------------------------------------
-- This reproduces reconciliation directly from staging data.
-- It intentionally performs the item and payment aggregation
-- inside the reporting query.

alter session set query_tag = 'portfolio_perf_baseline_financial_reconciliation';

with item_summary as (

    select
        order_id,
        count(*) as order_item_count,
        sum(price) as item_sales_value,
        sum(freight_value) as freight_value,
        sum(price + freight_value) as item_plus_freight_value
    from STG_ORDER_ITEMS
    group by order_id

),

payment_summary as (

    select
        order_id,
        count(*) as payment_record_count,
        sum(payment_value) as payment_value
    from STG_ORDER_PAYMENTS
    group by order_id

),

reconciliation as (

    select
        o.order_id,
        o.order_status,
        i.order_item_count,
        p.payment_record_count,
        i.item_sales_value,
        i.freight_value,
        i.item_plus_freight_value,
        p.payment_value,
        p.payment_value - i.item_plus_freight_value
            as payment_minus_item_freight_value,
        case
            when i.order_id is null or p.order_id is null then null
            when abs(p.payment_value - i.item_plus_freight_value) <= 0.01
                then true
            else false
        end as financial_values_match
    from STG_ORDERS o
    left join item_summary i
        on o.order_id = i.order_id
    left join payment_summary p
        on o.order_id = p.order_id

)

select
    count(*) as order_count,
    count_if(financial_values_match is not null) as comparable_orders,
    count_if(financial_values_match = true) as matching_orders,
    count_if(financial_values_match = false) as mismatching_orders,
    round(
        100.0 * count_if(financial_values_match = false)
        / nullif(count_if(financial_values_match is not null), 0),
        4
    ) as mismatch_pct,
    round(
        avg(
            case
                when financial_values_match = false
                    then abs(payment_minus_item_freight_value)
            end
        ),
        2
    ) as avg_abs_mismatch
from reconciliation;


-- ------------------------------------------------------------
-- 2. OPTIMIZED QUERY
-- ------------------------------------------------------------
-- Reads the explicitly created TEMPORARY TABLE, not the dbt VIEW.
-- Record the separate temporary-table build cost, not just read time.

alter session set query_tag = 'portfolio_perf_optimized_financial_reconciliation';

select
    count(*) as order_count,
    count_if(financial_values_match is not null) as comparable_orders,
    count_if(financial_values_match = true) as matching_orders,
    count_if(financial_values_match = false) as mismatching_orders,
    round(
        100.0 * count_if(financial_values_match = false)
        / nullif(count_if(financial_values_match is not null), 0),
        4
    ) as mismatch_pct,
    round(
        avg(
            case
                when financial_values_match = false
                    then abs(payment_minus_item_freight_value)
            end
        ),
        2
    ) as avg_abs_mismatch
from BENCHMARK_ORDER_FINANCIAL_RECONCILIATION;


-- ------------------------------------------------------------
-- 3. VERIFY LOGICAL EQUIVALENCE
-- ------------------------------------------------------------
-- Both approaches must return the same business result before
-- runtime differences are interpreted as an optimization.

with baseline as (

    with item_summary as (
        select
            order_id,
            count(*) as order_item_count,
            sum(price) as item_sales_value,
            sum(freight_value) as freight_value,
            sum(price + freight_value) as item_plus_freight_value
        from STG_ORDER_ITEMS
        group by order_id
    ),

    payment_summary as (
        select
            order_id,
            count(*) as payment_record_count,
            sum(payment_value) as payment_value
        from STG_ORDER_PAYMENTS
        group by order_id
    )

    select
        o.order_id,
        p.payment_value - i.item_plus_freight_value
            as payment_minus_item_freight_value,
        case
            when i.order_id is null or p.order_id is null then null
            when abs(p.payment_value - i.item_plus_freight_value) <= 0.01
                then true
            else false
        end as financial_values_match
    from STG_ORDERS o
    left join item_summary i
        on o.order_id = i.order_id
    left join payment_summary p
        on o.order_id = p.order_id

),

optimized as (

    select
        order_id,
        payment_minus_item_freight_value,
        financial_values_match
    from BENCHMARK_ORDER_FINANCIAL_RECONCILIATION

)

select
    count(*) as differing_rows
from baseline b
full outer join optimized o
    on b.order_id = o.order_id
where
       b.order_id is null
    or o.order_id is null
    or coalesce(b.financial_values_match::varchar, 'NULL')
       <> coalesce(o.financial_values_match::varchar, 'NULL')
    or abs(
        coalesce(b.payment_minus_item_freight_value, 0)
        - coalesce(o.payment_minus_item_freight_value, 0)
    ) > 0.0001;


-- ------------------------------------------------------------
-- 4. CAPTURE QUERY METRICS
-- ------------------------------------------------------------
-- QUERY_HISTORY_BY_SESSION is used because it is available
-- immediately, unlike ACCOUNT_USAGE views that may have latency.

alter session set query_tag = 'portfolio_perf_metrics_capture';

select
    query_id,
    query_tag,
    start_time,
    end_time,
    execution_status,
    total_elapsed_time,
    execution_time,
    compilation_time,
    bytes_scanned,
    partitions_scanned,
    partitions_total,
    rows_produced
from table(
    information_schema.query_history_by_session(
        result_limit => 100
    )
)
where query_tag in (
    'portfolio_perf_baseline_financial_reconciliation',
    'portfolio_perf_optimized_financial_reconciliation',
    'portfolio_perf_build_temp_reconciliation'
)
order by start_time;


-- ------------------------------------------------------------
-- 5. OPTIONAL NORMALIZED COMPARISON
-- ------------------------------------------------------------
-- Run each benchmark query several times in alternating order
-- if you want a more defensible comparison. Record every run,
-- report the median, and preserve warehouse size/configuration.
--
-- Do not present a single warm/cold run as a universal Snowflake
-- performance claim. Include the one-time table-build cost and
-- refresh frequency when discussing break-even across repeated reads.
-- ------------------------------------------------------------

alter session unset query_tag;
