with source as (
    select * from {{ source('bronze', 'patients') }}
),

cleaned as (
    select
        patient_id,
        first_name,
        last_name,
        first_name || ' ' || last_name as full_name,
        case
            when gender = 'M' then 'Male'
            when gender = 'F' then 'Female'
            else 'Other / Unspecified'
        end as gender,
        cast(birth_date as date) as birth_date,
        -- ANSI portable age calculation
        (extract(year from current_date) - extract(year from cast(birth_date as date)))::int as age,
        blood_type,
        insurance_type,
        cast(registration_date as date) as registration_date
    from source
)

select * from cleaned
