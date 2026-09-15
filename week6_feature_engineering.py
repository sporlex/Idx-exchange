import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import Point
import os
import warnings
warnings.filterwarnings("ignore")

base_dir = r"C:\Users\sean1\IDX internship"

# ============================================================
# LOAD CLEANED DATASETS
# ============================================================

print("Loading cleaned datasets...")
sold = pd.read_csv(os.path.join(base_dir, "sold_cleaned.csv"), low_memory=False)
listings = pd.read_csv(os.path.join(base_dir, "listings_cleaned.csv"), low_memory=False)

print(f"Sold:     {len(sold):,} rows x {len(sold.columns)} columns")
print(f"Listings: {len(listings):,} rows x {len(listings.columns)} columns")

# Convert date columns to datetime
date_cols = ["CloseDate", "PurchaseContractDate", "ListingContractDate", "ContractStatusChangeDate"]
for df in [sold, listings]:
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

# ============================================================
# 1. PRICE RATIO (ClosePrice / ListPrice)
# ============================================================

print("\n" + "=" * 60)
print("1. PRICE RATIO = ClosePrice / ListPrice")
print("   Purpose: Measures negotiation strength")
print("=" * 60)

for name, df in [("Sold", sold), ("Listings", listings)]:
    mask = (df["ClosePrice"].notna()) & (df["ListPrice"].notna()) & (df["ListPrice"] > 0)
    df["price_ratio"] = np.nan
    df.loc[mask, "price_ratio"] = (df.loc[mask, "ClosePrice"] / df.loc[mask, "ListPrice"]).round(4)
    valid = df["price_ratio"].notna().sum()
    print(f"  {name}: {valid:,} valid | median={df['price_ratio'].median():.4f}, mean={df['price_ratio'].mean():.4f}")

# ============================================================
# 2. CLOSE-TO-ORIGINAL-LIST RATIO
# ============================================================

print("\n" + "=" * 60)
print("2. CLOSE-TO-ORIGINAL-LIST RATIO = ClosePrice / OriginalListPrice")
print("   Purpose: Captures full price reduction history")
print("=" * 60)

for name, df in [("Sold", sold), ("Listings", listings)]:
    mask = (df["ClosePrice"].notna()) & (df["OriginalListPrice"].notna()) & (df["OriginalListPrice"] > 0)
    df["close_to_orig_ratio"] = np.nan
    df.loc[mask, "close_to_orig_ratio"] = (df.loc[mask, "ClosePrice"] / df.loc[mask, "OriginalListPrice"]).round(4)
    valid = df["close_to_orig_ratio"].notna().sum()
    print(f"  {name}: {valid:,} valid | median={df['close_to_orig_ratio'].median():.4f}, mean={df['close_to_orig_ratio'].mean():.4f}")

# ============================================================
# 3. PRICE PER SQUARE FOOT (PPSF)
# ============================================================

print("\n" + "=" * 60)
print("3. PPSF = ClosePrice / LivingArea")
print("   Purpose: Normalizes price across different property sizes")
print("=" * 60)

for name, df in [("Sold", sold), ("Listings", listings)]:
    mask = (df["ClosePrice"].notna()) & (df["LivingArea"].notna()) & (df["LivingArea"] > 0)
    df["ppsf"] = np.nan
    df.loc[mask, "ppsf"] = (df.loc[mask, "ClosePrice"] / df.loc[mask, "LivingArea"]).round(2)
    valid = df["ppsf"].notna().sum()
    print(f"  {name}: {valid:,} valid | median=${df['ppsf'].median():,.2f}, mean=${df['ppsf'].mean():,.2f}")

# ============================================================
# 4. DAYS ON MARKET (already exists as raw field)
# ============================================================

print("\n" + "=" * 60)
print("4. DAYS ON MARKET (raw field, already present)")
print("   Purpose: Time-to-sell indicator")
print("=" * 60)

for name, df in [("Sold", sold), ("Listings", listings)]:
    valid = df["DaysOnMarket"].notna().sum()
    print(f"  {name}: {valid:,} valid | median={df['DaysOnMarket'].median():.0f}, mean={df['DaysOnMarket'].mean():.1f}")

