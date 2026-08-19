with source_totals as (

    select
        count(*) as order_count,

        count_if(review_record_count is not null)
            as reviewed_order_count,

        count_if(review_record_count is null)
            as unreviewed_order_count,

        count_if(average_review_score is not null)
            as scored_order_count,

        sum(coalesce(review_record_count, 0))
            as review_record_count,

        round(avg(average_review_score), 4)
            as average_review_score,

        count_if(average_review_score <= 2)
            as low_score_order_count,

        count_if(
            average_review_score > 2
            and average_review_score < 4
        ) as mid_score_order_count,

        count_if(average_review_score >= 4)
            as high_score_order_count,

        count_if(average_review_score = 5)
            as five_score_order_count,

        count_if(review_record_count > 1)
            as multiple_review_record_order_count,

        count_if(has_multiple_review_scores = true)
            as multiple_review_score_order_count,

        count_if(has_review_title = true)
            as review_title_order_count,

        count_if(has_review_message = true)
            as review_message_order_count

    from {{ ref('fct_orders') }}

),

mart_totals as (

    select
        sum(order_count)
            as order_count,

        sum(reviewed_order_count)
            as reviewed_order_count,

        sum(unreviewed_order_count)
            as unreviewed_order_count,

        sum(scored_order_count)
            as scored_order_count,

        sum(review_record_count)
            as review_record_count,

        round(
            sum(average_review_score * scored_order_count)
            / nullif(sum(scored_order_count), 0),
            4
        ) as average_review_score,

        sum(low_score_order_count)
            as low_score_order_count,

        sum(mid_score_order_count)
            as mid_score_order_count,

        sum(high_score_order_count)
            as high_score_order_count,

        sum(five_score_order_count)
            as five_score_order_count,

        sum(multiple_review_record_order_count)
            as multiple_review_record_order_count,

        sum(multiple_review_score_order_count)
            as multiple_review_score_order_count,

        sum(review_title_order_count)
            as review_title_order_count,

        sum(review_message_order_count)
            as review_message_order_count

    from {{ ref('mart_customer_experience_reviews') }}

),

monthly_integrity_violations as (

    select
        month_start_date

    from {{ ref('mart_customer_experience_reviews') }}

    where
           reviewed_order_count + unreviewed_order_count
               <> order_count

        or low_score_order_count
           + mid_score_order_count
           + high_score_order_count
               <> scored_order_count

        or five_score_order_count
               > high_score_order_count

        or multiple_review_score_order_count
               > multiple_review_record_order_count

        or review_title_order_count
               > reviewed_order_count

        or review_message_order_count
               > reviewed_order_count

)

select
    s.order_count as source_order_count,
    m.order_count as mart_order_count

from source_totals as s
cross join mart_totals as m

where
       s.order_count <> m.order_count
    or s.reviewed_order_count <> m.reviewed_order_count
    or s.unreviewed_order_count <> m.unreviewed_order_count
    or s.scored_order_count <> m.scored_order_count
    or s.review_record_count <> m.review_record_count
    or s.average_review_score <> m.average_review_score
    or s.low_score_order_count <> m.low_score_order_count
    or s.mid_score_order_count <> m.mid_score_order_count
    or s.high_score_order_count <> m.high_score_order_count
    or s.five_score_order_count <> m.five_score_order_count
    or s.multiple_review_record_order_count <> m.multiple_review_record_order_count
    or s.multiple_review_score_order_count <> m.multiple_review_score_order_count
    or s.review_title_order_count <> m.review_title_order_count
    or s.review_message_order_count <> m.review_message_order_count

union all

select
    null as source_order_count,
    null as mart_order_count

from monthly_integrity_violations