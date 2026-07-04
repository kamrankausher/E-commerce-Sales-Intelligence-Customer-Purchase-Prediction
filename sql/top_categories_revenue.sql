SELECT 
    t.product_category_name_english AS category,
    COUNT(i.order_item_id) AS items_sold,
    SUM(i.price) AS total_revenue
FROM items i
JOIN products p ON i.product_id = p.product_id
JOIN category_translation t ON p.product_category_name = t.product_category_name
JOIN orders o ON i.order_id = o.order_id
WHERE o.order_status = 'delivered'
GROUP BY category
ORDER BY total_revenue DESC
LIMIT 10;
