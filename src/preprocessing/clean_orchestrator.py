"""
clean_orchestrator.py - Helper to merge and clean the data.
"""
import pandas as pd
from src.preprocessing.cleaner import fix_date_columns, handle_missing_values, cap_outliers, filter_delivered_orders

def build_master_dataset(dfs: dict) -> pd.DataFrame:
    """Merge all tables into a single master dataframe and apply basic cleaning."""
    orders = filter_delivered_orders(fix_date_columns(dfs['orders']))
    customers = dfs['customers']
    items = dfs['items']
    products = dfs['products']
    translations = dfs['category_translation']
    sellers = dfs['sellers']
    payments = dfs['payments']
    reviews = handle_missing_values(dfs['reviews'])
    
    # Translate products
    products = products.merge(translations, on='product_category_name', how='left')
    
    # Aggregate payments
    payments_agg = payments.groupby('order_id').agg({
        'payment_value': 'sum',
        'payment_installments': 'mean',
        'payment_type': 'nunique'
    }).rename(columns={'payment_type': 'payment_type_diversity'}).reset_index()
    
    # Merge
    master = orders.merge(customers, on='customer_id', how='left')
    master = master.merge(items, on='order_id', how='left')
    master = master.merge(products, on='product_id', how='left')
    master = master.merge(sellers, on='seller_id', how='left')
    master = master.merge(payments_agg, on='order_id', how='left')
    master = master.merge(reviews[['order_id', 'review_score']], on='order_id', how='left')
    
    # Cap outliers in price and freight_value
    if 'price' in master.columns:
        master = cap_outliers(master, 'price', factor=1.5)
    
    return master
