with orders as (

    select
        order_id,
        customer_id,
        order_status
    from {{ ref('stg_orders') }}

),

order_items as (

    select *
    from {{ ref('int_order_items_summary') }}

),

order_payments as (

    select *
    from {{ ref('int_order_payments_summary') }}

),

final as (

    select
        orders.order_id,
        orders.customer_id,
        orders.order_status,

        order_items.order_item_count,
        order_items.distinct_product_count,
        order_items.distinct_seller_count,
        order_items.item_sales_value,
        order_items.freight_value,
        order_items.item_plus_freight_value,

        order_payments.payment_record_count,
        order_payments.distinct_payment_type_count,
        order_payments.max_payment_installments,
        order_payments.payment_value,

        order_items.order_id is null as missing_item_summary,
        order_payments.order_id is null as missing_payment_summary,

        case
            when order_items.order_id is not null
             and order_payments.order_id is not null
            then order_payments.payment_value
                 - order_items.item_plus_freight_value
            else null
        end as payment_minus_item_freight_value,

        case
            when order_items.order_id is not null
             and order_payments.order_id is not null
            then abs(
                order_payments.payment_value
                - order_items.item_plus_freight_value
            ) <= 0.01
            else null
        end as financial_values_match

    from orders

    left join order_items
        on orders.order_id = order_items.order_id

    left join order_payments
        on orders.order_id = order_payments.order_id

)

select *
from final