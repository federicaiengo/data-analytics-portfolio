with recursive all_dates as (

    select order_purchase_timestamp::date as date_value
    from {{ ref('fct_orders') }}

    union all

    select order_approved_at::date
    from {{ ref('fct_orders') }}

    union all

    select order_delivered_carrier_date::date
    from {{ ref('fct_orders') }}

    union all

    select order_delivered_customer_date::date
    from {{ ref('fct_orders') }}

    union all

    select order_estimated_delivery_date::date
    from {{ ref('fct_orders') }}

    union all

    select first_review_creation_date::date
    from {{ ref('fct_orders') }}

    union all

    select last_review_creation_date::date
    from {{ ref('fct_orders') }}

    union all

    select first_review_answer_timestamp::date
    from {{ ref('fct_orders') }}

    union all

    select last_review_answer_timestamp::date
    from {{ ref('fct_orders') }}

    union all

    select shipping_limit_date::date
    from {{ ref('fct_order_items') }}

),

date_bounds as (

    select
        date_trunc('month', min(date_value))::date as min_date,
        last_day(max(date_value), 'month')::date as max_date
    from all_dates
    where date_value is not null

),

date_spine (date_day, max_date) as (

    select
        min_date,
        max_date
    from date_bounds

    union all

    select
        dateadd(day, 1, date_day),
        max_date
    from date_spine
    where date_day < max_date

)

select
    date_day,

    to_number(to_char(date_day, 'YYYYMMDD')) as date_key,

    year(date_day) as year_number,

    quarter(date_day) as quarter_number,

    'Q' || quarter(date_day) as quarter_name,

    date_trunc('quarter', date_day)::date as quarter_start_date,

    month(date_day) as month_number,

    monthname(date_day) as month_name,

    to_char(date_day, 'YYYY-MM') as year_month,

    date_trunc('month', date_day)::date as month_start_date,

    weekiso(date_day) as iso_week_number,

    yearofweekiso(date_day) as iso_week_year,

    date_trunc('week', date_day)::date as week_start_date,

    day(date_day) as day_of_month,

    dayofyear(date_day) as day_of_year,

    dayofweekiso(date_day) as iso_day_of_week,

    dayname(date_day) as day_name,

    case
        when dayofweekiso(date_day) in (6, 7) then true
        else false
    end as is_weekend

from date_spine
