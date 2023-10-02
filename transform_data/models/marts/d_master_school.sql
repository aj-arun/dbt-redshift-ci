WITH session AS (
    
    SELECT 
        t1.device_id,
        DATEDIFF(minute, t1.event_time, t2.event_time) AS session_duration_minutes

    FROM {{ ref("start_session_event") }} t1
    INNER JOIN {{ ref("end_session_event") }} t2
    USING (session_id)

), 
device_school AS (

    SELECT 
        t1.school_id,
        t3.school_name,
        t2.device_id,
        t2.session_duration_minutes

    FROM {{ ref("assign_device_to_school_event") }} t1
    INNER JOIN session t2
    USING (device_id)
    INNER JOIN {{ ref("set_school_name_event") }} t3
    USING (school_id)

),
school_master AS (

    SELECT
        school_id,
        school_name,
        COUNT(device_id) AS device_count,
        AVG(session_duration_minutes) AS mean_session_length, 
        MEDIAN(session_duration_minutes) AS median_session_length 
    
    FROM device_school t1
    GROUP BY 1, 2

)

SELECT * FROM school_master