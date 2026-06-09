import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pdfplumber
import numpy as np

# -----------------------------------
# PAGE CONFIG
# -----------------------------------

st.set_page_config(
    page_title="Palo Alto Networks - Attrition Analytics",
    layout="wide"
)

# -----------------------------------
# CUSTOM CSS
# -----------------------------------

st.markdown("""
<style>
.main {
    background-color: #f5f7fa;
}

.kpi-card {
    background: white;
    padding: 15px;
    border-radius: 12px;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.08);
    text-align:center;
}

.title {
    color:#0B3D91;
    font-size:40px;
    font-weight:bold;
}

.subtitle{
    color:#666;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------------
# HEADER
# -----------------------------------

st.markdown(
    "<div class='title'>Workforce Attrition Patterns & Risk Hotspot Analysis</div>",
    unsafe_allow_html=True
)

st.markdown(
    "<div class='subtitle'>Palo Alto Networks HR Analytics Dashboard</div>",
    unsafe_allow_html=True
)

st.markdown("---")

# -----------------------------------
# SIDEBAR
# -----------------------------------

st.sidebar.title("Upload Files")

data_file = st.sidebar.file_uploader(
    "Upload Employee Dataset",
    type=["csv", "xlsx"]
)

pdf_file = st.sidebar.file_uploader(
    "Upload HR PDF Report",
    type=["pdf"]
)

# -----------------------------------
# FLOWCHART
# -----------------------------------

with st.expander(" Project Workflow Flowchart", expanded=True):

    st.code("""
    Employee Data + PDF Report
                │
                ▼
      Data Cleaning & Validation
                │
                ▼
      Workforce Attrition Analysis
                │
      ┌─────────┼─────────┐
      ▼         ▼         ▼
 Department  Gender   Experience
 Analysis    Analysis Analysis
      │         │         │
      └──────┬──┴──┬──────┘
             ▼
      Risk Hotspot Detection
             ▼
      Dashboard Visualization
             ▼
      Employee Risk Scoring
    """)

# -----------------------------------
# PDF VIEWER
# -----------------------------------

if pdf_file:

    st.header(" Uploaded PDF Report")

    text = ""

    try:
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"

        st.text_area(
            "PDF Content Preview",
            text[:8000],
            height=300
        )

    except:
        st.warning("Unable to read PDF")

# -----------------------------------
# DATASET ANALYSIS
# -----------------------------------

if data_file:

    try:

        if data_file.name.endswith(".csv"):
            df = pd.read_csv(data_file)
        else:
            df = pd.read_excel(data_file)

        st.success("Dataset Loaded Successfully")

        st.subheader("Dataset Preview")
        st.dataframe(df.head())

        # -----------------------------
        # KPIs
        # -----------------------------

        total_emp = len(df)

        if "Attrition" in df.columns:

            attrition_emp = len(
                df[df["Attrition"].astype(str).str.upper() == "YES"]
            )

            attrition_rate = (
                attrition_emp / total_emp * 100
            )

        else:
            attrition_emp = 0
            attrition_rate = 0

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Total Employees",
            f"{total_emp:,}"
        )

        c2.metric(
            "Employees Left",
            attrition_emp
        )

        c3.metric(
            "Attrition Rate",
            f"{attrition_rate:.2f}%"
        )

        st.markdown("---")

        # -----------------------------
        # CHARTS
        # -----------------------------

        col1, col2 = st.columns(2)

        # Attrition Chart
        if "Attrition" in df.columns:

            fig = px.histogram(
                df,
                x="Attrition",
                color="Attrition",
                title="Attrition Distribution"
            )

            col1.plotly_chart(
                fig,
                use_container_width=True
            )

        # Gender Chart
        if "Gender" in df.columns:

            fig = px.pie(
                df,
                names="Gender",
                title="Gender Distribution"
            )

            col2.plotly_chart(
                fig,
                use_container_width=True
            )

        # -----------------------------
        # DEPARTMENT ANALYSIS
        # -----------------------------

        if "Department" in df.columns:

            dept = (
                df.groupby("Department")
                .size()
                .reset_index(name="Employees")
            )

            fig = px.bar(
                dept,
                x="Department",
                y="Employees",
                color="Department",
                title="Department Wise Employees"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        # -----------------------------
        # AGE ANALYSIS
        # -----------------------------

        if "Age" in df.columns:

            fig = px.histogram(
                df,
                x="Age",
                nbins=20,
                color_discrete_sequence=["#0B3D91"],
                title="Age Distribution"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        # -----------------------------
        # EXPERIENCE ANALYSIS
        # -----------------------------

        if (
            "YearsAtCompany" in df.columns
            and "Attrition" in df.columns
        ):

            fig = px.box(
                df,
                x="Attrition",
                y="YearsAtCompany",
                color="Attrition",
                title="Years At Company vs Attrition"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        # -----------------------------
        # RISK HOTSPOTS
        # -----------------------------

        if (
            "Department" in df.columns
            and "Attrition" in df.columns
        ):

            risk = (
                df[
                    df["Attrition"]
                    .astype(str)
                    .str.upper() == "YES"
                ]
                .groupby("Department")
                .size()
                .reset_index(name="RiskCount")
            )

            if len(risk) > 0:

                fig = px.treemap(
                    risk,
                    path=["Department"],
                    values="RiskCount",
                    color="RiskCount",
                    title=" Attrition Risk Hotspots"
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

        # -----------------------------
        # HEATMAP
        # -----------------------------

        st.subheader("Correlation Heatmap")

        numeric = df.select_dtypes(
            include=np.number
        )

        if len(numeric.columns) > 1:

            corr = numeric.corr()

            fig = px.imshow(
                corr,
                text_auto=True,
                color_continuous_scale="RdBu_r"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        # -----------------------------
        # RISK SCORE MODEL
        # -----------------------------

        st.subheader("Employee Risk Score")

        risk_score = pd.DataFrame()

        if "YearsAtCompany" in df.columns:

            risk_score["YearsAtCompany"] = df["YearsAtCompany"]

            risk_score["RiskScore"] = (
                100 -
                (
                    risk_score["YearsAtCompany"]
                    /
                    risk_score["YearsAtCompany"].max()
                ) * 100
            )

            risk_score["RiskCategory"] = np.where(
                risk_score["RiskScore"] > 70,
                "High Risk",
                np.where(
                    risk_score["RiskScore"] > 40,
                    "Medium Risk",
                    "Low Risk"
                )
            )

            st.dataframe(
                risk_score.head(20)
            )

            fig = px.histogram(
                risk_score,
                x="RiskCategory",
                color="RiskCategory",
                title="Employee Risk Categories"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        # -----------------------------
        # SUMMARY
        # -----------------------------

        st.success(
            "Analysis Completed Successfully"
        )

    except Exception as e:

        st.error(f"Error: {e}")

else:

    st.info(
        "Upload Employee Dataset (CSV/XLSX) and PDF Report to start analysis."
    )