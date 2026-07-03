with patient_admissions as (
    select
        admission_id,
        patient_id,
        department_name,
        admission_type,
        admission_date,
        discharge_date,
        lag(discharge_date) over (partition by patient_id order by admission_date) as prev_discharge_date
    from {{ ref('fct_admissions') }}
),

readmission_flags as (
    select
        *,
        case
            when prev_discharge_date is not null
             and cast(admission_date as date) >= cast(prev_discharge_date as date)
             and (cast(admission_date as date) - cast(prev_discharge_date as date)) <= 30
            then 1
            else 0
        end as is_30_day_readmission
    from patient_admissions
),

aggregated as (
    select
        department_name,
        admission_type,
        count(*) as total_admissions,
        sum(is_30_day_readmission) as readmission_count,
        round(cast(sum(is_30_day_readmission) * 100.0 / nullif(count(*), 0) as numeric), 2) as readmission_rate_pct
    from readmission_flags
    group by department_name, admission_type
)

select * from aggregated
order by readmission_rate_pct desc
