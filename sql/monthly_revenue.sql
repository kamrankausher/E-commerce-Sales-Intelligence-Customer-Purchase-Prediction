SELECT 
    strftime(CAST(o.order_purchase_timestamp AS TIMESTAMP), '%Y-%m') AS month,
    SUM(p.payment_value) AS total_revenue,
    COUNT(DISTINCT o.order_id) AS total_orders
FROM orders o
JOIN payments p ON o.order_id = p.order_id
WHERE o.order_status = 'delivered'
GROUP BY month
ORDER BY month ASC;
