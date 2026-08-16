with source as (

    select
        count(*) as source_payment_row_count,
        count(distinct order_id) as source_order_count,
        sum(payment_value) as source_payment_value

    from {{ ref('stg_order_payments') }}

),

summary as (

    select
        count(*) as summary_order_count,
        sum(payment_record_count) as summary_payment_row_count,
        sum(payment_value) as summary_payment_value

    from {{ ref('int_order_payments_summary') }}

)

select
    source_payment_row_count,
    summary_payment_row_count,
    source_order_count,
    summary_order_count,
    source_payment_value,
    summary_payment_value

from source
cross join summary

where
       source_payment_row_count <> summary_payment_row_count
    or source_order_count <> summary_order_count
    or source_payment_value <> summary_payment_value