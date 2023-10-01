WITH start_session_event AS (

    SELECT 
        "time" AS event_time,
        logId AS device_id,
        sessionId AS session_id
    FROM 
        {{ source('raw_device_events', 'user_behaviour') }}
    WHERE  
        "type" = 'StartSession'

)

SELECT * FROM start_session_event
