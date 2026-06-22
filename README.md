# 🏥 Hospital Operations Analytics

## Live Dashboard

**Tableau Public:**
https://public.tableau.com/app/profile/denis.king

---

# Executive Summary

Hospital leaders must continuously monitor patient flow, capacity utilization, operational bottlenecks, and care outcomes to maintain efficient healthcare delivery.

This project provides an executive-level hospital operations dashboard designed to answer one critical business question:

> **Where are operational bottlenecks, capacity constraints, and performance risks across the hospital?**

Using Tableau, SQL, Excel, and healthcare KPI reporting techniques, the dashboard combines operational KPIs, department performance monitoring, capacity strain analysis, patient flow analytics, and readmission tracking to support data-driven decision-making.

The solution enables hospital leadership to:

* Monitor hospital-wide operational performance
* Identify capacity constraints and bottlenecks
* Improve patient throughput
* Optimize resource allocation
* Reduce operational risk
* Support patient care delivery through KPI-driven insights

---

# Business Problem

Hospitals face ongoing operational challenges including:

* High bed occupancy rates
* Emergency Department congestion
* Patient throughput delays
* Capacity strain across departments
* Resource allocation inefficiencies
* Readmission pressure

Without centralized reporting, leadership teams may struggle to identify emerging operational risks and prioritize improvement initiatives.

This project was developed to provide visibility into hospital performance, patient flow efficiency, and operational bottlenecks across multiple service lines.

---

# Decision Support Use Case

This dashboard helps hospital leadership monitor operational KPIs, identify capacity constraints, evaluate department performance, track patient flow efficiency, and support decisions related to resource allocation, patient throughput, capacity planning, and operational improvement initiatives.

---

# KPIs

The Executive Dashboard monitors:

| KPI                          | Business Purpose                        |
| ---------------------------- | --------------------------------------- |
| Total Patients               | Measures hospital utilization           |
| Average Length of Stay (LOS) | Measures operational efficiency         |
| Bed Occupancy Rate           | Measures capacity utilization           |
| Readmission Rate             | Measures quality and continuity of care |
| Average ER Wait Time         | Measures patient flow efficiency        |
| Treatment Success Rate       | Measures clinical outcomes              |
| Patient Satisfaction Score   | Measures patient experience             |

---

# Dashboard Overview

The dashboard provides a comprehensive view of hospital operations, patient flow, capacity management, and department performance.

The solution consists of two executive reporting dashboards:

### Dashboard 1 – Hospital Operations Executive Dashboard

Focus Areas:

* Executive KPI Monitoring
* Hospital Alert Summary
* Operational Bottleneck Analysis
* Capacity Strain Monitoring
* Department Performance Evaluation
* Executive Decision Support

### Dashboard 2 – Patient Flow & Capacity Analytics

Focus Areas:

* Admissions Trend Analysis
* Throughput Monitoring
* Visit Outcome Analysis
* Treatment Success Tracking
* Length of Stay Analysis
* Readmission Risk Monitoring

These dashboards support healthcare leadership, operations teams, and decision-support analysts responsible for hospital performance management.

---

# Dashboard Screenshots

## Hospital Operations Executive Dashboard

![Hospital Operations Executive Dashboard](screenshots/hero_dashboard.png)

### KPI Scorecard

![KPI Scorecard](screenshots/kpi_scorecard.png)

### Capacity Strain Heatmap

![Capacity Strain Heatmap](screenshots/capacity_strain_heatmap.png)

### Department Performance Matrix

![Department Performance Matrix](screenshots/department_performance_matrix.png)

---

## Patient Flow & Capacity Analytics Dashboard

![Patient Flow & Capacity Analytics](screenshots/patient_flow_dashboard.png)

### Treatment Success Analysis

![Treatment Success](screenshots/treatment_success.png)

### Length of Stay Analysis

![LOS Analysis](screenshots/los_analysis.png)

### Readmission Risk Analysis

![Readmission Risk](screenshots/readmission_risk.png)

---

# Key Insight

Emergency Department and ICU services experience the highest operational strain due to elevated occupancy levels, longer wait times, and increased throughput pressure, making them the primary drivers of hospital capacity challenges.

---

# Business Impact

This dashboard supports hospital leadership by transforming operational data into actionable insights that improve resource planning, patient flow efficiency, and care delivery.

### Operational Benefits

* Identifies departments experiencing capacity strain
* Improves visibility into bed occupancy and throughput performance
* Highlights readmission trends requiring intervention
* Supports monitoring of Length of Stay drivers
* Centralizes operational KPI reporting

### Business Value

* Enables proactive identification of operational bottlenecks
* Supports data-driven capacity management
* Improves workflow optimization
* Enhances hospital performance reporting
* Strengthens executive decision-making

---

# Recommendation

Increase operational focus on Emergency Department and ICU services through staffing optimization, capacity planning, throughput improvements, and proactive monitoring of occupancy, wait times, and readmission trends.

---

# Data Dictionary

| Field                  | Description                         |
| ---------------------- | ----------------------------------- |
| patient_id             | Unique patient encounter identifier |
| department             | Hospital department                 |
| admission_date         | Patient admission date              |
| discharge_date         | Patient discharge date              |
| bed_occupancy_rate     | Department occupancy percentage     |
| er_wait_time           | Emergency Department wait time      |
| length_of_stay         | Patient length of stay              |
| readmission_flag       | Indicates readmission status        |
| treatment_success_rate | Treatment outcome indicator         |
| patient_satisfaction   | Patient satisfaction score          |

---

# Analytics Workflow

```text
Business Problem
        ↓
Data Collection
        ↓
Data Cleaning
        ↓
KPI Engineering
        ↓
Operational Analysis
        ↓
Dashboard Development
        ↓
Insight Generation
        ↓
Decision Support
        ↓
Business Impact
```

---

# Executive Decision Summary

### Insight

Emergency Department and ICU services experience the highest operational strain due to elevated occupancy levels, longer wait times, and increased throughput pressure.

### Action

Monitor occupancy, wait times, Length of Stay, and readmission trends while prioritizing high-strain departments.

### Recommendation

Improve staffing allocation, capacity planning, and patient flow processes within Emergency and ICU services.

### Decision

Prioritize capacity management and throughput improvement efforts before expanding service demand.

---

# Tools Used

* Tableau
* SQL
* Excel
* CSV Data Modeling
* Healthcare KPI Reporting

---

# Repository Structure

```text
Hospital-Operations-Analytics/

├── data/
│   └── healthcare_operations_dashboard_950_rows_final.csv

├── screenshots/
│   ├── hero_dashboard.png
│   ├── kpi_scorecard.png
│   ├── capacity_strain_heatmap.png
│   ├── department_performance_matrix.png
│   ├── readmission_risk.png
│   ├── los_analysis.png
│   └── treatment_success.png

├── tableau/
│   └── Hospital_Operations_Analytics.twbx

└── README.md
```

---

# Future Improvements

* Add predictive modeling for readmission risk
* Add patient demand forecasting
* Add department staffing optimization analysis
* Add automated KPI refresh workflows
* Connect to Snowflake, Redshift, or cloud-based healthcare data warehouses

---

# Disclaimer

* Dataset is synthetic and created for portfolio purposes.
* No Protected Health Information (PHI) is included.
* Project developed for educational and demonstration purposes.
* This project is not affiliated with or endorsed by Kaiser Permanente or any healthcare organization.

