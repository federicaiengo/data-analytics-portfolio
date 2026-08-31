with order_lifecycle as (

    select
        order_id,
        customer_id,
        order_status,

        order_purchase_timestamp,
        order_approved_at,
        order_delivered_carrier_date,
        order_delivered_customer_date,
        order_estimated_delivery_date,

        is_approval_missing,
        is_carrier_timestamp_missing,
        is_customer_delivery_timestamp_missing,

        is_delivered_order_missing_approval,
        is_delivered_order_missing_carrier_timestamp,
        is_delivered_order_missing_customer_delivery_timestamp,

        approval_before_purchase,
        carrier_before_approval,
        customer_delivery_before_carrier,
        customer_delivery_before_purchase,
        estimated_delivery_before_purchase,
        has_temporal_sequence_anomaly,

        purchase_to_approval_hours,
        approval_to_carrier_hours,
        carrier_to_customer_hours,
        purchase_to_customer_hours

    from {{ ref('int_orders_lifecycle') }}

),

financial_reconciliation as (

    select
        order_id,
        order_item_count,
        distinct_product_count,
        distinct_seller_count,
        item_sales_value,
        freight_value,
        item_plus_freight_value,
        payment_record_count,
        distinct_payment_type_count,
        max_payment_installments,
        payment_value,
        missing_item_summary,
        missing_payment_summary,
        payment_minus_item_freight_value,
        financial_values_match
    from {{ ref('int_order_financial_reconciliation') }}

),

review_summary as (

    select
        order_id,
        review_record_count,
        distinct_review_id_count,
        average_review_score,
        minimum_review_score,
        maximum_review_score,
        distinct_review_score_count,
        has_multiple_review_scores,
        first_review_creation_date,
        last_review_creation_date,
        first_review_answer_timestamp,
        last_review_answer_timestamp,
        review_title_record_count,
        review_message_record_count,
        has_review_title,
        has_review_message
    from {{ ref('int_order_reviews_summary') }}

)

select
    l.*,

    f.order_item_count,
    f.distinct_product_count,
    f.distinct_seller_count,
    f.item_sales_value,
    f.freight_value,
    f.item_plus_freight_value,
    f.payment_record_count,
    f.distinct_payment_type_count,
    f.max_payment_installments,
    f.payment_value,
    f.missing_item_summary,
    f.missing_payment_summary,
    f.payment_minus_item_freight_value,
    f.financial_values_match,

    r.review_record_count,
    r.distinct_review_id_count,
    r.average_review_score,
    r.minimum_review_score,
    r.maximum_review_score,
    r.distinct_review_score_count,
    r.has_multiple_review_scores,
    r.first_review_creation_date,
    r.last_review_creation_date,
    r.first_review_answer_timestamp,
    r.last_review_answer_timestamp,
    r.review_title_record_count,
    r.review_message_record_count,
    r.has_review_title,
    r.has_review_message

from order_lifecycle as l

left join financial_reconciliation as f
    on l.order_id = f.order_id

left join review_summary as r
    on l.order_id = r.order_id