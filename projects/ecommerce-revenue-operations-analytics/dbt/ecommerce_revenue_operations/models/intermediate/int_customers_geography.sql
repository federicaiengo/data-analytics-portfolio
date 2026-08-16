with customers as (

    select *
    from {{ ref('stg_customers') }}

),

geolocation as (

    select *
    from {{ ref('int_geolocation_zip') }}

),

final as (

    select
        customers.customer_id,
        customers.customer_unique_id,
        customers.customer_zip_code_prefix,
        customers.customer_city,
        customers.customer_state,

        geolocation.geolocation_lat,
        geolocation.geolocation_lng,
        geolocation.geolocation_city,
        geolocation.geolocation_state,
        geolocation.geolocation_observation_count,

        geolocation.geolocation_zip_code_prefix is null
            as is_geolocation_match_missing,

        (
            geolocation.geolocation_zip_code_prefix is not null
            and lower(customers.customer_city) <> lower(geolocation.geolocation_city)
        ) as is_customer_city_mismatch,

        (
            geolocation.geolocation_zip_code_prefix is not null
            and customers.customer_state <> geolocation.geolocation_state
        ) as is_customer_state_mismatch

    from customers

    left join geolocation
        on customers.customer_zip_code_prefix =
           geolocation.geolocation_zip_code_prefix

)

select *
from final