-- Executive KPI Summary
SELECT
  COUNT(DISTINCT patient_id) AS total_patients,
  ROUND(AVG(length_of_stay_days), 2) AS avg_los_days,
  ROUND(AVG(bed_occupancy_rate), 1) AS avg_bed_occupancy_rate,
  ROUND(100.0 * AVG(readmitted_30_days), 1) AS readmission_rate_pct,
  ROUND(AVG(er_wait_time_minutes), 1) AS avg_wait_time_minutes,
  ROUND(AVG(throughput_time_hours), 1) AS avg_throughput_hours,
  ROUND(100.0 * AVG(appointment_completed), 1) AS appointment_completion_pct,
  ROUND(100.0 * AVG(no_show), 1) AS no_show_rate_pct,
  ROUND(AVG(patient_satisfaction_score), 2) AS avg_satisfaction_score,
  ROUND(100.0 * AVG(treatment_success), 1) AS treatment_success_rate_pct,
  ROUND(AVG(capacity_strain_score), 1) AS avg_capacity_strain_score
FROM healthcare_operations;
