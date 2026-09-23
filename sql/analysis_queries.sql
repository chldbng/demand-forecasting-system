SELECT date, SUM(units_sold) AS total_units, SUM(revenue) AS total_revenue
FROM sales
GROUP BY date
ORDER BY date;

-- Top 10 best-selling products by units
SELECT p.product_name, p.category, SUM(s.units_sold) AS total_units, ROUND(SUM(s.revenue), 2) AS total_revenue
FROM sales s
JOIN products p ON p.product_id = s.product_id
GROUP BY p.product_name, p.category
ORDER BY total_units DESC
LIMIT 10;

-- 7-day rolling average demand per product
SELECT 
    date, product_id, units_sold, 
    AVG(units_sold) OVER (PARTITION BY product_id ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS rolling_7d_avg
FROM (
    SELECT date, product_id, SUM(units_sold) AS units_sold
    FROM sales
    GROUP BY date, product_id
)
ORDER BY product_id, date;

-- Year-over-year growth by product
WITH yearly AS (
    SELECT product_id, strftime('%Y', date) AS year, SUM(units_sold) AS total_units
    FROM sales
    GROUP BY product_id, year
)
SELECT 
    product_id, year, total_units,
    LAG(total_units) OVER (PARTITION BY product_id ORDER BY year) AS prev_year_units,
    ROUND(100.0 * (total_units - LAG(total_units) OVER (PARTITION BY product_id ORDER BY year))
        / NULLIF(LAG(total_units) OVER (PARTITION BY product_id ORDER BY year), 0), 1) AS yoy_growth_percentage
FROM yearly
ORDER BY product_id, year;

-- Day-of-week seasonality
SELECT
    CASE CAST(strftime('%w', date) AS INTEGER)
        WHEN 0 THEN 'Sunday'
        WHEN 1 THEN 'Monday'
        WHEN 2 THEN 'Tuesday'
        WHEN 3 THEN 'Wednesday'
        WHEN 4 THEN 'Thursday'
        WHEN 5 THEN 'Friday'
        WHEN 6 THEN 'Saturday'
    END AS weekday,
    ROUND(AVG(units_sold), 2) AS avg_units_sold
FROM sales
GROUP BY CAST(strftime('%w', date) AS INTEGER)
ORDER BY CAST(strftime('%w', date) AS INTEGER);

-- Store performance comparison
SELECT
    st.store_name, st.region, SUM(s.units_sold) AS total_units, ROUND(SUM(s.revenue), 2) AS total_revenue
FROM sales s
JOIN stores st ON st.store_id = s.store_id
GROUP BY st.store_name, st.region
ORDER BY total_revenue DESC;

-- Promotion lift: average units sold on promo days vs. non-promo days
SELECT
    p.product_name,
    ROUND(AVG(CASE WHEN s.promo_flag = 1 THEN s.units_sold END), 2) AS avg_units_promo,
    ROUND(AVG(CASE WHEN s.promo_flag = 0 THEN s.units_sold END), 2) AS avg_units_non_promo
FROM sales s
JOIN products p ON p.product_id = s.product_id
GROUP BY p.product_name
ORDER BY avg_units_promo DESC;
