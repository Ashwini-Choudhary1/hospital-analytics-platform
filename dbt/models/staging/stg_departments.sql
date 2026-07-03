with source as (
    select * from {{ source('bronze', 'departments') }}
),

renamed as (
    select
        department_id,
        department_name,
        bed_capacity,
        floor as floor_number
    from source
)

select * from renamed
