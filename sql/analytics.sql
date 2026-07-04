-- SQL Analytics for E-commerce Dashboard

-- 1. Top 10 Products by Revenue
SELECT 
    p.product_category_name_english AS category,
    COUNT(i.order_item_id) AS items_sold,
    SUM(i.price) AS total_revenue
FROM orders o
JOIN items i ON o.order_id = i.order_id
JOIN products p ON i.product_id = p.product_id
WHERE o.order_status = 'delivered'
GROUP BY category
ORDER BY total_revenue DESC
LIMIT 10;

-- 2. Monthly Revenue Trend
SELECT 
    strftime('%Y-%m', order_purchase_timestamp) AS month,
    SUM(p.payment_value) AS revenue
FROM orders o
JOIN payments p ON o.order_id = p.order_id
WHERE o.order_status = 'delivered'
GROUP BY month
ORDER BY month;

-- 3. Customer Purchase Frequency (Repeat Customers)
WITH customer_orders AS (
    SELECT 
        customer_unique_id,
        COUNT(order_id) AS num_orders
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    WHERE o.order_status = 'delivered'
    GROUP BY customer_unique_id
)
SELECT 
    num_orders,
    COUNT(customer_unique_id) AS number_of_customers
FROM customer_orders
GROUP BY num_orders
ORDER BY num_orders;

-- 4. Top States by Revenue
SELECT 
    c.customer_state,
    SUM(p.payment_value) AS total_revenue,
    COUNT(DISTINCT o.order_id) AS total_orders
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN payments p ON o.order_id = p.order_id
WHERE o.order_status = 'delivered'
GROUP BY c.customer_state
ORDER BY total_revenue DESC
LIMIT 10;
