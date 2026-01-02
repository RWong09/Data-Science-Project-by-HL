import pandas as pd

def recommend_districts(district_df, job_weight=0.6, house_weight=0.4, top_k=5):
    df = district_df.copy()

    df["total_score"] = (
        job_weight * df["job_score_norm"] +
        house_weight * df["house_score_norm"]
    )

    result = (
        df.groupby(["state", "district"], as_index=False)
        .agg(total_score=("total_score", "mean"))
        .sort_values("total_score", ascending=False)
    )

    return result.head(top_k)


def highest_lowest_salary_districts(job_df, mode="highest", top_k=5):
    avg_salary = (
        job_df.groupby(["state", "district"], as_index=False)
        .agg(avg_salary=("salary", "mean"))
    )

    #Round salaries to 2 decimal places for display
    if "avg_salary" in avg_salary.columns:
        avg_salary["avg_salary"] = avg_salary["avg_salary"].round(2)

    #Exclude zero or non-positive averages (but fallback to original if nothing remains)
    cleaned = avg_salary.dropna(subset=["avg_salary"]) if "avg_salary" in avg_salary.columns else avg_salary
    cleaned_pos = cleaned[cleaned["avg_salary"] > 0]

    use_df = cleaned_pos if not cleaned_pos.empty else avg_salary

    ascending = True if mode == "lowest" else False
    return use_df.sort_values("avg_salary", ascending=ascending).head(top_k)


def highest_lowest_house_price(house_df, house_type=None, mode="lowest", top_k=5, house_raw_df=None):
    """
    Compute average house rental prices by State and District.

    If `house_raw_df` is provided it will be used for price calculations (preferred),
    otherwise `house_df` is used. Returns averages rounded to 2 decimals.
    """
    #Prefer raw house data for accurate price values
    source_df = None
    if house_raw_df is not None:
        source_df = house_raw_df.copy()
        #Ensure Price is numeric (strip commas/quotes)
        if "Price" in source_df.columns:
            source_df["Price"] = (
                source_df["Price"].astype(str)
                .str.replace(",", "", regex=False)
                .str.replace('"', "", regex=False)
                .str.strip()
            )
            source_df["Price"] = pd.to_numeric(source_df["Price"], errors="coerce")
    else:
        source_df = house_df.copy()

    if house_type and "Type" in source_df.columns:
        source_df = source_df[source_df["Type"] == house_type]

    #Group by State/District (handle possible different column name casing)
    state_col = "State" if "State" in source_df.columns else "state" if "state" in source_df.columns else None
    district_col = "District" if "District" in source_df.columns else "district" if "district" in source_df.columns else None

    if state_col is None or district_col is None or "Price" not in source_df.columns:
        #Fallback: attempt to use provided house_df grouping
        df = house_df.copy()
        if house_type and "Type" in df.columns:
            df = df[df["Type"] == house_type]
        avg_price = (
            df.groupby(["State", "District"], as_index=False)
            .agg(avg_price=("Price", "mean"))
        )
    else:
        avg_price = (
            source_df.groupby([state_col, district_col], as_index=False)
            .agg(avg_price=("Price", "mean"))
        )

    #Round to 2 decimals and exclude zero/non-positive averages when possible
    if "avg_price" in avg_price.columns:
        avg_price["avg_price"] = avg_price["avg_price"].round(2)

    cleaned_p = avg_price.dropna(subset=["avg_price"]) if "avg_price" in avg_price.columns else avg_price
    cleaned_pos_p = cleaned_p[cleaned_p["avg_price"] > 0]

    use_price_df = cleaned_pos_p if not cleaned_pos_p.empty else avg_price

    ascending = True if mode == "lowest" else False
    return use_price_df.sort_values("avg_price", ascending=ascending).head(top_k)
