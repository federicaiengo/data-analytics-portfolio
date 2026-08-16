with source_customers as (

    select
        count(*) as row_count,
        count(distinct customer_id) as distinct_customer_count
    from {{ ref('stg_customers') }}

),

geography_customers as (

    select
        count(*) as row_count,
        count(distinct customer_id) as distinct_customer_count
    from {{ ref('int_customers_geography') }}

),

invalid_match_state as (

    select
        count(*) as invalid_row_count
    from {{ ref('int_customers_geography') }}

    where
        (
            is_geolocation_match_missing
            and (
                geolocation_lat is not null
                or geolocation_lng is not null
                or geolocation_city is not null
                or geolocation_state is not null
                or geolocation_observation_count is not null
            )
        )

        or

        (
            not is_geolocation_match_missing
            and (
                geolocation_lat is null
                or geolocation_lng is null
                or geolocation_city is null
                or geolocation_state is null
                or geolocation_observation_count is null
            )
        )

        or

        (
            is_geolocation_match_missing
            and (
                is_customer_city_mismatch
                or is_customer_state_mismatch
            )
        )

)

select
    source_customers.row_count as source_row_count,
    geography_customers.row_count as geography_row_count,
    source_customers.distinct_customer_count as source_distinct_customer_count,
    geography_customers.distinct_customer_count as geography_distinct_customer_count,
    invalid_match_state.invalid_row_count

from source_customers
cross join geography_customers
cross join invalid_match_state

where
       source_customers.row_count <> geography_customers.row_count
    or source_customers.distinct_customer_count <> geography_customers.distinct_customer_count
    or invalid_match_state.invalid_row_count <> 0