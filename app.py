import streamlit as st
import pandas as pd
import sqlite3
from pathlib import Path

DB = Path("fpo_income.db")

st.set_page_config(page_title="FPO Income Measurement", layout="wide")

def init_db():
    con = sqlite3.connect(DB)
    con.execute("""CREATE TABLE IF NOT EXISTS fpo_income (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fpo_name TEXT,
        location TEXT,
        baseline_income REAL,
        demand_services_income REAL,
        chc_income REAL,
        marketing_income REAL,
        other_intervention_income REAL
    )""")
    con.commit()
    con.close()

def get_data():
    con = sqlite3.connect(DB)
    df = pd.read_sql_query("SELECT * FROM fpo_income", con)
    con.close()
    return df

def add_record(values):
    con = sqlite3.connect(DB)
    con.execute("""INSERT INTO fpo_income
        (fpo_name, location, baseline_income, demand_services_income,
         chc_income, marketing_income, other_intervention_income)
         VALUES (?, ?, ?, ?, ?, ?, ?)""", values)
    con.commit()
    con.close()

init_db()

st.title("Developing an algorithm/programme to measure increase in income of FPOs on account of project interventions")
st.caption("FPO income measurement dashboard")

with st.sidebar:
    st.header("Add FPO Data")
    with st.form("fpo_form"):
        name = st.text_input("FPO Name")
        location = st.text_input("Location")
        baseline = st.number_input("Income before intervention (₹)", min_value=0.0, step=1000.0)
        demand = st.number_input("Demand-based services income (₹)", min_value=0.0, step=1000.0)
        chc = st.number_input("CHC income (₹)", min_value=0.0, step=1000.0)
        marketing = st.number_input("Produce marketing income (₹)", min_value=0.0, step=1000.0)
        other = st.number_input("Other intervention income (₹)", min_value=0.0, step=1000.0)
        submitted = st.form_submit_button("Add FPO")
        if submitted:
            if not name:
                st.error("Enter an FPO name.")
            else:
                add_record((name, location, baseline, demand, chc, marketing, other))
                st.success("FPO record added.")

df = get_data()

if df.empty:
    st.info("No FPO records yet. Add data using the sidebar.")
else:
    df["intervention_income"] = (
        df["demand_services_income"] + df["chc_income"] +
        df["marketing_income"] + df["other_intervention_income"]
    )
    df["income_after_intervention"] = df["baseline_income"] + df["intervention_income"]
    df["income_increase"] = df["income_after_intervention"] - df["baseline_income"]
    df["increase_percent"] = df.apply(
        lambda r: (r["income_increase"] / r["baseline_income"] * 100)
        if r["baseline_income"] else 0, axis=1
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("FPOs", len(df))
    c2.metric("Baseline Income", f"₹{df['baseline_income'].sum():,.0f}")
    c3.metric("Intervention Income", f"₹{df['intervention_income'].sum():,.0f}")
    c4.metric("Income Increase", f"₹{df['income_increase'].sum():,.0f}")

    st.subheader("FPO-wise Results")
    display = df[[
        "fpo_name", "location", "baseline_income",
        "intervention_income", "income_after_intervention",
        "income_increase", "increase_percent"
    ]].copy()
    display.columns = [
        "FPO", "Location", "Before Intervention",
        "Intervention Income", "After Intervention",
        "Income Increase", "Increase %"
    ]
    st.dataframe(display, use_container_width=True)

    st.subheader("Income Comparison")
    chart = display.set_index("FPO")[["Before Intervention", "After Intervention"]]
    st.bar_chart(chart)

    st.subheader("Intervention-wise Contribution")
    contribution = pd.DataFrame({
        "Intervention": [
            "Demand-based Services", "Custom Hiring Centre",
            "Produce Marketing", "Other Interventions"
        ],
        "Income": [
            df["demand_services_income"].sum(),
            df["chc_income"].sum(),
            df["marketing_income"].sum(),
            df["other_intervention_income"].sum()
        ]
    }).set_index("Intervention")
    st.bar_chart(contribution)

    st.download_button(
        "Download Results CSV",
        display.to_csv(index=False).encode("utf-8"),
        "fpo_income_results.csv",
        "text/csv"
    )
