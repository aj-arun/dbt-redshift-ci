WITH assign_device_to_school_event AS (

    SELECT 
        "time" AS event_time,
        logId AS device_id, 
        schoolId AS school_id
    FROM 
        {{ source('raw_events', 'event_logs') }}
    WHERE  
        "type" = 'AssignToSchool'

)

SELECT * FROM assign_device_to_school_event
