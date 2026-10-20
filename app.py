import streamlit as st
import pandas as pd

st.set_page_config(page_title="SQMS Supplier Portal", layout="wide")

st.markdown("""
<style>
.stApp { background-color: #0e2f4f; }
h1, h3, p, label { color: #e8f1f8 !important; }
div[data-testid="stMetric"] {
    background-color: #14395e;
    border: 1px solid #1e4a73;
    padding: 20px;
    border-radius: 12px;
}
div[data-testid="stMetricValue"] { color: #2ee5c8 !important; }
</style>
""", unsafe_allow_html=True)

st.title("SQMS Supplier Portal - Food Safety Compliance")

# Your 3 suppliers
df = pd.DataFrame([
    ["Savannah Fine Chemical (Pty) Ltd", "AARTI INDUSTRIES LTD", 918861, "CAFFEINE ANHYDROUS", "IN", 328628, 92],
    ["CJP Chemicals (PTY) Ltd", "DONGXIAO BIOTECHNOLOGY CO LTD", 956710, "PROTEA MALTODEXTRIN 20", "CN", 328629, 88],
    ["CLIVE TEUBES (PTY) LTD.", "CLIVE TEUBES (PTY) LTD.", 968192, "PROTEA OT ORANGE TERPENES", "ZA", 300560, 90],
], columns=["supplier_distributor", "manufacturer", "rm_code", "rm_description", "origin_country", "vendor_code", "compliance"])

c1, c2, c3 = st.columns(3)
c1.metric("Avg Compliance", "90%")
c2.metric("Approved", "2")
c3.metric("Pending", "1")

search = st.text_input("🔍 Search supplier, RM code, or description", "")
risk = st.selectbox("Filter by Risk", ["All", "Green ≥90%", "Yellow 70-89%", "Red <70%"])

filtered = df.copy()
if search:
    filtered = filtered[filtered["supplier_distributor"].str.contains(search, case=False) | filtered["rm_code"].astype(str).str.contains(search)]

if risk == "Green ≥90%":
    filtered = filtered[filtered["compliance"] >= 90]
elif risk == "Yellow 70-89%":
    filtered = filtered[(filtered["compliance"] >= 70) & (filtered["compliance"] < 90)]
elif risk == "Red <70%":
    filtered = filtered[filtered["compliance"] < 70]

# Add visual status without using styler - no error
filtered["status"] = filtered["compliance"].apply(lambda x: f"🟢 {x}%" if x >= 90 else f"🟡 {x}%")

st.dataframe(filtered, use_container_width=True, hide_index=True)

if st.toggle("🔒 Supplier Isolation Mode"):
    st.info("Isolation ON: Demo shows first row")
    st.dataframe(filtered.head(1), use_container_width=True, hide_index=True)
