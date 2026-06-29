# IDX Exchange — MLS Data Analyst Internship

## Project Overview
End-to-end real estate analytics pipeline analyzing CRMLS (California Regional Multiple Listing Service) transaction data. The project covers data extraction, cleaning, feature engineering, and interactive Tableau dashboard development.

## Objectives
- Clean and structure raw MLS listing and sold transaction datasets
- Engineer key market metrics (sale-to-list ratio, price per sq ft, days on market, etc.)
- Build interactive Tableau dashboards for market analysis and competitive intelligence
- Produce a 1-page market intelligence report with data-driven insights

## Data Source
- **Provider:** CoreLogic Trestle API via IDX Exchange pipeline
- **Coverage:** Southern California (CRMLS)
- **Period:** January 2024 – May 2026
- **Datasets:** Monthly MLS Listing & Sold transaction CSV files

> Note: Raw CSV data files are not included in this repository due to confidentiality.

## Tools
- **Python** (Pandas) — data cleaning, feature engineering, aggregation
- **Tableau Desktop Public Edition** — interactive dashboards and visualizations

## Project Structure
```
├── week1_listings.py        # Combine monthly listing CSVs, filter Residential
├── week1_sold.py            # Combine monthly sold CSVs, filter Residential
├── listings.csv             # (not tracked) Combined listings dataset
├── sold.csv                 # (not tracked) Combined sold dataset
└── README.md
```

## How to Run
1. Place all monthly `CRMLSListing*.csv` and `CRMLSSold*.csv` files in the `csv/` folder
2. Run the Week 1 scripts:
   ```
   python week1_listings.py
   python week1_sold.py
   ```
3. Output: `listings.csv` and `sold.csv` filtered to `PropertyType == 'Residential'`

## Weekly Progress
| Week | Topic | Status |
|------|-------|--------|
| 0 | MLS Data Pipeline Orientation | Done |
| 1 | Monthly Dataset Aggregation | Done |
| 2-3 | Dataset Structuring & Validation | |
| 4-5 | Data Cleaning & Preparation | |
| 6 | Feature Engineering & Market Metrics | |
| 7 | Outlier Detection & Data Quality | |
| 8-10 | Tableau Dashboard Development | |
| 11-12 | Final Presentation & Report | |
