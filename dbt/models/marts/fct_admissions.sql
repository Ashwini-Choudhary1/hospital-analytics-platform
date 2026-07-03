with admissions as (
    select * from {{ ref('stg_admissions') }}
),

patients as (
    select * from {{ ref('stg_patients') }}
),

departments as (
    select * from {{ ref('stg_departments') }}
),

primary_diagnoses as (
    select
        admission_id,
        icd10_code as primary_icd10_code,
        diagnosis_description as primary_diagnosis_description
    from {{ ref('stg_diagnoses') }}
    where is_primary = true
),

joined as (
    select
        a.admission_id,
        a.patient_id,
        p.full_name as patient_name,
        p.gender as patient_gender,
        p.age as patient_age,
        p.insurance_type,
        a.admission_date,
        a.discharge_date,
        a.length_of_stay_days,
        a.length_of_stay_hours,
        a.admission_type,
        a.department_id,
        d.department_name,
        d.floor_number as department_floor,
        a.discharge_disposition,
        a.is_mortality,
        a.hospital_cost,
        coalesce(diag.primary_icd10_code, 'UNKNOWN') as primary_icd10_code,
        coalesce(diag.primary_diagnosis_description, 'No Primary Diagnosis Recorded') as primary_diagnosis_description
    from admissions a
    left join patients p on a.patient_id = p.patient_id
    left join departments d on a.department_id = d.department_id
    left join primary_diagnoses diag on a.admission_id = diag.admission_id
)

select * from joined
