import streamlit as st
import pandas as pd
from recommender import recommend_districts, rename_columns_for_display

st.set_page_config(
    page_title="Malaysia District Living Recommendation System",
    layout="wide"
)

st.title("Malaysia District Living Recommendation System")

st.header("🌏 District Recommendation by District & State")

@st.cache_data
def load_data():
    return (
        pd.read_csv("district_scores.csv"),
        pd.read_csv("job_scores.csv"),
        pd.read_csv("house_scores.csv"),
        pd.read_csv("house_data_cleaned.csv")
    )

district_df, job_df, house_df, house_raw = load_data()

# Column rename mapping
column_rename = {
    'title': 'Job Title',
    'salary': 'Salary',
    'contract_type_name': 'Contract Type',
    'state': 'State',
    'district': 'District',
    'job_score': 'Job Score',
    'house_score': 'House Score'
}

job_weight = st.slider("Job importance", 0.0, 1.0, 0.5)
house_weight = 1 - job_weight

top_places = recommend_districts(
    district_df,
    job_weight=job_weight,
    house_weight=house_weight
)

st.subheader("Top 5 Recommended Districts")
st.dataframe(top_places)

houses_to_show = st.selectbox("Houses to show", [5, "All"]) 
jobs_to_show = st.selectbox("Jobs to show", [5, "All"]) 

for _, row in top_places.iterrows():
    st.markdown(f"### 📍 {row['District']}, {row['State']}")

    jobs = (
        job_df[
            (job_df["state"] == row["State"]) &
            (job_df["district"] == row["District"])
        ]
        .sort_values("job_score", ascending=False)
    )
    
    houses = (
        house_df[
            (house_df["State"] == row["State"]) &
            (house_df["District"] == row["District"]) 
        ]
        .sort_values("house_score", ascending=False)
    )
    #Merge selected top scored houses with raw cleaned data so display shows raw values
    if not houses.empty and isinstance(house_raw, pd.DataFrame):
        #Prefer merging on Name + State + District when available
        if {"Name", "State", "District"}.issubset(house_raw.columns):
            houses = houses.merge(
                house_raw,
                on=["Name", "State", "District"],
                how="left",
                suffixes=("_scaled", "")
            )
        elif "Name" in house_raw.columns:
            houses = houses.merge(house_raw, on=["Name"], how="left", suffixes=("_scaled", ""))

        #After merge, drop scaled columns (those with _scaled) or prefer raw values
        for col in ["Price", "Size", "Number of beds", "Number of bathrooms", "Type", "Furnished Status"]:
            scaled_col = f"{col}_scaled"
            if scaled_col in houses.columns and col in houses.columns:
                #Raw column (from house_raw) is present and scaled version exists: drop scaled
                houses = houses.drop(columns=[scaled_col])
            elif scaled_col in houses.columns and col not in houses.columns:
                #Only scaled exists: rename to base name for display
                houses = houses.rename(columns={scaled_col: col})

    if houses_to_show != "All":
        houses = houses.head(int(houses_to_show))
        
    if jobs_to_show != "All":
        jobs = jobs.head(int(jobs_to_show))
        
    st.markdown("**Top Jobs**")
    st.dataframe(jobs[["title", "salary", "contract_type_name", "job_score"]].rename(columns=column_rename))

    st.markdown("**Top Houses**")
    #Ensure the display columns exist after merging; fall back to available ones
    display_cols = [c for c in ["Name", "Size", "Price", "Number of beds", "Number of bathrooms", "Type", "house_score"] if c in houses.columns]
    st.dataframe(houses[display_cols].rename(columns=column_rename))
