USE caris_db;
set @start_date='2025-11-01';
set @end_date='2025-11-30';

SELECT 
	lhs.office,
	lhs.name as hospital,
    p.patient_code,
    tmi.first_name,
    tmi.last_name,
    tmi.is_abandoned,
    tmi.is_dead,
    tmi.dob,
    tp.dpa,
    tp.ddr,
    tp.actual_delivery_date AS delivery_date,
    tp.termination_of_pregnancy,
    MIN(c.date) AS first_date_in_club_session_during_pregnancy,
    MAX(c.date) AS last_date_in_club_session_during_pregnancy,
    IF(MIN(c.date) IS NOT NULL, 'yes', 'no') AS has_session_during_pregnancy,
    IF(v.id_patient IS NOT NULL,
        'yes',
        'no') AS has_viral_load_for_interval,
    IF((viral_load_date + INTERVAL 12 MONTH) > @end_date,
        'yes',
        'no') AS has_valide_viral_load,
    IF(((tp.dpa >= @start_date)
            OR ((tp.ddr + INTERVAL 9 MONTH + INTERVAL 7 DAY) >= @start_date))
            AND ((tp.ddr <= @end_date)
            OR ((tp.dpa - INTERVAL 9 MONTH - INTERVAL 7 DAY) <= @end_date)),
        'yes',
        'no') AS is_pregnant_in_the_interval,
    IF(tp.actual_delivery_date BETWEEN @start_date AND @end_date,
        'yes',
        'no') AS has_delivery_in_the_interval,
    IF((tp.dpa BETWEEN @start_date AND @end_date
            OR (tp.ddr + INTERVAL 9 MONTH + INTERVAL 7 DAY) BETWEEN @start_date AND @end_date),
        'yes',
        'no') AS expected_delivery_in_period,
    ll.name AS planned_place_of_birth_name,
    lh.name AS planned_place_of_birth_hospital_name,
    IF(tp.planned_place_of_birth_hospital_know = 1,
        'yes',
        IF(tp.planned_place_of_birth_hospital_know,
            'no',
            tp.planned_place_of_birth_hospital_know)) AS planned_place_of_birth_hospital_know_name,
    tp.created_at AS pregnancy_added_at,
    IF(tp.created_at BETWEEN @start_date AND @end_date,
        'yes',
        'no') AS pregnancy_added_in_the_interval,
    b.viral_load_date,
    b.viral_load_count,
    IF(v.id_patient IS NOT NULL,
        'yes',
        'no') AS has_viral_load_in_the_interval,
    IF((b.viral_load_date + INTERVAL 12 MONTH) > @start_date,
        'yes',
        'no') AS valide_viral_load_for_interval,
    IF(tp.infant_has_no_pcr_test = 1,
        'yes',
        IF(tp.infant_has_no_pcr_test = 2,
            'no',
            tp.infant_has_no_pcr_test)) AS has_pcr_test,
            
            timestampdiff(DAY,tp.actual_delivery_date,NOW()) as actual_delivery_nb_day
FROM
    tracking_pregnancy tp
        LEFT JOIN
    lookup_testing_birth_location ll ON ll.id = tp.planned_place_of_birth
        LEFT JOIN
    lookup_hospital lh ON lh.id = tp.planned_place_of_birth_hospital
        LEFT JOIN
    tracking_motherbasicinfo tmi ON tmi.id_patient = tp.id_patient_mother
        LEFT JOIN
    patient p ON p.id = tp.id_patient_mother
    LEFT JOIN lookup_hospital lhs on lhs.city_code=p.city_code and lhs.hospital_code=p.hospital_code
        LEFT JOIN
    (SELECT 
        s.id_patient, cs.date
    FROM
        session s
    JOIN club_session cs ON cs.id = s.id_club_session
    WHERE
        s.is_present = 1) c ON c.id_patient = tp.id_patient_mother
        AND ((c.date BETWEEN tp.ddr AND (tp.ddr + INTERVAL 9 MONTH + INTERVAL 7 DAY))
        OR (c.date BETWEEN (tp.dpa - INTERVAL 9 MONTH - INTERVAL 7 DAY) AND tp.dpa))
        LEFT JOIN
    (SELECT 
        tmf.id_patient, tmf.viral_load_date, tmf.viral_load_count
    FROM
        tracking_motherfollowup tmf
    INNER JOIN (SELECT 
        id_patient, MAX(viral_load_date) AS max_viral_load_date
    FROM
        tracking_motherfollowup
    GROUP BY id_patient) latest ON tmf.id_patient = latest.id_patient
        AND tmf.viral_load_date = latest.max_viral_load_date
    GROUP BY tmf.id_patient) b ON b.id_patient = tp.id_patient_mother
        LEFT JOIN
    (SELECT 
        tmf.id_patient
    FROM
        tracking_motherfollowup tmf
    WHERE
        viral_load_date BETWEEN @start_date AND @end_date
    GROUP BY tmf.id_patient) v ON v.id_patient = tp.id_patient_mother
WHERE
    (((tp.dpa >= @start_date)
        OR ((tp.ddr + INTERVAL 9 MONTH + INTERVAL 7 DAY) >= @start_date))
        AND ((tp.ddr <= @end_date)
        OR ((tp.dpa - INTERVAL 9 MONTH - INTERVAL 7 DAY) <= @end_date)))
        OR tp.actual_delivery_date BETWEEN @start_date AND @end_date
        OR tp.created_at BETWEEN @start_date AND @end_date
GROUP BY id_patient_mother