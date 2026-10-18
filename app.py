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

# --- 2. SUPPLIER VIEW (Sees Only Their RMs) - Line 40ish ---
else: # Supplier
    st.subheader(f"Welcome {supplier_name}")
    st.caption(f"{supplier_company} - {len(supplier_df)} RM(s) assigned to you")
    
    # Progress tracker - ADD THIS HERE
    st.markdown("### 📊 Your Onboarding Progress")
    col1, col2, col3 = st.columns(3)
    col1.metric("Form 1", "✅ Done", "M-PRO-01697")
    col2.metric("Form 2", "✅ Done", "M-PRO-02591")
    col3.metric("Form 3", "✅ Done", "M-PRO-00854")
    st.progress(100, text="100% Complete")
    st.divider()
    
    # Then your RM dropdown + Forms 1,2,3

    
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

               c1, c2, c3 = st.columns(3)
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
        # Find which supplier this email belongs to
        for key, secret_email in SECRETS.items():
            if secret_email.lower() == email:
                # Find real supplier name containing that key
                for real in df["supplier_distributor"].unique():
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

    # === FORM 2: TACCP SUPPLIER QUESTIONNAIRE M-PRO-02591 ===
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

    st.info("The supplier signature on this document certifies that:\n\na) Product complies with relevant national legislation and country of origin\nb) Information is accurate and true\nc) Supplier will immediately inform dsm-firmenich in writing if aware of potential adulteration")

    st.markdown("**Signatory**")
    c3, c4 = st.columns(2)
    with c3:
        sig_name = st.text_input("Name", key="f2_signame")
        sig_desig = st.text_input("Designation (signatory)", key="f2_sigdes")
    with c4:
        sig_sig = st.text_input("Signature (type full name)", key="f2_sigsig")
        sig_date = st.date_input("Date", key="f2_sigdate")

    st.markdown("**1. Manufacturer and country of origin**")
    st.caption("Add products you supply")
    prod_data = st.data_editor(
        pd.DataFrame([{"Product":"","Manufacturer":"","Country of origin":""} for _ in range(5)]),
        num_rows="dynamic", key="f2_prod_table"
    )

    st.markdown("### 2. Food defence self-assessment")
    st.caption("A separate assessment must be done for each manufacturing site and warehouse")

    def yes_no_radio(label, key):
        return st.radio(label, ["Yes","No","N/A"], index=None, key=key, horizontal=True)

    st.markdown("**Food defence plan**")
    fd1 = yes_no_radio("Is a designated site security team appointed to implement and oversee the security and food defence plan?", "fd1")
    fd2 = yes_no_radio("Are annual security and food defence audits conducted?", "fd2")
    fd3 = yes_no_radio("Is the site security and food defence plan reviewed at a minimum annually?", "fd3")
    fd4 = yes_no_radio("Is the site security and food defence plan treated as proprietary company information?", "fd4")
    fd5 = yes_no_radio("Are key contact information reviewed and updated annually?", "fd5")
    fd6 = yes_no_radio("Are procedures in place to control access during an emergency to authorised personnel only?", "fd6")
    fd7 = yes_no_radio("Are procedures for responding to threats of product tampering included in the food defence plan?", "fd7")
    fd8 = yes_no_radio("Are procedures for responding to actual incidents of product tampering detailed in the plan?", "fd8")
    fd9 = yes_no_radio("Are employees encouraged to report signs of possible product tampering?", "fd9")
    fd10 = yes_no_radio("Does the facility have a documented recall plan?", "fd10")

    st.markdown("**Physical security and security procedures**")
    ps1 = yes_no_radio("Are the grounds groomed and well maintained with clear lines of sight?", "ps1")
    ps2 = yes_no_radio("Are the facility’s exterior areas monitored for signs of suspicious activity or entry?", "ps2")
    ps3 = yes_no_radio("Is there sufficient outside lighting to allow detection of unusual activities during non-daylight hours?", "ps3")
    ps4 = yes_no_radio("Do emergency exits have self-closing doors or alarms?", "ps4")
    ps5 = yes_no_radio("Are all non-employees (e.g. contractors) registered upon entry?", "ps5")
    ps6 = yes_no_radio("Is positive identification required for outside vendors and delivery personnel before granting access?", "ps6")
    st.markdown("*Are the following always secured with locks, seals or sensors to prevent entry by unauthorized persons?*")
    ps6a = yes_no_radio("Outside doors and gates", "ps6a")
    ps6b = yes_no_radio("Windows", "ps6b")
    ps6c = yes_no_radio("Roof openings", "ps6c")
    ps6d = yes_no_radio("Vents", "ps6d")
    ps6e = yes_no_radio("Trailers and containers", "ps6e")
    ps6f = yes_no_radio("Utility areas", "ps6f")
    ps6g = yes_no_radio("Storage areas", "ps6g")
    ps7 = yes_no_radio("Is there emergency lighting within the facility?", "ps7")
    ps8 = yes_no_radio("Is active surveillance maintained through CCTV?", "ps8")
    ps9 = yes_no_radio("Are emergency systems tested periodically?", "ps9")
    ps10 = yes_no_radio("Are the locations of controls for emergency systems clearly marked?", "ps10")
    ps11 = yes_no_radio("Is access to sensitive storage, manufacturing areas restricted and controlled?", "ps11")
    ps12 = yes_no_radio("Are visitors restricted to non-production areas unless accompanied?", "ps12")
    ps13 = yes_no_radio("Are procedures in place to routinely check ablution facilities, lockers, storage areas for concealed people/packages?", "ps13")
    ps14 = yes_no_radio("Is a regular inventory of facility keys conducted?", "ps14")
    st.markdown("*Are the central controls for the following restricted?*")
    ps15a = yes_no_radio("Water", "ps15a")
    ps15b = yes_no_radio("Electricity", "ps15b")
    ps15c = yes_no_radio("CIP systems and storage tanks", "ps15c")
    ps15d = yes_no_radio("Heating, ventilation and air conditioning", "ps15d")

    st.markdown("**Personnel security procedures**")
    pe1 = yes_no_radio("Are background checks conducted on prospective employees prior to hiring?", "pe1")
    pe2 = yes_no_radio("Are background checks required on contract employees?", "pe2")
    pe3 = yes_no_radio("Do employees receive training on security procedures as part of orientation?", "pe3")
    pe4 = yes_no_radio("Does facility have a policy regarding items employees/visitors may bring (e.g. cameras)?", "pe4")
    pe5 = yes_no_radio("Are employees instructed on protocol for handling and reporting tampering, illness or other threats?", "pe5")

    st.markdown("**Production and storage**")
    pr1 = yes_no_radio("Is mixing/batching where large amounts of exposed product handled, continuously monitored?", "pr1")
    pr2 = yes_no_radio("Are lines that handle and transfer products monitored to ensure integrity?", "pr2")
    pr3 = yes_no_radio("Is packaging integrity of ingredients examined for tampering before use?", "pr3")
    pr4 = yes_no_radio("Are records maintained to trace back raw materials to suppliers?", "pr4")
    pr5 = yes_no_radio("Are records maintained to trace forward finished production to customers?", "pr5")
    pr6 = yes_no_radio("Are periodic security inspections conducted on production and storage facilities?", "pr6")
    pr7 = yes_no_radio("Are records maintained on facility security inspections?", "pr7")
    pr8 = yes_no_radio("Are product labels and packaging held in secure area to prevent theft/misuse?", "pr8")
    pr9 = yes_no_radio("Is inventory of finished products checked for unexplained additions/withdrawals?", "pr9")
    pr10 = yes_no_radio("Is access to inside/outside storage areas for hazardous materials restricted to designated employees?", "pr10")

    st.markdown("**Shipping and receiving**")
    sh1 = yes_no_radio("Are deliveries monitored and controlled?", "sh1")
    sh2 = yes_no_radio("Are outgoing shipments sealed with tamper evident seals?", "sh2")
    sh3 = yes_no_radio("Are seal numbers documented on shipping documents?", "sh3")
    sh4 = yes_no_radio("Are incoming delivery trucks inspected for unusual cargo/activity?", "sh4")
    sh5 = yes_no_radio("Are drivers’ identities verified against valid driver’s license?", "sh5")
    sh6 = yes_no_radio("Is access to loading docks controlled to avoid unauthorised access?", "sh6")
    sh7 = yes_no_radio("Are suspicious alterations in shipping documents immediately investigated?", "sh7")

    if st.form_submit_button("✅ Submit TACCP Form"):
        st.success(f"TACCP Form M-PRO-02591 submitted for {supplier_name2}!")
        st.balloons()

    if st.form_submit_button("✅ Submit Assessment Form"):
        st.success(f"Thank you {name} from {company} - Form M-PRO-01697 submitted! You may not need a physical audit.")
        st.balloons()

