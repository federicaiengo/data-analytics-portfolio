with source_stats as (

    select
        count(*) as source_row_count
    from {{ ref('stg_sellers') }}

),

model_stats as (

    select
        count(*) as model_row_count,
        count(distinct seller_id) as distinct_seller_count,
        count_if(seller_id is null) as null_seller_id_count,
        count_if(is_geolocation_match_missing) as missing_geolocation_count,
        count_if(
            geolocation_lat is null
            or geolocation_lng is null
        ) as null_coordinate_count,
        count_if(
            is_geolocation_match_missing
            and (
                is_seller_city_mismatch
                or is_seller_state_mismatch
            )
        ) as unmatched_rows_with_mismatch_flag
    from {{ ref('int_sellers_geography') }}

)

select
    source_row_count,
    model_row_count,
    distinct_seller_count,
    null_seller_id_count,
    missing_geolocation_count,
    null_coordinate_count,
    unmatched_rows_with_mismatch_flag

from source_stats
cross join model_stats

where
       model_row_count <> source_row_count
    or distinct_seller_count <> model_row_count
    or null_seller_id_count <> 0
    or missing_geolocation_count <> null_coordinate_count
    or unmatched_rows_with_mismatch_flag <> 0