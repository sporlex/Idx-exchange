import pandas as pd
import glob
import os

base_dir = r"C:\Users\sean1\IDX internship"
csv_dir = os.path.join(base_dir, "csv")

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



sold_files_all = sorted(glob.glob(os.path.join(csv_dir, "CRMLSSold*.csv")))


sold_file_map = {}
for f in sold_files_all:
    basename = os.path.basename(f)
    month_key = basename.replace("_filled", "").replace("CRMLSSold", "").replace(".csv", "")
    is_filled = "_filled" in basename
    if month_key not in sold_file_map or is_filled:
        sold_file_map[month_key] = f

sold_files = [sold_file_map[k] for k in sorted(sold_file_map.keys())]

print("\n" + "=" * 60)
print("SOLD FILES FOUND:")
print("=" * 60)
for f in sold_files:
    print(f"  {os.path.basename(f)}")
print(f"\nTotal sold files: {len(sold_files)}")

sold_dfs = []
for f in sold_files:
    df = pd.read_csv(f, low_memory=False)
    df.drop(columns=["latfilled", "lonfilled"], inplace=True, errors="ignore")
    print(f"  {os.path.basename(f)}: {len(df):,} rows, {len(df.columns)} columns")
    sold_dfs.append(df)

sold = pd.concat(sold_dfs, ignore_index=True)
print(f"\nCombined sold row count (before filter): {len(sold):,}")


print("\n" + "=" * 60)
print("PROPERTY TYPE FILTERING")
print("=" * 60)

print(f"\nListings - unique PropertyType values:")
print(listings["PropertyType"].value_counts())

print(f"\nSold - unique PropertyType values:")
print(sold["PropertyType"].value_counts())

listings_residential = listings[listings["PropertyType"] == "Residential"].copy()
sold_residential = sold[sold["PropertyType"] == "Residential"].copy()

print(f"\nListings before filter: {len(listings):,}")
print(f"Listings after Residential filter: {len(listings_residential):,}")
print(f"Rows removed: {len(listings) - len(listings_residential):,}")

print(f"\nSold before filter: {len(sold):,}")
print(f"Sold after Residential filter: {len(sold_residential):,}")
print(f"Rows removed: {len(sold) - len(sold_residential):,}")



output_listings = os.path.join(base_dir, "listings.csv")
output_sold = os.path.join(base_dir, "sold.csv")

listings_residential.to_csv(output_listings, index=False)
sold_residential.to_csv(output_sold, index=False)

print("\n" + "=" * 60)
print("OUTPUT FILES SAVED")
print("=" * 60)
print(f"  {output_listings} ({len(listings_residential):,} rows)")
print(f"  {output_sold} ({len(sold_residential):,} rows)")
print("\nDone!")
