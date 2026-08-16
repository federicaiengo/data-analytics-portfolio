with orders as (

    select *
    from {{ ref('stg_orders') }}

),

final as (

    select
        order_id,
        customer_id,
        order_status,

        order_purchase_timestamp,
        order_approved_at,
        order_delivered_carrier_date,
        order_delivered_customer_date,
        order_estimated_delivery_date,

        order_approved_at is null
            as is_approval_missing,

        order_delivered_carrier_date is null
            as is_carrier_timestamp_missing,

        order_delivered_customer_date is null
            as is_customer_delivery_timestamp_missing,

        (
            order_status = 'delivered'
            and order_approved_at is null
        ) as is_delivered_order_missing_approval,

        (
            order_status = 'delivered'
            and order_delivered_carrier_date is null
        ) as is_delivered_order_missing_carrier_timestamp,

        (
            order_status = 'delivered'
            and order_delivered_customer_date is null
        ) as is_delivered_order_missing_customer_delivery_timestamp,

        (
            order_approved_at is not null
            and order_purchase_timestamp is not null
            and order_approved_at < order_purchase_timestamp
        ) as approval_before_purchase,

        (
            order_delivered_carrier_date is not null
            and order_approved_at is not null
            and order_delivered_carrier_date < order_approved_at
        ) as carrier_before_approval,

        (
            order_delivered_customer_date is not null
            and order_delivered_carrier_date is not null
            and order_delivered_customer_date < order_delivered_carrier_date
        ) as customer_delivery_before_carrier,

        (
            order_delivered_customer_date is not null
            and order_purchase_timestamp is not null
            and order_delivered_customer_date < order_purchase_timestamp
        ) as customer_delivery_before_purchase,

        (
            order_estimated_delivery_date is not null
            and order_purchase_timestamp is not null
            and order_estimated_delivery_date < order_purchase_timestamp
        ) as estimated_delivery_before_purchase,

        (
            (
                order_approved_at is not null
                and order_purchase_timestamp is not null
                and order_approved_at < order_purchase_timestamp
            )
            or
            (
                order_delivered_carrier_date is not null
                and order_approved_at is not null
                and order_delivered_carrier_date < order_approved_at
            )
            or
            (
                order_delivered_customer_date is not null
                and order_delivered_carrier_date is not null
                and order_delivered_customer_date < order_delivered_carrier_date
            )
            or
            (
                order_delivered_customer_date is not null
                and order_purchase_timestamp is not null
                and order_delivered_customer_date < order_purchase_timestamp
            )
            or
            (
                order_estimated_delivery_date is not null
                and order_purchase_timestamp is not null
                and order_estimated_delivery_date < order_purchase_timestamp
            )
        ) as has_temporal_sequence_anomaly,

        case
            when order_approved_at >= order_purchase_timestamp
            then datediff(
                'second',
                order_purchase_timestamp,
                order_approved_at
            ) / 3600.0
        end as purchase_to_approval_hours,

        case
            when order_delivered_carrier_date >= order_approved_at
            then datediff(
                'second',
                order_approved_at,
                order_delivered_carrier_date
            ) / 3600.0
        end as approval_to_carrier_hours,

        case
            when order_delivered_customer_date >= order_delivered_carrier_date
            then datediff(
                'second',
                order_delivered_carrier_date,
                order_delivered_customer_date
            ) / 3600.0
        end as carrier_to_customer_hours,

        case
            when order_delivered_customer_date >= order_purchase_timestamp
            then datediff(
                'second',
                order_purchase_timestamp,
                order_delivered_customer_date
            ) / 3600.0
        end as purchase_to_customer_hours

    from orders

)

select *
from final