import pandas as pd
import os

base_dir = r"C:\Users\sean1\IDX internship"

# ============================================================
# PART 1: EDA
# ============================================================

sold = pd.read_csv(os.path.join(base_dir, "sold.csv"), low_memory=False)
listings = pd.read_csv(os.path.join(base_dir, "listings.csv"), low_memory=False)

print("Sold:", sold.shape)
print("Listings:", listings.shape)

print("\n--- Unique PropertyType values ---")
print("Sold:", sold["PropertyType"].unique())
print("Listings:", listings["PropertyType"].unique())
print("\nFiltering logic: PropertyType == 'Residential' (applied in Week 1)")
print("Both datasets are already 100% Residential after Week 1 filter.")

for name, df in [("Sold", sold), ("Listings", listings)]:
    miss_count = df.isnull().sum()
    miss_pct = (miss_count / len(df) * 100).round(2)
    summary = pd.DataFrame({"null_count": miss_count, "null_pct": miss_pct})
    summary = summary.sort_values("null_pct", ascending=False)

    print(f"\n--- {name}: null-count summary (all columns) ---")
    print(summary[summary["null_count"] > 0].to_string())

    print(f"\n--- {name}: columns >90% null (flagged) ---")
    flagged = summary[summary["null_pct"] > 90]
    if len(flagged) > 0:
        print(flagged.to_string())
    else:
        print("  None")

pcts = [0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99]
for name, df in [("Sold", sold), ("Listings", listings)]:
    print(f"\n--- {name}: numeric distribution ---")
    print(df[["ClosePrice", "LivingArea", "DaysOnMarket"]].describe(percentiles=pcts))

print("\nSold median ClosePrice:", sold["ClosePrice"].median())
print("Sold mean ClosePrice:", sold["ClosePrice"].mean())

above = (sold["ClosePrice"] > sold["ListPrice"]).sum()
below = (sold["ClosePrice"] < sold["ListPrice"]).sum()
print(f"\nAbove list: {above}  Below list: {below}")

print("\nTop 5 counties by median price:")
print(sold.groupby("CountyOrParish")["ClosePrice"].median().sort_values(ascending=False).head())

# ============================================================
# PART 2: SAVE
# ============================================================

dup_cols = [c for c in listings.columns if c.endswith(".1")]
if dup_cols:
    print(f"\nDropping {len(dup_cols)} duplicate '.1' columns from listings")
    listings.drop(columns=dup_cols, inplace=True)

listings.to_csv(os.path.join(base_dir, "listings_eda.csv"), index=False)
sold.to_csv(os.path.join(base_dir, "sold_eda.csv"), index=False)

print(f"\nSaved: sold_eda.csv ({len(sold):,} rows)")
print(f"Saved: listings_eda.csv ({len(listings):,} rows)")
print("\nDone!")
