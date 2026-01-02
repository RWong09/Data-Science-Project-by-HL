import streamlit as st
import pandas as pd
from recommender import (
    recommend_districts,
    highest_lowest_salary_districts,
    highest_lowest_house_price
)

st.set_page_config(
    page_title="Malaysia Living Place Recommendation System",
    layout="wide"
)

st.title("Malaysia Living Place Recommendation System")

#Load data
@st.cache_data
def load_data():
    job_df = pd.read_csv("job_scores.csv")
    house_df = pd.read_csv("house_scores.csv")
    district_df = pd.read_csv("district_scores.csv")
    #Load raw house data for accurate price averages/display
    try:
        house_raw = pd.read_csv("house_data_cleaned.csv")
    except Exception:
        house_raw = None
    return job_df, house_df, district_df, house_raw

job_df, house_df, district_df, house_raw = load_data()

#Section 1: Top Districts to Live
st.header("Top 5 Recommended Districts to Live")

job_weight = st.slider("Job importance", 0.0, 1.0, 0.5)
house_weight = 1 - job_weight

top_districts = recommend_districts(
    district_df,
    job_weight=job_weight,
    house_weight=house_weight
)

st.dataframe(top_districts)

#Section 2: Salary-based District Ranking
st.header("Salary Ranking by District")

salary_mode = st.radio(
    "View districts with:",
    ["highest", "lowest"],
    horizontal=True
)

salary_rank = highest_lowest_salary_districts(
    job_df,
    mode=salary_mode
)

st.dataframe(salary_rank)

#Section 3: House Rental Price Ranking
st.header("House Rental Price Ranking")

house_types = ["All"] + sorted(house_df["Type"].dropna().unique().tolist())
selected_type = st.selectbox("Select house type", house_types)

price_mode = st.radio(
    "View house rental prices:",
    ["lowest", "highest"],
    horizontal=True,
    key="price_mode"
)

house_rank = highest_lowest_house_price(
    house_df,
    house_type=None if selected_type == "All" else selected_type,
    mode=price_mode,
    house_raw_df=house_raw
)

st.dataframe(house_rank)
