import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Malaysia District Living Recommendation System",
    layout="wide"
)

st.title("Malaysia District Living Recommendation System")

st.header("💼 Job Recommendation System")

@st.cache_data
def load_jobs():
    return pd.read_csv("job_scores.csv")

job_df = load_jobs()

#Column rename mapping
column_rename = {
    'title' : 'Job Title',
    'salary': 'Salary',
    'contract_type_name': 'Contract Type',
    'state': 'State',
    'district': 'District',
    'job_score': 'Job Score'
}

title_search = st.text_input("Search job title (optional)")

state_options = sorted(job_df["state"].dropna().astype(str).unique().tolist())
state = st.selectbox("State", ["All"] + state_options)

district_options = sorted(job_df["district"].dropna().astype(str).unique().tolist())
district = st.selectbox("District", ["All"] + district_options)

contract_options = sorted(job_df["contract_type_name"].dropna().astype(str).unique().tolist())
contract = st.selectbox("Contract Type", ["All"] + contract_options)

salary_range = st.slider(
    "Salary Range",
    int(job_df["salary"].min()),
    int(job_df["salary"].max()),
    (
        int(job_df["salary"].min()),
        int(job_df["salary"].max())
    )
)

top_n = st.selectbox("Results to show", [5, 10, "All"])

df = job_df.copy()

if title_search:
    df = df[df["title"].str.contains(title_search, case=False, na=False)]

if state != "All":
    df = df[df["state"] == state]

if district != "All":
    df = df[df["district"] == district]

if contract != "All":
    df = df[df["contract_type_name"] == contract]

df = df[
    (df["salary"] >= salary_range[0]) &
    (df["salary"] <= salary_range[1])
]

df = df.sort_values("job_score", ascending=False)

if top_n != "All":
    df = df.head(top_n)

st.subheader("Recommended Jobs")
st.dataframe(
    df[[
        "title",
        "salary",
        "contract_type_name",
        "state",
        "district",
        "job_score"
    ]].rename(columns=column_rename)
)
