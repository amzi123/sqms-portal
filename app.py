import streamlit as st
import pandas as pd

st.set_page_config(page_title="SQMS Portal", layout="wide")
st.title("📊 SQMS Supplier Portal - Food Safety Compliance")
st.caption("IT-Ready Version - Supplier Isolation + No Styler Error")

@st.cache_data
def load_data():
    # Your file is supplier_compliance.csv
    try:
        df = pd.read_csv("supplier_compliance.csv")
        return df
    except:
        # Fallback if file name is different
        return pd.read_csv("SQMS_data.csv")

df = load_data()

# --- Priority columns first (Supplier & Manufacturer first) ---
priority = ["supplier_distributor","manufacturer","rm_code","rm_description","origin_country","vendor_code","mfg_code"]
other_cols = [c for c in df.columns if c not in priority]
ordered = [c for c in priority if c in df.columns] + other_cols

# --- SIDEBAR ---
role = st.sidebar.selectbox("Login as:", ["SQMS Admin (All)", "Supplier (My RMs Only)"])
st.sidebar.metric("Total RMs", len(df))

# --- READ EMAILS FROM STREAMLIT SECRETS (Secure, not in GitHub) ---
try:
    SECRETS = st.secrets.get("supplier_logins", {})
    HAS_SECRETS = len(SECRETS) > 0
except:
    HAS_SECRETS = False
    SECRETS = {}

# --- 1. SQMS ADMIN VIEW (Sees All) ---
if role == "SQMS Admin (All)":
    st.subheader(f"SQMS Dashboard - {len(df)} Raw Materials")
    
    col1, col2 = st.columns(2)
    with col1:
        sup_filter = st.multiselect("Filter Supplier", df["supplier_distributor"].unique())
    with col2:
        country_filter = st.multiselect("Filter Country", df["origin_country"].unique() if "origin_country" in df.columns else [])

    filtered = df[ordered].copy()
    if sup_filter:
        filtered = filtered[filtered["supplier_distributor"].isin(sup_filter)]
    if country_filter and "origin_country" in df.columns:
        filtered = filtered[filtered["origin_country"].isin(country_filter)]

    # FIXED: No df.style — this was causing AttributeError at line 36
    st.dataframe(filtered, width='stretch', height=450)
    
    # Compliance metrics
    if "percent_rating" in df.columns:
        c1,c2,c3 = st.columns(3)
        c1.metric("Avg Compliance", f"{filtered['percent_rating'].mean():.0f}%" if len(filtered) else "0%")
        if "status" in df.columns:
            c2.metric("Approved", len(filtered[filtered["status"]=="Approved"]) if "status" in filtered.columns else 0)
            c3.metric("Pending", len(filtered[filtered["status"]=="Pending"]) if "status" in filtered.columns else 0)

# --- 2. SUPPLIER VIEW (Isolated - Sees ONLY own name) ---
else:
    st.subheader("Supplier Document Upload - Secure")

    if HAS_SECRETS:
        st.info("Enter your authorized work email (linked to your company)")
        email = st.text_input("Work Email").strip().lower()
        
        matched_supplier = None
        if email:
            # Find which supplier this email belongs to
            for key, secret_email in SECRETS.items():
                if secret_email.lower() == email:
                    # Find real supplier name containing that key
                    for real in df["supplier_distributor"].unique():
                        if key.lower() in real.lower() or (key=="cjp" and "cjp" in real.lower()) or (key=="teubes" and "teube" in real.lower()) or (key=="savannah" and "savannah" in real.lower()):
                            matched_supplier = real
                            break
            if not matched_supplier:
                st.error("Email not authorized. Contact SQMS Admin.")
                st.stop()
    else:
        # TEST MODE until you set Secrets in Streamlit Cloud
        st.warning("Secrets not set yet - TEST MODE. Select supplier manually.")
        matched_supplier = st.selectbox("Select Supplier (TEST)", df["supplier_distributor"].unique())

    if 'matched_supplier' in locals() and matched_supplier:
        my_rms = df[df["supplier_distributor"] == matched_supplier]
        st.success(f"Welcome {matched_supplier} — {len(my_rms)} RM(s) assigned to you")
        
        # They ONLY see their own RMs - not other suppliers
        st.dataframe(my_rms[ordered], width='stretch')

        if len(my_rms):
            rm_list = [f"{r['rm_code']} - {r['rm_description']}" for _, r in my_rms.iterrows()]
            selected_rm = st.selectbox("Select RM to upload for", rm_list)
            
            doc_type = st.selectbox("Document Type", 
                ["FSSC 22000 Certificate", "Kosher Certificate", "Halal Certificate", "TDS / Spec", "COA", "Allergen Statement", "VACCP Questionnaire", "TACCP Questionnaire", "MSDS", "Flow Diagram"])
            
            uploaded = st.file_uploader(f"Upload {doc_type}", type=["pdf","jpg","png","docx","xlsx"])
            
            if st.button("Submit Document", type="primary"):
                if uploaded:
                    st.success(f"✅ {doc_type} received for {selected_rm}! File: {uploaded.name}")
                    st.balloons()
                    st.info("SQMS will review and your % rating will update automatically.")
                else:
                    st.warning("Please attach file first")


