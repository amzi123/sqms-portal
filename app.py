import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="SQMS Portal - Food Safety", layout="wide")

# REAL FOOD SAFETY DOCS
REQUIRED_DOCS=["FSSC 22000 Certificate","Kosher Certificate","Halal Certificate","TDS / Product Spec","COA","Allergen Statement"]

os.makedirs("uploads",exist_ok=True)
UPLOAD_LOG="uploads_log.csv"

if os.path.exists(UPLOAD_LOG):
    log_df=pd.read_csv(UPLOAD_LOG)
else:
    log_df=pd.DataFrame(columns=["Supplier","Document Type","File Name","Upload Date"])

try:
    df=pd.read_csv("SQMS_data.csv")
except:
    try:
        df=pd.read_csv("supplier_compliance.csv")
    except:
        df=pd.DataFrame({"Supplier":["Supplier A","Supplier B","Supplier C"],"Compliance Score":[85,60,92],"Status":["Approved","Pending","Approved"],"Last Audit":["2025-01-15","2024-11-20","2025-03-10"]})

suppliers_list=df['Supplier'].unique().tolist()
st.sidebar.title("SQMS Portal")
role=st.sidebar.selectbox("You are:",["Supplier Upload","Admin Dashboard"])

if role=="Supplier Upload":
    st.title("📤 Supplier Document Portal - Food Safety")
    st.caption("Upload: FSSC 22000, Kosher, Halal, TDS/Spec, COA, Allergen Statement")
    supplier_name=st.selectbox("Select your Supplier Name",suppliers_list)
    doc_type=st.selectbox("Document Type",REQUIRED_DOCS)
    uploaded_file=st.file_uploader(f"Upload {doc_type}",type=["pdf","jpg","png","docx","xlsx"])
    submit=st.button("Submit Document")
    if uploaded_file and submit:
        save_name=f"{supplier_name}_{doc_type}_{uploaded_file.name}"
        save_path=os.path.join("uploads",save_name)
        with open(save_path,"wb") as f:
            f.write(uploaded_file.getbuffer())
        new_row=pd.DataFrame([{"Supplier":supplier_name,"Document Type":doc_type,"File Name":save_name,"Upload Date":datetime.now().strftime("%Y-%m-%d %H:%M")}])
        log_df=pd.concat([log_df,new_row],ignore_index=True)
        log_df.to_csv(UPLOAD_LOG,index=False)
        st.success(f"✅ {doc_type} uploaded for {supplier_name}!")
        st.balloons()
    st.subheader(f"Your uploads: {supplier_name}")
    my_uploads=log_df[log_df["Supplier"]==supplier_name]
    if not my_uploads.empty:
        st.dataframe(my_uploads, use_container_width=True)
    else:
        st.warning("No documents uploaded yet.")

else:
    st.title("📊 SQMS Admin - Food Safety Compliance")
    st.subheader("1. Supplier Master Records")
    md_table="| Supplier | Score | Status | Last Audit |\n|---|---|---|---|\n"
    for _,row in df.iterrows():
        md_table+=f"| {row['Supplier']} | {row['Compliance Score']} | {row['Status']} | {row['Last Audit']} |\n"
    st.markdown(md_table)
    st.divider()
    st.subheader("2. Document Compliance - Food Safety Docs")
    st.write("✅ = Uploaded | ❌ = Missing | Tracking: FSSC 22000, Kosher, Halal, TDS/Spec, COA, Allergen")
    if log_df.empty:
        compliance_matrix=pd.DataFrame(0,index=suppliers_list,columns=REQUIRED_DOCS)
    else:
        compliance_matrix=pd.DataFrame(0,index=suppliers_list,columns=REQUIRED_DOCS)
        for _,r in log_df.iterrows():
            if r["Supplier"] in compliance_matrix.index and r["Document Type"] in compliance_matrix.columns:
                compliance_matrix.loc[r["Supplier"],r["Document Type"]]=1
    emoji_df=compliance_matrix.apply(lambda col: col.map({1: "✅", 0: "❌"}))
    st.dataframe(emoji_df,use_container_width=True)
    st.subheader("3. Compliance % per Supplier")
    temp=compliance_matrix.copy()
    temp["Uploaded"]=temp[REQUIRED_DOCS].sum(axis=1)
    temp["% Complete"]=(temp["Uploaded"]/len(REQUIRED_DOCS)*100).astype(int)
    st.bar_chart(temp["% Complete"])
    st.divider()
    st.subheader("4. All Uploaded Files - Audit Log")
    if not log_df.empty:
        st.dataframe(log_df.sort_values("Upload Date",ascending=False),use_container_width=True)
    else:
        st.info("No uploads yet - Suppliers need to upload FSSC, Kosher, Halal, etc.")
