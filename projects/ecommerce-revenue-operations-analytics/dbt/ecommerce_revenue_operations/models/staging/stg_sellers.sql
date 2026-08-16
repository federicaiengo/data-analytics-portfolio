with source as (

    select *
    from {{ source('olist_raw', 'sellers') }}

),

renamed_and_typed as (

    select
        seller_id,
        seller_zip_code_prefix,
        seller_city,
        seller_state

    from source

)

select *
from renamed_and_typed