# ============================================================
# 5. YEAR-MONTH (YrMo) from CloseDate
# ============================================================

print("\n" + "=" * 60)
print("5. YrMo = Year-Month derived from CloseDate")
print("   Purpose: Enables time-series analysis")
print("=" * 60)

for name, df in [("Sold", sold), ("Listings", listings)]:
    df["yr_mo"] = df["CloseDate"].dt.to_period("M").astype(str)
    df.loc[df["CloseDate"].isna(), "yr_mo"] = np.nan
    valid = df["yr_mo"].notna().sum()
    print(f"  {name}: {valid:,} valid | range: {df['yr_mo'].dropna().min()} to {df['yr_mo'].dropna().max()}")

# ============================================================
# 6. LISTING TO CONTRACT DAYS
# ============================================================

print("\n" + "=" * 60)
print("6. LISTING-TO-CONTRACT DAYS = PurchaseContractDate - ListingContractDate")
print("   Purpose: Measures time from listing to accepted offer")
print("=" * 60)

for name, df in [("Sold", sold), ("Listings", listings)]:
    mask = df["PurchaseContractDate"].notna() & df["ListingContractDate"].notna()
    df["listing_to_contract_days"] = np.nan
    df.loc[mask, "listing_to_contract_days"] = (
        df.loc[mask, "PurchaseContractDate"] - df.loc[mask, "ListingContractDate"]
    ).dt.days
    valid = df["listing_to_contract_days"].notna().sum()
    print(f"  {name}: {valid:,} valid | median={df['listing_to_contract_days'].median():.0f}, mean={df['listing_to_contract_days'].mean():.1f}")

# ============================================================
# 7. CONTRACT TO CLOSE DAYS
# ============================================================

print("\n" + "=" * 60)
print("7. CONTRACT-TO-CLOSE DAYS = CloseDate - PurchaseContractDate")
print("   Purpose: Escrow and closing period duration")
print("=" * 60)

for name, df in [("Sold", sold), ("Listings", listings)]:
    mask = df["CloseDate"].notna() & df["PurchaseContractDate"].notna()
    df["contract_to_close_days"] = np.nan
    df.loc[mask, "contract_to_close_days"] = (
        df.loc[mask, "CloseDate"] - df.loc[mask, "PurchaseContractDate"]
    ).dt.days
    valid = df["contract_to_close_days"].notna().sum()
    print(f"  {name}: {valid:,} valid | median={df['contract_to_close_days'].median():.0f}, mean={df['contract_to_close_days'].mean():.1f}")

# ============================================================
# 8. SCHOOL DISTRICT (spatial join using CA school district shapefile)
# ============================================================

print("\n" + "=" * 60)
print("8. SCHOOL DISTRICT (spatial join with CA school district boundaries)")
print("   Source: data.ca.gov California School District Areas 2024-25")
print("=" * 60)

school_url = (
    "https://data.ca.gov/dataset/7e013028-0057-4a4e-b715-2e12e06b8395/"
    "resource/7dfaf005-58eb-45db-93b1-7aff091b2172/download/"
    "california-school-district-areas-2024-25.csv"
)

try:
    import tempfile, urllib.request
    tmp_zip = os.path.join(tempfile.gettempdir(), "ca_school_districts.zip")
    urllib.request.urlretrieve(school_url, tmp_zip)
    school_gdf = gpd.read_file(f"zip://{tmp_zip}")
    school_gdf = school_gdf.to_crs("EPSG:4326")
    print(f"  School district shapefile loaded: {len(school_gdf):,} districts")

    name_col = "DistrictNa"
    print(f"  Using district name column: {name_col}")

    for ds_name, df in [("Sold", sold), ("Listings", listings)]:
        valid_coords = (
            df["Latitude"].notna() & df["Longitude"].notna() &
            (df["Latitude"] != 0) & (df["Longitude"] != 0) & (df["Longitude"] < 0)
        )
        coords_df = df.loc[valid_coords, ["Latitude", "Longitude"]].copy()
        points = gpd.GeoDataFrame(
            coords_df,
            geometry=[Point(lon, lat) for lon, lat in zip(coords_df["Longitude"], coords_df["Latitude"])],
            crs="EPSG:4326"
        )
        joined = gpd.sjoin(points, school_gdf[[name_col, "geometry"]], how="left", predicate="within")
        joined = joined[~joined.index.duplicated(keep="first")]

        df["school_district"] = np.nan
        df.loc[joined.index, "school_district"] = joined[name_col].values
        matched = df["school_district"].notna().sum()
        print(f"  {ds_name}: {matched:,}/{len(df):,} matched to a school district")

