select *
from {{ ref('int_order_financial_reconciliation') }}

where

    (
        not missing_item_summary
        and not missing_payment_summary
        and (
            payment_minus_item_freight_value is null
            or financial_values_match is null
        )
    )

    or

    (
        (
            missing_item_summary
            or missing_payment_summary
        )
        and (
            payment_minus_item_freight_value is not null
            or financial_values_match is not null
        )
    )