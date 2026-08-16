with products as (

    select *
    from {{ ref('stg_products') }}

),

category_translation as (

    select *
    from {{ ref('stg_product_category_name_translation') }}

),

final as (

    select
        products.product_id,

        products.product_category_name,
        category_translation.product_category_name_english,

        case
            when products.product_category_name is null
                then 'Unknown'

            when category_translation.product_category_name_english is null
                then 'Untranslated: ' || products.product_category_name

            else category_translation.product_category_name_english
        end as product_category_name_reporting,

        products.product_name_length,
        products.product_description_length,
        products.product_photos_qty,

        products.product_weight_g,
        products.product_length_cm,
        products.product_height_cm,
        products.product_width_cm,

        products.product_category_name is null
            as is_product_category_missing,

        (
            products.product_category_name is not null
            and category_translation.product_category_name_english is null
        ) as is_category_translation_missing,

        (
            products.product_category_name is null
            and products.product_name_length is null
            and products.product_description_length is null
            and products.product_photos_qty is null
        ) as is_core_descriptive_metadata_missing

    from products

    left join category_translation
        on products.product_category_name
         = category_translation.product_category_name

)

select *
from final