except Exception as e:
    print(f"  School district download/join failed: {e}")
    print("  Adding empty school_district column")
    for df in [sold, listings]:
        df["school_district"] = np.nan

# ============================================================
# 9. SEGMENTED SUMMARY TABLE (by CountyOrParish)
# ============================================================

print("\n" + "=" * 60)
print("9. SEGMENTED SUMMARY TABLE — Sold dataset by CountyOrParish")
print("=" * 60)

seg = sold.groupby("CountyOrParish").agg(
    count=("ClosePrice", "size"),
    median_close_price=("ClosePrice", "median"),
    mean_ppsf=("ppsf", "mean"),
    median_dom=("DaysOnMarket", "median"),
    median_price_ratio=("price_ratio", "median"),
    median_listing_to_contract=("listing_to_contract_days", "median"),
    median_contract_to_close=("contract_to_close_days", "median"),
).round(2).sort_values("count", ascending=False)

print(seg.head(10).to_string())

seg.to_csv(os.path.join(base_dir, "week6_deliverables", "week6_county_summary.csv"))
print(f"\nSaved: week6_county_summary.csv ({len(seg)} counties)")

# Also by PropertySubType
seg2 = sold.groupby("PropertySubType").agg(
    count=("ClosePrice", "size"),
    median_close_price=("ClosePrice", "median"),
    mean_ppsf=("ppsf", "mean"),
    median_dom=("DaysOnMarket", "median"),
    median_price_ratio=("price_ratio", "median"),
).round(2).sort_values("count", ascending=False)

seg2.to_csv(os.path.join(base_dir, "week6_deliverables", "week6_subtype_summary.csv"))
print(f"Saved: week6_subtype_summary.csv ({len(seg2)} subtypes)")

# ============================================================
# 10. SAMPLE OUTPUT TABLE
# ============================================================

print("\n" + "=" * 60)
print("10. SAMPLE OUTPUT — New engineered columns (first 5 rows)")
print("=" * 60)

new_cols = ["ClosePrice", "ListPrice", "OriginalListPrice", "LivingArea", "DaysOnMarket",
            "price_ratio", "close_to_orig_ratio", "ppsf", "yr_mo",
            "listing_to_contract_days", "contract_to_close_days", "school_district"]
sample = sold[new_cols].head(5)
print(sample.to_string(index=False))

sample.to_csv(os.path.join(base_dir, "week6_deliverables", "week6_sample_output.csv"), index=False)
print("\nSaved: week6_sample_output.csv")

# ============================================================
# SAVE ENGINEERED DATASETS
# ============================================================

print("\n" + "=" * 60)
print("SAVING ENGINEERED DATASETS")
print("=" * 60)

sold_path = os.path.join(base_dir, "sold_engineered.csv")
listings_path = os.path.join(base_dir, "listings_engineered.csv")

sold.to_csv(sold_path, index=False)
listings.to_csv(listings_path, index=False)

print(f"  {sold_path} ({len(sold):,} rows, {len(sold.columns)} cols)")
print(f"  {listings_path} ({len(listings):,} rows, {len(listings.columns)} cols)")
print("\nNew columns added: price_ratio, close_to_orig_ratio, ppsf, yr_mo,")
print("  listing_to_contract_days, contract_to_close_days, school_district")
print("\nDone!")
