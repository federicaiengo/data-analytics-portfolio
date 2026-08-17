-- Reconciliation test for int_order_reviews_summary
--
-- Validates that the order-level review aggregation preserves the
-- profiled source population and known multi-review characteristics.
--
-- dbt singular tests PASS when this query returns zero rows.

with reconciliation as (

    select
        count(*) as row_count,
        count(distinct order_id) as distinct_order_count,
        sum(review_record_count) as reconciled_review_rows,
        count_if(review_record_count > 1) as multi_review_orders,
        count_if(has_multiple_review_scores) as multi_score_orders,
        max(review_record_count) as max_reviews_per_order

    from {{ ref('int_order_reviews_summary') }}

)

select *
from reconciliation
where
       row_count <> 98673
    or distinct_order_count <> 98673
    or reconciled_review_rows <> 99224
    or multi_review_orders <> 547
    or multi_score_orders <> 202
    or max_reviews_per_order <> 3