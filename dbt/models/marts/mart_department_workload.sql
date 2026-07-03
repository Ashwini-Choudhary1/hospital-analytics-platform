with admissions as (
    select * from {{ ref('fct_admissions') }}
),

departments as (
    select * from {{ ref('stg_departments') }}
),

aggregated as (
    select
        d.department_id,
        d.department_name,
        d.bed_capacity,
        d.floor_number as floor,
        count(a.admission_id) as total_admissions,
        count(distinct a.patient_id) as unique_patients,
        round(cast(avg(a.length_of_stay_days) as numeric), 2) as avg_length_of_stay_days,
        round(cast(sum(a.length_of_stay_days) as numeric), 2) as total_bed_days_used,
        sum(a.is_mortality) as total_mortalities,
        round(cast(sum(a.is_mortality) * 100.0 / nullif(count(a.admission_id), 0) as numeric), 2) as mortality_rate_pct,
        round(cast(sum(a.hospital_cost) as numeric), 2) as total_revenue,
        round(cast(avg(a.hospital_cost) as numeric), 2) as avg_cost_per_admission
    from departments d
    left join admissions a on d.department_id = a.department_id
    group by d.department_id, d.department_name, d.bed_capacity, d.floor_number
)

select * from aggregated
order by total_admissions desc
