WITH set_school_name_event AS (

    SELECT 
        "time" AS event_time,
        logId AS school_id,
        "name" AS school_name
    FROM 
        {{ source('raw_events', 'event_logs') }}
    WHERE  
        "type" = 'SetName'

)

SELECT * FROM set_school_name_event
