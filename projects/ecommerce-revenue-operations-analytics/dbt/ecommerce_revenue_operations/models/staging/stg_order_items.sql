with source as (

    select *
    from {{ source('olist_raw', 'order_items') }}

),

renamed_and_typed as (

    select
        order_id,
        try_to_number(order_item_id, 38, 0) as order_item_id,
        product_id,
        seller_id,
        try_to_timestamp_ntz(shipping_limit_date) as shipping_limit_date,
        try_to_decimal(price, 12, 2) as price,
        try_to_decimal(freight_value, 12, 2) as freight_value

    from source

)

select *
from renamed_and_typed