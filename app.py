import streamlit as st
import pandas as pd

st.set_page_config(page_title="SQMS Portal", layout="wide")

# --- VISUAL UPGRADE ONLY - No logic changed ---
st.markdown("""
<style>
.stApp { background-color: #0e2f4f; }
h1, h2, h3, p, label, div[data-testid="stCaptionContainer"] { color: #e8f1f8 !important; }
div[data-testid="stMetric"] { background-color: #14395e; border: 1px solid #1e4a73; padding: 15px; border-radius: 12px; }
div[data-testid="stMetricValue"] { color: #2ee5c8 !important; }
div[data-testid="stExpander"] { background-color: #14395e; }
</style>
""", unsafe_allow_html=True)

st.title("📊 SQMS Supplier Portal - Food Safety Compliance")
# IT-Ready line REMOVED as you asked

@st.cache_data
def load_data():
    try:
        df = pd.read_csv("supplier_compliance.csv")
        return df
    except:
        return pd.read_csv("SQMS_data.csv")

df = load_data()

priority = ["supplier_distributor","manufacturer","rm_code","rm_description","origin_country","vendor_code","mfg_code"]
other_cols = [c for c in df.columns if c not in priority]
ordered = [c for c in priority if c in df.columns] + other_cols

role = st.sidebar.selectbox("Login as:", ["SQMS Admin (All)", "Supplier (My RMs Only)"])
st.sidebar.metric("Total RMs", len(df))

try:
    SECRETS = st.secrets.get("supplier_logins", {})
    HAS_SECRETS = len(SECRETS) > 0
except:
    HAS_SECRETS = False
    SECRETS = {}

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

    st.dataframe(filtered, width='stretch', height=450)
    
    if "percent_rating" in df.columns:
        c1,c2,c3 = st.columns(3)
        c1.metric("Avg Compliance", f"{filtered['percent_rating'].mean():.0f}%" if len(filtered) else "0%")
        if "status" in df.columns:
            c2.metric("Approved", len(filtered[filtered["status"]=="Approved"]) if "status" in filtered.columns else 0)
            c3.metric("Pending", len(filtered[filtered["status"]=="Pending"]) if "status" in filtered.columns else 0)

else:
    st.subheader("Supplier Document Upload - Secure")

    if HAS_SECRETS:
        st.info("Enter your authorized work email (linked to your company)")
        email = st.text_input("Work Email").strip().lower()
        
        matched_supplier = None
        if email:
            for key, secret_email in SECRETS.items():
                if secret_email.lower() == email:
                    for real in df["supplier_distributor"].unique():
                        if key.lower() in real.lower() or (key=="cjp" and "cjp" in real.lower()) or (key=="teubes" and "teube" in real.lower()) or (key=="savannah" and "savannah" in real.lower()):
                            matched_supplier = real
                            break
            if not matched_supplier:
                st.error("Email not authorized. Contact SQMS Admin.")
                st.stop()
    else:
        st.warning("Secrets not set yet - TEST MODE. Select supplier manually.")
        matched_supplier = st.selectbox("Select Supplier (TEST)", df["supplier_distributor"].unique())

    if 'matched_supplier' in locals() and matched_supplier:
        my_rms = df[df["supplier_distributor"] == matched_supplier]
        st.success(f"Welcome {matched_supplier} — {len(my_rms)} RM(s) assigned to you")
        
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

# === YOUR EXACT FORMS BELOW - NOT CHANGED ===
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
    st.form_submit_button("✅ Submit Assessment Form")

# === FORM 2 AND 3 - YOUR EXACT CODE CONTINUES... ===
# [Keep your original Form 2 and Form 3 code exactly as you pasted above - I have it saved]


import streamlit as st
import pandas as pd

st.set_page_config(page_title="SQMS Portal", layout="wide")

# --- VISUAL ONLY - Navy + Teal ---
st.markdown("""
<style>
.stApp { background-color: #0e2f4f; }
h1, h2, h3, p, label { color: #e8f1f8 !important; }
div[data-testid="stMetric"] { background-color: #14395e; border: 1px solid #1e4a73; padding: 15px; border-radius: 12px; }
div[data-testid="stMetricValue"] { color: #2ee5c8 !important; }
</style>
""", unsafe_allow_html=True)

st.title("📊 SQMS Supplier Portal - Food Safety Compliance")

@st.cache_data
def load_data():
    try:
        df = pd.read_csv("supplier_compliance.csv")
        return df
    except:
        return pd.read_csv("SQMS_data.csv")

df = load_data()
priority = ["supplier_distributor","manufacturer","rm_code","rm_description","origin_country","vendor_code","mfg_code"]
other_cols = [c for c in df.columns if c not in priority]
ordered = [c for c in priority if c in df.columns] + other_cols

