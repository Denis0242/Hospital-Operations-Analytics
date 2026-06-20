-- Department Performance Ranking
SELECT
  department,
  COUNT(DISTINCT patient_id) AS patients,
  ROUND(AVG(length_of_stay_days), 2) AS avg_los_days,
  ROUND(AVG(bed_occupancy_rate), 1) AS avg_occupancy_rate,
  ROUND(AVG(er_wait_time_minutes), 1) AS avg_wait_time_minutes,
  ROUND(100.0 * AVG(readmitted_30_days), 1) AS readmission_rate_pct,
  ROUND(AVG(patient_satisfaction_score), 2) AS avg_satisfaction,
  ROUND(AVG(capacity_strain_score), 1) AS avg_capacity_strain
FROM healthcare_operations
GROUP BY department
ORDER BY avg_capacity_strain DESC;
