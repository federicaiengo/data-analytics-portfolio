-- ============================================================
-- 06_financial_reconciliation_analysis.sql
-- E-Commerce Revenue & Operations Analytics
-- Financial reconciliation diagnostics
-- ============================================================


-- ------------------------------------------------------------
-- 1. OVERALL ORDER-LEVEL FINANCIAL RECONCILIATION
-- ------------------------------------------------------------

select
    count(*) as order_count,
    count(distinct order_id) as distinct_order_count,
    count_if(missing_item_summary) as missing_item_orders,
    count_if(missing_payment_summary) as missing_payment_orders,
    count_if(
        not missing_item_summary
        and not missing_payment_summary
    ) as comparable_orders,
    count_if(financial_values_match = true) as matching_orders,
    count_if(financial_values_match = false) as mismatching_orders,
    round(
        100.0 * count_if(financial_values_match = false)
        / nullif(count_if(financial_values_match is not null), 0),
        4
    ) as mismatch_pct
from ECOMMERCE_ANALYTICS.ANALYTICS.INT_ORDER_FINANCIAL_RECONCILIATION;


/*
Observed:
- Orders: 99,441
- Distinct orders: 99,441
- Missing item summary: 775
- Missing payment summary: 1
- Comparable orders: 98,665
- Matching orders: 98,362
- Mismatching orders: 303
- Mismatch rate: approximately 0.3071%
*/


-- ------------------------------------------------------------
-- 2. MISMATCH MAGNITUDE
-- ------------------------------------------------------------

select
    round(min(abs(payment_minus_item_freight_value)), 2) as min_abs,
    round(median(abs(payment_minus_item_freight_value)), 2) as median_abs,
    round(avg(abs(payment_minus_item_freight_value)), 2) as avg_abs,
    round(max(abs(payment_minus_item_freight_value)), 2) as max_abs
from ECOMMERCE_ANALYTICS.ANALYTICS.INT_ORDER_FINANCIAL_RECONCILIATION
where financial_values_match = false;


/*
Observed:
- Minimum absolute mismatch: BRL 0.02
- Median absolute mismatch: BRL 5.90
- Average absolute mismatch: BRL 10.79
- Maximum absolute mismatch: BRL 182.81
*/


-- ------------------------------------------------------------
-- 3. MISMATCH BY ORDER STATUS AND DIRECTION
-- ------------------------------------------------------------

select
    order_status,

    case
        when payment_minus_item_freight_value > 0.01
            then 'PAYMENT_GT_ITEM_FREIGHT'
        when payment_minus_item_freight_value < -0.01
            then 'PAYMENT_LT_ITEM_FREIGHT'
        else 'WITHIN_TOLERANCE'
    end as mismatch_direction,

    count(*) as mismatch_orders,
    count_if(payment_record_count > 1) as multi_payment_orders,

    round(
        median(abs(payment_minus_item_freight_value)),
        2
    ) as median_abs,

    round(
        avg(abs(payment_minus_item_freight_value)),
        2
    ) as avg_abs

from ECOMMERCE_ANALYTICS.ANALYTICS.INT_ORDER_FINANCIAL_RECONCILIATION

where financial_values_match = false

group by
    order_status,
    mismatch_direction

order by
    mismatch_orders desc,
    order_status,
    mismatch_direction;


/*
Observed:
- Delivered / payment > item + freight: 260
- Delivered / payment < item + freight: 39
- Canceled / payment > item + freight: 2
- Shipped / payment > item + freight: 2

299 of 303 mismatches are delivered orders.
Multi-payment records do not explain the majority of mismatches.
*/


-- ------------------------------------------------------------
-- 4. PAYMENT-TYPE / INSTALLMENT MISMATCH RATE
-- Single-payment orders only
-- ------------------------------------------------------------

