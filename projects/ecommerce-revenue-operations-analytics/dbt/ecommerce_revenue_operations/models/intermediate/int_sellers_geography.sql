with sellers as (

    select *
    from {{ ref('stg_sellers') }}

),

geolocation as (

    select *
    from {{ ref('int_geolocation_zip') }}

)

select
    s.seller_id,
    s.seller_zip_code_prefix,
    s.seller_city,
    s.seller_state,

    g.geolocation_lat,
    g.geolocation_lng,
    g.geolocation_city,
    g.geolocation_state,
    g.geolocation_observation_count,

    g.geolocation_zip_code_prefix is null
        as is_geolocation_match_missing,

    case
        when g.geolocation_zip_code_prefix is null then false
        when lower(trim(s.seller_city)) <> lower(trim(g.geolocation_city)) then true
        else false
    end as is_seller_city_mismatch,

    case
        when g.geolocation_zip_code_prefix is null then false
        when upper(trim(s.seller_state)) <> upper(trim(g.geolocation_state)) then true
        else false
    end as is_seller_state_mismatch

from sellers as s

left join geolocation as g
    on s.seller_zip_code_prefix = g.geolocation_zip_code_prefix