import pandas as pd
import glob
import os

base_dir = r"C:\Users\sean1\IDX internship"
csv_dir = os.path.join(base_dir, "csv")

# ============================================================
# 1. Combine all Listing monthly CSVs
# ============================================================

listing_files_csv = sorted(glob.glob(os.path.join(csv_dir, "CRMLSListing*.csv")))
listing_files_root = sorted(glob.glob(os.path.join(base_dir, "CRMLSListing*.csv")))
listing_files = listing_files_root + listing_files_csv

print("=" * 60)
print("LISTING FILES FOUND:")
print("=" * 60)
for f in listing_files:
    print(f"  {os.path.basename(f)}")
print(f"\nTotal listing files: {len(listing_files)}")

listing_dfs = []
for f in listing_files:
    df = pd.read_csv(f, low_memory=False)
    print(f"  {os.path.basename(f)}: {len(df):,} rows, {len(df.columns)} columns")
    listing_dfs.append(df)

listings = pd.concat(listing_dfs, ignore_index=True)
print(f"\nCombined listings row count (before filter): {len(listings):,}")

# ============================================================
# 2. Filter to PropertyType == 'Residential'
# ============================================================

print("\n" + "=" * 60)
print("PROPERTY TYPE FILTERING")
print("=" * 60)

print(f"\nUnique PropertyType values:")
print(listings["PropertyType"].value_counts())

listings_residential = listings[listings["PropertyType"] == "Residential"].copy()

print(f"\nBefore filter: {len(listings):,}")
print(f"After Residential filter: {len(listings_residential):,}")
print(f"Rows removed: {len(listings) - len(listings_residential):,}")

# ============================================================
# 3. Save combined, filtered dataset
# ============================================================

output_path = os.path.join(base_dir, "listings.csv")
listings_residential.to_csv(output_path, index=False)

print("\n" + "=" * 60)
print("OUTPUT FILE SAVED")
print("=" * 60)
print(f"  {output_path} ({len(listings_residential):,} rows)")
print("\nDone!")
