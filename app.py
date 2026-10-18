import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(page_title="SQMS Portal", layout="wide")
st.title("📊 SQMS Supplier Portal - Food Safety Compliance")

@st.cache_data
def load_data():
    try:
        df = pd.read_csv("supplier_compliance.csv")
        return df
    except Exception as e:
        st.error(f"Could not load supplier_compliance.csv: {e}")
        return None

df = load_data()
if df is None:
    st.stop()

# Reorder: Supplier & Manufacturer FIRST
priority_cols = ["supplier_distributor", "manufacturer", "rm_code", "rm_description", "origin_country", "vendor_code", "mfg_code"]
other_cols = [c for c in df.columns if c not in priority_cols]
ordered_cols = [c for c in priority_cols if c in df.columns] + other_cols

# --- SIDEBAR ---
role = st.sidebar.selectbox("You are:", ["SQMS View", "Supplier Upload"])
st.sidebar.metric("Total RM", len(df))

# --- TRY TO READ SECRETS (if set), else work without crashing ---
try:
    supplier_emails = st.secrets.get("supplier_logins", {})
    has_secrets = len(supplier_emails) > 0
except:
    has_secrets = False
    supplier_emails = {}

# --- SQMS VIEW ---
if role == "SQMS View":
    st.subheader(f"SQMS Compliance Dashboard - {len(df)} Raw Materials")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        sup_filter = st.multiselect("Filter by Supplier", options=df["supplier_distributor"].unique())
    with c2:
        country_filter = st.multiselect("Filter by Country", options=df["origin_country"].unique())
    with c3:
        if "status" in df.columns:
            status_filter = st.multiselect("Filter by Status", options=df["status"].unique())
        else:
            status_filter = []

    filtered = df[ordered_cols].copy()
    if sup_filter:
        filtered = filtered[filtered["supplier_distributor"].isin(sup_filter)]
    if country_filter:
        filtered = filtered[filtered["origin_country"].isin(country_filter)]
    if status_filter:
        filtered = filtered[filtered["status"].isin(status_filter)]

    # FIXED: No Styler, just plain dataframe
    st.dataframe(filtered, width='stretch', height=400)
    
    if "percent_rating" in filtered.columns:
        m1, m2, m3 = st.columns(3)
        m1.metric("Avg Compliance", f"{filtered['percent_rating'].astype(int).mean():.0f}%")
        if "status" in filtered.columns:
            m2.metric("Approved", len(filtered[filtered['status']=='Approved']))
            m3.metric("Pending", len(filtered[filtered['status']=='Pending']))

# --- SUPPLIER UPLOAD (WITH ISOLATION) ---
else:
    st.subheader("Supplier Document Upload - Secure Access")

    if has_secrets:
        st.info("Secure mode: Enter your authorized email")
        email_input = st.text_input("Work Email").lower().strip()
        authorized_supplier = None
        
        if email_input:
            # Match email to supplier (contains check)
            for key, secret_email in supplier_emails.items():
                if secret_email.lower() == email_input:
                    # Find supplier name that contains key
                    for real_name in df["supplier_distributor"].unique():
                        if key.lower() in real_name.lower() or key.lower() in secret_email.lower():
                            # Map savannah -> Savannah, cjp -> CJP, teubes -> TEUBES
                            if "savannah" in key.lower() and "savannah" in real_name.lower():
                                authorized_supplier = real_name
                            elif "cjp" in key.lower() and "cjp" in real_name.lower():
                                authorized_supplier = real_name
                            elif "teubes" in key.lower() and "teubes" in real_name.lower():
                                authorized_supplier = real_name
                    if authorized_supplier:
                        break
            
            if not authorized_supplier:
                st.error("Email not authorized. Contact SQMS if this is an error.")
                st.stop()
        else:
            st.warning("Please enter email to continue")
            st.stop()
    else:
        # Fallback if Secrets not set yet - allow manual select (for testing)
        st.warning("Secrets not set yet - running in TEST mode (IT will require Secrets)")
        authorized_supplier = st.selectbox("Select your Supplier Name (TEST)", df["supplier_distributor"].unique())

    # Show ONLY their RMs
    my_rms = df[df["supplier_distributor"] == authorized_supplier]
    st.success(f"Welcome {authorized_supplier} - {len(my_rms)} RM(s) assigned")
    st.dataframe(my_rms[ordered_cols], width='stretch')

    rm_options = [f"{row['rm_code']} - {row['rm_description']}" for _, row in my_rms.iterrows()]
    selected_rm = st.selectbox("Select RM to upload for", rm_options) if rm_options else None

    doc_type = st.selectbox("Document Type", ["FSSC 22000 Certificate", "Kosher Certificate", "Halal Certificate", "TDS/Spec", "COA", "Allergen Statement", "VACCP Questionnaire", "TACCP Questionnaire", "MSDS"])
    uploaded = st.file_uploader(f"Upload {doc_type} for {selected_rm}", type=["pdf","jpg","png","docx","xlsx"])

    if st.button("Submit Document", type="primary"):
        if uploaded:
            st.success(f"✅ {doc_type} received for {selected_rm} ({authorized_supplier})! {uploaded.name}")
            st.balloons()
        else:
            st.warning("Please upload a file first")
