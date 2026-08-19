with source_totals as (

    select
        count(*) as order_count,

        round(sum(item_sales_value), 2) as item_sales_value,
        round(sum(freight_value), 2) as freight_value,
        round(sum(item_plus_freight_value), 2) as item_plus_freight_value,
        round(sum(payment_value), 2) as payment_value,

        count_if(financial_values_match is not null) as comparable_order_count,
        count_if(financial_values_match = true) as matching_order_count,
        count_if(financial_values_match = false) as mismatching_order_count

    from {{ ref('fct_orders') }}

),

mart_totals as (

    select
        sum(order_count) as order_count,

        round(sum(item_sales_value), 2) as item_sales_value,
        round(sum(freight_value), 2) as freight_value,
        round(sum(item_plus_freight_value), 2) as item_plus_freight_value,
        round(sum(payment_value), 2) as payment_value,

        sum(comparable_order_count) as comparable_order_count,
        sum(matching_order_count) as matching_order_count,
        sum(mismatching_order_count) as mismatching_order_count

    from {{ ref('mart_revenue_financial_reconciliation') }}

)

select
    s.order_count as source_order_count,
    m.order_count as mart_order_count,

    s.item_sales_value as source_item_sales_value,
    m.item_sales_value as mart_item_sales_value,

    s.freight_value as source_freight_value,
    m.freight_value as mart_freight_value,

    s.item_plus_freight_value as source_item_plus_freight_value,
    m.item_plus_freight_value as mart_item_plus_freight_value,

    s.payment_value as source_payment_value,
    m.payment_value as mart_payment_value,

    s.comparable_order_count as source_comparable_order_count,
    m.comparable_order_count as mart_comparable_order_count,

    s.matching_order_count as source_matching_order_count,
    m.matching_order_count as mart_matching_order_count,

    s.mismatching_order_count as source_mismatching_order_count,
    m.mismatching_order_count as mart_mismatching_order_count

from source_totals as s
cross join mart_totals as m

where
       s.order_count <> m.order_count
    or s.item_sales_value <> m.item_sales_value
    or s.freight_value <> m.freight_value
    or s.item_plus_freight_value <> m.item_plus_freight_value
    or s.payment_value <> m.payment_value
    or s.comparable_order_count <> m.comparable_order_count
    or s.matching_order_count <> m.matching_order_count
    or s.mismatching_order_count <> m.mismatching_order_count