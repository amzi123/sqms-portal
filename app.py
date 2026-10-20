import streamlit as st
import pandas as pd

st.set_page_config(page_title="SQMS Supplier Portal", layout="wide")
st.markdown("""
<style>
.stApp { background-color: #0e2f4f; }
h1, h2, h3, p, label { color: #e8f1f8 !important; }
div[data-testid="stMetric"] { background-color: #14395e; border: 1px solid #1e4a73; padding: 20px; border-radius: 12px; }
div[data-testid="stMetricValue"] { color: #2ee5c8 !important; }
</style>
""", unsafe_allow_html=True)

st.title("SQMS Supplier Portal - Food Safety Compliance")

suppliers = [
    {"supplier_distributor": "Savannah Fine Chemical (Pty) Ltd", "manufacturer": "AARTI INDUSTRIES LTD", "rm_code": 918861, "rm_description": "CAFFEINE ANHYDROUS", "origin_country": "IN", "vendor_code": 328628, "compliance": 92, "docs": ["FSSC 22000 Certificate.pdf", "COA - Caffeine.pdf", "Allergen Declaration.pdf"], "gfs": "FSSC 22000", "halal": "Yes", "shelf_life": "36 months"},
    {"supplier_distributor": "CJP Chemicals (PTY) Ltd", "manufacturer": "DONGXIAO BIOTECHNOLOGY CO LTD", "rm_code": 956710, "rm_description": "PROTEA MALTODEXTRIN 20", "origin_country": "CN", "vendor_code": 328629, "compliance": 88, "docs": ["ISO 22000 Certificate.pdf"], "gfs": "ISO 22000", "halal": "Pending", "shelf_life": "24 months"},
    {"supplier_distributor": "CLIVE TEUBES (PTY) LTD.", "manufacturer": "CLIVE TEUBES (PTY) LTD.", "rm_code": 968192, "rm_description": "PROTEA OT ORANGE TERPENES", "origin_country": "ZA", "vendor_code": 300560, "compliance": 90, "docs": ["FSSC Certificate.pdf", "SDS - Orange Terpenes.pdf"], "gfs": "FSSC 22000", "halal": "N/A", "shelf_life": "18 months"},
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

# --- FULL RESTORE WITH QUESTIONNAIRES + PRODUCT INFO FORM ---
st.subheader("📁 Supplier Uploads - Click to View")

for idx, row in filtered.iterrows():
    status_icon = "🟢" if row["compliance"] >= 90 else "🟡"
    with st.expander(f"{status_icon} {row['supplier_distributor']} - {row['rm_description']} ({row['compliance']}%)"):
        
        tab1, tab2, tab3 = st.tabs(["📄 Uploaded Documents", "📋 Questionnaire", "🧾 Product Information Form"])
        
        with tab1:
            colA, colB = st.columns(2)
            with colA:
                st.write(f"**Manufacturer:** {row['manufacturer']}")
                st.write(f"**RM Code:** {row['rm_code']}")
                st.write(f"**Origin:** {row['origin_country']}")
                st.write(f"**Vendor Code:** {row['vendor_code']}")
            with colB:
                st.write("**Uploaded Documents:**")
                for doc in row["docs"]:
                    st.success(f"✅ {doc}")
            st.progress(row["compliance"]/100)
        
        with tab2:
            st.write("**Food Safety Questionnaire**")
            st.checkbox("Is your facility GFSI certified?", value=True, key=f"gfs_{row['rm_code']}")
            st.checkbox("Do you have a HACCP plan?", value=True, key=f"haccp_{row['rm_code']}")
            st.checkbox("Allergen management program in place?", value=True, key=f"allergen_{row['rm_code']}")
            st.selectbox("GFSI Scheme", [row["gfs"], "BRCGS", "IFS", "SQF"], key=f"scheme_{row['rm_code']}")
            st.text_area("Describe your traceability system", "Batch traceability from RM to FG in 4 hours", key=f"trace_{row['rm_code']}")
            st.file_uploader("Upload completed questionnaire", key=f"q_up_{row['rm_code']}")
        
        with tab3:
            st.write("**Product Information Form (PIF)**")
            c1,c2 = st.columns(2)
            c1.text_input("Product Name", row["rm_description"], key=f"pname_{row['rm_code']}")
            c1.text_input("Shelf Life", row["shelf_life"], key=f"shelf_{row['rm_code']}")
            c1.selectbox("Halal Certified", [row["halal"], "Yes", "No", "N/A"], key=f"halal_{row['rm_code']}")
            c2.text_input("Manufacturer", row["manufacturer"], key=f"mfg_{row['rm_code']}")
            c2.text_input("Country of Origin", row["origin_country"], key=f"origin_{row['rm_code']}")
            c2.text_input("Storage Conditions", "Store in cool, dry place <25°C", key=f"store_{row['rm_code']}")
            st.text_area("Composition / Ingredients", "100% Caffeine Anhydrous - CAS 58-08-2", key=f"comp_{row['rm_code']}")
            st.file_uploader("Upload PIF / SDS / Spec", key=f"pif_up_{row['rm_code']}")
            if st.button("Submit PIF", key=f"submit_{row['rm_code']}"):
                st.success("PIF submitted!")

st.divider()
if st.toggle("🔒 Supplier Isolation Mode"):
    st.info("Isolation ON")
