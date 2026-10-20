import streamlit as st
import pandas as pd

st.set_page_config(page_title="SQMS Portal", layout="wide")
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
        return pd.read_csv("supplier_compliance.csv")
    except:
        return pd.read_csv("SQMS_data.csv")

df = load_data()
priority = ["supplier_distributor","manufacturer","rm_code","rm_description","origin_country","vendor_code","mfg_code"]
other_cols = [c for c in df.columns if c not in priority]
ordered = [c for c in priority if c in df.columns] + other_cols

# UNIQUE KEY FIXES DUPLICATE ERROR
role = st.sidebar.selectbox("Login as:", ["SQMS Admin (All)", "Supplier (My RMs Only)"], key="role_login_unique")
st.sidebar.metric("Total RMs", len(df))

try:
    SECRETS = st.secrets.get("supplier_logins", {})
    HAS_SECRETS = len(SECRETS) > 0
except:
    HAS_SECRETS = False
    SECRETS = {}

if role == "SQMS Admin (All)":
    st.subheader(f"SQMS Dashboard - {len(df)} Raw Materials")
    c1, c2 = st.columns(2)
    with c1:
        sup_filter = st.multiselect("Filter Supplier", df["supplier_distributor"].unique(), key="admin_sup_filter")
    with c2:
        country_filter = st.multiselect("Filter Country", df["origin_country"].unique() if "origin_country" in df.columns else [], key="admin_country_filter")
    filtered = df[ordered].copy()
    if sup_filter:
        filtered = filtered[filtered["supplier_distributor"].isin(sup_filter)]
    if country_filter and "origin_country" in df.columns:
        filtered = filtered[filtered["origin_country"].isin(country_filter)]
    st.dataframe(filtered, width='stretch', height=450)
else:
    st.subheader("Supplier Document Upload - Secure")
    if HAS_SECRETS:
        email = st.text_input("Work Email", key="supplier_email_unique").strip().lower()
        matched_supplier = None
        if email:
            for k, v in SECRETS.items():
                if v.lower() == email:
                    for real in df["supplier_distributor"].unique():
                        if k.lower() in real.lower():
                            matched_supplier = real
                            break
    else:
        st.warning("TEST MODE")
        matched_supplier = st.selectbox("Select Supplier (TEST)", df["supplier_distributor"].unique(), key="test_supplier_unique")
    if 'matched_supplier' in locals() and matched_supplier:
        my_rms = df[df["supplier_distributor"] == matched_supplier]
        st.success(f"Welcome {matched_supplier} — {len(my_rms)} RM(s)")
        st.dataframe(my_rms[ordered], width='stretch')

