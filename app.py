import streamlit as st
import pandas as pd
import os
from datetime import datetime
st.set_page_config(page_title="SQMS Portal", layout="wide")
REQUIRED_DOCS=["Safety Certificate","Quality Audit","Insurance","Compliance Declaration"]
os.makedirs("uploads",exist_ok=True)
UPLOAD_LOG="uploads_log.csv"
if os.path.exists(UPLOAD_LOG):
 log_df=pd.read_csv(UPLOAD_LOG)
else:
 log_df=pd.DataFrame(columns=["Supplier","Document Type","File Name","Upload Date"])
try:
 df=pd.read_csv("SQMS_data.csv")
except:
 df=pd.read_csv("supplier_compliance.csv")
suppliers_list=df['Supplier'].unique().tolist()
st.sidebar.title("SQMS Portal")
role=st.sidebar.selectbox("You are:",["Supplier Upload","Admin Dashboard"])
if role=="Supplier Upload":
 st.title("📤 Supplier Document Portal")
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
  st.dataframe(my_uploads)
 else:
  st.warning("No documents uploaded yet.")
else:
 st.title("📊 SQMS Admin - Compliance Visual")
 st.subheader("1. Supplier Master Records")
 md_table="| Supplier | Score | Status | Last Audit |\n|---|---|---|---|\n"
 for _,row in df.iterrows():
  md_table+=f"| {row['Supplier']} | {row['Compliance Score']} | {row['Status']} | {row['Last Audit']} |\n"
 st.markdown(md_table)
 st.divider()
 st.subheader("2. Document Compliance - Who Uploaded What?")
 st.write("✅ = Uploaded | ❌ = Missing")
 if log_df.empty:
  compliance_matrix=pd.DataFrame(0,index=suppliers_list,columns=REQUIRED_DOCS)
 else:
  compliance_matrix=pd.DataFrame(0,index=suppliers_list,columns=REQUIRED_DOCS)
  for _,r in log_df.iterrows():
   if r["Supplier"] in compliance_matrix.index and r["Document Type"] in compliance_matrix.columns:
    compliance_matrix.loc[r["Supplier"],r["Document Type"]]=1
 emoji_df=compliance_matrix.replace({1:"✅",0:"❌"})
 st.dataframe(emoji_df,use_container_width=True)
 st.subheader("3. Compliance % per Supplier")
 temp=compliance_matrix.copy()
 temp["Uploaded"]=temp[REQUIRED_DOCS].sum(axis=1)
 temp["% Complete"]=(temp["Uploaded"]/len(REQUIRED_DOCS)*100).astype(int)
 st.bar_chart(temp["% Complete"])
