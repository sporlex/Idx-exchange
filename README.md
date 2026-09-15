# IDX Exchange — MLS Data Analyst Internship

## Project Overview
End-to-end real estate analytics pipeline analyzing **377,601 sold transactions** and **531,414 new listings** from the CRMLS (California Regional Multiple Listing Service). The project covers the full data lifecycle: extraction, cleaning, feature engineering, outlier detection, interactive Tableau dashboard development, and market intelligence reporting.

## Objectives
- Clean and structure raw MLS listing and sold transaction datasets
- Engineer key market metrics (close-to-original ratio, PPSF, days on market, listing-to-contract days, etc.)
- Detect and flag outliers using IQR-based statistical methods
- Build interactive Tableau dashboards for market analysis and competitive intelligence
- Produce a 1-page market intelligence report with data-driven insights
- Deliver a 5-minute live presentation with dashboard walkthrough

## Key Findings
- **Price Resilience:** California median close price held within a 1% band (~$790K) across 2.5 years despite mortgage rates above 6.5%
- **2025 Soft Spot:** Average DOM rose 18% (24 to 28 days) and close-to-original ratio dipped below 1.00
- **County Disparity:** Orange County median ($1.08M) is 2x Riverside ($595K)
- **Compass Dominance:** 23,674 units / $28.3B volume, 1.5x #2 Coldwell Banker
- **Inland Empire = Volume Engine:** Riverside + San Bernardino = 88,480 sales (23% of total) at $455K-$750K

## Data Source
- **Provider:** CoreLogic Trestle API via IDX Exchange pipeline
- **Coverage:** Southern California (CRMLS)
- **Period:** January 2024 - June 2026
- **Datasets:** Monthly MLS Listing & Sold transaction CSV files

> **Note:** Raw CSV data files are not included in this repository due to confidentiality. All datasets are sourced from live MLS transaction records and are for program use only.

## Tools
- **Python** (Pandas, NumPy) - data cleaning, feature engineering, outlier detection, aggregation
- **Tableau Desktop Public Edition** - interactive dashboards and visualizations
- **Git / GitHub** - version control and project documentation

## Dashboards
Published on Tableau Public: [Yang-Hsuan Lin's Profile](https://public.tableau.com/app/profile/yang.hsuan.lin/vizzes)

### Market Overview
- Monthly Median Close Price trend
- Average Days on Market trend
- Average Close-to-Original Ratio trend
- Monthly Closed Sales volume
- Monthly New Listings volume
- Filters: City, County, Zip Code, Property Sub Type

### Competitive Analysis
- Median Close Price by ZIP Code (filled map)
- Homes Sold by ZIP Code (filled map)
- Top Listing Agents by Sales Volume (bar chart)
- Top Listing Offices by Sales Volume (bar chart)
- Filters: City, County, Sub Type, Postal Code

## Project Structure
```
├── week1_listings.py              # Week 1: Combine monthly listing CSVs, filter Residential
├── week1_sold.py                  # Week 1: Combine monthly sold CSVs, filter Residential
├── week1_combine_datasets.py      # Week 1: Unified aggregation script
├── week2_eda.py                   # Week 2-3: EDA, missing value analysis, data validation
├── week3_mortgage_enrichment.py   # Week 3: Mortgage rate enrichment (30-yr fixed)
├── week4_cleaning.py              # Week 4-5: Data cleaning & preparation
├── week6_feature_engineering.py   # Week 6: Feature engineering (ratios, PPSF, time metrics)
├── week7_outlier_detection.py     # Week 7: IQR-based outlier detection & flagging
├── week8_tableau_prep.py          # Week 8: Prepare Tableau-ready datasets
├── listings.csv                   # (not tracked) Combined listings dataset
├── sold.csv                       # (not tracked) Combined sold dataset
└── README.md
```

## Pipeline Overview
```
Raw MLS CSVs
  |
  ├── week1: Concatenate monthly files -> listings.csv, sold.csv
  |          Filter PropertyType == 'Residential'
  |
  ├── week2-3: EDA & validation -> listings_eda.csv, sold_eda.csv
  |            Missing value analysis, data type checks
  |
  ├── week3: Mortgage enrichment -> listings_enriched.csv, sold_enriched.csv
  |          Join 30-yr fixed rate by month
  |
  ├── week4-5: Cleaning -> listings_cleaned.csv, sold_cleaned.csv
  |            Remove duplicates, standardize fields
  |
  ├── week6: Feature engineering -> listings_engineered.csv, sold_engineered.csv
  |          price_ratio, close_to_orig_ratio, ppsf, listing_to_contract_days, etc.
  |
  ├── week7: Outlier detection -> *_flagged.csv, *_filtered.csv
  |          IQR method on ClosePrice, LivingArea, DaysOnMarket
  |
  └── week8: Tableau prep -> tableau_data/
             market_sold.csv, market_listings.csv,
             competitive_top100_agents.csv, competitive_top100_offices.csv,
             competitive_zipcode_heatmap.csv
```

## How to Run
1. Place all monthly `CRMLSListing*.csv` and `CRMLSSold*.csv` files in the `csv/` folder

2. Run the pipeline in order:
   ```bash
   python week1_listings.py
   python week1_sold.py
   python week2_eda.py
   python week3_mortgage_enrichment.py
   python week4_cleaning.py
   python week6_feature_engineering.py
   python week7_outlier_detection.py
   python week8_tableau_prep.py
   ```

3. Output Tableau-ready CSVs will be in the `tableau_data/` folder

4. Import into Tableau Public to build dashboards

## Weekly Progress
| Week | Topic | Script | Status |
|------|-------|--------|--------|
| 0 | MLS Data Pipeline Orientation | - | Done |
| 1 | Monthly Dataset Aggregation | `week1_*.py` | Done |
| 2-3 | Dataset Structuring & Validation | `week2_eda.py` | Done |
| 3 | Mortgage Rate Enrichment | `week3_mortgage_enrichment.py` | Done |
| 4-5 | Data Cleaning & Preparation | `week4_cleaning.py` | Done |
| 6 | Feature Engineering & Market Metrics | `week6_feature_engineering.py` | Done |
| 7 | Outlier Detection & Data Quality | `week7_outlier_detection.py` | Done |
| 8-10 | Tableau Dashboard Development | `week8_tableau_prep.py` | Done |
| 11-12 | Final Presentation & Report | - | Done |

## Author
**Yang-Hsuan Lin** - Data Analyst Intern, IDX Exchange (Summer 2026)
- Tableau Public: [yang.hsuan.lin](https://public.tableau.com/app/profile/yang.hsuan.lin/vizzes)
