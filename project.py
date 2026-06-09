import streamlit as st
import pandas as pd
import numpy as np
import pdfplumber
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(
    page_title="Palo Alto Networks Attrition Analytics",
    layout="wide"
)

st.title("Workforce Attrition Patterns & Risk Hotspot Analysis")
st.subheader("Palo Alto Networks HR Analytics Dashboard")

# Sidebar
st.sidebar.title("Upload Files")

data_file = st.sidebar.file_uploader(
    "Upload Employee Dataset",
    type=["csv", "xlsx"]
)

pdf_file = st.sidebar.file_uploader(
    "Upload HR PDF Report",
    type=["pdf"]
)

# PDF Reader
if pdf_file:

    st.header("PDF Report Preview")

    try:
        text = ""

        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                content = page.extract_text()
                if content:
                    text += content

        st.text_area(
            "Extracted Text",
            text[:5000],
            height=250
        )

    except Exception as e:
        st.error(f"PDF Error: {e}")

# Dataset Analysis
if data_file:

    try:

        if data_file.name.endswith(".csv"):
            df = pd.read_csv(data_file)
        else:
            df = pd.read_excel(data_file)

        st.success("Dataset Loaded Successfully")

        st.subheader("Dataset Preview")
        st.dataframe(df.head())

        total_emp = len(df)

        if "Attrition" in df.columns:
            left_emp = len(
                df[
                    df["Attrition"]
                    .astype(str)
                    .str.upper()
                    == "YES"
                ]
            )
        else:
            left_emp = 0

        attrition_rate = (
            left_emp / total_emp * 100
            if total_emp > 0
            else 0
        )

        c1, c2, c3 = st.columns(3)

        c1.metric("Total Employees", total_emp)
        c2.metric("Employees Left", left_emp)
        c3.metric("Attrition Rate", f"{attrition_rate:.2f}%")

        # Attrition Chart
        if "Attrition" in df.columns:

            st.subheader("Attrition Distribution")

            fig, ax = plt.subplots()

            sns.countplot(
                data=df,
                x="Attrition",
                palette="Set2",
                ax=ax
            )

            st.pyplot(fig)

        # Gender Pie Chart
        if "Gender" in df.columns:

            st.subheader("Gender Distribution")

            fig, ax = plt.subplots()

            df["Gender"].value_counts().plot.pie(
                autopct="%1.1f%%",
                ax=ax
            )

            ax.set_ylabel("")

            st.pyplot(fig)

        # Department Analysis
        if "Department" in df.columns:

            st.subheader("Department Wise Employees")

            dept = (
                df.groupby("Department")
                .size()
                .reset_index(name="Employees")
            )

            fig, ax = plt.subplots(figsize=(8,4))

            sns.barplot(
                data=dept,
                x="Department",
                y="Employees",
                palette="viridis",
                ax=ax
            )

            plt.xticks(rotation=45)

            st.pyplot(fig)

        # Age Distribution
        if "Age" in df.columns:

            st.subheader("Age Distribution")

            fig, ax = plt.subplots()

            sns.histplot(
                df["Age"],
                bins=20,
                kde=True,
                color="blue",
                ax=ax
            )

            st.pyplot(fig)

        # Years At Company
        if (
            "YearsAtCompany" in df.columns
            and "Attrition" in df.columns
        ):

            st.subheader(
                "Years At Company vs Attrition"
            )

            fig, ax = plt.subplots()

            sns.boxplot(
                data=df,
                x="Attrition",
                y="YearsAtCompany",
                palette="Set3",
                ax=ax
            )

            st.pyplot(fig)

        # Risk Hotspots
        if (
            "Department" in df.columns
            and "Attrition" in df.columns
        ):

            st.subheader(
                "Attrition Risk Hotspots"
            )

            risk = (
                df[
                    df["Attrition"]
                    .astype(str)
                    .str.upper()
                    == "YES"
                ]
                .groupby("Department")
                .size()
                .reset_index(name="RiskCount")
            )

            if len(risk) > 0:

                fig, ax = plt.subplots()

                sns.barplot(
                    data=risk,
                    x="Department",
                    y="RiskCount",
                    palette="Reds",
                    ax=ax
                )

                plt.xticks(rotation=45)

                st.pyplot(fig)

        # Correlation Heatmap
        numeric = df.select_dtypes(
            include=np.number
        )

        if len(numeric.columns) > 1:

            st.subheader(
                "Correlation Heatmap"
            )

            fig, ax = plt.subplots(
                figsize=(10,6)
            )

            sns.heatmap(
                numeric.corr(),
                annot=True,
                cmap="coolwarm",
                ax=ax
            )

            st.pyplot(fig)

        # Risk Score
        if "YearsAtCompany" in df.columns:

            st.subheader(
                "Employee Risk Score"
            )

            risk_df = pd.DataFrame()

            risk_df["YearsAtCompany"] = (
                df["YearsAtCompany"]
            )

            max_years = (
                df["YearsAtCompany"].max()
            )

            risk_df["RiskScore"] = (
                100
                - (
                    risk_df["YearsAtCompany"]
                    / max_years
                ) * 100
            )

            risk_df["RiskCategory"] = np.where(
                risk_df["RiskScore"] > 70,
                "High Risk",
                np.where(
                    risk_df["RiskScore"] > 40,
                    "Medium Risk",
                    "Low Risk"
                )
            )

            st.dataframe(
                risk_df.head(20)
            )

            fig, ax = plt.subplots()

            sns.countplot(
                data=risk_df,
                x="RiskCategory",
                palette="Set1",
                ax=ax
            )

            st.pyplot(fig)

        st.success(
            "Analysis Completed Successfully"
        )

    except Exception as e:

        st.error(
            f"Application Error: {e}"
        )

else:

    st.info(
        "Upload Employee Dataset (CSV/XLSX) and PDF Report to Start Analysis"
    )