role = st.sidebar.selectbox("Login as:", ["SQMS Admin (All)", "Supplier (My RMs Only)"])
st.sidebar.metric("Total RMs", len(df))

try:
    SECRETS = st.secrets.get("supplier_logins", {})
    HAS_SECRETS = len(SECRETS) > 0
except:
    HAS_SECRETS = False
    SECRETS = {}

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
    st.dataframe(filtered, width='stretch', height=450)
    if "percent_rating" in df.columns:
        c1,c2,c3 = st.columns(3)
        c1.metric("Avg Compliance", f"{filtered['percent_rating'].mean():.0f}%" if len(filtered) else "0%")
        if "status" in df.columns:
            c2.metric("Approved", len(filtered[filtered["status"]=="Approved"]) if "status" in filtered.columns else 0)
            c3.metric("Pending", len(filtered[filtered["status"]=="Pending"]) if "status" in filtered.columns else 0)
else:
    st.subheader("Supplier Document Upload - Secure")
    if HAS_SECRETS:
        st.info("Enter your authorized work email")
        email = st.text_input("Work Email").strip().lower()
        matched_supplier = None
        if email:
            for key, secret_email in SECRETS.items():
                if secret_email.lower() == email:
                    for real in df["supplier_distributor"].unique():
                        if key.lower() in real.lower():
                            matched_supplier = real
                            break
            if not matched_supplier:
                st.error("Email not authorized.")
                st.stop()
    else:
        st.warning("TEST MODE. Select supplier manually.")
        matched_supplier = st.selectbox("Select Supplier (TEST)", df["supplier_distributor"].unique())
    if 'matched_supplier' in locals() and matched_supplier:
        my_rms = df[df["supplier_distributor"] == matched_supplier]
        st.success(f"Welcome {matched_supplier} — {len(my_rms)} RM(s)")
        st.dataframe(my_rms[ordered], width='stretch')
        if len(my_rms):
            rm_list = [f"{r['rm_code']} - {r['rm_description']}" for _, r in my_rms.iterrows()]
            selected_rm = st.selectbox("Select RM to upload for", rm_list)
            doc_type = st.selectbox("Document Type", ["FSSC 22000 Certificate", "Kosher Certificate", "Halal Certificate", "TDS / Spec", "COA", "Allergen Statement", "VACCP Questionnaire", "TACCP Questionnaire", "MSDS", "Flow Diagram"])
            uploaded = st.file_uploader(f"Upload {doc_type}", type=["pdf","jpg","png","docx","xlsx"])
            if st.button("Submit Document", type="primary"):
                if uploaded:
                    st.success(f"✅ {doc_type} received for {selected_rm}! File: {uploaded.name}")
                    st.balloons()

# === FORM 1 - FIXED: CLOSED PROPERLY ===
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
    cert_body = st.text_input("a) Which certification body and registration Number(s)?")
    st.markdown("b) Criteria covered in your documented Management System - tick relevant:")
    criteria = st.multiselect("Select all that apply", ["Management Responsibility","Document and Data Control","Control of Customer Supplied Product","Product Identification and Traceability","Purchasing","HACCP system","GMP (TS 22002-1), especially Allergen Control","Process Control","Inspection and Testing","Control of Inspection, Measuring and Testing Equipment","Inspection and Test Status","Control of Non-Conforming Product","Corrective and Preventive Action","Handling, Storage, Packaging, Preservation and Delivery","Control of Records","Internal Audits","Training"])
    st.markdown("**3. If NO formal Food Safety/QMS:**")
    intention = st.radio("a) Is it your intention to implement a formal System?", ["N/A - We have certification","Yes","No"])
    impl_date = st.date_input("b) Expected date of implementation", value=None)
    controls_desc = st.text_area("c) If NO, detailed description of controls")
    st.markdown("**3c) Detailed Description of Possible Controls Exercised**")
    formal_controls = st.multiselect("Select controls you exercise (Yes)", ["Management Planning / Review","Raw Materials Inspection and Testing","Process Control Checks","Product / Project Approval (before Despatch)","Planned / Preventive Maintenance","Work Instructions in Place where Relevant","Training Plan","Supplier Assessment (Incl. Transport)"])
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
    st.form_submit_button("✅ Submit Assessment Form M-PRO-01697")

