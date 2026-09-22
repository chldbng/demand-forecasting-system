import numpy as np
import pandas as pd

START_DATE, END_DATE = "2022-01-01", "2025-12-31"

STORES = [
    {"store_id": 1, "store_name": "Downtown Flagship", "region": "Northeast", "city": "New York"},
    {"store_id": 2, "store_name": "Westside Mall", "region": "West", "city": "Los Angeles"},
    {"store_id": 3, "store_name": "Lakeview Plaza", "region": "Midwest", "city": "Chicago"},
    {"store_id": 4, "store_name": "Riverside Outlet", "region": "South", "city": "Houston"},
    {"store_id": 5, "store_name": "Harbor Point", "region": "West", "city": "Seattle"},
]

PRODUCTS = [
    {"product_id": 101, "product_name": "Wireless Earbuds", "category": "Electronics", "base_demand": 18, "price": 59.99},
    {"product_id": 102, "product_name": "Running Shoes", "category": "Apparel", "base_demand": 25, "price": 89.99},
    {"product_id": 103, "product_name": "Coffee Maker", "category": "Home & Kitchen", "base_demand": 12, "price": 49.99},
    {"product_id": 104, "product_name": "Yoga Mat", "category": "Sports & Outdoors", "base_demand": 20, "price": 24.99},
]

calendar = pd.date_range(START_DATE, END_DATE, freq='D')
print(f"{len(calendar)} days from {calendar.min().date} to {calendar.max().date()}")

day_of_week = calendar.dayofweek
year_index = calendar.year - calendar.year.min()

weekly_factor = 1.0 + 0.18 * np.isin(day_of_week, [ 4, 5, 6]) # Friday, Saturday, Sunday
trend_factor = 1.0 + 0.06 * (year_index + calendar.dayofyear / 365.0) # 6% increase per year

HOLIDAY_BOOSTS = {
    (11, 29): 2.8, # Black Friday
    (12, 24): 2.2, # Christmas Eve
    (12, 25): 0.3, # Christmas Day
    (1, 1): 0.4, # New Year's Day
    (7, 4): 1.6 # July 4th
}

CATEGORY_YEARLY_PHASE = {
    "Electronics": 330,     # peaks near year-end
    "Apparel": 60,          # peaks near spring
    "Home & Kitchen": 300,
    "Sports & Outdoors": 150,   # peaks in summer
}

STORE_SIZE_FACTOR = {1: 1.3, 2: 1.1, 3: 1.0, 4: 0.8, 5: 0.9}

def generate_sales(seed = 42):
    rng = np.random.default_rng(seed)
    day_of_year = calendar.dayofyear.to_numpy()

    rows = []
    for store in STORES:
        store_factor = STORE_SIZE_FACTOR[store["store_id"]]
        for product in PRODUCTS:
            phase = CATEGORY_YEARLY_PHASE[product["category"]]
            yearly_factor = 1.0 + 0.35 * np.cos(2 * np.pi * (day_of_year - phase) / 365.0)
            base = product["base_demand"] * store_factor

            promo_flag = rng.random(len(calendar)) < 0.04
            promo_lift = np.where(promo_flag, rng.uniform(1.3, 1.9, len(calendar)), 1.0)

            holiday_mult = np.ones(len(calendar))
            for i, d in enumerate(calendar):
                if (d.month, d.day) in HOLIDAY_BOOSTS:
                    holiday_mult[i] = HOLIDAY_BOOSTS[(d.month, d.day)]

            expected = base * trend_factor * weekly_factor * yearly_factor * promo_lift * holiday_mult
            units_sold = rng.poisson(np.clip(expected, 0.5, None))
            stockout_flag = rng.random(len(calendar)) < 0.02
            units_sold = np.where(stockout_flag, np.minimum(units_sold, rng.integers(0,3, len(calendar))), units_sold)
            unit_price = product["price"] * np.where(promo_flag, rng.uniform(0.75, 0.9, len(calendar)), 1.0)
            revenue = np.round(units_sold * unit_price, 2)

            rows.append(pd.DataFrame({
                "date": calendar,
                "store_id": store["store_id"],
                "product_id": product["product_id"],
                "units_sold": units_sold,
                "promo_flag": promo_flag.astype(int),
                "stockout_flag": stockout_flag.astype(int),
                "unit_price": unit_price,
                "revenue": revenue
            }))
    return pd.concat(rows, ignore_index = True)

from pathlib import Path
import sqlite3

def main():
    project_root = Path(__file__).resolve().parents[1]
    data_dir = project_root / "data"

    stores_df = pd.DataFrame(STORES)
    products_df = pd.DataFrame(PRODUCTS)
    sales_df = generate_sales()
    sales_df["date"] = sales_df["date"].dt.strftime("%Y-%m-%d")

    stores_df.to_csv(data_dir / "stores.csv", index=False)
    products_df.to_csv(data_dir / "products.csv", index=False)
    sales_df.to_csv(data_dir / "sales.csv", index=False)

    db_path = data_dir / "demand_forecasting.db"
    conn = sqlite3.connect(db_path)
    conn.executescript((project_root / "sql" / "schema.sql").read_text())
    stores_df.to_sql("stores", conn, if_exists="append", index=False)
    products_df.to_sql("products", conn, if_exists="append", index=False)
    sales_df.to_sql("sales", conn, if_exists="append", index=False)
    conn.commit()
    conn.close()
    print(f"Wrote {len(sales_df):,} rows to {db_path}")

if __name__ == "__main__":
    main()


