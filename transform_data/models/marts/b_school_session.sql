WITH session AS (
    
    SELECT 
        t1.session_id,
        t1.device_id,
        t1.event_time AS session_start_time,
        t2.event_time AS session_end_time

    FROM {{ ref("start_session_event") }} t1
    INNER JOIN {{ ref("end_session_event") }} t2
    USING (session_id)

), 
session_device AS (

    SELECT 
        t1.session_id,
        t1.session_start_time,
        t1.session_end_time,
        t2.school_id

    FROM session t1
    LEFT JOIN {{ ref("assign_device_to_school_event") }} t2
    USING (device_id)

),
session_school AS (

    SELECT
        t1.session_id,
        t1.session_start_time,
        t1.session_end_time, 
        t2.school_name
    
    FROM session_device t1
    LEFT JOIN {{ ref("set_school_name_event") }} t2
    USING (school_id)

)

SELECT * FROM session_school


