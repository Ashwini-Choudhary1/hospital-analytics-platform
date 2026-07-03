with admissions as (
    select * from {{ ref('fct_admissions') }}
),

aggregated as (
    select
        primary_icd10_code as icd10_code,
        primary_diagnosis_description as diagnosis_description,
        count(admission_id) as total_admissions,
        count(distinct patient_id) as unique_patients,
        round(cast(avg(patient_age) as numeric), 1) as avg_patient_age,
        round(cast(avg(length_of_stay_days) as numeric), 2) as avg_length_of_stay_days,
        sum(is_mortality) as total_mortalities,
        round(cast(sum(is_mortality) * 100.0 / nullif(count(admission_id), 0) as numeric), 2) as mortality_rate_pct,
        round(cast(avg(hospital_cost) as numeric), 2) as avg_treatment_cost
    from admissions
    group by primary_icd10_code, primary_diagnosis_description
)

select * from aggregated
order by total_admissions desc
