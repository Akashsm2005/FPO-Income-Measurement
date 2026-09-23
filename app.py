import streamlit as st
import sqlite3
import pandas as pd
import hashlib
from datetime import date

DB = "fpo_complete.db"

st.set_page_config(
    page_title="FPO Income Impact",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

def db():
    return sqlite3.connect(DB, check_same_thread=False)

def hash_pin(pin):
    return hashlib.sha256(pin.encode()).hexdigest()

def init_db():
    c = db()
    c.execute("""CREATE TABLE IF NOT EXISTS farmers(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        farmer_code TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        phone TEXT,
        village TEXT,
        fpo_name TEXT,
        crop TEXT,
        pin_hash TEXT,
        created_at TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS income_records(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        farmer_code TEXT NOT NULL,
        intervention TEXT NOT NULL,
        before_income REAL NOT NULL,
        after_income REAL NOT NULL,
        intervention_income REAL NOT NULL,
        intervention_cost REAL NOT NULL,
        record_date TEXT NOT NULL,
        notes TEXT
    )""")
    c.commit()
    c.close()

def money(v):
    return f"₹{v:,.0f}"

def clear_login():
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.session_state.farmer_code = None

init_db()

if "logged_in" not in st.session_state:
    clear_login()

# Presentation styling
st.markdown("""
<style>
.block-container {padding-top: 2rem; padding-bottom: 3rem;}
.hero {
    padding: 2rem 2.2rem;
    border-radius: 20px;
    border: 1px solid rgba(128,128,128,.25);
    background: linear-gradient(135deg, rgba(46,125,50,.10), rgba(255,193,7,.10));
    margin-bottom: 1.5rem;
}
.hero h1 {font-size: 2.5rem; margin-bottom: .4rem;}
.hero p {font-size: 1.05rem; color: #666;}
.feature {
    padding: 1.1rem;
    border-radius: 15px;
    border: 1px solid rgba(128,128,128,.25);
    min-height: 135px;
}
.section-title {font-size: 1.35rem; font-weight: 700; margin-top: .5rem;}
.muted {color:#777;}
</style>
""", unsafe_allow_html=True)

# ================= PUBLIC HOME / LOGIN =================
if not st.session_state.logged_in:
    st.markdown("""
    <div class="hero">
      <h1>🌾 FPO Income Impact Measurement</h1>
      <p>Digital platform to capture individual farmer income changes and measure project intervention impact at FPO level.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🎯 Project Objective")
    st.write(
        "The system collects structured farmer-level income information before and after "
        "project interventions, calculates the observed income change, and aggregates "
        "the results for an FPO-level impact view."
    )

    f1,f2,f3 = st.columns(3)
    with f1:
        st.markdown('<div class="feature"><h3>👨‍🌾 Farmer Module</h3><p>Create an account, maintain a profile and submit intervention-linked income records.</p></div>', unsafe_allow_html=True)
    with f2:
        st.markdown('<div class="feature"><h3>🏢 FPO Module</h3><p>View farmer records, aggregate income changes and monitor intervention performance.</p></div>', unsafe_allow_html=True)
    with f3:
        st.markdown('<div class="feature"><h3>📊 Impact Reports</h3><p>Compare before and after income, analyze interventions and export reports.</p></div>', unsafe_allow_html=True)

    st.markdown("### 🔄 System Workflow")
    st.progress(100)
    st.markdown("**Farmer Registration → Baseline Income → Project Intervention → Post-Intervention Income → Individual Analysis → FPO Aggregation → Report**")

    st.divider()
    login_tab, register_tab, info_tab = st.tabs(["🔐 Login", "👨‍🌾 New Farmer", "ℹ️ Project Information"])

    with login_tab:
        role = st.selectbox("Login as", ["Farmer", "FPO Admin"])
        if role == "Farmer":
            code = st.text_input("Farmer ID", placeholder="F001")
            pin = st.text_input("PIN", type="password", placeholder="4-digit PIN")
            if st.button("Login as Farmer", type="primary"):
                c=db()
                row=c.execute("SELECT farmer_code,pin_hash FROM farmers WHERE farmer_code=?", (code.strip(),)).fetchone()
                c.close()
                if row and row[1] == hash_pin(pin):
                    st.session_state.logged_in=True
                    st.session_state.user_role="Farmer"
                    st.session_state.farmer_code=row[0]
                    st.rerun()
                st.error("Invalid Farmer ID or PIN.") if not row or row[1] != hash_pin(pin) else None
        else:
            user=st.text_input("Admin Username", value="admin")
            password=st.text_input("Admin Password", type="password")
            st.caption("Demo credentials: admin / admin123")
            if st.button("Login as FPO Admin", type="primary"):
                if user=="admin" and password=="admin123":
                    st.session_state.logged_in=True
                    st.session_state.user_role="FPO Admin"
                    st.session_state.farmer_code=None
                    st.rerun()
                else:
                    st.error("Invalid administrator credentials.")

    with register_tab:
        with st.form("new_farmer"):
            st.subheader("Create Farmer Account")
            a,b=st.columns(2)
            with a:
                code=st.text_input("Farmer ID *", placeholder="F001")
                name=st.text_input("Full Name *")
                phone=st.text_input("Mobile Number")
                village=st.text_input("Village")
            with b:
                fpo=st.text_input("FPO Name", value="Demo FPO")
                crop=st.selectbox("Primary Crop",["Rice","Cotton","Maize","Pulses","Vegetables","Other"])
                pin=st.text_input("Create 4-digit PIN *", type="password")
                confirm=st.text_input("Confirm PIN *", type="password")
            create=st.form_submit_button("Create Farmer Account",type="primary")
        if create:
            if not code or not name or not pin:
                st.error("Farmer ID, name and PIN are required.")
            elif not pin.isdigit() or len(pin)!=4:
                st.error("PIN must contain exactly 4 digits.")
            elif pin!=confirm:
                st.error("PINs do not match.")
            else:
                try:
                    c=db()
                    c.execute("""INSERT INTO farmers
                    (farmer_code,name,phone,village,fpo_name,crop,pin_hash,created_at)
                    VALUES(?,?,?,?,?,?,?,?)""",
                    (code.strip(),name.strip(),phone.strip(),village.strip(),fpo.strip(),crop,hash_pin(pin),date.today().isoformat()))
                    c.commit(); c.close()
                    st.success("Farmer account created successfully. Open Login to continue.")
                except sqlite3.IntegrityError:
                    st.error("That Farmer ID already exists.")

    with info_tab:
        st.markdown("### Problem Statement")
        st.write("Develop an algorithm/programme to measure increase in income of FPOs on account of project interventions.")
        st.markdown("### Proposed Solution")
        st.write("Capture individual farmer-level records and aggregate verified records to produce an FPO income-impact dashboard.")
        st.markdown("### Core Algorithm")
        st.code("""Income Increase = Income After Intervention - Income Before Intervention
Increase % = (Income Increase / Income Before Intervention) × 100
Net Benefit = Income Increase - Intervention Cost
FPO metrics = aggregation of individual farmer records""")
        st.markdown("### Technology Stack")
        st.write("Python • Streamlit • SQLite • Pandas • Data Visualization")
        st.info("For a formal evaluation, entered income data should be supported by verified project records and an appropriate evaluation methodology.")

    st.caption("Academic prototype • FPO Income Impact Measurement")
    st.stop()

# ================= SIDEBAR =================
with st.sidebar:
    st.markdown("## 🌾 FPO Income Impact")
    if st.session_state.user_role=="Farmer":
        st.caption(f"Farmer ID: {st.session_state.farmer_code}")
        module=st.radio("Navigation",["Dashboard","Income Record","Profile"])
    else:
        st.caption("FPO Administrator")
        module=st.radio("Navigation",["Dashboard","Farmers","Reports","Methodology"])
    st.divider()
    if st.button("🚪 Logout"):
        clear_login()
        st.rerun()

# ================= FARMER =================
if st.session_state.user_role=="Farmer":
    code=st.session_state.farmer_code
    c=db()
    profile=pd.read_sql_query("SELECT * FROM farmers WHERE farmer_code=?",c,params=(code,))
    records=pd.read_sql_query("SELECT * FROM income_records WHERE farmer_code=? ORDER BY record_date DESC,id DESC",c,params=(code,))
    c.close()
    if profile.empty:
        st.error("Farmer account not found.")
        st.stop()
    p=profile.iloc[0]

    if module=="Dashboard":
        st.markdown(f'<div class="hero"><h1>Welcome, {p["name"]} 👋</h1><p>Your individual farmer income-impact dashboard</p></div>',unsafe_allow_html=True)
        if records.empty:
            a,b,c1,d=st.columns(4)
            a.metric("Income Records",0)
            b.metric("Baseline Income","₹0")
            c1.metric("After Income","₹0")
            d.metric("Income Increase","₹0")
            st.info("You have no income records yet. Use **Income Record** to add your first intervention.")
        else:
            before=records.before_income.sum()
            after=records.after_income.sum()
            increase=records.intervention_income.sum()
            costs=records.intervention_cost.sum()
            inc_pct=increase/before*100 if before else 0
            net=increase-costs
            a,b,c1,d,e=st.columns(5)
            a.metric("Records",len(records))
            b.metric("Baseline Income",money(before))
            c1.metric("After Income",money(after))
            d.metric("Income Increase",money(increase),delta=f"{inc_pct:.1f}%")
            e.metric("Net Benefit",money(net))
            st.divider()
            l,r=st.columns(2)
            with l:
                st.subheader("Income Before vs After")
                st.bar_chart(pd.DataFrame({"Income":[before,after]},index=["Before","After"]))
            with r:
                st.subheader("Intervention Impact")
                st.bar_chart(records.groupby("intervention")["intervention_income"].sum())
            st.subheader("Income History")
            st.dataframe(records[["record_date","intervention","before_income","after_income","intervention_income","intervention_cost"]],use_container_width=True,hide_index=True)

    elif module=="Income Record":
        st.markdown('<div class="hero"><h1>💰 Record Income Impact</h1><p>Enter income data associated with a project intervention.</p></div>',unsafe_allow_html=True)
        with st.form("income"):
            intervention=st.selectbox("Project Intervention",["FPO produce marketing","Custom Hiring Centre (CHC)","Demand-based service","Input support","Value addition","Training / capacity building","Other"])
            a,b,c1=st.columns(3)
            before=a.number_input("Income before (₹)",min_value=0.0,step=1000.0)
            after=b.number_input("Income after (₹)",min_value=0.0,step=1000.0)
            cost=c1.number_input("Intervention cost (₹)",min_value=0.0,step=500.0)
            notes=st.text_area("Evidence / notes")
            save=st.form_submit_button("Save Income Record",type="primary")
        if save:
            increase=after-before
            c=db()
            c.execute("""INSERT INTO income_records
            (farmer_code,intervention,before_income,after_income,intervention_income,intervention_cost,record_date,notes)
            VALUES(?,?,?,?,?,?,?,?)""",
            (code,intervention,before,after,increase,cost,date.today().isoformat(),notes))
            c.commit(); c.close()
            a,b,c1=st.columns(3)
            a.metric("Income Increase",money(increase))
            b.metric("Increase %",f"{increase/before*100:.1f}%" if before else "0.0%")
            c1.metric("Net Benefit",money(increase-cost))
            st.success("Income record saved successfully.")

    else:
        st.markdown('<div class="hero"><h1>👤 Farmer Profile</h1><p>Your registered information</p></div>',unsafe_allow_html=True)
        a,b=st.columns(2)
        with a:
            st.text_input("Farmer ID",p.farmer_code,disabled=True)
            st.text_input("Full Name",p["name"],disabled=True)
            st.text_input("Mobile",p["phone"],disabled=True)
            st.text_input("Village",p["village"],disabled=True)
        with b:
            st.text_input("FPO",p["fpo_name"],disabled=True)
            st.text_input("Primary Crop",p["crop"],disabled=True)
            st.text_input("Account Created",p["created_at"],disabled=True)
        st.info("Profile editing can be added in a later release.")

# ================= ADMIN =================
else:
    c=db()
    farmers=pd.read_sql_query("SELECT * FROM farmers ORDER BY farmer_code",c)
    records=pd.read_sql_query("SELECT * FROM income_records ORDER BY record_date DESC,id DESC",c)
    c.close()
    total_before=records.before_income.sum() if not records.empty else 0
    total_after=records.after_income.sum() if not records.empty else 0
    total_inc=records.intervention_income.sum() if not records.empty else 0
    total_cost=records.intervention_cost.sum() if not records.empty else 0
    inc_pct=total_inc/total_before*100 if total_before else 0
    net=total_inc-total_cost

    if module=="Dashboard":
        st.markdown('<div class="hero"><h1>🏢 FPO Admin Dashboard</h1><p>Organization-level income impact overview</p></div>',unsafe_allow_html=True)
        a,b,c1,d,e=st.columns(5)
        a.metric("Farmers",len(farmers))
        b.metric("Baseline Income",money(total_before))
        c1.metric("After Income",money(total_after))
        d.metric("Total Increase",money(total_inc),delta=f"{inc_pct:.1f}%")
        e.metric("Net Benefit",money(net))
        if records.empty:
            st.info("No income records available yet.")
        else:
            l,r=st.columns(2)
            with l:
                st.subheader("FPO Income Comparison")
                st.bar_chart(pd.DataFrame({"Income":[total_before,total_after]},index=["Before","After"]))
            with r:
                st.subheader("Intervention-wise Impact")
                st.bar_chart(records.groupby("intervention")["intervention_income"].sum().sort_values(ascending=False))
            merged=records.groupby("farmer_code").agg(
                baseline_income=("before_income","sum"),
                after_income=("after_income","sum"),
                income_increase=("intervention_income","sum"),
                intervention_cost=("intervention_cost","sum")).reset_index()
            merged["increase_percent"]=(merged.income_increase/merged.baseline_income*100).where(merged.baseline_income!=0,0)
            merged["net_benefit"]=merged.income_increase-merged.intervention_cost
            merged=merged.merge(farmers[["farmer_code","name","village","crop"]],on="farmer_code",how="left")
            st.subheader("Farmer-wise Impact")
            st.dataframe(merged[["farmer_code","name","village","crop","baseline_income","after_income","income_increase","increase_percent","intervention_cost","net_benefit"]],use_container_width=True,hide_index=True)

    elif module=="Farmers":
        st.markdown('<div class="hero"><h1>👨‍🌾 Farmer Management</h1><p>Search and review registered farmers</p></div>',unsafe_allow_html=True)
        search=st.text_input("🔎 Search Farmer ID, name or village")
        view=farmers.copy()
        if search:
            view=view[
                view.farmer_code.str.contains(search,case=False,na=False) |
                view.name.str.contains(search,case=False,na=False) |
                view.village.str.contains(search,case=False,na=False)]
        st.dataframe(view[["farmer_code","name","phone","village","fpo_name","crop","created_at"]],use_container_width=True,hide_index=True)

    elif module=="Reports":
        st.markdown('<div class="hero"><h1>📑 Reports</h1><p>Download project income-impact data for further analysis.</p></div>',unsafe_allow_html=True)
        if records.empty:
            st.info("No records available.")
        else:
            st.download_button("⬇️ Download All Income Records",records.to_csv(index=False).encode(),"All_Farmer_Income_Records.csv","text/csv")
            merged=records.groupby("farmer_code").agg(
                baseline_income=("before_income","sum"),after_income=("after_income","sum"),
                income_increase=("intervention_income","sum"),intervention_cost=("intervention_cost","sum")).reset_index()
            merged["increase_percent"]=(merged.income_increase/merged.baseline_income*100).where(merged.baseline_income!=0,0)
            merged["net_benefit"]=merged.income_increase-merged.intervention_cost
            merged=merged.merge(farmers[["farmer_code","name","village","fpo_name","crop"]],on="farmer_code",how="left")
            st.dataframe(merged,use_container_width=True,hide_index=True)
            st.download_button("⬇️ Download FPO Impact Report",merged.to_csv(index=False).encode(),"FPO_Income_Impact_Report.csv","text/csv")

    else:
        st.markdown('<div class="hero"><h1>🧮 Methodology</h1><p>How the system measures income impact</p></div>',unsafe_allow_html=True)
        st.markdown("### 1. Collect")
        st.write("Capture farmer identity, crop, FPO and intervention-linked income information.")
        st.markdown("### 2. Calculate")
        st.code("""Income Increase = After Income - Before Income
Increase % = (Income Increase / Before Income) × 100
Net Benefit = Income Increase - Intervention Cost""")
        st.markdown("### 3. Aggregate")
        st.write("Individual farmer records are aggregated to produce FPO-level totals and intervention-wise summaries.")
        st.markdown("### 4. Report")
        st.write("The application provides dashboards and downloadable CSV reports.")
        st.warning("The application reports observed differences in entered records. Formal causal attribution requires verified data and an appropriate evaluation design.")
