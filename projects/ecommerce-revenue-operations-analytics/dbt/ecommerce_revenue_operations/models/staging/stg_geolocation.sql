with source as (

    select *
    from {{ source('olist_raw', 'geolocation') }}

),

renamed_and_typed as (

    select
        geolocation_zip_code_prefix,
        try_to_double(geolocation_lat) as geolocation_lat,
        try_to_double(geolocation_lng) as geolocation_lng,
        geolocation_city,
        geolocation_state

    from source

)

select *
from renamed_and_typed