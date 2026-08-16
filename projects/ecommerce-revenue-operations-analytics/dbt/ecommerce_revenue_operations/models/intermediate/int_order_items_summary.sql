with order_items as (

    select *
    from {{ ref('stg_order_items') }}

),

aggregated as (

    select
        order_id,

        count(*) as order_item_count,
        count(distinct product_id) as distinct_product_count,
        count(distinct seller_id) as distinct_seller_count,

        sum(price) as item_sales_value,
        sum(freight_value) as freight_value,
        sum(price + freight_value) as item_plus_freight_value

    from order_items

    group by
        order_id

)

select *
from aggregated