WITH end_session_event AS (

    SELECT 
        "time" AS event_time,
        logId AS device_id, 
        sessionId AS session_id
    FROM 
        {{ source('raw_events', 'event_logs') }}
    WHERE  
        "type" = 'EndSession'

)

SELECT * FROM end_session_event
