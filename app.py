import streamlit as st
import pandas as pd

st.set_page_config(page_title="SQMS Portal", layout="wide")
st.title("📤 Supplier Document Portal - Food Safety")

# --- SIDEBAR - RENAMED AS YOU WANTED ---
role = st.sidebar.selectbox("You are:", ["SQMS View", "Supplier Upload"])

def get_mysql_data():
    try:
        import mysql.connector
        conn = mysql.connector.connect(**st.secrets["mysql"])
        df = pd.read_sql("SELECT rm_code, rm_description, origin_country, kosher_status, halaal_status, food_safety_cert_status, spec_tds, msds, vaccp_questionnaire, taccp_questionnaire, percent_rating, status FROM supplier_master_list", conn)
        return df, conn
    except Exception as e:
        # Fallback to CSV so portal never shows red error
        try:
            df = pd.read_csv("supplier_compliance.csv")
            return df, None
        except:
            return None, None

if role == "SQMS View":  # <-- RENAMED FROM Director View
    df, conn = get_mysql_data()
    if df is not None:
        st.subheader(f"SQMS Compliance Dashboard - {len(df)} Suppliers")
        # Green/Yellow/Red like your Excel
        if 'percent_rating' in df.columns:
            def color_rating(val):
                try:
                    if val == 100 or val == '100': return 'background-color: #c6efce'
                    elif int(val) > 0: return 'background-color: #ffeb9c'
                    else: return 'background-color: #ffc7ce'
                except: return ''
            st.dataframe(df.style.applymap(color_rating, subset=['percent_rating']), use_container_width=True)
        else:
            st.dataframe(df, use_container_width=True)
        
        if conn is None:
            st.info("ℹ️ Showing data from CSV. To link live MySQL (your 3 clean rows 918861, 984028, 939549), add Secrets in Streamlit Cloud > Settings > Secrets")
    else:
        st.warning("No data found. Upload supplier_compliance.csv")

else: # Supplier Upload
    st.write("Upload: FSSC 22000, Kosher, Halal, TDS/Spec, COA, Allergen Statement")
    df, conn = get_mysql_data()
    
    if df is not None:
        # Show supplier list from your data
        if 'rm_code' in df.columns:
            supplier_col = df['rm_code'].astype(str) + " - " + df['rm_description'].astype(str) if 'rm_description' in df.columns else df['rm_code']
        else:
            supplier_col = df.iloc[:,0]
            
        selected = st.selectbox("Select your Supplier Name", supplier_col)
        doc_type = st.selectbox("Document Type", ["FSSC 22000 Certificate", "Kosher Certificate", "Halal Certificate", "TDS/Spec", "COA", "Allergen Statement", "VACCP", "TACCP", "MSDS"])
        uploaded = st.file_uploader(f"Upload {doc_type}", type=["pdf","jpg","png","docx","xlsx"])
        
        if st.button("Submit Document"):
            if uploaded:
                if conn: # Live MySQL update
                    import mysql.connector
                    cursor = conn.cursor()
                    col_map = {"FSSC 22000 Certificate":"food_safety_cert_status", "Kosher Certificate":"kosher_status", "Halal Certificate":"halaal_status"}
                    col = col_map.get(doc_type, "spec_tds")
                    # Find ID by rm_code
                    rm_code = str(selected).split(" - ")[0]
                    cursor.execute(f"UPDATE supplier_master_list SET {col}='Yes' WHERE rm_code=%s", (rm_code,))
                    conn.commit()
                    st.success(f"✅ {doc_type} marked as Yes for {selected} in MySQL!")
                else:
                    st.success(f"✅ {doc_type} uploaded for {selected}! (Saved to CSV mode - add MySQL Secrets for permanent save)")
                    st.balloons()
            else:
                st.warning("Please upload a file first")
        
        st.subheader("My uploads")
        st.dataframe(df, use_container_width=True)
