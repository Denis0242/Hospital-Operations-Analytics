# Tableau Dashboard Plan — Healthcare Operations Executive Dashboard

## Project Goal
Build an executive-style hospital operations dashboard that answers:

**Where are operational bottlenecks, capacity issues, and performance risks across the hospital?**

Use the final CSV: `data/healthcare_operations_dashboard_950_rows_final.csv`.

## Dashboard 1: Hospital Executive Operations Dashboard

### KPI Cards
1. Total Patients = `COUNTD([patient_id])`
2. Avg Length of Stay = `AVG([length_of_stay_days])`
3. Bed Occupancy Rate = `AVG([bed_occupancy_rate])`
4. Readmission Rate = `AVG([readmitted_30_days])`
5. Avg ER Wait Time = `AVG([er_wait_time_minutes])`
6. Patient Throughput = `AVG([throughput_time_hours])`
7. Appointment Completion % = `AVG([appointment_completed])`
8. No-show Rate = `AVG([no_show])`
9. Patient Satisfaction Score = `AVG([patient_satisfaction_score])`
10. Treatment Success Rate = `AVG([treatment_success])`

### Recommended Visuals
1. **Executive KPI Scorecard** — KPI cards with benchmark comparison.
2. **Department Performance Matrix** — Department vs KPIs: occupancy, LOS, wait time, satisfaction, readmission.
3. **Capacity Strain Heatmap** — Department by month, color by `AVG(capacity_strain_score)`.
4. **Operational Bottlenecks Bar Chart** — count of `bottleneck_reason`.
5. **Hospital Alert Summary** — Red/Orange/Green count by department.
6. **Monthly KPI Trend** — parameter-driven trend for LOS, wait time, readmission, satisfaction, occupancy.

### Key Filters
- Date Range
- Department
- Admission Type
- Severity Level
- Insurance Type
- Age Group
- Shift

## Dashboard 2: Patient Flow & Capacity Analytics

### Recommended Visuals
1. Admissions by Department and Month
2. Average LOS by Department and Severity
3. Readmission Rate by Department and Age Group
4. Throughput Time by Shift
5. Cost Burden by Department
6. Visit Outcome Distribution

## Tableau Calculated Fields

### Readmission Rate
```tableau
AVG([readmitted_30_days])
```
Format as percentage.

### No-show Rate
```tableau
AVG([no_show])
```
Format as percentage.

### Treatment Success Rate
```tableau
AVG([treatment_success])
```
Format as percentage.

### Appointment Completion Rate
```tableau
AVG([appointment_completed])
```
Format as percentage.

### KPI Status — Bed Occupancy
```tableau
IF AVG([bed_occupancy_rate]) > AVG([target_bed_occupancy_rate]) THEN "Above Target / Capacity Risk"
ELSE "Within Target"
END
```

### KPI Status — ER Wait Time
```tableau
IF AVG([er_wait_time_minutes]) > AVG([target_er_wait_time]) THEN "Above Target / Delay Risk"
ELSE "Within Target"
END
```

### Executive Summary Text
Use a dashboard text box like:

> Emergency Department and ICU show the highest operational strain, driven by elevated wait times, occupancy pressure, and higher resource utilization. Outpatient services show stronger completion performance but require no-show monitoring.

## Design Recommendation
Use a clean executive style: white background, 4–5 KPI cards per row, simple color status, and 2 dashboard pages only. Keep the dashboard readable for leadership.
