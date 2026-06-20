# Data Dictionary

This dataset is synthetic and de-identified. It is designed for a Healthcare Operations Executive Dashboard portfolio project.

| Column | Description |
|---|---|
| `patient_id` | Synthetic patient identifier; de-identified and safe for GitHub. |
| `visit_id` | Unique visit/encounter identifier. |
| `visit_date` | Date of hospital visit or encounter. |
| `year` | Calendar year for trend analysis. |
| `month` | Year-month field for monthly KPI trends. |
| `quarter` | Quarter for executive period reporting. |
| `day_of_week` | Day name to analyze weekday/weekend operations. |
| `is_weekend` | Weekend flag used for volume and no-show analysis. |
| `department` | Hospital department/service line. |
| `admission_type` | How the patient entered the care pathway. |
| `insurance_type` | High-level insurance category. |
| `severity_level` | Clinical/operational acuity proxy. |
| `shift` | Day, Evening, or Night shift. |
| `provider_type` | Primary provider/staffing group involved in encounter. |
| `age` | Synthetic patient age. |
| `age_group` | Age band used for population-level analysis. |
| `length_of_stay_days` | Total length of stay in days. |
| `er_wait_time_minutes` | Wait time proxy in minutes. |
| `throughput_time_hours` | Time from arrival/intake to completion/discharge. |
| `bed_occupancy_rate` | Department-level occupancy proxy on the visit date. |
| `appointment_completed` | 1 if visit/appointment was completed; 0 otherwise. |
| `no_show` | 1 if patient no-showed; 0 otherwise. |
| `readmitted_30_days` | 1 if patient was readmitted within 30 days; 0 otherwise. |
| `treatment_success` | 1 if visit outcome was clinically/operationally successful; 0 otherwise. |
| `patient_satisfaction_score` | Patient satisfaction score from 1.0 to 5.0. |
| `visit_outcome` | Executive-friendly outcome classification. |
| `discharge_status` | Discharge disposition. |
| `resource_utilization_index` | Composite 0–100 proxy for resource intensity. |
| `estimated_cost_per_visit` | Synthetic cost estimate for the visit. |
| `department_cost_burden` | Cost weighted by resource utilization. |
| `capacity_strain_score` | Composite 0–100 hospital strain score. |
| `capacity_status` | Stable, Moderate Risk, or High Strain based on strain score. |
| `operational_risk_level` | Low, Moderate, or High operational risk classification. |
| `bottleneck_reason` | Main drivers of operational strain. |
| `hospital_alert_flag` | Green, Orange, or Red executive alert flag. |
| `target_bed_occupancy_rate` | Benchmark target for occupancy. |
| `target_readmission_rate` | Benchmark target for readmission percentage. |
| `target_er_wait_time` | Benchmark target for ED/wait time. |
| `target_no_show_rate` | Benchmark target for no-show percentage. |
| `target_satisfaction_score` | Benchmark target for satisfaction. |
| `target_treatment_success_rate` | Benchmark target for treatment success percentage. |