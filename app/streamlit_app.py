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
        .section-title {
            color: #2f6fb3;
            font-size: 24px;
            font-weight: 700;
            margin-top: 0.7rem;
            margin-bottom: 0.35rem;
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
            min-height: 142px;
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

        /* Safety: hide accidental Plotly title placeholder if Plotly renders undefined */
        .js-plotly-plot .gtitle {
            display: none !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------------------------------------------
# Data Loading
# -------------------------------------------------------------
def candidate_paths() -> list[Path]:
    """Return likely CSV locations from both current working directory and script directory."""
    script_dir = Path(__file__).resolve().parent
    cwd = Path.cwd()
    names = [
        "data/healthcare_operations_cleaned.csv",
        "data/cleaned/healthcare_operations_cleaned.csv",
        "data/healthcare_operations_dashboard_950_rows_final.csv",
        "data/cleaned/healthcare_operations_dashboard_950_rows_final.csv",
        "healthcare_operations_cleaned.csv",
        "healthcare_operations_dashboard_950_rows_final.csv",
    ]
    paths: list[Path] = []
    for base in [cwd, script_dir, script_dir.parent]:
        for name in names:
            p = base / name
            if p not in paths:
                paths.append(p)
    return paths


@st.cache_data
def load_data() -> pd.DataFrame:
    data_path = next((p for p in candidate_paths() if p.exists()), None)
    if data_path is None:
        st.error(
            "Dataset not found. Place your CSV in one of these locations: "
            "`data/healthcare_operations_cleaned.csv`, "
            "`data/cleaned/healthcare_operations_cleaned.csv`, or "
            "`data/healthcare_operations_dashboard_950_rows_final.csv`."
        )
        with st.expander("Show paths Streamlit checked"):
            for p in candidate_paths():
                st.write(str(p))
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

    numeric_cols = [
        "length_of_stay_days", "bed_occupancy_rate", "er_wait_time_minutes",
        "throughput_time_hours", "patient_satisfaction_score", "capacity_strain_score",
        "readmitted_30_days", "treatment_success", "appointment_completed", "no_show",
        "target_bed_occupancy_rate", "target_er_wait_time",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Support either 0-1 or 0-100 rates consistently.
    for col in ["bed_occupancy_rate", "target_bed_occupancy_rate"]:
        if col in df.columns and df[col].dropna().max() <= 1.5:
            df[col] = df[col] * 100

    return df


# -------------------------------------------------------------
# Helper Functions
# -------------------------------------------------------------
def pct(value: float, digits: int = 2) -> str:
    if pd.isna(value):
        return f"{0:.{digits}f}%"
    return f"{value * 100:.{digits}f}%" if value <= 1.5 else f"{value:.{digits}f}%"


def number(value: float, digits: int = 2) -> str:
    if pd.isna(value):
        return f"{0:.{digits}f}"
    return f"{value:.{digits}f}"


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
    strain = row.get("capacity_strain_score", 0) or 0
    occupancy = row.get("bed_occupancy_rate", 0) or 0
    wait = row.get("er_wait_time_minutes", 0) or 0
    if strain >= 75 or occupancy >= 90 or wait >= 60:
        return "High Risk"
    if strain >= 60 or occupancy >= 80 or wait >= 45:
        return "Moderate Risk"
    return "Stable"


def standardize_bottleneck_reason(value: object) -> str:
    """Group operational bottleneck labels into the 7 clean dashboard categories requested."""
    if pd.isna(value):
        return "No Bottleneck"

    raw = str(value).strip()
    text = raw.lower().replace("_", " ").replace("-", " ")

    # Keep already-clean labels stable.
    clean_labels = {
        "high resource": "High Resource",
        "long los": "Long LOS",
        "extended wait time": "Extended Wait Time",
        "bed occupancy": "Bed Occupancy",
        "high long los": "High Long LOS",
        "no bottleneck": "No Bottleneck",
        "readmission pressure": "Readmission Pressure",
    }
    if text in clean_labels:
        return clean_labels[text]

    if any(term in text for term in ["no bottleneck", "none", "stable", "normal", "no issue"]):
        return "No Bottleneck"
    if "readmission" in text:
        return "Readmission Pressure"
    if ("high" in text and ("los" in text or "length of stay" in text)) or "extended los" in text:
        return "High Long LOS"
    if "los" in text or "length of stay" in text:
        return "Long LOS"
    if "wait" in text or "delay" in text or "er" in text or "ed" in text:
        return "Extended Wait Time"
    if "occupancy" in text or "bed" in text or "capacity" in text:
        return "Bed Occupancy"
    if "resource" in text or "staff" in text or "strain" in text or "utilization" in text:
        return "High Resource"

    # Any unexpected legacy value is still grouped so the chart never grows beyond 7 categories.
    return "High Resource"



def build_exclusive_bottleneck_categories(df: pd.DataFrame) -> pd.Series:
    """
    Build one mutually exclusive bottleneck category per row.
    This keeps the Operational Bottlenecks chart total equal to the filtered record count.
    It also allows No Bottleneck and Bed Occupancy to appear without double-counting rows.
    """
    categories = df["bottleneck_reason"].apply(standardize_bottleneck_reason).copy()

    low_risk_conditions = []
    if "capacity_strain_score" in df.columns:
        low_risk_conditions.append(df["capacity_strain_score"].fillna(0) < 60)
    if "bed_occupancy_rate" in df.columns:
        low_risk_conditions.append(df["bed_occupancy_rate"].fillna(0) < 80)
    if "er_wait_time_minutes" in df.columns:
        low_risk_conditions.append(df["er_wait_time_minutes"].fillna(0) < 45)

    if low_risk_conditions:
        low_risk_mask = low_risk_conditions[0]
        for condition in low_risk_conditions[1:]:
            low_risk_mask = low_risk_mask & condition
        categories.loc[low_risk_mask] = "No Bottleneck"

    if "bed_occupancy_rate" in df.columns:
        bed_mask = (df["bed_occupancy_rate"].fillna(0) >= 85) & (categories != "No Bottleneck")
        categories.loc[bed_mask] = "Bed Occupancy"

    return categories


def colorful_decision_cards():
    st.divider()
    st.markdown('<div class="section-title">Executive Decision Summary</div>', unsafe_allow_html=True)
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


def chart_layout(fig, height=430):
    fig.update_layout(
        height=height,
        margin=dict(l=10, r=10, t=55, b=20),
        font=dict(size=12),
        title_font=dict(size=22, color="#2f6fb3"),
    )
    return fig


def clean_title(title: str):
    """Use Plotly title only; Streamlit section headers are intentionally not duplicated."""
    return title


def top_n_with_other(df: pd.DataFrame, label_col: str, value_col: str, n: int = 6) -> pd.DataFrame:
    """Return the top N categories and group the rest as Other, keeping the final chart clean."""
    if df.empty or label_col not in df.columns or value_col not in df.columns:
        return df
    ordered = df.sort_values(value_col, ascending=False).copy()
    top = ordered.head(n).copy()
    rest = ordered.iloc[n:]
    if not rest.empty:
        other = pd.DataFrame([{label_col: "Other", value_col: rest[value_col].sum()}])
        top = pd.concat([top, other], ignore_index=True)
    return top.sort_values(value_col, ascending=True)


def add_top_x_axis(fig):
    """Move heatmap column headers to the top for better readability."""
    fig.update_xaxes(side="top")
    fig.update_layout(margin=dict(l=10, r=10, t=80, b=25))
    return fig


# -------------------------------------------------------------
# Load + Filter Data
# -------------------------------------------------------------
df = load_data()
filtered = apply_filters(df)
show_empty_warning(filtered)

# -------------------------------------------------------------
# Dashboard Header
# -------------------------------------------------------------
st.markdown('<div class="main-title">Hospital Operations Executive Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Operational Performance, Capacity Risk & Patient Flow Monitoring</div>', unsafe_allow_html=True)
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
    add_metric_card("Avg<br>LOS", number(mean_or_zero(filtered, "length_of_stay_days")))
with kpi_cols[2]:
    add_metric_card("Bed<br>Occupancy", pct(mean_or_zero(filtered, "bed_occupancy_rate")))
with kpi_cols[3]:
    add_metric_card("Readmission<br>Rate", pct(mean_or_zero(filtered, "readmitted_30_days")))
with kpi_cols[4]:
    add_metric_card("Avg ER Wait<br>Time", number(mean_or_zero(filtered, "er_wait_time_minutes")))
with kpi_cols[5]:
    add_metric_card("Treatment Success<br>Rate", pct(mean_or_zero(filtered, "treatment_success")))
with kpi_cols[6]:
    add_metric_card("Patient<br>Satisfaction", number(mean_or_zero(filtered, "patient_satisfaction_score")))

st.divider()

# -------------------------------------------------------------
# Dashboard 1: Supporting Visuals
# Small charts can stay two per row.
# Large/important visuals are standalone.
# -------------------------------------------------------------
st.markdown('<div class="section-title">Hospital Alerts & Bottlenecks</div>', unsafe_allow_html=True)

# Full-width alert chart for a cleaner executive view.
if "department" in filtered.columns:
    alert_df = filtered.copy()
    alert_df["hospital_alert"] = alert_df.apply(create_alert_flag, axis=1)
    alert_summary = alert_df.groupby(["department", "hospital_alert"], as_index=False).agg(
        patients=("patient_id", "nunique") if "patient_id" in alert_df.columns else ("department", "size")
    )
    dept_order = (
        alert_summary.groupby("department")["patients"]
        .sum()
        .sort_values(ascending=True)
        .index.tolist()
    )
    fig_alert = px.bar(
        alert_summary,
        x="patients",
        y="department",
        color="hospital_alert",
        orientation="h",
        title="Hospital Alert Summary",
        text="patients",
        category_orders={
            "department": dept_order,
            "hospital_alert": ["High Risk", "Moderate Risk", "Stable"],
        },
        color_discrete_map={"High Risk": "#2b5c8a", "Moderate Risk": "#49a6b8", "Stable": "#a7d8d4"},
    )
    fig_alert.update_traces(textposition="outside", cliponaxis=False)
    fig_alert.update_layout(
        yaxis_title="",
        xaxis_title="Patients",
        legend_title="Alert Level",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    st.plotly_chart(chart_layout(fig_alert, 500), use_container_width=True)

# Clean 7-category bottleneck chart using the requested names only.
if "bottleneck_reason" in filtered.columns:
    bottleneck_order = [
        "High Resource",
        "Long LOS",
        "Extended Wait Time",
        "Bed Occupancy",
        "High Long LOS",
        "No Bottleneck",
        "Readmission Pressure",
    ]
    bottleneck_df = filtered.copy()
    bottleneck_df["bottleneck_reason_clean"] = build_exclusive_bottleneck_categories(bottleneck_df)
    bottlenecks = (
        bottleneck_df.groupby("bottleneck_reason_clean", as_index=False)
        .size()
        .rename(columns={"size": "count"})
    )
    bottlenecks = (
        pd.DataFrame({"bottleneck_reason_clean": bottleneck_order})
        .merge(bottlenecks, on="bottleneck_reason_clean", how="left")
        .fillna({"count": 0})
    )
    bottlenecks["count"] = bottlenecks["count"].astype(int)
    bottlenecks = bottlenecks.sort_values("count", ascending=True)

    fig_bottleneck = px.bar(
        bottlenecks,
        x="count",
        y="bottleneck_reason_clean",
        orientation="h",
        title="Operational Bottlenecks",
        text="count",
        color_discrete_sequence=["#008c8c"],
    )
    fig_bottleneck.update_traces(textposition="outside", cliponaxis=False, marker_color="#008c8c", showlegend=False)
    fig_bottleneck.update_layout(yaxis_title="", xaxis_title="Cases")
    st.plotly_chart(chart_layout(fig_bottleneck, 470), use_container_width=True)

# Standalone: Capacity Strain Heatmap
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
    fig_heat.update_layout(xaxis_title="", yaxis_title="Department")
    st.plotly_chart(chart_layout(fig_heat, 520), use_container_width=True)

# Standalone: Department Performance Matrix
required = {"department", "bed_occupancy_rate", "length_of_stay_days", "er_wait_time_minutes", "patient_satisfaction_score", "readmitted_30_days"}
if required.issubset(filtered.columns):
    matrix = filtered.groupby("department", as_index=False).agg(
        Occupancy=("bed_occupancy_rate", "mean"),
        LOS=("length_of_stay_days", "mean"),
        Wait_Time=("er_wait_time_minutes", "mean"),
        Satisfaction=("patient_satisfaction_score", "mean"),
        Readmission=("readmitted_30_days", "mean"),
    )
    matrix["Readmission"] = matrix["Readmission"] * 100 if matrix["Readmission"].max() <= 1.5 else matrix["Readmission"]
    matrix = matrix.sort_values("department")
    kpis = ["Occupancy", "LOS", "Wait_Time", "Satisfaction", "Readmission"]
    labels = ["Occupancy", "LOS", "Wait Time", "Satisfaction", "Readmission"]
    z_values = matrix[kpis].round(2).values
    text_values = [[f"{val:.2f}" for val in row] for row in z_values]
    fig_matrix = go.Figure(
        data=go.Heatmap(
            z=z_values,
            x=labels,
            y=matrix["department"],
            text=text_values,
            texttemplate="%{text}",
            colorscale="Teal",
            colorbar=dict(title="Value"),
            hovertemplate="Department=%{y}<br>KPI=%{x}<br>Value=%{z:.2f}<extra></extra>",
        )
    )
    fig_matrix.update_layout(title="Department Performance Matrix", xaxis_title="", yaxis_title="Department")
    st.plotly_chart(add_top_x_axis(chart_layout(fig_matrix, 540)), use_container_width=True)

# Standalone: Monthly KPI Trend
st.markdown('<div class="section-title">Monthly KPI Trend</div>', unsafe_allow_html=True)
kpi_options = {
    "Readmission": "readmitted_30_days",
    "LOS": "length_of_stay_days",
    "Wait Time": "er_wait_time_minutes",
    "Satisfaction": "patient_satisfaction_score",
    "Occupancy": "bed_occupancy_rate",
    "Treatment Success": "treatment_success",
}
available_options = {k: v for k, v in kpi_options.items() if v in filtered.columns}
selected_kpi = st.selectbox("Select a KPI", list(available_options.keys()), index=0)
trend = filtered.groupby("month", as_index=False).agg(selected_kpi=(available_options[selected_kpi], "mean"))
if selected_kpi in ["Readmission", "Treatment Success"]:
    trend["selected_kpi"] = trend["selected_kpi"] * 100 if trend["selected_kpi"].max() <= 1.5 else trend["selected_kpi"]
# Build the Monthly KPI chart without any Plotly title placeholder.
# This removes the unwanted "undefined" word under the KPI selector.
fig_trend = go.Figure()
fig_trend.add_trace(
    go.Scatter(
        x=trend["month"],
        y=trend["selected_kpi"],
        mode="lines+markers",
        hovertemplate="Month=%{x}<br>Value=%{y:.2f}<extra></extra>",
        name="",
        showlegend=False,
    )
)
fig_trend.update_layout(
    title=dict(text=""),
    showlegend=False,
    xaxis_title="",
    yaxis_title=selected_kpi,
    margin=dict(l=10, r=10, t=8, b=20),
    height=500,
    font=dict(size=12),
)
fig_trend.update_annotations(text="")
st.plotly_chart(fig_trend, use_container_width=True)

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

# Smaller charts can stay two per row.
r1c1, r1c2 = st.columns(2)
with r1c1:
    if "visit_outcome" in filtered.columns:
        outcome = filtered.groupby("visit_outcome", as_index=False).agg(
            patients=("patient_id", "nunique") if "patient_id" in filtered.columns else ("visit_outcome", "size")
        ).sort_values("patients", ascending=True)
        fig_outcome = px.bar(
            outcome,
            x="patients",
            y="visit_outcome",
            orientation="h",
            title="Visit Outcome",
            text="patients",
            color_discrete_sequence=["#4f7fac"],
        )
        fig_outcome.update_layout(xaxis_title="", yaxis_title="")
        st.plotly_chart(chart_layout(fig_outcome, 420), use_container_width=True)

with r1c2:
    if "shift" in filtered.columns and "throughput_time_hours" in filtered.columns:
        throughput = filtered.groupby("shift", as_index=False).agg(
            throughput=("throughput_time_hours", "mean")
        ).sort_values("throughput", ascending=False)
        fig_throughput = px.bar(
            throughput,
            x="shift",
            y="throughput",
            text="throughput",
            title="Throughput by Shift",
            color_discrete_sequence=["#4f7fac"],
        )
        fig_throughput.update_traces(texttemplate="%{text:.2f}", textposition="outside")
        fig_throughput.update_layout(xaxis_title="", yaxis_title="Avg Throughput Hours")
        st.plotly_chart(chart_layout(fig_throughput, 420), use_container_width=True)

# Standalone: Admissions Trend
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
        text_auto=".0f",
        title="Admissions Trend",
        color_continuous_scale="Teal",
    )
    fig_adm.update_traces(texttemplate="%{z:.0f}", hovertemplate="Month=%{x}<br>Department=%{y}<br>Patients=%{z:.0f}<extra></extra>")
    fig_adm.update_layout(xaxis_title="", yaxis_title="Department")
    st.plotly_chart(add_top_x_axis(chart_layout(fig_adm, 540)), use_container_width=True)

# Remaining detailed charts. Treatment Success stays compact; LOS Analysis stands alone.
if {"department", "treatment_success"}.issubset(filtered.columns):
    success = filtered.groupby("department", as_index=False).agg(
        success=("treatment_success", "mean")
    ).sort_values("success", ascending=True)
    success["success_pct"] = success["success"] * 100 if success["success"].max() <= 1.5 else success["success"]
    fig_success = px.bar(
        success,
        x="success_pct",
        y="department",
        orientation="h",
        title="Treatment Success",
        text="success_pct",
        color_discrete_sequence=["#4f7fac"],
    )
    fig_success.update_traces(texttemplate="%{text:.2f}%", textposition="outside", cliponaxis=False)
    fig_success.update_layout(
        xaxis_title="Treatment Success Rate",
        yaxis_title="",
        xaxis=dict(range=[0, max(105, float(success["success_pct"].max()) + 8)]),
        margin=dict(l=10, r=80, t=55, b=20),
    )
    st.plotly_chart(chart_layout(fig_success, 460), use_container_width=True)

if {"department", "severity_level", "length_of_stay_days"}.issubset(filtered.columns):
    los = filtered.groupby(["department", "severity_level"], as_index=False).agg(
        avg_los=("length_of_stay_days", "mean")
    )
    fig_los = px.density_heatmap(
        los,
        x="severity_level",
        y="department",
        z="avg_los",
        histfunc="avg",
        text_auto=".2f",
        title="LOS Analysis",
        color_continuous_scale="Teal",
    )
    fig_los.update_traces(texttemplate="%{z:.2f}", hovertemplate="Severity=%{x}<br>Department=%{y}<br>Avg LOS=%{z:.2f}<extra></extra>")
    fig_los.update_layout(xaxis_title="Severity Level", yaxis_title="Department")
    st.plotly_chart(add_top_x_axis(chart_layout(fig_los, 540)), use_container_width=True)

# Readmission Risk can stay full width for readability.
if {"department", "age_group", "readmitted_30_days"}.issubset(filtered.columns):
    readm = filtered.groupby(["department", "age_group"], as_index=False).agg(
        readmission=("readmitted_30_days", "mean")
    )
    readm["readmission_pct"] = readm["readmission"] * 100 if readm["readmission"].max() <= 1.5 else readm["readmission"]
    fig_readm = px.density_heatmap(
        readm,
        x="age_group",
        y="department",
        z="readmission_pct",
        histfunc="avg",
        text_auto=".2f",
        title="Readmission Risk",
        color_continuous_scale="Teal",
    )
    fig_readm.update_traces(texttemplate="%{z:.2f}%", hovertemplate="Age Group=%{x}<br>Department=%{y}<br>Readmission=%{z:.2f}%<extra></extra>")
    fig_readm.update_layout(xaxis_title="Age Group", yaxis_title="Department")
    st.plotly_chart(add_top_x_axis(chart_layout(fig_readm, 540)), use_container_width=True)

# Executive Decision Summary appears ONCE only, at the bottom.
colorful_decision_cards()
