with orders as (

    select
        order_id,
        order_purchase_timestamp,
        order_status,

        item_sales_value,
        freight_value,
        item_plus_freight_value,
        payment_value,

        missing_item_summary,
        missing_payment_summary,
        financial_values_match,
        payment_minus_item_freight_value

    from {{ ref('fct_orders') }}

),

monthly_reconciliation as (

    select
        date_trunc('month', order_purchase_timestamp)::date as month_start_date,

        count(*) as order_count,

        count_if(order_status = 'delivered') as delivered_order_count,

        sum(item_sales_value) as item_sales_value,
        sum(freight_value) as freight_value,
        sum(item_plus_freight_value) as item_plus_freight_value,
        sum(payment_value) as payment_value,

        count_if(missing_item_summary) as missing_item_summary_order_count,
        count_if(missing_payment_summary) as missing_payment_summary_order_count,

        count_if(financial_values_match is not null) as comparable_order_count,
        count_if(financial_values_match = true) as matching_order_count,
        count_if(financial_values_match = false) as mismatching_order_count,

        sum(
            case
                when financial_values_match = false
                    then abs(payment_minus_item_freight_value)
                else 0
            end
        ) as absolute_mismatch_value,

        avg(
            case
                when financial_values_match = false
                    then abs(payment_minus_item_freight_value)
            end
        ) as average_absolute_mismatch_value,

        max(
            case
                when financial_values_match = false
                    then abs(payment_minus_item_freight_value)
            end
        ) as maximum_absolute_mismatch_value

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

    item_sales_value,
    freight_value,
    item_plus_freight_value,
    payment_value,

    missing_item_summary_order_count,
    missing_payment_summary_order_count,

    comparable_order_count,
    matching_order_count,
    mismatching_order_count,

    case
        when comparable_order_count > 0
            then mismatching_order_count * 100.0 / comparable_order_count
    end as mismatch_rate_pct,

    absolute_mismatch_value,
    average_absolute_mismatch_value,
    maximum_absolute_mismatch_value

from monthly_reconciliation
