# Demand Forecasting System

A SQL + Python project analyzing retail demand pattterns across a synthetic multi-store, multi-product sales dataset, with a Jupyter notebook forecasting layer in progress.

## Status

This project is actively in progress. Current state:
- [X] Designed a normalized SQL schema (stores, products, sales)
- [X] Built a synthetic data generator with trend, weekly/yearly seasonality, promotions, and stockout stimulation
- [X] Wrote SQL analysis queries: rolling averages, year-over-year growth, promotion lift, day-of-week seasonability, store rankings, stockout tracking
- [ ] Build the forecasting notebook - baseline models (seasonal naive, rolling average), then linear regression and Holt-Winters exponential smoothing, evaluated with MAE/RMSE/MAPE *(in progress)*
- [ ] Add model comparison results and visualizations to this README
- [ ] Extend to per-store/per-product forecasts

## Why I built this

Retail and e-commerce companies rely heavily on demand forecasting for inventory and staffing decisions, and I wanted a project that mirrored that real workflow end to end from a normalized SQL schema through exploratory queries to an actual forecast, rather than just a cleaned CSV and a model.fit() call. I generated the dataset synthetically so I could design specific, realistic wrinkles (stockouts capping observed demand, promotions confounding the trend) that are worth reasoning about even without a licensed dataset.

## Project structure
```
demand-forecasting-system/
├── data/
│   ├── stores.csv
│   ├── products.csv
│   ├── sales.csv
│   └── demand_forecasting.db
├── sql/
│   ├── schema.sql
│   └── analysis_queries.sql
├── notebooks/
│   └── demand_forecasting.ipynb
├── src/
│   └── generate-data.py
├── requirements.txt
└── README.md
```

## Dataset

Synthetic daily sales spanning **2022-01-01 to 2025-12-31** (1,641) days across **5 stores** and **4 products**, totaling **29,220 rows**. Generated rather than sourced publicly, so the mechanics are fully known and documented, which is useful for a project meant to demonstrate SQL and forecasting technique rather than data cleaning.

The generator (`src/generate-data.py`) models:
- An upward yearly trend (~6% per year)
- Weekly seasonality (weekend lift)
- Category-specific yearly seasonality (e.g. electronics peak near year-end)
- Random promotions (~4% of days) with a demand and price lift
- Fixed holiday effects (Black Friday-style spike, Christmas closure, etc.)
- Occasional stockouts that cap observed demand below "true" demand

Regenerate it at any time:
```bash
python src/generate-data.py
```

## SQL

`sql/schema.sql` defines the schema: `stores`, `products`, and a `sales` fact table. `sql/analysis_queries.sql` has queries covering daily/monthly demand, 7-day rolling averages (window functions), year-over-year growth (`LAG()` + CTEs), promotion lift, day-of-week seasonality, and store performance.

Run them:
```bash
sqlite3 data/demand_forecasting.db < sql/analysis_queries.sql
```

## Setup
```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python src/generate-data.py
```

## Roadmap
- Build out the forecasting notebook (baseline models -> linear regression -> Hold-Winters), evaluated on a 90-day holdout
- Add a model comparison chart and results table to this README
- Extend from an aggregate forecast to per-store/per-product forecasts
- Explore SARIMA/Prophet or gradient-boosted model as a stretch goal