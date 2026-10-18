import streamlit as st
import pandas as pd
import mysql.connector

st.set_page_config(page_title="SQMS Portal", layout="wide")
st.title("📤 Supplier Document Portal - Food Safety")

# --- CONNECT TO YOUR CLEAN MYSQL TABLE ---
def get_connection():
    return mysql.connector.connect(
        host=st.secrets["mysql"]["host"],
        user=st.secrets["mysql"]["user"],
        password=st.secrets["mysql"]["password"],
        database=st.secrets["mysql"]["database"]
    )

# --- SIDEBAR - ROLE SELECTOR (from your screenshot) ---
role = st.sidebar.selectbox("You are:", ["Director View", "Supplier Upload"])

if role == "Director View":
    try:
        conn = get_connection()
        df = pd.read_sql("SELECT rm_code, rm_description, origin_country, kosher_status, halaal_status, food_safety_cert_status, spec_tds, msds, vaccp_questionnaire, taccp_questionnaire, percent_rating, status FROM supplier_master_list", conn)
        st.subheader(f"Director Dashboard - {len(df)} Suppliers")
        
        # Color coding like Excel
        def color_rating(val):
            if val == 100: return 'background-color: #c6efce' # Green
            elif val > 0: return 'background-color: #ffeb9c' # Yellow
            else: return 'background-color: #ffc7ce' # Red
        st.dataframe(df.style.applymap(color_rating, subset=['percent_rating']), use_container_width=True)
        
        st.metric("Average Compliance", f"{df['percent_rating'].mean():.1f}%")
    except Exception as e:
        st.error(f"MySQL not connected yet. Add Secrets in Streamlit Cloud. Error: {e}")
        st.info("Go to Streamlit Cloud > App > Settings > Secrets and add your MySQL details")

else: # Supplier Upload - THIS IS YOUR SCREENSHOT
    st.write("Upload: FSSC 22000, Kosher, Halal, TDS/Spec, COA, Allergen Statement")
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, rm_code, rm_description FROM supplier_master_list")
        suppliers = cursor.fetchall()
        
        supplier_options = {f"{s['rm_code']} - {s['rm_description']}": s['id'] for s in suppliers}
        
        selected_name = st.selectbox("Select your Supplier Name", list(supplier_options.keys()))
        selected_id = supplier_options[selected_name]

        doc_map = {
            "FSSC 22000 Certificate": "food_safety_cert_status",
            "Kosher Certificate": "kosher_status",
            "Halal Certificate": "halaal_status",
            "TDS/Spec": "spec_tds",
            "MSDS": "msds",
            "VACCP Questionnaire": "vaccp_questionnaire",
            "TACCP Questionnaire": "taccp_questionnaire",
            "Allergen Declaration": "allergen_declaration"
        }
        
        doc_type = st.selectbox("Document Type", list(doc_map.keys()))
        uploaded_file = st.file_uploader(f"Upload {doc_type}", type=["pdf","jpg","png","docx","xlsx"])

        if st.button("Submit Document"):
            if uploaded_file:
                col = doc_map[doc_type]
                cursor.execute(f"UPDATE supplier_master_list SET {col}='Yes' WHERE id=%s", (selected_id,))
                # Recalculate rating
                cursor.execute("""
                UPDATE supplier_master_list SET percent_rating = ROUND((
                (kosher_status='Yes')+(halaal_status='Yes')+(food_safety_cert_status='Yes')+
                (spec_tds='Yes')+(msds='Yes')+(vaccp_questionnaire='Yes')+(taccp_questionnaire='Yes')+
                (allergen_declaration='Yes'))/26*100) WHERE id=%s
                """, (selected_id,))
                conn.commit()
                st.success(f"✅ {doc_type} saved as Yes for {selected_name}!")
                st.balloons()
            else:
                st.warning("Please upload a file first")

        # Show my uploads
        cursor.execute("SELECT * FROM supplier_master_list WHERE id=%s", (selected_id,))
        my_data = cursor.fetchone()
        st.subheader(f"Your uploads: {selected_name}")
        st.write(my_data)
        
    except Exception as e:
        st.error(f"Connect MySQL first in Secrets: {e}")
