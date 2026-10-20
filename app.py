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

import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="SQMS Supplier Portal",
    layout="wide",
    page_icon="🌮"
)

# --- VISUAL THEME (Navy + Teal from your reference) ---
st.markdown("""
<style>
.stApp { background-color: #0e2f4f; }
h1, h2, h3, h4, p, label, div[data-testid="stCaptionContainer"] { color: #e8f1f8 !important; }
div[data-testid="stMetric"] {
    background-color: #14395e;
    border: 1px solid #1e4a73;
    padding: 20px;
    border-radius: 12px;
}
div[data-testid="stMetricValue"] { color: #2ee5c8 !important; font-size: 32px; }
div[data-testid="stMetricLabel"] { color: #a8c0d6 !important; }
[data-testid="stDataFrame"] { background-color: #14395e; border-radius: 12px; }
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.title("SQMS Supplier Portal - Food Safety Compliance")
st.caption("IT-Ready Version - Supplier Isolation + No Styler Error - Visual Edition")

# --- YOUR EXACT DATA FROM SCREENSHOT ---
data = [
    {
        "supplier_distributor": "Savannah Fine Chemical (Pty) Ltd",
        "manufacturer": "AARTI INDUSTRIES LTD",
        "rm_code": 918861,
        "rm_description": "CAFFEINE ANHYDROUS",
        "origin_country": "IN",
        "vendor_code": 328628,
        "mfg_code": 327264,
        "compliance": 92
    },
    {
        "supplier_distributor": "CJP Chemicals (PTY) Ltd",
        "manufacturer": "DONGXIAO BIOTECHNOLOGY CO LTD",
        "rm_code": 956710,
        "rm_description": "PROTEA MALTODEXTRIN 20",
        "origin_country": "CN",
        "vendor_code": 328629,
        "mfg_code": 307114,
        "compliance": 88
    },
    {
        "supplier_distributor": "CLIVE TEUBES (PTY) LTD.",
        "manufacturer": "CLIVE TEUBES (PTY) LTD.",
        "rm_code": 968192,
        "rm_description": "PROTEA OT ORANGE TERPENES",
        "origin_country": "ZA",
        "vendor_code": 300560,
        "mfg_code": 300560,
        "compliance": 90
    },
]
df = pd.DataFrame(data)

# --- KPIs (Your numbers: 90% / 2 / 1) ---
avg_comp = df["compliance"].mean()
approved = len(df[df["compliance"] >= 90])
pending = len(df[df["compliance"] < 90])

c1, c2, c3 = st.columns(3)
c1.metric("Avg Compliance", f"{avg_comp:.0f}%")
c2.metric("Approved", f"{approved}")
c3.metric("Pending", f"{pending}")

st.write("")

# --- FILTERS (like your reference dashboard) ---
col_search, col_status = st.columns([2,1])
search = col_search.text_input("🔍 Search supplier, RM code, or description", "")
status_filter = col_status.selectbox("Filter by Risk", ["All", "Green ≥90%", "Yellow 70-89%", "Red <70%"])

filtered = df.copy()
if search:
    filtered = filtered[
        filtered["supplier_distributor"].str.contains(search, case=False) |
        filtered["rm_description"].str.contains(search, case=False) |
        filtered["rm_code"].astype(str).str.contains(search)
    ]

if status_filter == "Green ≥90%":
    filtered = filtered[filtered["compliance"] >= 90]
elif status_filter == "Yellow 70-89%":
    filtered = filtered[(filtered["compliance"] >= 70) & (filtered["compliance"] < 90)]
elif status_filter == "Red <70%":
    filtered = filtered[filtered["compliance"] < 70]

# --- COLOR CODING FUNCTION ---
def color_compliance(val):
    if val >= 90:
        return 'background-color: #2ee5c8; color: black; font-weight: bold; border-radius: 4px;'
    elif val >= 70:
        return 'background-color: #facc15; color: black; font-weight: bold; border-radius: 4px;'
    else:
        return 'background-color: #f87171; color: white; font-weight: bold; border-radius: 4px;'

# Add status emoji
filtered_display = filtered.copy()
filtered_display["status"] = filtered_display["compliance"].apply(
    lambda x: f"🟢 {x}%" if x >= 90 else (f"🟡 {x}%" if x >= 70 else f"🔴 {x}%")
)

st.dataframe(
    filtered_display.style.applymap(color_compliance, subset=["compliance"]),
    use_container_width=True,
    hide_index=True
)

# --- Supplier Isolation Toggle ---
st.divider()
isolation = st.toggle("🔒 Supplier Isolation Mode (each supplier sees only own row)")
if isolation:
    st.info("Isolation ON: In production, this filters by logged-in supplier email. Demo shows first row only.")
    st.dataframe(filtered_display.head(1).style.applymap(color_compliance, subset=["compliance"]), use_container_width=True, hide_index=True)
