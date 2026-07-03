with source as (
    select * from {{ source('bronze', 'admissions') }}
),

cleaned as (
    select
        admission_id,
        patient_id,
        cast(admission_date as timestamp) as admission_date,
        cast(discharge_date as timestamp) as discharge_date,
        -- Exact duration calculations
        round(cast(extract(epoch from (cast(discharge_date as timestamp) - cast(admission_date as timestamp))) / 86400.0 as numeric), 2) as length_of_stay_days,
        round(cast(extract(epoch from (cast(discharge_date as timestamp) - cast(admission_date as timestamp))) / 3600.0 as numeric), 2) as length_of_stay_hours,
        admission_type,
        department_id,
        discharge_disposition,
        case when discharge_disposition = 'EXPIRED' then 1 else 0 end as is_mortality,
        hospital_cost
    from source
)

select * from cleaned
