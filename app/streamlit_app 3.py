import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# -------------------------------------------------------------
# Page Config
# -------------------------------------------------------------
st.set_page_config(
    page_title="Hospital Operations Analytics",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -------------------------------------------------------------
# Styling
# -------------------------------------------------------------
st.markdown(
    """
    <style>
        .main-title {
            text-align: center;
            color: #2f6fb3;
            font-size: 34px;
            font-weight: 700;
            margin-bottom: 0.2rem;
        }
        .sub-title {
            text-align: center;
            color: #555;
            font-size: 15px;
            margin-bottom: 1.0rem;
        }
        .metric-card {
            background: #ffffff;
            border: 1px solid #d9e2ef;
            border-radius: 12px;
            padding: 16px 12px;
            box-shadow: 0 1px 4px rgba(0,0,0,0.06);
            text-align: center;
            min-height: 105px;
        }
        .metric-label {
            color: #2f6fb3;
            font-size: 18px;
            font-weight: 600;
            line-height: 1.15;
        }
        .metric-value {
            color: #222222;
            font-size: 25px;
            font-weight: 800;
            margin-top: 8px;
        }
        .summary-box {
            background: #f8fbff;
            border-left: 6px solid #2f6fb3;
            border-radius: 10px;
            padding: 14px 18px;
            margin: 8px 0 16px 0;
            font-size: 15px;
        }
        .insight-card {
            border-radius: 12px;
            padding: 16px;
            min-height: 132px;
            box-shadow: 0 1px 4px rgba(0,0,0,0.08);
            color: #111;
        }
        .insight-title {
            font-weight: 800;
            font-size: 18px;
            margin-bottom: 8px;
        }
        .insight-text {
            font-size: 14.5px;
            line-height: 1.35;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------------------------------------------
# Helper Functions
# -------------------------------------------------------------
DATA_CANDIDATES = [
    Path("data/healthcare_operations_cleaned.csv"),
    Path("data/healthcare_operations_dashboard_950_rows_final.csv"),
    Path("healthcare_operations_dashboard_950_rows_final.csv"),
]

@st.cache_data
def load_data() -> pd.DataFrame:
    data_path = next((p for p in DATA_CANDIDATES if p.exists()), None)
    if data_path is None:
        st.error(
            "Dataset not found. Place your CSV in `data/healthcare_operations_cleaned.csv` "
            "or `data/healthcare_operations_dashboard_950_rows_final.csv`."
        )
        st.stop()

    df = pd.read_csv(data_path)
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    if "visit_date" in df.columns:
        df["visit_date"] = pd.to_datetime(df["visit_date"], errors="coerce")
    elif "date" in df.columns:
        df["visit_date"] = pd.to_datetime(df["date"], errors="coerce")
    else:
        st.error("No date column found. Expected `visit_date` or `date`.")
        st.stop()

    df = df.dropna(subset=["visit_date"]).copy()
    df["month"] = df["visit_date"].dt.to_period("M").astype(str)
    df["visit_year"] = df["visit_date"].dt.year.astype(str)

    # Keep binary rate columns as numeric
    for col in ["readmitted_30_days", "treatment_success", "appointment_completed", "no_show"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    numeric_cols = [
        "length_of_stay_days", "bed_occupancy_rate", "er_wait_time_minutes",
        "throughput_time_hours", "patient_satisfaction_score", "capacity_strain_score"
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def pct(value: float, digits: int = 2) -> str:
    if pd.isna(value):
        return "0.00%"
    return f"{value * 100:.{digits}f}%" if value <= 1.5 else f"{value:.{digits}f}%"


def mean_or_zero(df: pd.DataFrame, col: str) -> float:
    return float(df[col].mean()) if col in df.columns and not df.empty else 0.0


def count_patients(df: pd.DataFrame) -> int:
    if "patient_id" in df.columns:
        return int(df["patient_id"].nunique())
    return int(len(df))


def add_metric_card(label: str, value: str):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def apply_filters(df: pd.DataFrame) -> pd.DataFrame:
    with st.sidebar:
        st.header("Filters")

        min_date = df["visit_date"].min().date()
        max_date = df["visit_date"].max().date()

        date_range = st.date_input(
            "Visit Date",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
        )

        filter_cols = {
            "visit_year": "Visit Year",
            "department": "Department",
            "admission_type": "Admission Type",
            "insurance_type": "Insurance Type",
            "severity_level": "Severity Level",
            "age_group": "Age Group",
            "shift": "Shift",
        }

        selections = {}
        for col, label in filter_cols.items():
            if col in df.columns:
                values = sorted(df[col].dropna().astype(str).unique())
                selections[col] = st.multiselect(label, values)

    out = df.copy()

    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        out = out[(out["visit_date"] >= start_date) & (out["visit_date"] <= end_date)]

    for col, selected in selections.items():
        if selected:
            out = out[out[col].astype(str).isin(selected)]

    return out


def show_empty_warning(df: pd.DataFrame):
    if df.empty:
        st.warning("No records match the selected filters. Please adjust your filters.")
        st.stop()


def create_alert_flag(row):
    strain = row.get("capacity_strain_score", 0)
    occupancy = row.get("bed_occupancy_rate", 0)
    wait = row.get("er_wait_time_minutes", 0)
    if strain >= 75 or occupancy >= 90 or wait >= 60:
        return "High Risk"
    if strain >= 60 or occupancy >= 80 or wait >= 45:
        return "Moderate Risk"
    return "Stable"


def colorful_decision_cards():
    st.markdown("### Executive Decision Summary")
    c1, c2, c3, c4 = st.columns(4)
    cards = [
        (c1, "📊 Insight", "Emergency and ICU departments show the highest operational strain due to elevated occupancy and longer wait times.", "#e8f2ff"),
        (c2, "⚡ Action", "Prioritize staffing and resource allocation in high-demand departments to reduce delays and improve patient flow.", "#fff4df"),
        (c3, "💡 Recommendation", "Monitor occupancy, wait time, and readmission trends monthly to proactively identify capacity risks.", "#eaf8ef"),
        (c4, "🎯 Decision", "Focus operational improvement efforts on Emergency and ICU services to enhance efficiency and patient experience.", "#f6eefe"),
    ]
    for col, title, text, bg in cards:
        with col:
            st.markdown(
                f"""
                <div class="insight-card" style="background:{bg};">
                    <div class="insight-title">{title}</div>
                    <div class="insight-text">{text}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

# -------------------------------------------------------------
# Load + Filter Data
# -------------------------------------------------------------
df = load_data()
filtered = apply_filters(df)
show_empty_warning(filtered)

# -------------------------------------------------------------
# Header
# -------------------------------------------------------------
st.markdown('<div class="main-title">Hospital Operations Executive Dashboard</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">Operational Performance, Capacity Risk & Patient Flow Monitoring</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="summary-box">
        <strong>Executive Summary:</strong> Emergency and ICU departments show the highest operational strain due to elevated occupancy and longer wait times.
    </div>
    """,
    unsafe_allow_html=True,
)

# -------------------------------------------------------------
# Dashboard 1: KPI Scorecard
# -------------------------------------------------------------
kpi_cols = st.columns(7)
with kpi_cols[0]:
    add_metric_card("Total<br>Patients", f"{count_patients(filtered):,}")
with kpi_cols[1]:
    add_metric_card("Avg<br>LOS", f"{mean_or_zero(filtered, 'length_of_stay_days'):.3f}")
with kpi_cols[2]:
    add_metric_card("Bed<br>Occupancy", f"{mean_or_zero(filtered, 'bed_occupancy_rate'):.2f}")
with kpi_cols[3]:
    add_metric_card("Readmission<br>Rate", pct(mean_or_zero(filtered, 'readmitted_30_days')))
with kpi_cols[4]:
    add_metric_card("Avg ER Wait<br>Time", f"{mean_or_zero(filtered, 'er_wait_time_minutes'):.2f}")
with kpi_cols[5]:
    add_metric_card("Treatment Success<br>Rate", pct(mean_or_zero(filtered, 'treatment_success')))
with kpi_cols[6]:
    add_metric_card("Patient<br>Satisfaction", f"{mean_or_zero(filtered, 'patient_satisfaction_score'):.3f}")

st.divider()

# -------------------------------------------------------------
# Dashboard 1: Main Visuals
# -------------------------------------------------------------
left, middle, right = st.columns([1.05, 1.05, 1.65])

with left:
    if "department" in filtered.columns:
        alert_df = filtered.copy()
        alert_df["hospital_alert"] = alert_df.apply(create_alert_flag, axis=1)
        alert_summary = alert_df.groupby(["department", "hospital_alert"], as_index=False).agg(
            patients=("patient_id", "nunique") if "patient_id" in alert_df.columns else ("department", "size")
        )
        fig_alert = px.bar(
            alert_summary,
            x="patients",
            y="department",
            color="hospital_alert",
            orientation="h",
            title="Hospital Alert Summary",
            color_discrete_map={"High Risk": "#2b5c8a", "Moderate Risk": "#49a6b8", "Stable": "#a7d8d4"},
        )
        fig_alert.update_layout(height=320, margin=dict(l=10, r=10, t=50, b=10), yaxis_title="", xaxis_title="")
        st.plotly_chart(fig_alert, use_container_width=True)

with middle:
    if "bottleneck_reason" in filtered.columns:
        bottlenecks = (
            filtered.groupby("bottleneck_reason", as_index=False)
            .size()
            .rename(columns={"size": "count"})
            .sort_values("count", ascending=True)
        )
        fig_bottleneck = px.bar(
            bottlenecks,
            x="count",
            y="bottleneck_reason",
            orientation="h",
            title="Operational Bottlenecks",
            color_discrete_sequence=["#5a86b5"],
        )
        fig_bottleneck.update_layout(height=320, margin=dict(l=10, r=10, t=50, b=10), yaxis_title="", xaxis_title="")
        st.plotly_chart(fig_bottleneck, use_container_width=True)

with right:
    if {"department", "month", "capacity_strain_score"}.issubset(filtered.columns):
        heat = filtered.groupby(["department", "month"], as_index=False).agg(
            capacity_strain=("capacity_strain_score", "mean")
        )
        fig_heat = px.density_heatmap(
            heat,
            x="month",
            y="department",
            z="capacity_strain",
            histfunc="avg",
            text_auto=".2f",
            title="Capacity Strain Heatmap",
            color_continuous_scale="Teal",
        )
        fig_heat.update_layout(height=320, margin=dict(l=10, r=10, t=50, b=10), xaxis_title="", yaxis_title="")
        st.plotly_chart(fig_heat, use_container_width=True)

matrix_col, trend_col = st.columns([1.35, 1])

with matrix_col:
    required = {"department", "bed_occupancy_rate", "length_of_stay_days", "er_wait_time_minutes", "patient_satisfaction_score", "readmitted_30_days"}
    if required.issubset(filtered.columns):
        matrix = filtered.groupby("department", as_index=False).agg(
            Occupancy=("bed_occupancy_rate", "mean"),
            LOS=("length_of_stay_days", "mean"),
            Wait_Time=("er_wait_time_minutes", "mean"),
            Satisfaction=("patient_satisfaction_score", "mean"),
            Readmission=("readmitted_30_days", "mean"),
        )
        melted = matrix.melt(id_vars="department", var_name="KPI", value_name="Value")
        fig_matrix = px.scatter(
            melted,
            x="KPI",
            y="department",
            color="Value",
            size=[10] * len(melted),
            title="Department Performance Matrix",
            color_continuous_scale="RdYlGn_r",
        )
        fig_matrix.update_traces(marker=dict(symbol="square", sizemode="diameter", size=11))
        fig_matrix.update_layout(height=360, margin=dict(l=10, r=10, t=50, b=20), xaxis_title="", yaxis_title="")
        st.plotly_chart(fig_matrix, use_container_width=True)

with trend_col:
    kpi_options = {
        "Readmission": "readmitted_30_days",
        "LOS": "length_of_stay_days",
        "Wait Time": "er_wait_time_minutes",
        "Satisfaction": "patient_satisfaction_score",
        "Occupancy": "bed_occupancy_rate",
    }
    available_options = {k: v for k, v in kpi_options.items() if v in filtered.columns}
    selected_kpi = st.selectbox("Select a KPI", list(available_options.keys()), index=0)
    trend = filtered.groupby("month", as_index=False).agg(selected_kpi=(available_options[selected_kpi], "mean"))
    fig_trend = px.line(trend, x="month", y="selected_kpi", title="Monthly KPI Trend", markers=True)
    fig_trend.update_layout(height=360, margin=dict(l=10, r=10, t=50, b=20), xaxis_title="", yaxis_title="Selected KPI")
    st.plotly_chart(fig_trend, use_container_width=True)

colorful_decision_cards()

# -------------------------------------------------------------
# Dashboard 2: Patient Flow & Capacity Analytics
# -------------------------------------------------------------
st.divider()
st.markdown('<div class="main-title">Patient Flow & Capacity Analytics</div>', unsafe_allow_html=True)
st.markdown(
    """
    <div class="summary-box">
        <strong>Operational Summary:</strong> High-severity patients drive longer stays and increased readmission risk. Departments with elevated throughput times should be prioritized for workflow improvements.
    </div>
    """,
    unsafe_allow_html=True,
)

r1c1, r1c2, r1c3 = st.columns([1, 1, 1.55])

with r1c1:
    if "visit_outcome" in filtered.columns:
        outcome = filtered.groupby("visit_outcome", as_index=False).agg(
            patients=("patient_id", "nunique") if "patient_id" in filtered.columns else ("visit_outcome", "size")
        ).sort_values("patients", ascending=True)
        fig_outcome = px.bar(outcome, x="patients", y="visit_outcome", orientation="h", title="Visit Outcome", color_discrete_sequence=["#4f7fac"])
        fig_outcome.update_layout(height=330, margin=dict(l=10, r=10, t=50, b=10), xaxis_title="", yaxis_title="")
        st.plotly_chart(fig_outcome, use_container_width=True)

with r1c2:
    if "shift" in filtered.columns and "throughput_time_hours" in filtered.columns:
        throughput = filtered.groupby("shift", as_index=False).agg(throughput=("throughput_time_hours", "mean")).sort_values("throughput", ascending=False)
        fig_throughput = px.bar(throughput, x="shift", y="throughput", text="throughput", title="Throughput by Shift", color_discrete_sequence=["#4f7fac"])
        fig_throughput.update_traces(texttemplate="%{text:.1f}", textposition="outside")
        fig_throughput.update_layout(height=330, margin=dict(l=10, r=10, t=50, b=10), xaxis_title="", yaxis_title="")
        st.plotly_chart(fig_throughput, use_container_width=True)

with r1c3:
    if {"department", "month"}.issubset(filtered.columns):
        admissions = filtered.groupby(["department", "month"], as_index=False).agg(
            patients=("patient_id", "nunique") if "patient_id" in filtered.columns else ("department", "size")
        )
        fig_adm = px.density_heatmap(
            admissions,
            x="month",
            y="department",
            z="patients",
            histfunc="avg",
            text_auto=True,
            title="Admissions Trend",
            color_continuous_scale="Teal",
        )
        fig_adm.update_layout(height=330, margin=dict(l=10, r=10, t=50, b=10), xaxis_title="", yaxis_title="")
        st.plotly_chart(fig_adm, use_container_width=True)

r2c1, r2c2, r2c3 = st.columns([1, 1.25, 1.25])

with r2c1:
    if {"department", "treatment_success"}.issubset(filtered.columns):
        success = filtered.groupby("department", as_index=False).agg(success=("treatment_success", "mean")).sort_values("success", ascending=True)
        fig_success = px.bar(success, x="success", y="department", orientation="h", title="Treatment Success", text="success", color_discrete_sequence=["#4f7fac"])
        fig_success.update_traces(texttemplate="%{text:.1%}", textposition="outside")
        fig_success.update_layout(height=360, margin=dict(l=10, r=10, t=50, b=10), xaxis_title="", yaxis_title="")
        st.plotly_chart(fig_success, use_container_width=True)

with r2c2:
    if {"department", "severity_level", "length_of_stay_days"}.issubset(filtered.columns):
        los = filtered.groupby(["department", "severity_level"], as_index=False).agg(avg_los=("length_of_stay_days", "mean"))
        fig_los = px.density_heatmap(
            los,
            x="severity_level",
            y="department",
            z="avg_los",
            histfunc="avg",
            text_auto=".1f",
            title="LOS Analysis",
            color_continuous_scale="Teal",
        )
        fig_los.update_layout(height=360, margin=dict(l=10, r=10, t=50, b=10), xaxis_title="", yaxis_title="")
        st.plotly_chart(fig_los, use_container_width=True)

with r2c3:
    if {"department", "age_group", "readmitted_30_days"}.issubset(filtered.columns):
        readm = filtered.groupby(["department", "age_group"], as_index=False).agg(readmission=("readmitted_30_days", "mean"))
        fig_readm = px.density_heatmap(
            readm,
            x="age_group",
            y="department",
            z="readmission",
            histfunc="avg",
            text_auto=".1%",
            title="Readmission Risk",
            color_continuous_scale="Teal",
        )
        fig_readm.update_layout(height=360, margin=dict(l=10, r=10, t=50, b=10), xaxis_title="", yaxis_title="")
        st.plotly_chart(fig_readm, use_container_width=True)

colorful_decision_cards()