select
    p.payment_type,

    case
        when p.payment_installments <= 1 then '1'
        when p.payment_installments between 2 and 5 then '2-5'
        when p.payment_installments between 6 and 10 then '6-10'
        else '11+'
    end as installment_bucket,

    count(*) as comparable_orders,

    count_if(
        r.financial_values_match = false
    ) as mismatch_orders,

    round(
        100.0
        * count_if(r.financial_values_match = false)
        / count(*),
        4
    ) as mismatch_pct,

    count_if(
        r.payment_minus_item_freight_value > 0.01
    ) as pay_gt_orders,

    count_if(
        r.payment_minus_item_freight_value < -0.01
    ) as pay_lt_orders,

    round(
        avg(
            case
                when r.financial_values_match = false
                    then abs(r.payment_minus_item_freight_value)
            end
        ),
        2
    ) as avg_abs_mismatch

from ECOMMERCE_ANALYTICS.ANALYTICS.INT_ORDER_FINANCIAL_RECONCILIATION r

join ECOMMERCE_ANALYTICS.ANALYTICS.STG_ORDER_PAYMENTS p
    on r.order_id = p.order_id

where
    r.financial_values_match is not null
    and r.payment_record_count = 1

group by
    p.payment_type,
    installment_bucket

order by
    p.payment_type,
    case installment_bucket
        when '1' then 1
        when '2-5' then 2
        when '6-10' then 3
        else 4
    end;


/*
Key observed credit-card pattern:

1 installment
- 23,591 comparable orders
- 8 mismatches
- 0.034% mismatch rate

2-5 installments
- 34,216 comparable orders
- 120 mismatches
- 0.351% mismatch rate

6-10 installments
- 15,348 comparable orders
- 113 mismatches
- 0.736% mismatch rate

11+ installments
- 325 comparable orders
- 24 mismatches
- 7.385% mismatch rate

Other payment types:
- boleto: 14 mismatches / 19,614 orders
- debit_card: 7 mismatches / 1,519 orders
- voucher: 0 mismatches / 1,116 orders
*/


-- ------------------------------------------------------------
-- 5. CREDIT-CARD MISMATCH SEVERITY BY INSTALLMENTS
-- Single-payment orders only
-- ------------------------------------------------------------

select
    case
        when p.payment_installments <= 1 then '1'
        when p.payment_installments between 2 and 5 then '2-5'
        when p.payment_installments between 6 and 10 then '6-10'
        else '11+'
    end as installments,

    count(*) as orders,

    count_if(
        r.financial_values_match = false
    ) as mismatches,

    round(
        100.0
        * count_if(r.financial_values_match = false)
        / count(*),
        3
    ) as mismatch_pct,

    round(
        100.0
        * count_if(r.payment_minus_item_freight_value > 0.01)
        / nullif(
            count_if(r.financial_values_match = false),
            0
        ),
        1
    ) as pct_pay_gt,

    round(
        avg(
            case
                when r.financial_values_match = false
                    then abs(r.payment_minus_item_freight_value)
            end
        ),
        2
    ) as avg_abs_diff,

    round(
        median(
            case
                when r.financial_values_match = false
                    then abs(r.payment_minus_item_freight_value)
            end
        ),
        2
    ) as median_abs_diff

from ECOMMERCE_ANALYTICS.ANALYTICS.INT_ORDER_FINANCIAL_RECONCILIATION r

join ECOMMERCE_ANALYTICS.ANALYTICS.STG_ORDER_PAYMENTS p
    on r.order_id = p.order_id

where
    r.financial_values_match is not null
    and r.payment_record_count = 1
    and p.payment_type = 'credit_card'

group by
    installments

order by
    case installments
        when '1' then 1
        when '2-5' then 2
        when '6-10' then 3
        else 4
    end;


/*
Observed:

1 installment
- mismatch rate: 0.034%
- payment > item+freight among mismatches: 25.0%
- average absolute difference: BRL 3.13

2-5 installments
- mismatch rate: 0.351%
- payment > item+freight: 89.2%
- average absolute difference: BRL 4.48

6-10 installments
- mismatch rate: 0.736%
- payment > item+freight: 93.8%
- average absolute difference: BRL 16.50

11+ installments
- mismatch rate: 7.385%
- payment > item+freight: 100.0%
- average absolute difference: BRL 30.94
*/