with source as (

    select *
    from {{ source('olist_raw', 'order_reviews') }}

),

renamed_and_typed as (

    select
        review_id,
        order_id,
        try_to_number(review_score, 38, 0) as review_score,
        review_comment_title,
        review_comment_message,
        try_to_timestamp_ntz(review_creation_date) as review_creation_date,
        try_to_timestamp_ntz(review_answer_timestamp) as review_answer_timestamp

    from source

)

select *
from renamed_and_typed