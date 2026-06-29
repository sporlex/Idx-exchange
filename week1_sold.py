import pandas as pd
import glob
import os

base_dir = r"C:\Users\sean1\IDX internship"
csv_dir = os.path.join(base_dir, "csv")



sold_files_all = sorted(glob.glob(os.path.join(csv_dir, "CRMLSSold*.csv")))


sold_file_map = {}
for f in sold_files_all:
    basename = os.path.basename(f)
    month_key = basename.replace("_filled", "").replace("CRMLSSold", "").replace(".csv", "")
    is_filled = "_filled" in basename
    if month_key not in sold_file_map or is_filled:
        sold_file_map[month_key] = f

sold_files = [sold_file_map[k] for k in sorted(sold_file_map.keys())]

print("=" * 60)
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

print(f"\nUnique PropertyType values:")
print(sold["PropertyType"].value_counts())

sold_residential = sold[sold["PropertyType"] == "Residential"].copy()

print(f"\nBefore filter: {len(sold):,}")
print(f"After Residential filter: {len(sold_residential):,}")
print(f"Rows removed: {len(sold) - len(sold_residential):,}")



output_path = os.path.join(base_dir, "sold.csv")
sold_residential.to_csv(output_path, index=False)

print("\n" + "=" * 60)
print("OUTPUT FILE SAVED")
print("=" * 60)
print(f"  {output_path} ({len(sold_residential):,} rows)")
print("\nDone!")
