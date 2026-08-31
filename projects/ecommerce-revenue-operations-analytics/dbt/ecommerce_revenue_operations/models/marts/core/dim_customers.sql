with customers as (

    select *
    from {{ ref('int_customers_geography') }}

)

select
    customer_id,
    customer_unique_id,
    customer_zip_code_prefix,
    customer_city,
    customer_state,

    geolocation_lat,
    geolocation_lng,
    geolocation_city,
    geolocation_state,
    geolocation_observation_count,

    is_geolocation_match_missing,
    is_customer_city_mismatch,
    is_customer_state_mismatch

from customers