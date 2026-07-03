with source as (
    select * from {{ source('bronze', 'diagnoses') }}
),

cleaned as (
    select
        diagnosis_id,
        admission_id,
        upper(trim(icd10_code)) as icd10_code,
        trim(diagnosis_description) as diagnosis_description,
        is_primary
    from source
)

select * from cleaned
