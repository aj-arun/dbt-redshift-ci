WITH set_device_log_type_event AS (

    SELECT 
        "time" AS event_time,
        logId AS device_id
    FROM 
        {{ source('raw_device_events', 'user_behaviour') }}
    WHERE  
        "type" = 'SetLogType'
        AND LOWER(logType) = 'device'

)

SELECT * FROM set_device_log_type_event
