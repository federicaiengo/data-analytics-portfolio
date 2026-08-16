with deduplicated as (

    select count(*) as expected_observation_count
    from {{ ref('int_geolocation_deduplicated') }}

),

zip_model as (

    select sum(geolocation_observation_count) as actual_observation_count
    from {{ ref('int_geolocation_zip') }}

)

select
    expected_observation_count,
    actual_observation_count

from deduplicated
cross join zip_model

where expected_observation_count <> actual_observation_count
