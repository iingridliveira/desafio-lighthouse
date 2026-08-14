SET search_path TO lh_nautical, public;

CREATE OR REPLACE VIEW v_orders_eda AS
SELECT
    COUNT(*) AS total_rows,
    MIN(created_at) AS min_created_at,
    MAX(created_at) AS max_created_at,
    MIN(total) AS min_total,
    MAX(total) AS max_total,
    AVG(total) AS avg_total,
    COUNT(*) FILTER (WHERE total IS NULL) AS null_total,
    COUNT(*) FILTER (WHERE total < 0) AS negative_total
FROM orders;

CREATE OR REPLACE VIEW v_orders_by_month AS
SELECT
    DATE_TRUNC('month', created_at)::date AS month,
    COUNT(*) AS orders_count,
    SUM(total) AS total_sales,
    AVG(total) AS average_ticket
FROM orders
WHERE created_at IS NOT NULL
GROUP BY 1
ORDER BY 1;

CREATE OR REPLACE VIEW v_orders_by_channel AS
SELECT
    COALESCE(channel, '[NULO]') AS channel,
    COUNT(*) AS orders_count,
    SUM(total) AS total_sales,
    AVG(total) AS average_ticket
FROM orders
GROUP BY 1
ORDER BY total_sales DESC NULLS LAST;

CREATE OR REPLACE VIEW v_orders_nulls AS
SELECT 'id' AS column_name, COUNT(*) FILTER (WHERE id IS NULL) AS null_count, COUNT(*) AS total_rows FROM orders
UNION ALL SELECT 'order_number', COUNT(*) FILTER (WHERE order_number IS NULL), COUNT(*) FROM orders
UNION ALL SELECT 'channel', COUNT(*) FILTER (WHERE channel IS NULL), COUNT(*) FROM orders
UNION ALL SELECT 'customer_id', COUNT(*) FILTER (WHERE customer_id IS NULL), COUNT(*) FROM orders
UNION ALL SELECT 'salesperson_id', COUNT(*) FILTER (WHERE salesperson_id IS NULL), COUNT(*) FROM orders
UNION ALL SELECT 'location_id', COUNT(*) FILTER (WHERE location_id IS NULL), COUNT(*) FROM orders
UNION ALL SELECT 'status', COUNT(*) FILTER (WHERE status IS NULL), COUNT(*) FROM orders
UNION ALL SELECT 'subtotal', COUNT(*) FILTER (WHERE subtotal IS NULL), COUNT(*) FROM orders
UNION ALL SELECT 'discount_amount', COUNT(*) FILTER (WHERE discount_amount IS NULL), COUNT(*) FROM orders
UNION ALL SELECT 'total', COUNT(*) FILTER (WHERE total IS NULL), COUNT(*) FROM orders
UNION ALL SELECT 'placed_at', COUNT(*) FILTER (WHERE placed_at IS NULL), COUNT(*) FROM orders
UNION ALL SELECT 'created_at', COUNT(*) FILTER (WHERE created_at IS NULL), COUNT(*) FROM orders
UNION ALL SELECT 'updated_at', COUNT(*) FILTER (WHERE updated_at IS NULL), COUNT(*) FROM orders;
