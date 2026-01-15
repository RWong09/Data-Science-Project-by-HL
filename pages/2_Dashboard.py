import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(layout="wide")

st.title("📊 Malaysia Living Data Dashboard")

@st.cache_data
def load_data():
    jobs = pd.read_csv("job_scores.csv")
    houses = pd.read_csv("house_data_cleaned.csv")
    return jobs, houses

job_df, house_df = load_data()

#Column rename mapping for display
column_rename = {
    'contract_type_name': 'Contract Type',
    'state': 'State',
    'district': 'District'
}

st.sidebar.header("🔎 Filters")

#Let user choose which dashboard filters to show. "Both Dashboards" shows only the State filter.
dashboard_filter = st.sidebar.selectbox(
    "Dashboard Filters",
    ["Both Dashboards", "Job Dashboard", "House Dashboard"],
    index=0,
)

#State filter is always available (applies to both datasets)
state_options = sorted(
    pd.concat([
        job_df["state"].dropna().astype(str),
        house_df["State"].dropna().astype(str),
    ]).unique()
)
selected_states = st.sidebar.multiselect(
    "Select State(s)",
    state_options,
    default=state_options,
)

if not selected_states:
    selected_states = state_options

#Conditional filters shown only when a specific dashboard is chosen
selected_contracts = None
selected_furnished = None
selected_house_types = None

if dashboard_filter == "Job Dashboard":
    contract_opts = sorted(job_df["contract_type_name"].dropna().astype(str).unique())
    selected_contracts = st.sidebar.multiselect(
        "Contract Type",
        contract_opts,
        default=contract_opts,
    )
    if not selected_contracts:
        selected_contracts = contract_opts

elif dashboard_filter == "House Dashboard":
    furnished_opts = sorted(house_df["Furnished Status"].dropna().astype(str).unique())
    selected_furnished = st.sidebar.multiselect(
        "Furnished Status",
        furnished_opts,
        default=furnished_opts,
    )
    if not selected_furnished:
        selected_furnished = furnished_opts

    type_opts = sorted(house_df["Type"].dropna().astype(str).unique())
    selected_house_types = st.sidebar.multiselect(
        "House Type",
        type_opts,
        default=type_opts,
    )
    if not selected_house_types:
        selected_house_types = type_opts

#Apply filters to create dataframes used by the charts
job_df_f = job_df[job_df["state"].isin(selected_states)]
if selected_contracts is not None:
    job_df_f = job_df_f[job_df_f["contract_type_name"].isin(selected_contracts)]

house_df_f = house_df[house_df["State"].isin(selected_states)]
if selected_furnished is not None:
    house_df_f = house_df_f[house_df_f["Furnished Status"].isin(selected_furnished)]
if selected_house_types is not None:
    house_df_f = house_df_f[house_df_f["Type"].isin(selected_house_types)]
job_tab, house_tab = st.tabs(["Job Dashboard", "House Dashboard"]) 

