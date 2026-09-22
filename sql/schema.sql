DROP TABLE IF EXISTS sales;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS stores;

CREATE TABLE stores (
    store_id    INTEGER PRIMARY KEY,
    store_name  TEXT NOT NULL,
    region      TEXT NOT NULL,
    city        TEXT NOT NULL
);

CREATE TABLE products (
    product_id      INTEGER PRIMARY KEY,
    product_name    TEXT NOT NULL,
    category        TEXT NOT NULL,
    base_demand     REAL NOT NULL,
    price           REAL NOT NULL
);

CREATE TABLE sales (
    sale_id         INTEGER PRIMARY KEY,
    date            TEXT NOT NULL,
    store_id        INTEGER NOT NULL REFERENCES stores(store_id),
    product_id      INTEGER NOT NULL REFERENCES products(product_id),
    units_sold      INTEGER NOT NULL,
    unit_price      REAL NOT NULL,
    revenue         REAL NOT NULL,
    promo_flag      INTEGER NOT NULL DEFAULT 0,
    stockout_flag   INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX idx_sales_date ON sales(date);
CREATE INDEX idx_sales_store_product_date ON sales(store_id, product_id, date)