import streamlit as st
import pandas as pd

st.set_page_config(page_title="SQMS Dashboard", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("supplier_compliance.csv", sep=";", engine="python", on_bad_lines="skip", encoding="latin1")
    # Clean column names: "Compliance Score" -> "compliance_score"
    df.columns = [c.strip().lower().replace(" ", "_").replace("-", "_") for c in df.columns]
    df = df.rename(columns={"material_cat": "material_category"})
    return df

df = load_data()

st.title("SQMS Dashboard")
st.write(f"Total Raw Materials: {len(df)}")
st.write("COLUMNS:", list(df.columns))

# Filters - only show if column exists
if "supplier_distributor" in df.columns:
    suppliers = sorted(df["supplier_distributor"].dropna().unique().tolist())
    sup_filter = st.multiselect("Filter Supplier", suppliers)
    if sup_filter:
        df = df[df["supplier_distributor"].isin(sup_filter)]

if "material_category" in df.columns:
    cats = sorted(df["material_category"].dropna().unique().tolist())
    cat_filter = st.multiselect("Filter Material Category", cats)
    if cat_filter:
        df = df[df["material_category"].isin(cat_filter)]

st.dataframe(df, use_container_width=True)
