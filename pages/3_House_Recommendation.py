import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Malaysia Living Place Recommendation System",
    layout="wide"
)

st.title("Malaysia Living Place Recommendation System")

st.header("🏠 House Rental Recommendation System")

@st.cache_data
def load_houses():
    return (pd.read_csv("house_scores.csv"), pd.read_csv("house_data_cleaned.csv"))

house_df, house_raw = load_houses()

#Use raw cleaned data for filter options and slider bounds
#Ensure numeric columns in house_raw are proper types
if "Price" in house_raw.columns:
    house_raw["Price"] = (
        house_raw["Price"].astype(str)
        .str.replace(",", "", regex=False)
        .str.replace('"', "", regex=False)
        .str.strip()
    )
    house_raw["Price"] = pd.to_numeric(house_raw["Price"], errors="coerce")

for col in ["Size", "Number of beds", "Number of bathrooms"]:
    if col in house_raw.columns:
        house_raw[col] = pd.to_numeric(house_raw[col], errors="coerce")

state_options = sorted(house_raw["State"].dropna().astype(str).unique().tolist())
district_options = sorted(house_raw["District"].dropna().astype(str).unique().tolist())
house_type_options = sorted(house_raw["Type"].dropna().astype(str).unique().tolist())
furnished_options = sorted(house_raw["Furnished Status"].dropna().astype(str).unique().tolist())

state = st.selectbox("State", ["All"] + state_options)
district = st.selectbox("District", ["All"] + district_options)
house_type = st.selectbox("House Type", ["All"] + house_type_options)
furnished = st.selectbox("Furnished Status", ["All"] + furnished_options)

price_min = int(house_raw["Price"].min()) if "Price" in house_raw.columns else 0
price_max = int(house_raw["Price"].max()) if "Price" in house_raw.columns else 10000
price_range = st.slider(
    "Price Range",
    price_min,
    price_max,
    (price_min, price_max)
)

beds_max = int(house_raw["Number of beds"].max()) if "Number of beds" in house_raw.columns else 10
baths_max = int(house_raw["Number of bathrooms"].max()) if "Number of bathrooms" in house_raw.columns else 10

beds = st.slider("Minimum Bedrooms", 0, beds_max, 0)
baths = st.slider("Minimum Bathrooms", 0, baths_max, 0)

top_n = st.selectbox("Results to show", [5, "All"])

#Start from scored dataframe, then merge raw columns for display and accurate filtering
df = house_df.copy()

#Prepare raw selection and merge on identifying columns (Name, State, District)
raw_sel_cols = [c for c in ["Name", "Price", "Size", "Number of beds", "Number of bathrooms", "Type", "Furnished Status", "State", "District"] if c in house_raw.columns]
raw_sel = house_raw[raw_sel_cols].copy()

#Rename raw measurement columns to keep them distinct before replacing
rename_map = {}
for c in ["Price", "Size", "Number of beds", "Number of bathrooms", "Type", "Furnished Status"]:
    if c in raw_sel.columns:
        rename_map[c] = f"{c}_raw"
raw_sel = raw_sel.rename(columns=rename_map)

merge_on = [col for col in ["Name", "State", "District"] if col in df.columns and col in raw_sel.columns]
if merge_on:
    df = df.merge(raw_sel, on=merge_on, how="left")
else:
    #Fallback: attach raw columns by index if lengths match
    if df.shape[0] == raw_sel.shape[0]:
        df = df.reset_index(drop=True).join(raw_sel.reset_index(drop=True))

#Replace base columns with raw values when present
base_cols = ["Price", "Size", "Number of beds", "Number of bathrooms", "Type", "Furnished Status"]
for col in base_cols:
    raw_col = f"{col}_raw"
    if raw_col in df.columns:
        df[col] = df[raw_col]
        df = df.drop(columns=[raw_col])

#Apply filters against the (now raw-backed) display columns
if state != "All":
    df = df[df["State"] == state]

if district != "All":
    df = df[df["District"] == district]

if house_type != "All":
    df = df[df["Type"] == house_type]

if furnished != "All":
    df = df[df["Furnished Status"] == furnished]

# Ensure numeric columns exist before filtering
if "Price" in df.columns:
    df["Price"] = pd.to_numeric(df["Price"], errors="coerce")
if "Number of beds" in df.columns:
    df["Number of beds"] = pd.to_numeric(df["Number of beds"], errors="coerce")
if "Number of bathrooms" in df.columns:
    df["Number of bathrooms"] = pd.to_numeric(df["Number of bathrooms"], errors="coerce")

df = df[
    (df.get("Price", 0) >= price_range[0]) &
    (df.get("Price", 0) <= price_range[1]) &
    (df.get("Number of beds", 0) >= beds) &
    (df.get("Number of bathrooms", 0) >= baths)
]

# Sort by the scored house_score (descending)
df = df.sort_values("house_score", ascending=False)

if top_n != "All":
    df = df.head(top_n)

st.subheader("Recommended Houses")
st.dataframe(
    df[[
        "Name",
        "Price",
        "Size",
        "Number of beds",
        "Number of bathrooms",
        "Type",
        "Furnished Status",
        "State",
        "District",
        "house_score"
    ]]
)