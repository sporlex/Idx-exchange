import pandas as pd
import numpy as np
import os

base_dir = r"C:\Users\sean1\IDX internship"
out_dir = os.path.join(base_dir, "tableau_data")
os.makedirs(out_dir, exist_ok=True)

# ============================================================
# LOAD FILTERED (OUTLIER-REMOVED) DATASETS
# ============================================================

print("Loading filtered datasets...")
sold = pd.read_csv(os.path.join(base_dir, "sold_filtered.csv"), low_memory=False)
listings = pd.read_csv(os.path.join(base_dir, "listings_filtered.csv"), low_memory=False)

print(f"Sold:     {len(sold):,} rows")
print(f"Listings: {len(listings):,} rows")

# ============================================================
# 1. MARKET ANALYSIS DATA (for market_analysis.twbx)
# ============================================================

print("\n" + "=" * 60)
print("1. MARKET ANALYSIS — Tableau-ready export")
print("=" * 60)

market_cols = [
    "CloseDate", "yr_mo", "ClosePrice", "ListPrice", "OriginalListPrice",
    "LivingArea", "DaysOnMarket", "BedroomsTotal", "BathroomsTotalInteger",
    "price_ratio", "close_to_orig_ratio", "ppsf",
    "listing_to_contract_days", "contract_to_close_days",
    "City", "CountyOrParish", "PostalCode", "PropertySubType",
    "school_district", "YearBuilt",
    "Latitude", "Longitude",
    "rate_30yr_fixed",
]

# Sold — main dataset for market analysis dashboards
sold_market = sold[[c for c in market_cols if c in sold.columns]].copy()
sold_market["record_type"] = "Sold"

# Listings — for "New Listings" dashboard
listing_market_cols = [
    "ListingContractDate", "yr_mo", "ListPrice", "OriginalListPrice",
    "LivingArea", "DaysOnMarket", "BedroomsTotal", "BathroomsTotalInteger",
    "ppsf", "City", "CountyOrParish", "PostalCode", "PropertySubType",
    "school_district", "YearBuilt",
    "Latitude", "Longitude",
    "rate_30yr_fixed",
]
listings_market = listings[[c for c in listing_market_cols if c in listings.columns]].copy()
listings_market["record_type"] = "Listing"

# Derive yr_mo for listings from ListingContractDate
listings_market["listing_yr_mo"] = pd.to_datetime(
    listings_market["ListingContractDate"], errors="coerce"
).dt.to_period("M").astype(str)

sold_market.to_csv(os.path.join(out_dir, "market_sold.csv"), index=False)
listings_market.to_csv(os.path.join(out_dir, "market_listings.csv"), index=False)

print(f"  market_sold.csv: {len(sold_market):,} rows x {len(sold_market.columns)} cols")
print(f"  market_listings.csv: {len(listings_market):,} rows x {len(listings_market.columns)} cols")

# Monthly aggregation for quick Tableau line charts
sold_market["CloseDate"] = pd.to_datetime(sold_market["CloseDate"], errors="coerce")
monthly = sold_market.groupby("yr_mo").agg(
    closed_sales=("ClosePrice", "size"),
    median_close_price=("ClosePrice", "median"),
    mean_close_price=("ClosePrice", "mean"),
    median_ppsf=("ppsf", "median"),
    median_dom=("DaysOnMarket", "median"),
    avg_price_ratio=("close_to_orig_ratio", "mean"),
).round(2).reset_index()

listings_market["ListingContractDate"] = pd.to_datetime(
    listings_market["ListingContractDate"], errors="coerce"
)
new_listings_monthly = listings_market.groupby("listing_yr_mo").agg(
    new_listings=("ListPrice", "size"),
).reset_index().rename(columns={"listing_yr_mo": "yr_mo"})

monthly = monthly.merge(new_listings_monthly, on="yr_mo", how="left")
monthly.to_csv(os.path.join(out_dir, "market_monthly_summary.csv"), index=False)
print(f"  market_monthly_summary.csv: {len(monthly)} months")

# ============================================================
# 2. COMPETITIVE ANALYSIS DATA (for competitive_analysis.twbx)
# ============================================================

print("\n" + "=" * 60)
print("2. COMPETITIVE ANALYSIS — Top agents & offices")
print("=" * 60)

# Top listing agents by volume and units
agent_stats = sold.groupby("ListAgentFullName").agg(
    units_sold=("ClosePrice", "size"),
    total_volume=("ClosePrice", "sum"),
    avg_price=("ClosePrice", "mean"),
    median_dom=("DaysOnMarket", "median"),
).round(2).reset_index().sort_values("total_volume", ascending=False)

agent_stats["rank_by_volume"] = range(1, len(agent_stats) + 1)
top100_agents = agent_stats.head(100)
top100_agents.to_csv(os.path.join(out_dir, "competitive_top100_agents.csv"), index=False)
print(f"  competitive_top100_agents.csv: {len(top100_agents)} agents")

# Top listing offices by volume and units
office_stats = sold.groupby("ListOfficeName").agg(
    units_sold=("ClosePrice", "size"),
    total_volume=("ClosePrice", "sum"),
    avg_price=("ClosePrice", "mean"),
    median_dom=("DaysOnMarket", "median"),
).round(2).reset_index().sort_values("total_volume", ascending=False)

# Add filterable dimensions
office_detail = sold.groupby("ListOfficeName").agg(
    cities=("City", lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else ""),
    counties=("CountyOrParish", lambda x: ", ".join(x.dropna().unique()[:3])),
    subtypes=("PropertySubType", lambda x: ", ".join(x.dropna().unique()[:3])),
).reset_index()

office_stats = office_stats.merge(office_detail, on="ListOfficeName", how="left")
office_stats["rank_by_volume"] = range(1, len(office_stats) + 1)
top100_offices = office_stats.head(100)
top100_offices.to_csv(os.path.join(out_dir, "competitive_top100_offices.csv"), index=False)
print(f"  competitive_top100_offices.csv: {len(top100_offices)} offices")

# Zip code level data for heat maps
zip_stats = sold.groupby("PostalCode").agg(
    homes_sold=("ClosePrice", "size"),
    median_close_price=("ClosePrice", "median"),
    avg_lat=("Latitude", "mean"),
    avg_lon=("Longitude", "mean"),
    county=("CountyOrParish", lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else ""),
    city=("City", lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else ""),
).round(2).reset_index()

zip_stats.to_csv(os.path.join(out_dir, "competitive_zipcode_heatmap.csv"), index=False)
print(f"  competitive_zipcode_heatmap.csv: {len(zip_stats)} zip codes")

# Zip code by month (for monthly filterable heat maps)
zip_monthly = sold.groupby(["PostalCode", "yr_mo"]).agg(
    homes_sold=("ClosePrice", "size"),
    median_close_price=("ClosePrice", "median"),
).round(2).reset_index()

zip_monthly.to_csv(os.path.join(out_dir, "competitive_zipcode_monthly.csv"), index=False)
print(f"  competitive_zipcode_monthly.csv: {len(zip_monthly):,} rows")

print("\n" + "=" * 60)
print("ALL TABLEAU DATA EXPORTED TO: tableau_data/")
print("=" * 60)
print("\nDone!")
