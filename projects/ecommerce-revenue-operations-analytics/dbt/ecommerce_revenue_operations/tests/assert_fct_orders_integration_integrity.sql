with lifecycle as (

    select
        count(*) as row_count,
        count(distinct order_id) as distinct_order_count
    from {{ ref('int_orders_lifecycle') }}

),

financial as (

    select
        count(*) as row_count,
        count(distinct order_id) as distinct_order_count
    from {{ ref('int_order_financial_reconciliation') }}

),

reviews as (

    select
        count(*) as row_count,
        count(distinct order_id) as distinct_order_count
    from {{ ref('int_order_reviews_summary') }}

),

fact as (

    select
        count(*) as row_count,
        count(distinct order_id) as distinct_order_count,
        count_if(order_id is null) as null_order_id_count,
        count_if(missing_item_summary is null) as missing_financial_join_count,
        count_if(missing_payment_summary is null) as missing_payment_flag_count,
        count_if(review_record_count is not null) as orders_with_review_summary
    from {{ ref('fct_orders') }}

)

select
    lifecycle.row_count as lifecycle_row_count,
    financial.row_count as financial_row_count,
    reviews.row_count as review_summary_row_count,
    fact.row_count as fact_row_count,
    fact.distinct_order_count as fact_distinct_order_count,
    fact.null_order_id_count,
    fact.missing_financial_join_count,
    fact.missing_payment_flag_count,
    fact.orders_with_review_summary
from lifecycle
cross join financial
cross join reviews
cross join fact
where
       fact.row_count <> lifecycle.row_count
    or fact.distinct_order_count <> lifecycle.distinct_order_count
    or fact.null_order_id_count <> 0
    or financial.row_count <> lifecycle.row_count
    or financial.distinct_order_count <> lifecycle.distinct_order_count
    or reviews.row_count <> reviews.distinct_order_count
    or fact.orders_with_review_summary <> reviews.row_count
    or fact.missing_financial_join_count <> 0
    or fact.missing_payment_flag_count <> 0