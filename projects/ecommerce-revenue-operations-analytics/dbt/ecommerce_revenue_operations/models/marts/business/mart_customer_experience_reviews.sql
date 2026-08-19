with orders as (

    select
        order_id,
        order_purchase_timestamp,

        review_record_count,
        average_review_score,
        has_multiple_review_scores,
        has_review_title,
        has_review_message

    from {{ ref('fct_orders') }}

),

monthly_customer_experience as (

    select
        date_trunc('month', order_purchase_timestamp)::date as month_start_date,

        count(*) as order_count,

        count_if(review_record_count is not null)
            as reviewed_order_count,

        count_if(review_record_count is null)
            as unreviewed_order_count,

        count_if(average_review_score is not null)
            as scored_order_count,

        sum(coalesce(review_record_count, 0))
            as review_record_count,

        avg(average_review_score)
            as average_review_score,

        count_if(
            average_review_score <= 2
        ) as low_score_order_count,

        count_if(
            average_review_score > 2
            and average_review_score < 4
        ) as mid_score_order_count,

        count_if(
            average_review_score >= 4
        ) as high_score_order_count,

        count_if(
            average_review_score = 5
        ) as five_score_order_count,

        count_if(
            review_record_count > 1
        ) as multiple_review_record_order_count,

        count_if(
            has_multiple_review_scores = true
        ) as multiple_review_score_order_count,

        count_if(
            has_review_title = true
        ) as review_title_order_count,

        count_if(
            has_review_message = true
        ) as review_message_order_count

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

    reviewed_order_count,
    unreviewed_order_count,

    case
        when order_count > 0
            then reviewed_order_count * 100.0 / order_count
    end as review_coverage_rate_pct,

    scored_order_count,
    review_record_count,

    average_review_score,

    low_score_order_count,
    mid_score_order_count,
    high_score_order_count,
    five_score_order_count,

    case
        when scored_order_count > 0
            then low_score_order_count * 100.0 / scored_order_count
    end as low_score_rate_pct,

    case
        when scored_order_count > 0
            then high_score_order_count * 100.0 / scored_order_count
    end as high_score_rate_pct,

    case
        when scored_order_count > 0
            then five_score_order_count * 100.0 / scored_order_count
    end as five_score_rate_pct,

    multiple_review_record_order_count,
    multiple_review_score_order_count,

    review_title_order_count,
    review_message_order_count,

    case
        when reviewed_order_count > 0
            then review_title_order_count * 100.0 / reviewed_order_count
    end as review_title_rate_pct,

    case
        when reviewed_order_count > 0
            then review_message_order_count * 100.0 / reviewed_order_count
    end as review_message_rate_pct

from monthly_customer_experience