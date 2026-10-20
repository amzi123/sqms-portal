import streamlit as st
import pandas as pd

st.set_page_config(page_title="SQMS Supplier Portal", layout="wide")
st.markdown("""
<style>
.stApp { background-color: #0e2f4f; }
h1, h3, p, label, div[data-testid="stExpander"] { color: #e8f1f8 !important; }
div[data-testid="stMetric"] { background-color: #14395e; border: 1px solid #1e4a73; padding: 20px; border-radius: 12px; }
div[data-testid="stMetricValue"] { color: #2ee5c8 !important; }
</style>
""", unsafe_allow_html=True)

st.title("SQMS Supplier Portal - Food Safety Compliance")

# Your data + simulated uploads
suppliers = [
    {"supplier_distributor": "Savannah Fine Chemical (Pty) Ltd", "manufacturer": "AARTI INDUSTRIES LTD", "rm_code": 918861, "rm_description": "CAFFEINE ANHYDROUS", "origin_country": "IN", "vendor_code": 328628, "compliance": 92, "docs": ["FSSC 22000 Certificate.pdf", "COA - Caffeine.pdf", "Allergen Declaration.pdf"]},
    {"supplier_distributor": "CJP Chemicals (PTY) Ltd", "manufacturer": "DONGXIAO BIOTECHNOLOGY CO LTD", "rm_code": 956710, "rm_description": "PROTEA MALTODEXTRIN 20", "origin_country": "CN", "vendor_code": 328629, "compliance": 88, "docs": ["ISO 22000 Certificate.pdf", "Halal Certificate.pdf - PENDING"]},
    {"supplier_distributor": "CLIVE TEUBES (PTY) LTD.", "manufacturer": "CLIVE TEUBES (PTY) LTD.", "rm_code": 968192, "rm_description": "PROTEA OT ORANGE TERPENES", "origin_country": "ZA", "vendor_code": 300560, "compliance": 90, "docs": ["FSSC Certificate.pdf", "SDS - Orange Terpenes.pdf", "Origin Declaration.pdf"]},
]
df = pd.DataFrame(suppliers)

c1,c2,c3 = st.columns(3)
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
    filtered = filtered[filtered["compliance"] >= 70]
elif risk == "Red <70%":
    filtered = filtered[filtered["compliance"] < 70]

st.dataframe(filtered[["supplier_distributor","manufacturer","rm_code","rm_description","origin_country","vendor_code","compliance"]].assign(status=lambda x: x["compliance"].apply(lambda v: f"🟢 {v}%" if v>=90 else f"🟡 {v}%")), use_container_width=True, hide_index=True)

# --- THIS IS THE DROPDOWN YOU LOST - RESTORED ---
st.subheader("📁 Supplier Uploads - Click to View")
for idx, row in filtered.iterrows():
    status_icon = "🟢" if row["compliance"] >= 90 else "🟡"
    with st.expander(f"{status_icon} {row['supplier_distributor']} - {row['rm_description']} ({row['compliance']}%)"):
        colA, colB = st.columns(2)
        with colA:
            st.write(f"**Manufacturer:** {row['manufacturer']}")
            st.write(f"**RM Code:** {row['rm_code']}")
            st.write(f"**Origin:** {row['origin_country']}")
            st.write(f"**Vendor Code:** {row['vendor_code']}")
        with colB:
            st.write("**Uploaded Documents:**")
            for doc in row["docs"]:
                if "PENDING" in doc:
                    st.warning(f"⚠️ {doc}")
                else:
                    st.success(f"✅ {doc}")
        st.progress(row["compliance"]/100)

st.divider()
if st.toggle("🔒 Supplier Isolation Mode"):
    st.info("Isolation ON: Suppliers only see their own uploads")