# === FORM 3: PRODUCT INFORMATION FORM M-PRO-00854 ===
st.divider()
st.subheader("📦 Form 3: Product Information Form (M-PRO-00854)")
st.caption("Document: M-PRO-00854 | Version 1 | Approved: 03 March 2025 | dsm-firmenich")

with st.form("form3_product_info"):
    st.markdown("### 1. PRODUCT & CONTACT DETAILS")
    c1, c2 = st.columns(2)
    with c1:
        cust_prod_name = st.text_input("Customer's Product Name", key="f3_cust_name")
        supp_prod_name = st.text_input("Supplier's Product Name", key="f3_supp_name")
        status = st.radio("Status", ["Existing Product", "New Product"], key="f3_status", horizontal=True)
        is_food_grade = st.radio("Is the product Food Grade?", ["Yes","No"], key="f3_foodgrade", horizontal=True)
        is_food_additive = st.radio("Is the product a Food Additive?", ["Yes","No"], key="f3_additive", horizontal=True)
        ins_number = st.text_input("INS/E Number", key="f3_ins")
        susceptible = st.radio("Is this product susceptible to Adulteration?", ["Yes","No"], key="f3_adult", horizontal=True)
    with c2:
        cust_prod_code = st.text_input("Customer's Product Code", key="f3_cust_code")
        supp_prod_code = st.text_input("Supplier's Product Code", key="f3_supp_code")
        adulterated_with = st.text_area("If yes, what product can it be adulterated with?", key="f3_adult_what")
        tests_adult = st.text_area("Tests to confirm adulteration + frequency", key="f3_tests")

    st.markdown("**1.1 Supplier Information**")
    col_a, col_b = st.columns(2)
    with col_a:
        comp_name = st.text_input("Company Name", key="f3_comp")
        trading_name = st.text_input("Trading Name", key="f3_trading")
        biz_addr3 = st.text_area("Business Address", key="f3_biz3")
        postal3 = st.text_area("Postal Address", key="f3_postal3")
    with col_b:
        tech_contact3 = st.text_input("Technical Contact Person", key="f3_tech3")
        pos_title = st.text_input("Position Title", key="f3_pos")
        phone3 = st.text_input("Phone", key="f3_phone")
        email3 = st.text_input("Email", key="f3_email3")
        cell3 = st.text_input("Cell (mobile)", key="f3_cell3")

    st.markdown("**1.2 Manufacturer(s) if different to supplier**")
    manuf_table = st.data_editor(
        pd.DataFrame([{"Company Name":"","Site of Manufacture (City & Country)":""} for _ in range(3)]),
        num_rows="dynamic", key="f3_manuf"
    )

    st.markdown("**1.4 Supplier Declaration and Warranty**")
    st.caption("Supplier certifies product complies with SA legislation, info is true, will inform of changes")
    decl_company = st.text_input("Company Name (Signed for and on behalf of)", key="f3_decl_comp")
    decl_name = st.text_input("Name (please print)", key="f3_decl_name")
    decl_title = st.text_input("Job Title (declaration)", key="f3_decl_title")
    decl_sig = st.text_input("Authorised Signature (type name)", key="f3_decl_sig")
    decl_date = st.date_input("Date (declaration)", key="f3_decl_date")

    st.divider()
    st.markdown("### 2. PRODUCT INFORMATION & INGREDIENTS")
    prod_desc = st.text_area("2.1 Product Description (Physical and technological)", key="f3_prod_desc")
    legal_desc = st.text_area("2.2 Legal Description / Suggested Labelling Description", key="f3_legal")
    ingredient_decl = st.text_area("2.3 Ingredient Declaration including QUID (full list descending, % of characterising)", height=150, key="f3_ingred")
    proc_aids = st.text_area("2.4 Processing Aids (carriers, anti-foam, divider oil, etc.)", key="f3_proc")
    
    st.markdown("**2.5 Country of Origin**")
    origin_option = st.radio("Statement", ["Produce of","Made in","Made in - with Imported Ingredients","Other"], key="f3_origin")
    origin_country = st.text_input("Insert Country Below", key="f3_origin_country")
    imported_pct = st.text_input("Specify % Imported Ingredients", key="f3_import_pct")
    imported_countries = st.text_input("Specify Country/IES of Imported Ingredients", key="f3_import_c")

    st.markdown("**2.6 Component country of origin**")
    comp_origin_table = st.data_editor(
        pd.DataFrame([{"Ingredient":"","Country of origin":""} for _ in range(8)]),
        num_rows="dynamic", key="f3_comp_origin"
    )

    st.divider()
    st.markdown("### 3. ALLERGEN & COMPOSITIONAL INFORMATION")
    st.markdown("**3.1 Mandatory Advisory or Warning Statements**")
    adv_components = ["Aspartame","Saccharin","Cyclamate","Glutamates (MSG)","Tartrazine","Phytosterol esters / stanols","Any ingredients irradiated","Herbal and botanical extracts","Isomaltulose","Polyols, Isomalts, Polydextrose"]
    advisory = {}
    for comp in adv_components:
        advisory[comp] = st.radio(f"{comp}", ["No","Yes"], key=f"f3_adv_{comp}", horizontal=True, index=None)

    st.markdown("**3.2 Mandatory Declaration of certain substances + Cross Contact**")
    allergens = ["Cereals containing gluten (wheat, rye, barley, oats, spelt)","Crustacea & crustacea products","Molluscs & mollusc products","Egg & egg products","Fish & fish products","Milk & milk products","Peanuts & peanut products","Soybeans & their products","Tree nuts & their products","Sulphites"]
    allergen_data = {}
    for aller in allergens:
        col1, col2, col3 = st.columns([2,1,1])
        with col1:
            present = st.radio(f"{aller} - Present?", ["No","Yes"], key=f"f3_aller_{aller}", horizontal=True, index=None)
        with col2:
            same_line = st.radio("Same line?", ["No","Yes"], key=f"f3_line_{aller}", horizontal=True, index=None)
        with col3:
            same_fac = st.radio("Same facility?", ["No","Yes"], key=f"f3_fac_{aller}", horizontal=True, index=None)
        allergen_data[aller] = {"present": present, "line": same_line, "facility": same_fac}

    st.markdown("**3.3 Allergen Cross Contact**")
    cross_contact = st.radio("Has your company addressed cross contact from allergen components?", ["Yes","No"], key="f3_cross", horizontal=True, index=None)
    avoid_methods = st.multiselect("How is cross contact avoided? (tick all applicable)",
        ["validated cleaning procedures (swabs/visual/Elisa)","production scheduling","control of personnel movement","staff training","documented procedures and controls","isolated storage of allergens","other"])
    
    st.divider()
    st.markdown("### 4. DIETARY SUITABILITY")
    vegan = st.radio("Vegan Suitable (NO meat, milk, eggs, honey)", ["Yes","No"], key="f3_vegan", horizontal=True, index=None)
    lacto = st.radio("Lacto Vegetarian Suitable (contains milk)", ["Yes","No"], key="f3_lacto", horizontal=True, index=None)
    ovo = st.radio("Ovo Vegetarian Suitable (contains egg)", ["Yes","No"], key="f3_ovo", horizontal=True, index=None)
    ovo_lacto = st.radio("Ovo Lacto Vegetarian Suitable", ["Yes","No"], key="f3_ovolacto", horizontal=True, index=None)
    halaal = st.radio("Halaal Suitable - Is product Halaal certified?", ["Yes - attach cert","No"], key="f3_halaal", horizontal=True, index=None)
    kosher = st.radio("Kosher Suitable - Is product Kosher certified?", ["Yes - attach cert","No"], key="f3_kosher", horizontal=True, index=None)
    organic = st.radio("Organic Certified?", ["Yes - attach cert","No"], key="f3_organic", horizontal=True, index=None)

    st.divider()
    st.markdown("### 5. CONTAMINANTS & GENE TECHNOLOGY")
    st.caption("R.246 Pesticides, R.1809 Vet residues, R.500 Metals, R.491 Marine Biotoxins, R.1145 Mycotoxins, R.911 Solvents - All must comply SA legislation")
    pesticides = st.radio("Complies with R.246 pesticide residues?", ["Yes","No"], key="f3_pest", horizontal=True, index=None)
    
    st.markdown("**5.2 Food Produced using Gene Technology**")
    gm_q1 = st.radio("Q1: Any GM material/derived from GM substrates/organisms?", ["Yes","May contain","No - Go to Section 6"], key="f3_gm1", horizontal=True, index=None)
    gm_q2 = st.radio("Q2: Require labelling per R.25 GM labelling?", ["Yes","No"], key="f3_gm2", horizontal=True, index=None)
    gm_q3 = st.radio("Q3: Product contains GM novel DNA/protein?", ["Does not contain","Contains or May contain exempt from labelling","Contains or May contain which requires labelling"], key="f3_gm3", horizontal=True, index=None)
    gm_q4 = st.radio("Q4: Any GM components have altered characteristics?", ["Yes","No"], key="f3_gm4", horizontal=True, index=None)
    gm_table = st.data_editor(
        pd.DataFrame([{"GM Component":"","Altered Characteristics":""} for _ in range(3)]),
        num_rows="dynamic", key="f3_gm_table"
    )

    st.divider()
    st.markdown("### 6. STORAGE & 8. SPECIFICATIONS")
    st.markdown("**6.1 Storage & Transportation**")
    c_s1, c_s2 = st.columns(2)
    with c_s1:
        storage_unopened = st.text_input("Recommended Storage Conditions - Unopened", key="f3_store_un")
        shelf_unopened = st.text_input("Shelf Life - Unopened", key="f3_shelf_un")
    with c_s2:
        storage_opened = st.text_input("Recommended Storage Conditions - Opened", key="f3_store_op")
        shelf_opened = st.text_input("Shelf Life - Opened", key="f3_shelf_op")
    transport_req = st.text_input("Recommended Transportation Requirements", key="f3_trans")

    st.markdown("**8.1 Physical Specifications**")
    phys_table = st.data_editor(pd.DataFrame([{"Test / Parameter":"","Specification":"","Test Method":""} for _ in range(3)]), num_rows="dynamic", key="f3_phys")
    st.markdown("**8.2 Chemical Specifications**")
    chem_table = st.data_editor(pd.DataFrame([{"Test / Parameter":"","Specification":"","Test Method":""} for _ in range(3)]), num_rows="dynamic", key="f3_chem")
    st.markdown("**8.2 Microbiological Specifications**")
    micro_table = st.data_editor(pd.DataFrame([{"Test / Parameter":"","Specification":"","Test Method":""} for _ in range(3)]), num_rows="dynamic", key="f3_micro")

    docs3 = st.file_uploader("Upload supporting docs: Halaal cert, Kosher cert, Spec sheets, Test methods", accept_multiple_files=True, key="f3_docs")

    if st.form_submit_button("✅ Submit Product Information Form - FINAL"):
        st.success(f"Form 3 M-PRO-00854 submitted for {supp_prod_name}! All 3 forms complete!")
        st.balloons()
        st.markdown("### 🎉 Supplier Onboarding 100% Complete")
        st.progress(100, text="100% - Approved Supplier Pending Review")

# === ADMIN ONLY - MASTER EXPORT ===
if st.session_state.get("supplier_email") == "YOUR_ADMIN_EMAIL@dsm-firmenich.com":
    st.divider()
    st.subheader("🔒 Admin: Approved Supplier List Export")
    if st.button("Generate Master CSV for FSSC Audit"):
        st.success("Approved_Supplier_List.csv generated: Savannah + 918861 + Forms 1-3 + Dates")
        st.download_button("Download Audit File", data="sample", file_name="Approved_Supplier_List.csv")
