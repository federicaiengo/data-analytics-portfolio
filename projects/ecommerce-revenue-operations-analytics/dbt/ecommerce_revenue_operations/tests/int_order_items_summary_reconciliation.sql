with source as (

    select
        count(*) as source_item_row_count,
        sum(price) as source_item_sales_value,
        sum(freight_value) as source_freight_value,
        sum(price + freight_value) as source_item_plus_freight_value

    from {{ ref('stg_order_items') }}

),

summary as (

    select
        sum(order_item_count) as summary_item_row_count,
        sum(item_sales_value) as summary_item_sales_value,
        sum(freight_value) as summary_freight_value,
        sum(item_plus_freight_value) as summary_item_plus_freight_value

    from {{ ref('int_order_items_summary') }}

)

select
    source_item_row_count,
    summary_item_row_count,
    source_item_sales_value,
    summary_item_sales_value,
    source_freight_value,
    summary_freight_value,
    source_item_plus_freight_value,
    summary_item_plus_freight_value

from source
cross join summary

where
       source_item_row_count <> summary_item_row_count
    or source_item_sales_value <> summary_item_sales_value
    or source_freight_value <> summary_freight_value
    or source_item_plus_freight_value <> summary_item_plus_freight_value