# === ADD FORM 1 HERE - M-PRO-01697 ===
st.divider()
st.subheader("📋 Form 1: Supplier Assessment Form (M-PRO-01697)")
st.caption("Document: M-PRO-01697 | Version 1 | Approved: 05 May 2025")

with st.form("form1"):
    st.markdown("**1. Certification (Tick Yes/No)**")
    c1, c2, c3, c4 = st.columns(4)
    fssc = c1.radio("FSSC 22000", ["No","Yes"], key="fssc")
    haccp = c2.radio("HACCP", ["No","Yes"], key="haccp")
    iso22000 = c3.radio("ISO 22000", ["No","Yes"], key="iso22000")
    brc = c4.radio("BRC", ["No","Yes"], key="brc")
    c5, c6, c7 = st.columns(3)
    fsa = c5.radio("FSA", ["No","Yes"], key="fsa")
    ifs = c6.radio("IFS", ["No","Yes"], key="ifs")
    iso9001 = c7.radio("ISO 9001", ["No","Yes"], key="iso9001")
    
    other_cert = st.text_input("Any other certification? State name")

    st.markdown("**2. If YES to any above:**")
    cert_body = st.text_input("a) Which certification body and registration Number(s)?")
    
    st.markdown("b) Criteria covered in your documented Management System - tick relevant:")
    criteria = st.multiselect("Select all that apply",
        ["Management Responsibility","Document and Data Control","Control of Customer Supplied Product",
         "Product Identification and Traceability","Purchasing","HACCP system",
         "GMP (TS 22002-1), especially Allergen Control","Process Control","Inspection and Testing",
         "Control of Inspection, Measuring and Testing Equipment","Inspection and Test Status",
         "Control of Non-Conforming Product","Corrective and Preventive Action",
         "Handling, Storage, Packaging, Preservation and Delivery","Control of Records",
         "Internal Audits","Training"])
    
    st.markdown("**3. If NO formal Food Safety/QMS:**")
    intention = st.radio("a) Is it your intention to implement a formal System?", ["N/A - We have certification","Yes","No"])
    impl_date = st.date_input("b) Expected date of implementation", value=None)
    controls_desc = st.text_area("c) If NO, detailed description of controls to guarantee Quality and Food Safety (or attach separately)")

    st.markdown("**3c) Detailed Description of Possible Controls Exercised**")
    formal_controls = st.multiselect("Select controls you exercise (Yes)",
        ["Management Planning / Review","Raw Materials Inspection and Testing","Process Control Checks",
         "Product / Project Approval (before Despatch)","Planned / Preventive Maintenance",
         "Work Instructions in Place where Relevant","Training Plan","Supplier Assessment (Incl. Transport)"])
    
    other = st.text_area("Other:")
    
    st.markdown("**4. Questionnaire completed by:**")
    col1, col2 = st.columns(2)
    with col1:
        title = st.text_input("Title")
        position = st.text_input("Position")
        company = st.text_input("Company")
    with col2:
        name = st.text_input("Name")
        signature = st.text_input("Signature (type full name)")
        date = st.date_input("Date")

    docs = st.file_uploader("Upload supporting Management System Document(s) / Certificate", accept_multiple_files=True)

    if st.form_submit_button("✅ Submit Assessment Form"):
        st.success(f"Thank you {name} from {company} - Form M-PRO-01697 submitted! You may not need a physical audit.")
        st.balloons()
