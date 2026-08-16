with source_products as (

    select
        count(*) as row_count,
        count(distinct product_id) as distinct_product_count,
        count_if(product_category_name is null) as missing_category_count,
        count_if(
            product_category_name is null
            and product_name_length is null
            and product_description_length is null
            and product_photos_qty is null
        ) as missing_core_metadata_count
    from {{ ref('stg_products') }}

),

enriched_products as (

    select
        count(*) as row_count,
        count(distinct product_id) as distinct_product_count,
        count_if(is_product_category_missing) as missing_category_count,
        count_if(is_core_descriptive_metadata_missing) as missing_core_metadata_count
    from {{ ref('int_products_enriched') }}

)

select
    source_products.row_count as source_row_count,
    enriched_products.row_count as enriched_row_count,

    source_products.distinct_product_count as source_distinct_product_count,
    enriched_products.distinct_product_count as enriched_distinct_product_count,

    source_products.missing_category_count as source_missing_category_count,
    enriched_products.missing_category_count as enriched_missing_category_count,

    source_products.missing_core_metadata_count as source_missing_core_metadata_count,
    enriched_products.missing_core_metadata_count as enriched_missing_core_metadata_count

from source_products
cross join enriched_products

where
       source_products.row_count <> enriched_products.row_count
    or source_products.distinct_product_count <> enriched_products.distinct_product_count
    or source_products.missing_category_count <> enriched_products.missing_category_count
    or source_products.missing_core_metadata_count <> enriched_products.missing_core_metadata_count