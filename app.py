import streamlit as st
import pandas as pd

st.set_page_config(page_title="SQMS Portal", layout="wide")
st.title("📊 Supplier Document Portal - Food Safety")

@st.cache_data
def load_data():
    try:
        df = pd.read_csv("supplier_compliance.csv")
        return df
    except Exception as e:
        st.error(f"Could not load CSV: {e}")
        return None

df = load_data()
if df is None:
    st.stop()

# Reorder: Supplier & Manufacturer FIRST
priority_cols = ["supplier_distributor", "manufacturer", "rm_code", "rm_description", "origin_country", "vendor_code", "mfg_code"]
other_cols = [c for c in df.columns if c not in priority_cols]
ordered_cols = [c for c in priority_cols if c in df.columns] + other_cols
df_ordered = df[ordered_cols]

role = st.sidebar.selectbox("You are:", ["SQMS View", "Supplier Upload"])
st.sidebar.metric("Total RM", len(df))

if role == "SQMS View":
    st.subheader(f"SQMS Compliance Dashboard - {len(df)} Suppliers")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        sup_filter = st.multiselect("Filter by Supplier", options=df["supplier_distributor"].unique())
    with c2:
        country_filter = st.multiselect("Filter by Country", options=df["origin_country"].unique())
    with c3:
        status_filter = st.multiselect("Filter by Status", options=df["status"].unique() if "status" in df.columns else [])

    filtered = df_ordered.copy()
    if sup_filter:
        filtered = filtered[filtered["supplier_distributor"].isin(sup_filter)]
    if country_filter:
        filtered = filtered[filtered["origin_country"].isin(country_filter)]
    if status_filter:
        filtered = filtered[filtered["status"].isin(status_filter)]

    # FIXED: No applymap - just show dataframe
    st.dataframe(filtered, use_container_width=True, height=400)
    
    if "percent_rating" in filtered.columns:
        m1, m2, m3 = st.columns(3)
        m1.metric("Avg Compliance", f"{filtered['percent_rating'].astype(int).mean():.0f}%")
        m2.metric("Approved", f"{len(filtered[filtered['status']=='Approved'])}" if "status" in filtered.columns else "0")
        m3.metric("Pending", f"{len(filtered[filtered['status']=='Pending'])}" if "status" in filtered.columns else "0")

else:
    st.subheader("Upload: FSSC 22000, Kosher, Halal, TDS/Spec, COA, Allergen Statement")
    
    supplier_list = df["supplier_distributor"].unique()
    selected_supplier = st.selectbox("Select your Supplier Name", supplier_list)
    
    my_rms = df[df["supplier_distributor"] == selected_supplier]
    rm_options = [f"{row['rm_code']} - {row['rm_description']}" for _, row in my_rms.iterrows()]
    selected_rm = st.selectbox("Select RM", rm_options) if rm_options else st.selectbox("Select RM", ["No RM"])

    doc_type = st.selectbox("Document Type", ["FSSC 22000 Certificate", "Kosher Certificate", "Halal Certificate", "TDS/Spec", "COA", "Allergen Statement", "VACCP Questionnaire", "TACCP Questionnaire", "MSDS"])
    uploaded = st.file_uploader(f"Upload {doc_type} for {selected_rm}", type=["pdf","jpg","png","docx","xlsx"])

    if st.button("Submit Document", type="primary"):
        if uploaded:
            st.success(f"✅ {doc_type} received for {selected_rm} ({selected_supplier})! {uploaded.name}")
            st.balloons()
        else:
            st.warning("Please upload a file first")
    
    st.markdown("---")
    st.subheader(f"My uploads - {selected_supplier}")
    st.dataframe(my_rms[ordered_cols], use_container_width=True)
