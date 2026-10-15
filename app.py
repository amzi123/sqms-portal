import streamlit as st
import pandas as pd

st.set_page_config(page_title="SQMS Dashboard", layout="wide")
st.title("✅ SQMS Supplier Compliance Dashboard")

try:
    df = pd.read_csv("SQMS_data.csv")
    # Fix if Excel saved all data in one column
    if len(df.columns) == 1:
        df = pd.read_csv("SQMS_data.csv", sep=',', engine='python')
except FileNotFoundError:
    st.warning("SQMS_data.csv not found, trying supplier_compliance.csv")
    df = pd.read_csv("supplier_compliance.csv")

st.success(f"Loaded {len(df)} records")

st.subheader("Supplier Records")
md_table = "| Supplier | Score | Status | Last Audit |\n"
md_table += "|---|---|---|---|\n"
for _, row in df.iterrows():
    md_table += f"| {row['Supplier']} | {row['Compliance Score']} | {row['Status']} | {row['Last Audit']} |\n"
st.markdown(md_table)

st.subheader("Summary")
st.write(f"Average Compliance Score: {df['Compliance Score'].mean():.1f}")
st.write("---")
for _, row in df.iterrows():
    st.write(f"**{row['Supplier']}**: {row['Compliance Score']} - {row['Status']}")
