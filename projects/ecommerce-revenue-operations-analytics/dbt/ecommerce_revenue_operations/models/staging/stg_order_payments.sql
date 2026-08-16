with source as (

    select *
    from {{ source('olist_raw', 'order_payments') }}

),

renamed_and_typed as (

    select
        order_id,
        try_to_number(payment_sequential, 38, 0) as payment_sequential,
        payment_type,
        try_to_number(payment_installments, 38, 0) as payment_installments,
        try_to_decimal(payment_value, 12, 2) as payment_value

    from source

)

select *
from renamed_and_typed