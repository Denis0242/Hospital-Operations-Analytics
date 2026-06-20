-- Patient Flow and Capacity Trend
SELECT
  month,
  department,
  COUNT(*) AS encounters,
  ROUND(AVG(throughput_time_hours), 1) AS avg_throughput_hours,
  ROUND(AVG(length_of_stay_days), 2) AS avg_los_days,
  ROUND(AVG(resource_utilization_index), 1) AS avg_resource_utilization,
  ROUND(AVG(department_cost_burden), 2) AS avg_cost_burden
FROM healthcare_operations
GROUP BY month, department
ORDER BY month, department;
