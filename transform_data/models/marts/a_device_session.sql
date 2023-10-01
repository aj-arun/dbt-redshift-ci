SELECT
    t1.device_id AS device_id, 
    MIN(t2.event_time) AS first_session_start_time
    
FROM {{ ref("set_device_log_type_event") }} AS t1
LEFT JOIN {{ ref("start_session_event") }} AS t2
USING (device_id)
GROUP BY 1
