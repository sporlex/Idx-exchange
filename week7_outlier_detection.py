import pandas as pd
import numpy as np
import os

base_dir = r"C:\Users\sean1\IDX internship"

# ============================================================
# LOAD ENGINEERED DATASETS
# ============================================================

print("Loading engineered datasets...")
sold = pd.read_csv(os.path.join(base_dir, "sold_engineered.csv"), low_memory=False)
listings = pd.read_csv(os.path.join(base_dir, "listings_engineered.csv"), low_memory=False)

print(f"Sold:     {len(sold):,} rows x {len(sold.columns)} columns")
print(f"Listings: {len(listings):,} rows x {len(listings.columns)} columns")

# ============================================================
# IQR OUTLIER DETECTION
# ============================================================

print("\n" + "=" * 60)
print("IQR OUTLIER DETECTION")
print("Why: Extreme values (e.g., $50M estate, $10K distressed sale) distort")
print("     market averages. IQR flagging identifies these without deleting them.")
print("=" * 60)

iqr_cols = ["ClosePrice", "LivingArea", "DaysOnMarket"]

for name, df in [("Sold", sold), ("Listings", listings)]:
    print(f"\n{'='*40}")
    print(f"  {name} Dataset")
    print(f"{'='*40}")

    for col in iqr_cols:
        if col not in df.columns:
            continue

        valid = df[col].dropna()
        Q1 = valid.quantile(0.25)
        Q3 = valid.quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR

        flag_col = f"{col}_outlier"
        df[flag_col] = False
        mask = df[col].notna() & ((df[col] < lower) | (df[col] > upper))
        df.loc[mask, flag_col] = True

        outlier_count = df[flag_col].sum()
        total_valid = df[col].notna().sum()

        print(f"\n  {col}:")
        print(f"    Q1={Q1:,.2f}  Q3={Q3:,.2f}  IQR={IQR:,.2f}")
        print(f"    Lower bound: {lower:,.2f}")
        print(f"    Upper bound: {upper:,.2f}")
        print(f"    Outliers flagged: {outlier_count:,} / {total_valid:,} ({outlier_count/total_valid*100:.2f}%)")

# ============================================================
# BEFORE / AFTER COMPARISON
# ============================================================

print("\n" + "=" * 60)
print("BEFORE / AFTER COMPARISON")
print("=" * 60)

comparison_rows = []

for name, df in [("Sold", sold), ("Listings", listings)]:
    any_outlier = df[[f"{c}_outlier" for c in iqr_cols if f"{c}_outlier" in df.columns]].any(axis=1)
    clean = df[~any_outlier]

    print(f"\n  {name}:")
    print(f"    Full (flagged):    {len(df):,} rows")
    print(f"    Clean (filtered):  {len(clean):,} rows")
    print(f"    Removed:           {any_outlier.sum():,} rows ({any_outlier.sum()/len(df)*100:.2f}%)")

    for col in iqr_cols:
        if col not in df.columns:
            continue
        before_median = df[col].median()
        after_median = clean[col].median()
        before_mean = df[col].mean()
        after_mean = clean[col].mean()
        print(f"\n    {col}:")
        print(f"      Median: {before_median:>12,.2f} -> {after_median:>12,.2f}  (change: {(after_median-before_median)/before_median*100:+.2f}%)")
        print(f"      Mean:   {before_mean:>12,.2f} -> {after_mean:>12,.2f}  (change: {(after_mean-before_mean)/before_mean*100:+.2f}%)")

        comparison_rows.append({
            "dataset": name, "metric": col,
            "before_rows": len(df), "after_rows": len(clean),
            "before_median": round(before_median, 2), "after_median": round(after_median, 2),
            "median_change_pct": round((after_median - before_median) / before_median * 100, 2),
            "before_mean": round(before_mean, 2), "after_mean": round(after_mean, 2),
            "mean_change_pct": round((after_mean - before_mean) / before_mean * 100, 2),
        })

# ============================================================
# SAVE DELIVERABLES
# ============================================================

print("\n" + "=" * 60)
print("SAVING DATASETS AND DELIVERABLES")
print("=" * 60)

out_dir = os.path.join(base_dir, "week7_deliverables")
os.makedirs(out_dir, exist_ok=True)

# 1. Full flagged datasets
sold_flagged_path = os.path.join(base_dir, "sold_flagged.csv")
listings_flagged_path = os.path.join(base_dir, "listings_flagged.csv")
sold.to_csv(sold_flagged_path, index=False)
listings.to_csv(listings_flagged_path, index=False)
print(f"  Full flagged: {sold_flagged_path} ({len(sold):,} rows, {len(sold.columns)} cols)")
print(f"  Full flagged: {listings_flagged_path} ({len(listings):,} rows, {len(listings.columns)} cols)")

# 2. Clean filtered datasets (outliers removed)
sold_any_outlier = sold[[f"{c}_outlier" for c in iqr_cols if f"{c}_outlier" in sold.columns]].any(axis=1)
listings_any_outlier = listings[[f"{c}_outlier" for c in iqr_cols if f"{c}_outlier" in listings.columns]].any(axis=1)

sold_clean = sold[~sold_any_outlier]
listings_clean = listings[~listings_any_outlier]

sold_clean_path = os.path.join(base_dir, "sold_filtered.csv")
listings_clean_path = os.path.join(base_dir, "listings_filtered.csv")
sold_clean.to_csv(sold_clean_path, index=False)
listings_clean.to_csv(listings_clean_path, index=False)
print(f"  Clean filtered: {sold_clean_path} ({len(sold_clean):,} rows)")
print(f"  Clean filtered: {listings_clean_path} ({len(listings_clean):,} rows)")

# 3. Comparison CSV
comp_df = pd.DataFrame(comparison_rows)
comp_path = os.path.join(out_dir, "week7_before_after_comparison.csv")
comp_df.to_csv(comp_path, index=False)
print(f"  Comparison: {comp_path}")

# 4. Outlier summary CSV
outlier_rows = []
for name, df in [("Sold", sold), ("Listings", listings)]:
    for col in iqr_cols:
        flag_col = f"{col}_outlier"
        if flag_col in df.columns:
            valid = df[col].dropna()
            Q1 = valid.quantile(0.25)
            Q3 = valid.quantile(0.75)
            IQR = Q3 - Q1
            outlier_rows.append({
                "dataset": name, "column": col,
                "Q1": round(Q1, 2), "Q3": round(Q3, 2), "IQR": round(IQR, 2),
                "lower_bound": round(Q1 - 1.5 * IQR, 2),
                "upper_bound": round(Q3 + 1.5 * IQR, 2),
                "outlier_count": int(df[flag_col].sum()),
                "total_valid": int(df[col].notna().sum()),
                "outlier_pct": round(df[flag_col].sum() / df[col].notna().sum() * 100, 2),
            })

outlier_df = pd.DataFrame(outlier_rows)
outlier_path = os.path.join(out_dir, "week7_outlier_summary.csv")
outlier_df.to_csv(outlier_path, index=False)
print(f"  Outlier summary: {outlier_path}")

print("\nDone!")
