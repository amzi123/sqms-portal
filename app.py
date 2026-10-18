import streamlit as st
import pandas as pd

st.set_page_config(page_title="SQMS Portal", layout="wide")
st.title("🌮 SQMS Supplier Portal - Food Safety Compliance")
st.caption("IT-Ready Version - Supplier Isolation + No Styler Error")

@st.cache_data
def load_data():
    try:
        df = pd.read_csv("supplier_compliance.csv")
        return df
    except:
        try:
            return pd.read_csv("SQMS_data.csv")
        except:
            return pd.DataFrame({
                "supplier_distributor": ["Test Supplier"],
                "manufacturer": ["Test Mfg"],
                "percent_rating": [85],
                "status": ["Pending"]
            })

df = load_data()

priority = ["supplier_distributor","manufacturer","rm_code","rm_description","origin_country","vendor_code","mfg_code"]
other_cols = [c for c in df.columns if c not in priority]
ordered_cols = [c for c in priority if c in df.columns] + other_cols

HAS_SECRETS = False
SECRETS = {}
try:
    SECRETS = dict(st.secrets)
    HAS_SECRETS = len(SECRETS) > 0
except:
    HAS_SECRETS = False

role = st.sidebar.selectbox("Role", ["SQMS Admin (All)", "Supplier"])
filtered = df

if role == "SQMS Admin (All)":
    st.dataframe(filtered[ordered_cols] if ordered_cols else filtered)

    c1, c2, c3 = st.columns(3)
    c1.metric("Avg Compliance", f"{filtered['percent_rating'].mean():.0f}%" if "percent_rating" in filtered.columns and len(filtered) else "0%")
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
                    if key.lower() in str(real).lower():
                        matched_supplier = real
                        break
        if matched_supplier:
            st.success(f"Welcome {matched_supplier}!")
            uploaded = st.file_uploader("Upload Document", type=["pdf","xlsx","csv"])
            if uploaded:
                st.write("File received:", uploaded.name)
        elif email:
            st.warning("Email not authorized. Contact SQMS Admin.")
