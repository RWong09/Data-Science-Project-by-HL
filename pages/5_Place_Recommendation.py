import streamlit as st
import pandas as pd
from recommender import recommend_districts

st.set_page_config(
    page_title="Malaysia Living Place Recommendation System",
    layout="wide"
)

st.title("Malaysia Living Place Recommendation System")

st.header("🌏 Place Recommendation by District & State")

@st.cache_data
def load_data():
    return (
        pd.read_csv("district_scores.csv"),
        pd.read_csv("job_scores.csv"),
        pd.read_csv("house_scores.csv"),
        pd.read_csv("house_data_cleaned.csv")
    )

district_df, job_df, house_df, house_raw = load_data()

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

for _, row in top_places.iterrows():
    st.markdown(f"### 📍 {row['district']}, {row['state']}")

    jobs = (
        job_df[
            (job_df["state"] == row["state"]) &
            (job_df["district"] == row["district"])
        ]
        .sort_values("job_score", ascending=False)
        .head(5)
    )
    
    houses = (
        house_df[
            (house_df["State"] == row["state"]) &
            (house_df["District"] == row["district"]) 
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
        
    st.markdown("**Top Jobs**")
    st.dataframe(jobs[["title", "salary", "contract_type_name", "job_score"]])

    st.markdown("**Top Houses**")
    #Ensure the display columns exist after merging; fall back to available ones
    display_cols = [c for c in ["Name", "Size", "Price", "Number of beds", "Number of bathrooms", "Type", "house_score"] if c in houses.columns]
    st.dataframe(houses[display_cols])