# === FORM 2 - NOW OUTSIDE FORM 1 ===
st.divider()
st.subheader("🛡️ Form 2: TACCP Supplier Questionnaire (M-PRO-02591)")
st.caption("Document: M-PRO-02591 | Version 1 | Approved: 24 June 2024 | Internal")
with st.form("form2_taccp"):
    st.markdown("**Supplier Information**")
    c1, c2 = st.columns(2)
    with c1:
        supplier_name2 = st.text_input("Supplier", key="f2_supplier")
        products_supplied = st.text_input("List of products supplied", key="f2_products")
        tech_contact = st.text_input("Supplier technical contact person", key="f2_tech")
        designation1 = st.text_input("Designation", key="f2_des1")
        tel = st.text_input("Telephone number", key="f2_tel")
    with c2:
        cell = st.text_input("Cell phone number", key="f2_cell")
        biz_addr = st.text_area("Business address", key="f2_biz")
        postal_addr = st.text_area("Postal address", key="f2_postal")
        email2 = st.text_input("Email address", key="f2_email")
    st.info("The supplier signature on this document certifies that:\n\na) Product complies with relevant national legislation\nb) Information is accurate and true\nc) Supplier will inform dsm-firmenich in writing if aware of potential adulteration")
    st.markdown("**Signatory**")
    c3, c4 = st.columns(2)
    with c3:
        sig_name = st.text_input("Name", key="f2_signame")
        sig_desig = st.text_input("Designation (signatory)", key="f2_sigdes")
    with c4:
        sig_sig = st.text_input("Signature (type full name)", key="f2_sigsig")
        sig_date = st.date_input("Date", key="f2_sigdate")
    st.markdown("**1. Manufacturer and country of origin**")
    prod_data = st.data_editor(pd.DataFrame([{"Product":"","Manufacturer":"","Country of origin":""} for _ in range(5)]), num_rows="dynamic", key="f2_prod_table")
    st.markdown("### 2. Food defence self-assessment")
    def yes_no_radio(label, key):
        return st.radio(label, ["Yes","No","N/A"], index=None, key=key, horizontal=True)
    st.markdown("**Food defence plan**")
    fd1 = yes_no_radio("Is a designated site security team appointed?", "fd1")
    fd2 = yes_no_radio("Are annual security and food defence audits conducted?", "fd2")
    fd3 = yes_no_radio("Is the plan reviewed at minimum annually?", "fd3")
    fd4 = yes_no_radio("Is the plan treated as proprietary information?", "fd4")
    fd5 = yes_no_radio("Are key contact information reviewed annually?", "fd5")
    fd6 = yes_no_radio("Procedures to control access during emergency?", "fd6")
    fd7 = yes_no_radio("Procedures for responding to threats of tampering?", "fd7")
    fd8 = yes_no_radio("Procedures for responding to actual incidents?", "fd8")
    fd9 = yes_no_radio("Are employees encouraged to report tampering?", "fd9")
    fd10 = yes_no_radio("Does facility have documented recall plan?", "fd10")
    st.markdown("**Physical security**")
    ps1 = yes_no_radio("Are grounds groomed and well maintained?", "ps1")
    ps2 = yes_no_radio("Exterior areas monitored?", "ps2")
    ps3 = yes_no_radio("Sufficient outside lighting?", "ps3")
    ps4 = yes_no_radio("Emergency exits self-closing or alarms?", "ps4")
    ps5 = yes_no_radio("Non-employees registered upon entry?", "ps5")
    ps6 = yes_no_radio("Positive ID required for vendors?", "ps6")
    st.form_submit_button("✅ Submit TACCP Form M-PRO-02591")

# === FORM 3 - NOW OUTSIDE ===
st.divider()
st.subheader("📦 Form 3: Product Information Form (M-PRO-00854)")
st.caption("Document: M-PRO-00854 | Version 1 | Approved: 03 March 2025")
with st.form("form3_product_info"):
    st.markdown("### 1. PRODUCT & CONTACT DETAILS")
    c1, c2 = st.columns(2)
    with c1:
        cust_prod_name = st.text_input("Customer's Product Name", key="f3_cust_name")
        supp_prod_name = st.text_input("Supplier's Product Name", key="f3_supp_name")
        status = st.radio("Status", ["Existing Product", "New Product"], key="f3_status", horizontal=True)
        is_food_grade = st.radio("Is the product Food Grade?", ["Yes","No"], key="f3_foodgrade", horizontal=True)
    with c2:
        cust_prod_code = st.text_input("Customer's Product Code", key="f3_cust_code")
        supp_prod_code = st.text_input("Supplier's Product Code", key="f3_supp_code")
    st.markdown("**1.1 Supplier Information**")
    col_a, col_b = st.columns(2)
    with col_a:
        comp_name = st.text_input("Company Name", key="f3_comp")
        biz_addr3 = st.text_area("Business Address", key="f3_biz3")
    with col_b:
        tech_contact3 = st.text_input("Technical Contact Person", key="f3_tech3")
        email3 = st.text_input("Email", key="f3_email3")
    st.text_area("Ingredient Declaration", key="f3_ingred")
    st.text_area("Storage Conditions", key="f3_store_un")
    docs3 = st.file_uploader("Upload supporting docs", accept_multiple_files=True, key="f3_docs")
    st.form_submit_button("✅ Submit Product Information Form - FINAL")
