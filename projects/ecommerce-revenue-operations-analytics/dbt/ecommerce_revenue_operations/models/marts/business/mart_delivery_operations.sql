with orders as (

    select
        order_id,
        order_status,
        order_purchase_timestamp,
        order_approved_at,
        order_delivered_carrier_date,
        order_delivered_customer_date,
        order_estimated_delivery_date,

        purchase_to_approval_hours,
        approval_to_carrier_hours,
        carrier_to_customer_hours,
        purchase_to_customer_hours,

        has_temporal_sequence_anomaly,
        carrier_before_approval,
        customer_delivery_before_carrier

    from {{ ref('fct_orders') }}

),

monthly_operations as (

    select
        date_trunc('month', order_purchase_timestamp)::date as month_start_date,

        count(*) as order_count,

        count_if(order_status = 'delivered') as delivered_order_count,

        count_if(
            order_status = 'delivered'
            and order_delivered_customer_date is not null
            and order_estimated_delivery_date is not null
        ) as punctuality_comparable_order_count,

        count_if(
            order_status = 'delivered'
            and order_delivered_customer_date is not null
            and order_estimated_delivery_date is not null
            and order_delivered_customer_date <= order_estimated_delivery_date
        ) as on_time_or_early_order_count,

        count_if(
            order_status = 'delivered'
            and order_delivered_customer_date is not null
            and order_estimated_delivery_date is not null
            and order_delivered_customer_date > order_estimated_delivery_date
        ) as late_delivery_order_count,

        count_if(
            order_status = 'delivered'
            and (
                order_delivered_customer_date is null
                or order_estimated_delivery_date is null
            )
        ) as punctuality_not_comparable_order_count,

        count_if(
            order_status = 'delivered'
            and order_approved_at is null
        ) as delivered_missing_approval_count,

        count_if(
            order_status = 'delivered'
            and order_delivered_carrier_date is null
        ) as delivered_missing_carrier_timestamp_count,

        count_if(
            order_status = 'delivered'
            and order_delivered_customer_date is null
        ) as delivered_missing_customer_delivery_count,

        count_if(has_temporal_sequence_anomaly) as temporal_anomaly_order_count,

        count_if(carrier_before_approval) as carrier_before_approval_order_count,

        count_if(customer_delivery_before_carrier) as customer_delivery_before_carrier_order_count,

        count_if(purchase_to_approval_hours is not null)
            as valid_purchase_to_approval_order_count,

        count_if(approval_to_carrier_hours is not null)
            as valid_approval_to_carrier_order_count,

        count_if(carrier_to_customer_hours is not null)
            as valid_carrier_to_customer_order_count,

        count_if(purchase_to_customer_hours is not null)
            as valid_purchase_to_customer_order_count,

        avg(purchase_to_approval_hours)
            as average_purchase_to_approval_hours,

        avg(approval_to_carrier_hours)
            as average_approval_to_carrier_hours,

        avg(carrier_to_customer_hours)
            as average_carrier_to_customer_hours,

        avg(purchase_to_customer_hours)
            as average_purchase_to_customer_hours

    from orders

    group by
        date_trunc('month', order_purchase_timestamp)::date

)

select
    month_start_date,

    year(month_start_date) as year_number,
    month(month_start_date) as month_number,
    to_char(month_start_date, 'YYYY-MM') as year_month,

    order_count,
    delivered_order_count,

    punctuality_comparable_order_count,
    on_time_or_early_order_count,
    late_delivery_order_count,
    punctuality_not_comparable_order_count,

    case
        when punctuality_comparable_order_count > 0
            then late_delivery_order_count * 100.0
                / punctuality_comparable_order_count
    end as late_delivery_rate_pct,

    case
        when punctuality_comparable_order_count > 0
            then on_time_or_early_order_count * 100.0
                / punctuality_comparable_order_count
    end as on_time_or_early_rate_pct,

    delivered_missing_approval_count,
    delivered_missing_carrier_timestamp_count,
    delivered_missing_customer_delivery_count,

    temporal_anomaly_order_count,
    carrier_before_approval_order_count,
    customer_delivery_before_carrier_order_count,

    valid_purchase_to_approval_order_count,
    valid_approval_to_carrier_order_count,
    valid_carrier_to_customer_order_count,
    valid_purchase_to_customer_order_count,

    average_purchase_to_approval_hours,
    average_approval_to_carrier_hours,
    average_carrier_to_customer_hours,
    average_purchase_to_customer_hours

from monthly_operations