with job_tab:
    #Dashboard 1: Job Dashboard
    st.markdown(
        "<h2 style='text-align: center;'>💼 Job in Malaysia Dashboard</h2>",
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    #Number of jobs
    with col1:
        st.metric("Total Number of Jobs", f"{len(job_df_f):,}")
        st.metric("Average Salary (RM)", f"{job_df_f['salary'].mean():,.2f}")

    #Jobs by State
    jobs_by_state = (
        job_df_f.groupby("state")
        .size()
        .reset_index(name="job_count")
        .sort_values("job_count", ascending=False)
        .rename(columns={'state': 'State'})
    )

    fig_jobs_state = px.bar(
        jobs_by_state,
        x="job_count",
        y="State",
        orientation="h",
        title="Number of Jobs by State",
        labels={"job_count": "Number of Jobs", "State": "State"},
        color="job_count",
        color_continuous_scale="Inferno"
    )
    fig_jobs_state.update_layout(yaxis=dict(autorange="reversed"))

    with col2:
        st.plotly_chart(fig_jobs_state, use_container_width=True)

    #Contract Type
    col3, col4 = st.columns(2)

    contract_counts = (
        job_df_f.groupby("contract_type_name")
        .size()
        .reset_index(name="count")
        .rename(columns={'contract_type_name': 'Contract Type'})
    )

    fig_contract = px.pie(
        contract_counts,
        values="count",
        names="Contract Type",
        hole=0.45,
        title="Jobs by Contract Type"
    )

    with col3:
        st.plotly_chart(fig_contract, use_container_width=True)

    #Average Salary by State
    salary_state = (
        job_df_f.groupby("state")
        .salary.mean()
        .reset_index()
        .rename(columns={'state': 'State'})
    )

    fig_salary_tree = px.treemap(
        salary_state,
        path=["State"],
        values="salary",
        color="salary",
        title="Average Salary by State (RM)",
        color_continuous_scale="Viridis"
    )

    with col4:
        st.plotly_chart(fig_salary_tree, use_container_width=True)

with house_tab:
    #Dashboard 2: House Dashboard
    st.markdown(
        "<h2 style='text-align: center;'>🏠 House Rental in Malaysia Dashboard</h2>",
        unsafe_allow_html=True
    )

    col5, col6 = st.columns(2)

    #Number of house rentals
    with col5:
        st.metric("Total House Rentals", f"{len(house_df_f):,}")
        st.metric("Average Rental Price (RM)", f"{house_df_f['Price'].mean():,.2f}")
        st.metric("Average House Size (sqft)", f"{house_df_f['Size'].mean():,.2f}")
        
    #Furnished Status
    furnish_counts = (
        house_df_f.groupby("Furnished Status")
        .size()
        .reset_index(name="count")
    )

    fig_furnished = px.pie(
        furnish_counts,
        values="count",
        names="Furnished Status",
        title="Furnished Status Distribution"
    )

    with col6:
        st.plotly_chart(fig_furnished, use_container_width=True)

    #Size vs Beds and Bathrooms
    avg_by_beds = (
        house_df_f.groupby("Number of beds")
        .agg(
            avg_size=("Size", "mean"),
            count=("Size", "count")
        )
        .reset_index()
    )

    avg_by_baths = (
        house_df_f.groupby("Number of bathrooms")
        .agg(
            avg_size=("Size", "mean"),
            count=("Size", "count")
        )
        .reset_index()
    )

    fig_combo = go.Figure()

    fig_combo.add_trace(go.Bar(
        x=avg_by_beds["Number of beds"],
        y=avg_by_beds["avg_size"],
        name="Avg Size by Beds",
        yaxis="y2",
        opacity=0.7
    ))

    fig_combo.add_trace(go.Bar(
        x=avg_by_baths["Number of bathrooms"],
        y=avg_by_baths["avg_size"],
        name="Avg Size by Baths",
        yaxis="y2",
        opacity=0.8
    ))

    fig_combo.add_trace(go.Scatter(
        x=avg_by_beds["Number of beds"],
        y=avg_by_beds["count"],
        mode="lines+markers",
        name="House Count (Beds)",
        yaxis="y1",
        line=dict(width=3),
        marker=dict(size=8)
    ))

    fig_combo.update_layout(
        title="House Size vs Beds & Bathrooms",
        yaxis=dict(title="Number of Houses"),
        yaxis2=dict(
            title="Average Size (sqft)",
            overlaying="y",
            side="right",
            position=0.99
        ),
        barmode="group"
    )
    #Increase right margin so yaxis2 labels don't overlap and ensure line appears on top
    fig_combo.update_layout(margin=dict(r=20))

    st.plotly_chart(fig_combo, use_container_width=True)

    #House Type
    house_type_counts = (
        house_df_f.groupby("Type")
        .size()
        .reset_index(name="count")
        .sort_values("count")
    )
    
    fig_type = px.treemap(
        house_type_counts,
        path=["Type"],
        values="count",
        color="count",
        title="Number of House Rentals by Type",
        color_continuous_scale="Rainbow"
    )

    st.plotly_chart(fig_type, use_container_width=True)

    #Cheapest Average Rental by State
    avg_price_state = (
        house_df_f.groupby("State")
        .Price.mean()
        .reset_index()
        .sort_values("Price", ascending=False)
    )

    fig_price_state = px.bar(
        avg_price_state,
        x="Price",
        y="State",
        orientation="h",
        title="Cheapest Average House Rental by State (RM)",
        labels={"Price": "Average Price (RM)"},
        color="Price",
        color_continuous_scale="Purples"
    )

    st.plotly_chart(fig_price_state, use_container_width=True)