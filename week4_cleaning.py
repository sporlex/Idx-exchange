import pandas as pd
import numpy as np
import os

base_dir = r"C:\Users\sean1\IDX internship"

# ============================================================
# LOAD DATASETS
# ============================================================

print("Loading datasets...")
sold = pd.read_csv(os.path.join(base_dir, "sold_enriched.csv"), low_memory=False)
listings = pd.read_csv(os.path.join(base_dir, "listings_enriched.csv"), low_memory=False)

print(f"Sold:     {len(sold):,} rows x {len(sold.columns)} columns")
print(f"Listings: {len(listings):,} rows x {len(listings.columns)} columns")

# ============================================================
# 1. CONVERT DATE FIELDS TO DATETIME
# ============================================================

print("\n" + "=" * 60)
print("1. DATE CONVERSION")
print("Why: Date fields are stored as strings in the CSV. Converting to datetime")
print("     enables date math (e.g., calculating days between listing and close).")
print("=" * 60)

date_cols = ["CloseDate", "PurchaseContractDate", "ListingContractDate", "ContractStatusChangeDate"]

for name, df in [("Sold", sold), ("Listings", listings)]:
    print(f"\n{name}:")
    for col in date_cols:
        if col in df.columns:
            before_dtype = df[col].dtype
            df[col] = pd.to_datetime(df[col], errors="coerce")
            null_count = df[col].isnull().sum()
            print(f"  {col}: {before_dtype} -> {df[col].dtype} (nulls: {null_count:,})")

# ============================================================
# 2. REMOVE UNNECESSARY / REDUNDANT COLUMNS
# ============================================================

print("\n" + "=" * 60)
print("2. REMOVE UNNECESSARY COLUMNS")
print("Why: Columns with 100% missing values contain no data at all.")
print("     Columns with >95% missing have too little data to be useful for analysis.")
print("=" * 60)

# 100% missing columns (identified in Week 2 EDA)
cols_100_missing = [
    "FireplacesTotal", "AboveGradeFinishedArea", "TaxAnnualAmount",
    "TaxYear", "ElementarySchoolDistrict", "BusinessType",
    "CoveredSpaces", "MiddleOrJuniorSchoolDistrict"
]

# >95% missing and low analytical value
cols_high_missing = [
    "WaterfrontYN", "BelowGradeFinishedArea", "BasementYN",
    "LotSizeDimensions", "BuilderName", "BuildingAreaTotal",
    "CoBuyerAgentFirstName"
]

cols_to_drop = cols_100_missing + cols_high_missing

for name, df in [("Sold", sold), ("Listings", listings)]:
    existing = [c for c in cols_to_drop if c in df.columns]
    df.drop(columns=existing, inplace=True)
    print(f"{name}: dropped {len(existing)} columns -> {len(df.columns)} columns remaining")

# ============================================================
# 3. ENSURE NUMERIC FIELDS ARE PROPERLY TYPED
# ============================================================

print("\n" + "=" * 60)
print("3. NUMERIC TYPE CHECK")
print("Why: Some numeric columns may be read as strings (object type) from CSV.")
print("     Ensuring proper numeric types allows correct calculations and comparisons.")
print("=" * 60)

numeric_cols = [
    "ClosePrice", "ListPrice", "OriginalListPrice", "LivingArea",
    "LotSizeAcres", "BedroomsTotal", "BathroomsTotalInteger",
    "DaysOnMarket", "YearBuilt", "ParkingTotal", "GarageSpaces",
    "Stories", "AssociationFee"
]

for name, df in [("Sold", sold), ("Listings", listings)]:
    print(f"\n{name}:")
    for col in numeric_cols:
        if col in df.columns:
            if df[col].dtype == "object":
                df[col] = pd.to_numeric(df[col], errors="coerce")
                print(f"  {col}: converted to numeric")
            else:
                print(f"  {col}: already {df[col].dtype}")

# ============================================================
# 4. FLAG / REMOVE INVALID NUMERIC VALUES
# ============================================================

print("\n" + "=" * 60)
print("4. INVALID NUMERIC VALUES")
print("Why: Values like ClosePrice=0, LivingArea=0, or DaysOnMarket<0 are data entry")
print("     errors that would distort averages and medians. Setting them to NaN prevents")
print("     them from affecting downstream analysis.")
print("=" * 60)

