select
    order_id,
    order_item_id,
    count(*) as record_count

from {{ ref('fct_order_items') }}

group by
    order_id,
    order_item_id

having count(*) <> 1