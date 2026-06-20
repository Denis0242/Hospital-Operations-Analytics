-- Readmission by Department, Age Group, and Severity
SELECT
  department,
  age_group,
  severity_level,
  COUNT(*) AS encounters,
  ROUND(100.0 * AVG(readmitted_30_days), 1) AS readmission_rate_pct,
  ROUND(AVG(length_of_stay_days), 2) AS avg_los_days,
  ROUND(AVG(patient_satisfaction_score), 2) AS avg_satisfaction
FROM healthcare_operations
GROUP BY department, age_group, severity_level
ORDER BY readmission_rate_pct DESC;
