with source_orders as (

    select
        count(*) as row_count,
        count(distinct order_id) as distinct_order_count
    from {{ ref('stg_orders') }}

),

reconciliation as (

    select
        count(*) as row_count,
        count(distinct order_id) as distinct_order_count
    from {{ ref('int_order_financial_reconciliation') }}

)

select
    source_orders.row_count as source_row_count,
    reconciliation.row_count as reconciliation_row_count,
    source_orders.distinct_order_count as source_distinct_order_count,
    reconciliation.distinct_order_count as reconciliation_distinct_order_count
from source_orders
cross join reconciliation

where
       source_orders.row_count <> reconciliation.row_count
    or source_orders.distinct_order_count <> reconciliation.distinct_order_count