# === FORM 1 ===
st.divider()
st.subheader("📋 Form 1: Supplier Assessment Form (M-PRO-01697)")
st.caption("Document: M-PRO-01697 | Version 1 | Approved: 05 May 2025")
with st.form("form1_final_unique"):
    c1,c2,c3,c4 = st.columns(4)
    c1.radio("FSSC 22000", ["No","Yes"], key="fssc1")
    c2.radio("HACCP", ["No","Yes"], key="haccp1")
    c3.radio("ISO 22000", ["No","Yes"], key="iso22000_1")
    c4.radio("BRC", ["No","Yes"], key="brc1")
    c5,c6,c7 = st.columns(3)
    c5.radio("FSA", ["No","Yes"], key="fsa1")
    c6.radio("IFS", ["No","Yes"], key="ifs1")
    c7.radio("ISO 9001", ["No","Yes"], key="iso9001_1")
    st.text_input("Any other certification? State name", key="other_cert1")
    st.text_input("Which certification body and registration Number(s)?", key="cert_body1")
    st.multiselect("Criteria covered in Management System", ["Management Responsibility","Document and Data Control","Control of Customer Supplied Product","Product Identification and Traceability","Purchasing","HACCP system","GMP (TS 22002-1)","Process Control","Inspection and Testing","Control of Inspection, Measuring and Testing Equipment","Inspection and Test Status","Control of Non-Conforming Product","Corrective and Preventive Action","Handling, Storage, Packaging, Preservation and Delivery","Control of Records","Internal Audits","Training"], key="criteria1")
    st.radio("Intention to implement formal System?", ["N/A - We have certification","Yes","No"], key="intention1")
    st.date_input("Expected date of implementation", value=None, key="impl_date1")
    st.text_area("Description of controls", key="controls1")
    st.multiselect("Controls Exercised", ["Management Planning / Review","Raw Materials Inspection and Testing","Process Control Checks","Product / Project Approval","Planned / Preventive Maintenance","Work Instructions","Training Plan","Supplier Assessment"], key="formal_controls1")
    st.text_area("Other:", key="other1")
    col1,col2 = st.columns(2)
    with col1:
        st.text_input("Title", key="title1")
        st.text_input("Position", key="pos1")
        st.text_input("Company", key="comp1")
    with col2:
        st.text_input("Name", key="name1")
        st.text_input("Signature", key="sig1")
        st.date_input("Date", key="date1")
    st.file_uploader("Upload supporting docs", accept_multiple_files=True, key="docs1")
    st.form_submit_button("✅ Submit Assessment Form M-PRO-01697")

# === FORM 2 ===
st.divider()
st.subheader("🛡️ Form 2: TACCP Supplier Questionnaire (M-PRO-02591)")
st.caption("Document: M-PRO-02591 | Version 1 | Approved: 24 June 2024")
with st.form("form2_final_unique"):
    st.text_input("Supplier", key="f2_supplier_final")
    st.text_input("List of products supplied", key="f2_products_final")
    st.text_input("Technical contact", key="f2_tech_final")
    st.text_input("Designation", key="f2_des1_final")
    st.text_input("Telephone", key="f2_tel_final")
    st.text_input("Cell", key="f2_cell_final")
    st.text_area("Business address", key="f2_biz_final")
    st.text_area("Postal address", key="f2_postal_final")
    st.text_input("Email", key="f2_email_final")
    st.text_input("Name (Signatory)", key="f2_signame_final")
    st.text_input("Designation (signatory)", key="f2_sigdes_final")
    st.text_input("Signature", key="f2_sigsig_final")
    st.date_input("Date", key="f2_sigdate_final")
    st.data_editor(pd.DataFrame([{"Product":"","Manufacturer":"","Country of origin":""} for _ in range(5)]), num_rows="dynamic", key="f2_prod_table_final")
    def yes_no_radio(label, key):
        return st.radio(label, ["Yes","No","N/A"], index=None, key=key, horizontal=True)
    yes_no_radio("Is a designated site security team appointed?", "fd1_final")
    yes_no_radio("Are annual security audits conducted?", "fd2_final")
    yes_no_radio("Is plan reviewed annually?", "fd3_final")
    yes_no_radio("Does facility have documented recall plan?", "fd10_final")
    st.form_submit_button("✅ Submit TACCP Form M-PRO-02591")

# === FORM 3 ===
st.divider()
st.subheader("📦 Form 3: Product Information Form (M-PRO-00854)")
st.caption("Document: M-PRO-00854 | Version 1 | Approved: 03 March 2025")
with st.form("form3_final_unique"):
    st.text_input("Customer's Product Name", key="f3_cust_name_final")
    st.text_input("Supplier's Product Name", key="f3_supp_name_final")
    st.radio("Status", ["Existing Product", "New Product"], key="f3_status_final", horizontal=True)
    st.text_input("Company Name", key="f3_comp_final")
    st.text_area("Ingredient Declaration", key="f3_ingred_final")
    st.text_area("Storage Conditions", key="f3_store_final")
    st.file_uploader("Upload supporting docs", accept_multiple_files=True, key="f3_docs_final")
    st.form_submit_button("✅ Submit Product Information Form - FINAL")
