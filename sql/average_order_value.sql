SELECT 
    COUNT(DISTINCT o.order_id) AS total_orders,
    SUM(p.payment_value) AS total_revenue,
    SUM(p.payment_value) / COUNT(DISTINCT o.order_id) AS average_order_value
FROM orders o
JOIN payments p ON o.order_id = p.order_id
WHERE o.order_status = 'delivered';
