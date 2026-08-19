with date_sequence as (

    select
        date_day,
        lag(date_day) over (order by date_day) as previous_date_day

    from {{ ref('dim_date') }}

)

select
    date_day,
    previous_date_day,
    datediff(day, previous_date_day, date_day) as day_gap

from date_sequence

where previous_date_day is not null
  and datediff(day, previous_date_day, date_day) <> 1