for name, df in [("Sold", sold), ("Listings", listings)]:
    print(f"\n{name}:")
    before = len(df)

    # ClosePrice <= 0
    if "ClosePrice" in df.columns:
        bad = (df["ClosePrice"].notna()) & (df["ClosePrice"] <= 0)
        print(f"  ClosePrice <= 0: {bad.sum():,}")
        df.loc[bad, "ClosePrice"] = np.nan

    # ListPrice <= 0
    if "ListPrice" in df.columns:
        bad = (df["ListPrice"].notna()) & (df["ListPrice"] <= 0)
        print(f"  ListPrice <= 0: {bad.sum():,}")
        df.loc[bad, "ListPrice"] = np.nan

    # OriginalListPrice <= 0
    if "OriginalListPrice" in df.columns:
        bad = (df["OriginalListPrice"].notna()) & (df["OriginalListPrice"] <= 0)
        print(f"  OriginalListPrice <= 0: {bad.sum():,}")
        df.loc[bad, "OriginalListPrice"] = np.nan

    # LivingArea <= 0
    if "LivingArea" in df.columns:
        bad = (df["LivingArea"].notna()) & (df["LivingArea"] <= 0)
        print(f"  LivingArea <= 0: {bad.sum():,}")
        df.loc[bad, "LivingArea"] = np.nan

    # DaysOnMarket < 0
    if "DaysOnMarket" in df.columns:
        bad = (df["DaysOnMarket"].notna()) & (df["DaysOnMarket"] < 0)
        print(f"  DaysOnMarket < 0: {bad.sum():,}")
        df.loc[bad, "DaysOnMarket"] = np.nan

    # BedroomsTotal < 0
    if "BedroomsTotal" in df.columns:
        bad = (df["BedroomsTotal"].notna()) & (df["BedroomsTotal"] < 0)
        print(f"  BedroomsTotal < 0: {bad.sum():,}")
        df.loc[bad, "BedroomsTotal"] = np.nan

    # BathroomsTotalInteger < 0
    if "BathroomsTotalInteger" in df.columns:
        bad = (df["BathroomsTotalInteger"].notna()) & (df["BathroomsTotalInteger"] < 0)
        print(f"  BathroomsTotalInteger < 0: {bad.sum():,}")
        df.loc[bad, "BathroomsTotalInteger"] = np.nan

# ============================================================
# 5. DATE CONSISTENCY CHECKS + FLAG COLUMNS
# ============================================================

print("\n" + "=" * 60)
print("5. DATE CONSISTENCY FLAGS")
print("Why: Listing date should come before purchase date, which should come before")
print("     close date. Records violating this order likely have data entry errors.")
print("     Flagging (not deleting) preserves the data while marking suspect records.")
print("=" * 60)

for name, df in [("Sold", sold), ("Listings", listings)]:
    print(f"\n{name}:")

    # listing_after_close_flag: ListingContractDate > CloseDate
    if "ListingContractDate" in df.columns and "CloseDate" in df.columns:
        both_valid = df["ListingContractDate"].notna() & df["CloseDate"].notna()
        df["listing_after_close_flag"] = False
        df.loc[both_valid, "listing_after_close_flag"] = (
            df.loc[both_valid, "ListingContractDate"] > df.loc[both_valid, "CloseDate"]
        )
        print(f"  listing_after_close_flag: {df['listing_after_close_flag'].sum():,} flagged")

    # purchase_after_close_flag: PurchaseContractDate > CloseDate
    if "PurchaseContractDate" in df.columns and "CloseDate" in df.columns:
        both_valid = df["PurchaseContractDate"].notna() & df["CloseDate"].notna()
        df["purchase_after_close_flag"] = False
        df.loc[both_valid, "purchase_after_close_flag"] = (
            df.loc[both_valid, "PurchaseContractDate"] > df.loc[both_valid, "CloseDate"]
        )
        print(f"  purchase_after_close_flag: {df['purchase_after_close_flag'].sum():,} flagged")

    # negative_timeline_flag: ListingContractDate > PurchaseContractDate
    if "ListingContractDate" in df.columns and "PurchaseContractDate" in df.columns:
        both_valid = df["ListingContractDate"].notna() & df["PurchaseContractDate"].notna()
        df["negative_timeline_flag"] = False
        df.loc[both_valid, "negative_timeline_flag"] = (
            df.loc[both_valid, "ListingContractDate"] > df.loc[both_valid, "PurchaseContractDate"]
        )
        print(f"  negative_timeline_flag: {df['negative_timeline_flag'].sum():,} flagged")

