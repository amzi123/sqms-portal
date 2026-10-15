import streamlit as st
import pandas as pd

st.set_page_config(page_title="SQMS Dashboard", layout="wide")
st.title("✅ SQMS Supplier Compliance Dashboard")

df = pd.read_csv("SQMS_data.csv")
st.success(f"Loaded {len(df)} records")

st.subheader("Supplier Records")
# Build a simple markdown table that tunnel can't break
md_table = "| Supplier | Score | Status | Last Audit |\n"
md_table += "|---|---|---|---|\n"
for _, row in df.iterrows():
    md_table += f"| {row['Supplier']} | {row['Compliance Score']} | {row['Status']} | {row['Last Audit']} |\n"
st.markdown(md_table)

st.subheader("Summary")
st.write(f"Average Compliance Score: {df['Compliance Score'].mean():.1f}")
st.write("---")
for _, row in df.iterrows():
    st.write(f"**{row['Supplier']}**: {row['Compliance Score']} — {row['Status']}")
