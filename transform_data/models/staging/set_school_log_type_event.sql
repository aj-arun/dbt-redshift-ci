WITH set_school_log_type_event AS (

    SELECT 
        "time" AS event_time,
        logId AS school_id
    FROM 
        {{ source('raw_events', 'event_logs') }}
    WHERE  
        "type" = 'SetLogType'
        AND LOWER(logType) = 'school'

)

SELECT * FROM set_school_log_type_event
