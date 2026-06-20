-- Operational Bottleneck Analysis
SELECT
  bottleneck_reason,
  hospital_alert_flag,
  operational_risk_level,
  COUNT(*) AS encounter_count,
  ROUND(AVG(capacity_strain_score), 1) AS avg_capacity_strain,
  ROUND(AVG(er_wait_time_minutes), 1) AS avg_wait_minutes,
  ROUND(AVG(bed_occupancy_rate), 1) AS avg_occupancy
FROM healthcare_operations
GROUP BY bottleneck_reason, hospital_alert_flag, operational_risk_level
ORDER BY encounter_count DESC;
