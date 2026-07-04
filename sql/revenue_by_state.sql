SELECT 
    c.customer_state AS state,
    COUNT(DISTINCT c.customer_id) AS unique_customers,
    SUM(p.payment_value) AS total_revenue
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN payments p ON o.order_id = p.order_id
WHERE o.order_status = 'delivered'
GROUP BY state
ORDER BY total_revenue DESC
LIMIT 10;
