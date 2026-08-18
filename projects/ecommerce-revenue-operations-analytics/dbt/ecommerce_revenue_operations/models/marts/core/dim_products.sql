with products as (

    select *
    from {{ ref('int_products_enriched') }}

)

select *
from products
