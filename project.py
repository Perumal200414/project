import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Attrition Analytics",
    layout="wide"
)

st.title("Workforce Attrition Analytics Dashboard")

file = st.file_uploader(
    "Upload Employee Dataset",
    type=["csv", "xlsx"]
)

if file:

    if file.name.endswith(".csv"):
        df = pd.read_csv(file)
    else:
        df = pd.read_excel(file)

    st.success("Dataset Loaded Successfully")

    st.dataframe(df.head())

    total = len(df)

    if "Attrition" in df.columns:
        left = len(
            df[
                df["Attrition"]
                .astype(str)
                .str.upper()
                == "YES"
            ]
        )
    else:
        left = 0

    rate = (
        left / total * 100
        if total > 0
        else 0
    )

    c1, c2, c3 = st.columns(3)

    c1.metric("Total Employees", total)
    c2.metric("Employees Left", left)
    c3.metric("Attrition Rate", f"{rate:.2f}%")

    if "Attrition" in df.columns:

        fig, ax = plt.subplots()

        df["Attrition"].value_counts().plot(
            kind="bar",
            ax=ax,
            color=["green", "red"]
        )

        ax.set_title("Attrition Distribution")

        st.pyplot(fig)

else:
    st.info("Upload a CSV or Excel file.")
