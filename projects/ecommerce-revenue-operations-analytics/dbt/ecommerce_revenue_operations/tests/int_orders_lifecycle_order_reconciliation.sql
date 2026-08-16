with source_orders as (

    select
        count(*) as row_count,
        count(distinct order_id) as distinct_order_count
    from {{ ref('stg_orders') }}

),

lifecycle_orders as (

    select
        count(*) as row_count,
        count(distinct order_id) as distinct_order_count
    from {{ ref('int_orders_lifecycle') }}

)

select
    source_orders.row_count as source_row_count,
    lifecycle_orders.row_count as lifecycle_row_count,
    source_orders.distinct_order_count as source_distinct_order_count,
    lifecycle_orders.distinct_order_count as lifecycle_distinct_order_count

from source_orders
cross join lifecycle_orders

where
       source_orders.row_count <> lifecycle_orders.row_count
    or source_orders.distinct_order_count <> lifecycle_orders.distinct_order_count