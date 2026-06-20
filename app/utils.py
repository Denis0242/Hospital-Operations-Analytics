import pandas as pd
import numpy as np


def load_data(path: str = "data/cleaned/healthcare_operations_cleaned.csv") -> pd.DataFrame:
    """Load the cleaned healthcare operations dataset."""
    df = pd.read_csv(path)
    df["visit_date"] = pd.to_datetime(df["visit_date"], errors="coerce")
    return df


def apply_filters(df: pd.DataFrame, departments, admission_types, insurance_types, severity_levels, age_groups, shifts, date_range):
    """Apply sidebar filters for the Streamlit app."""
    filtered = df.copy()
    if date_range and len(date_range) == 2:
        start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        filtered = filtered[(filtered["visit_date"] >= start) & (filtered["visit_date"] <= end)]

    filter_map = {
        "department": departments,
        "admission_type": admission_types,
        "insurance_type": insurance_types,
        "severity_level": severity_levels,
        "age_group": age_groups,
        "shift": shifts,
    }
    for col, values in filter_map.items():
        if values:
            filtered = filtered[filtered[col].isin(values)]
    return filtered


def calculate_kpis(df: pd.DataFrame) -> dict:
    """Calculate executive KPI values."""
    if df.empty:
        return {
            "total_patients": 0, "avg_los": 0, "bed_occupancy": 0, "readmission_rate": 0,
            "avg_er_wait": 0, "no_show_rate": 0, "satisfaction": 0, "treatment_success": 0,
            "capacity_strain": 0, "estimated_cost": 0,
        }
    return {
        "total_patients": int(df["patient_id"].nunique()),
        "avg_los": round(df["length_of_stay_days"].mean(), 1),
        "bed_occupancy": round(df["bed_occupancy_rate"].mean(), 1),
        "readmission_rate": round(df["readmitted_30_days"].mean() * 100, 1),
        "avg_er_wait": round(df["er_wait_time_minutes"].mean(), 0),
        "no_show_rate": round(df["no_show"].mean() * 100, 1),
        "satisfaction": round(df["patient_satisfaction_score"].mean(), 1),
        "treatment_success": round(df["treatment_success"].mean() * 100, 1),
        "capacity_strain": round(df["capacity_strain_score"].mean(), 0),
        "estimated_cost": round(df["estimated_cost_per_visit"].mean(), 0),
    }


def generate_executive_insights(df: pd.DataFrame) -> list[str]:
    """Generate simple executive-style insights from filtered data."""
    if df.empty:
        return ["No data available for the selected filters."]

    dept_summary = df.groupby("department", as_index=False).agg(
        avg_capacity_strain=("capacity_strain_score", "mean"),
        avg_wait=("er_wait_time_minutes", "mean"),
        avg_los=("length_of_stay_days", "mean"),
        readmission_rate=("readmitted_30_days", "mean"),
        treatment_success_rate=("treatment_success", "mean"),
        patient_volume=("patient_id", "nunique"),
    )

    highest_strain = dept_summary.sort_values("avg_capacity_strain", ascending=False).iloc[0]
    highest_wait = dept_summary.sort_values("avg_wait", ascending=False).iloc[0]
    highest_los = dept_summary.sort_values("avg_los", ascending=False).iloc[0]
    best_success = dept_summary.sort_values("treatment_success_rate", ascending=False).iloc[0]

    insights = [
        f"{highest_strain['department']} shows the highest capacity strain with an average score of {highest_strain['avg_capacity_strain']:.1f}.",
        f"{highest_wait['department']} has the longest average ER wait time at {highest_wait['avg_wait']:.0f} minutes.",
        f"{highest_los['department']} has the highest average length of stay at {highest_los['avg_los']:.1f} days.",
        f"{best_success['department']} has the strongest treatment success rate at {best_success['treatment_success_rate']*100:.1f}%.",
    ]

    if df["bed_occupancy_rate"].mean() > 85:
        insights.append("Average bed occupancy is above the 85% benchmark, indicating potential capacity pressure.")
    if df["readmitted_30_days"].mean() * 100 > 12:
        insights.append("Readmission rate is above the 12% benchmark and should be monitored by department and severity level.")
    if df["patient_satisfaction_score"].mean() < 4.2:
        insights.append("Patient satisfaction is below the 4.2 benchmark, suggesting a need to investigate patient experience drivers.")

    return insights