# ============================================================
# 6. GEOGRAPHIC DATA CHECKS
# ============================================================

print("\n" + "=" * 60)
print("6. GEOGRAPHIC DATA QUALITY")
print("Why: Missing or invalid coordinates (lat/lon=0, positive longitude, out-of-CA)")
print("     would cause errors in map visualizations and school district lookups.")
print("     Flagging these records allows geographic analysis to exclude bad data.")
print("=" * 60)

for name, df in [("Sold", sold), ("Listings", listings)]:
    print(f"\n{name}:")

    # Missing coordinates
    missing_lat = df["Latitude"].isnull().sum()
    missing_lon = df["Longitude"].isnull().sum()
    print(f"  Missing Latitude: {missing_lat:,}")
    print(f"  Missing Longitude: {missing_lon:,}")

    # Lat/Lon = 0 (sentinel nulls)
    lat_zero = ((df["Latitude"] == 0) & df["Latitude"].notna()).sum()
    lon_zero = ((df["Longitude"] == 0) & df["Longitude"].notna()).sum()
    print(f"  Latitude = 0: {lat_zero:,}")
    print(f"  Longitude = 0: {lon_zero:,}")

    # Longitude > 0 (California should be negative)
    lon_positive = ((df["Longitude"] > 0) & df["Longitude"].notna()).sum()
    print(f"  Longitude > 0 (should be negative for CA): {lon_positive:,}")

    # Out-of-state: CA roughly lat 32-42, lon -125 to -114
    valid_coords = df["Latitude"].notna() & df["Longitude"].notna()
    out_of_ca = valid_coords & (
        (df["Latitude"] < 32) | (df["Latitude"] > 42) |
        (df["Longitude"] < -125) | (df["Longitude"] > -114)
    )
    # Exclude zero/positive lon (already flagged)
    out_of_ca = out_of_ca & (df["Longitude"] < 0) & (df["Latitude"] != 0)
    print(f"  Out-of-CA coordinates: {out_of_ca.sum():,}")

    # Create geo flag columns
    df["missing_coords_flag"] = df["Latitude"].isnull() | df["Longitude"].isnull()
    df["zero_coords_flag"] = (
        ((df["Latitude"] == 0) & df["Latitude"].notna()) |
        ((df["Longitude"] == 0) & df["Longitude"].notna())
    )
    df["positive_lon_flag"] = (df["Longitude"] > 0) & df["Longitude"].notna()
    df["out_of_ca_flag"] = out_of_ca

    geo_flags = ["missing_coords_flag", "zero_coords_flag", "positive_lon_flag", "out_of_ca_flag"]
    any_geo_issue = df[geo_flags].any(axis=1).sum()
    print(f"  Total records with any geo issue: {any_geo_issue:,}")

# ============================================================
# 7. SUMMARY
# ============================================================

print("\n" + "=" * 60)
print("7. FINAL SUMMARY")
print("=" * 60)

for name, df in [("Sold", sold), ("Listings", listings)]:
    print(f"\n{name}: {len(df):,} rows x {len(df.columns)} columns")

    # Data type confirmation
    print(f"  Data types: {df.dtypes.value_counts().to_dict()}")

    # Date consistency flag counts
    flag_cols = [c for c in df.columns if c.endswith("_flag")]
    if flag_cols:
        print(f"  Flag columns:")
        for fc in flag_cols:
            print(f"    {fc}: {df[fc].sum():,}")

# ============================================================
# SAVE
# ============================================================

print("\n" + "=" * 60)
print("SAVING CLEANED DATASETS")
print("=" * 60)

sold_path = os.path.join(base_dir, "sold_cleaned.csv")
listings_path = os.path.join(base_dir, "listings_cleaned.csv")

sold.to_csv(sold_path, index=False)
listings.to_csv(listings_path, index=False)

print(f"  {sold_path} ({len(sold):,} rows, {len(sold.columns)} cols)")
print(f"  {listings_path} ({len(listings):,} rows, {len(listings.columns)} cols)")
print("\nDone!")
