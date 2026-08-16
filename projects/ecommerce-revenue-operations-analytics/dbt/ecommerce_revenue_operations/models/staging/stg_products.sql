with source as (

    select *
    from {{ source('olist_raw', 'products') }}

),

renamed_and_typed as (

    select
        product_id,
        product_category_name,

        try_to_number(product_name_lenght, 38, 0) as product_name_length,
        try_to_number(product_description_lenght, 38, 0) as product_description_length,
        try_to_number(product_photos_qty, 38, 0) as product_photos_qty,
        try_to_number(product_weight_g, 38, 0) as product_weight_g,
        try_to_number(product_length_cm, 38, 0) as product_length_cm,
        try_to_number(product_height_cm, 38, 0) as product_height_cm,
        try_to_number(product_width_cm, 38, 0) as product_width_cm

    from source

)

select *
from renamed_and_typed