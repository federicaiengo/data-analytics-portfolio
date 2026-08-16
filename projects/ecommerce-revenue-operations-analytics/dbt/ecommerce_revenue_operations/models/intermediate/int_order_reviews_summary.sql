with reviews as (

    select *
    from {{ ref('stg_order_reviews') }}

),

final as (

    select
        order_id,

        count(*) as review_record_count,
        count(distinct review_id) as distinct_review_id_count,

        avg(review_score) as average_review_score,
        min(review_score) as minimum_review_score,
        max(review_score) as maximum_review_score,
        count(distinct review_score) as distinct_review_score_count,

        count(distinct review_score) > 1
            as has_multiple_review_scores,

        min(review_creation_date) as first_review_creation_date,
        max(review_creation_date) as last_review_creation_date,

        min(review_answer_timestamp) as first_review_answer_timestamp,
        max(review_answer_timestamp) as last_review_answer_timestamp,

        count_if(review_comment_title is not null)
            as review_title_record_count,

        count_if(review_comment_message is not null)
            as review_message_record_count,

        count_if(review_comment_title is not null) > 0
            as has_review_title,

        count_if(review_comment_message is not null) > 0
            as has_review_message

    from reviews

    group by
        order_id

)

select *
from final