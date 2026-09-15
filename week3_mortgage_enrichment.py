import pandas as pd
import os

base_dir = r"C:\Users\sean1\IDX internship"

sold = pd.read_csv(os.path.join(base_dir, "sold_eda.csv"), low_memory=False)
listings = pd.read_csv(os.path.join(base_dir, "listings_eda.csv"), low_memory=False)


url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=MORTGAGE30US"
mortgage = pd.read_csv(url, parse_dates=["observation_date"])
mortgage.columns = ["date", "rate_30yr_fixed"]
mortgage["rate_30yr_fixed"] = pd.to_numeric(mortgage["rate_30yr_fixed"], errors="coerce")
mortgage = mortgage.dropna()

mortgage["year_month"] = mortgage["date"].dt.to_period("M")
mortgage_monthly = mortgage.groupby("year_month")["rate_30yr_fixed"].mean().round(2).reset_index()

sold.drop(columns=["year_month", "rate_30yr_fixed"], inplace=True, errors="ignore")
listings.drop(columns=["year_month", "rate_30yr_fixed"], inplace=True, errors="ignore")

sold["year_month"] = pd.to_datetime(sold["CloseDate"], errors="coerce").dt.to_period("M").astype(str)
listings["year_month"] = pd.to_datetime(listings["ListingContractDate"], errors="coerce").dt.to_period("M").astype(str)

mortgage_monthly["year_month"] = mortgage_monthly["year_month"].astype(str)

sold = sold.merge(mortgage_monthly, on="year_month", how="left")
listings = listings.merge(mortgage_monthly, on="year_month", how="left")

print("\nSold null rates:", sold["rate_30yr_fixed"].isnull().sum())
print("Listings null rates:", listings["rate_30yr_fixed"].isnull().sum())

sold["year_month"] = sold["year_month"].astype(str)
listings["year_month"] = listings["year_month"].astype(str)

sold.to_csv(os.path.join(base_dir, "sold_enriched.csv"), index=False)
listings.to_csv(os.path.join(base_dir, "listings_enriched.csv"), index=False)

print(f"\nSaved: sold_enriched.csv ({len(sold):,} rows)")
print(f"Saved: listings_enriched.csv ({len(listings):,} rows)")
print("\nDone!")
