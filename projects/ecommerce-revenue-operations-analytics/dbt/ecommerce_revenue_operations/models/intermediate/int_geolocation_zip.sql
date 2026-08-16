with geolocation as (

    select *
    from {{ ref('int_geolocation_deduplicated') }}

),

coordinate_summary as (

    select
        geolocation_zip_code_prefix,
        median(geolocation_lat) as geolocation_lat,
        median(geolocation_lng) as geolocation_lng,
        count(*) as geolocation_observation_count

    from geolocation

    group by
        geolocation_zip_code_prefix

),

location_counts as (

    select
        geolocation_zip_code_prefix,
        geolocation_city,
        geolocation_state,
        count(*) as location_observation_count

    from geolocation

    group by
        geolocation_zip_code_prefix,
        geolocation_city,
        geolocation_state

),

ranked_locations as (

    select
        geolocation_zip_code_prefix,
        geolocation_city,
        geolocation_state,
        location_observation_count,

        row_number() over (
            partition by geolocation_zip_code_prefix
            order by
                location_observation_count desc,
                geolocation_state asc,
                geolocation_city asc
        ) as location_rank

    from location_counts

),

representative_location as (

    select
        geolocation_zip_code_prefix,
        geolocation_city,
        geolocation_state

    from ranked_locations

    where location_rank = 1

),

final as (

    select
        coordinates.geolocation_zip_code_prefix,
        coordinates.geolocation_lat,
        coordinates.geolocation_lng,
        locations.geolocation_city,
        locations.geolocation_state,
        coordinates.geolocation_observation_count

    from coordinate_summary as coordinates

    left join representative_location as locations
        on coordinates.geolocation_zip_code_prefix =
           locations.geolocation_zip_code_prefix

)

select *
from final