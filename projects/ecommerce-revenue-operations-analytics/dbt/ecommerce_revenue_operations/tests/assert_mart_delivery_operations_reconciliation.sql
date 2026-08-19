with source_totals as (

    select
        count(*) as order_count,

        count_if(order_status = 'delivered')
            as delivered_order_count,

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

        count_if(has_temporal_sequence_anomaly)
            as temporal_anomaly_order_count,

        count_if(carrier_before_approval)
            as carrier_before_approval_order_count,

        count_if(customer_delivery_before_carrier)
            as customer_delivery_before_carrier_order_count,

        count_if(purchase_to_approval_hours is not null)
            as valid_purchase_to_approval_order_count,

        count_if(approval_to_carrier_hours is not null)
            as valid_approval_to_carrier_order_count,

        count_if(carrier_to_customer_hours is not null)
            as valid_carrier_to_customer_order_count,

        count_if(purchase_to_customer_hours is not null)
            as valid_purchase_to_customer_order_count,

        round(avg(purchase_to_approval_hours), 2)
            as average_purchase_to_approval_hours,

        round(avg(approval_to_carrier_hours), 2)
            as average_approval_to_carrier_hours,

        round(avg(carrier_to_customer_hours), 2)
            as average_carrier_to_customer_hours,

        round(avg(purchase_to_customer_hours), 2)
            as average_purchase_to_customer_hours

    from {{ ref('fct_orders') }}

),

mart_totals as (

    select
        sum(order_count) as order_count,

        sum(delivered_order_count)
            as delivered_order_count,

        sum(punctuality_comparable_order_count)
            as punctuality_comparable_order_count,

        sum(on_time_or_early_order_count)
            as on_time_or_early_order_count,

        sum(late_delivery_order_count)
            as late_delivery_order_count,

        sum(punctuality_not_comparable_order_count)
            as punctuality_not_comparable_order_count,

        sum(delivered_missing_approval_count)
            as delivered_missing_approval_count,

        sum(delivered_missing_carrier_timestamp_count)
            as delivered_missing_carrier_timestamp_count,

        sum(delivered_missing_customer_delivery_count)
            as delivered_missing_customer_delivery_count,

        sum(temporal_anomaly_order_count)
            as temporal_anomaly_order_count,

        sum(carrier_before_approval_order_count)
            as carrier_before_approval_order_count,

        sum(customer_delivery_before_carrier_order_count)
            as customer_delivery_before_carrier_order_count,

        sum(valid_purchase_to_approval_order_count)
            as valid_purchase_to_approval_order_count,

        sum(valid_approval_to_carrier_order_count)
            as valid_approval_to_carrier_order_count,

        sum(valid_carrier_to_customer_order_count)
            as valid_carrier_to_customer_order_count,

        sum(valid_purchase_to_customer_order_count)
            as valid_purchase_to_customer_order_count,

        round(
            sum(
                average_purchase_to_approval_hours
                * valid_purchase_to_approval_order_count
            )
            / nullif(sum(valid_purchase_to_approval_order_count), 0),
            2
        ) as average_purchase_to_approval_hours,

        round(
            sum(
                average_approval_to_carrier_hours
                * valid_approval_to_carrier_order_count
            )
            / nullif(sum(valid_approval_to_carrier_order_count), 0),
            2
        ) as average_approval_to_carrier_hours,

        round(
            sum(
                average_carrier_to_customer_hours
                * valid_carrier_to_customer_order_count
            )
            / nullif(sum(valid_carrier_to_customer_order_count), 0),
            2
        ) as average_carrier_to_customer_hours,

        round(
            sum(
                average_purchase_to_customer_hours
                * valid_purchase_to_customer_order_count
            )
            / nullif(sum(valid_purchase_to_customer_order_count), 0),
            2
        ) as average_purchase_to_customer_hours

    from {{ ref('mart_delivery_operations') }}

),

monthly_integrity_violations as (

    select
        month_start_date

    from {{ ref('mart_delivery_operations') }}

    where
           on_time_or_early_order_count + late_delivery_order_count
               <> punctuality_comparable_order_count

        or punctuality_comparable_order_count
           + punctuality_not_comparable_order_count
               <> delivered_order_count

)

select
    s.order_count as source_order_count,
    m.order_count as mart_order_count

from source_totals as s
cross join mart_totals as m

where
       s.order_count <> m.order_count
    or s.delivered_order_count <> m.delivered_order_count
    or s.punctuality_comparable_order_count <> m.punctuality_comparable_order_count
    or s.on_time_or_early_order_count <> m.on_time_or_early_order_count
    or s.late_delivery_order_count <> m.late_delivery_order_count
    or s.punctuality_not_comparable_order_count <> m.punctuality_not_comparable_order_count
    or s.delivered_missing_approval_count <> m.delivered_missing_approval_count
    or s.delivered_missing_carrier_timestamp_count <> m.delivered_missing_carrier_timestamp_count
    or s.delivered_missing_customer_delivery_count <> m.delivered_missing_customer_delivery_count
    or s.temporal_anomaly_order_count <> m.temporal_anomaly_order_count
    or s.carrier_before_approval_order_count <> m.carrier_before_approval_order_count
    or s.customer_delivery_before_carrier_order_count <> m.customer_delivery_before_carrier_order_count
    or s.valid_purchase_to_approval_order_count <> m.valid_purchase_to_approval_order_count
    or s.valid_approval_to_carrier_order_count <> m.valid_approval_to_carrier_order_count
    or s.valid_carrier_to_customer_order_count <> m.valid_carrier_to_customer_order_count
    or s.valid_purchase_to_customer_order_count <> m.valid_purchase_to_customer_order_count
    or s.average_purchase_to_approval_hours <> m.average_purchase_to_approval_hours
    or s.average_approval_to_carrier_hours <> m.average_approval_to_carrier_hours
    or s.average_carrier_to_customer_hours <> m.average_carrier_to_customer_hours
    or s.average_purchase_to_customer_hours <> m.average_purchase_to_customer_hours

union all

select
    null as source_order_count,
    null as mart_order_count

from monthly_integrity_violations