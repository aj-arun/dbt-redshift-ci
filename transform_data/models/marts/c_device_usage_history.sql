WITH device_minutes AS (
    
	SELECT
		t1.device_id,
        t1.event_time::DATE as date,
        SUM(CASE WHEN DATEDIFF(day, t1.event_time::DATE, t2.event_time::DATE) = 0
       		 THEN DATEDIFF(minute, t1.event_time, t2.event_time)
       		 ELSE 0
       		 END) AS usage_minutes

    FROM {{ ref("start_session_event") }} t1
    INNER JOIN {{ ref("end_session_event") }} t2
    USING (session_id)
    GROUP BY 1,2

), 
device_minutes_avg AS(

	SELECT
		t1.*,
        COALESCE(ROUND(SUM(t2.usage_minutes)/7.0, 2), 0.0) AS avg_usage_minutes_7d

	FROM device_minutes t1
	LEFT JOIN device_minutes t2
	    ON t1.device_id = t2.device_id AND 
	    t2.date BETWEEN (t1.date - interval '7 days') AND (t1.date - interval '1 days')
        -- past 7 days excluding the date
        -- if date included then condition: t2.date BETWEEN (t1.date - interval '6 days') AND t1.date
	GROUP BY 1, 2, 3
	ORDER BY 1, 2

)

SELECT * FROM device_minutes_avg