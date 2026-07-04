"""
data_loader.py — Load and merge all Olist CSV files into DataFrames.

WHY THIS EXISTS:
    The raw dataset is split across 8 CSV files (customers, orders, items,
    payments, reviews, products, sellers, category translations). This module
    provides a single function to load them all and a second function to merge
    them into one analytical DataFrame — the starting point for EDA and ML.

INTERVIEW EXPLANATION:
    "I created a data loader module because the Olist dataset is relational —
    8 separate CSVs connected by foreign keys. Rather than repeating merge
    logic in every notebook, I centralized it here. load_all() returns a
    dictionary of DataFrames, and build_master_df() joins them into one
    flat table ready for analysis."
"""

import os
import pandas as pd
import config

def load_all(data_dir: str = config.RAW_DATA_DIR) -> dict:
    """
    Load all 8 Olist CSV files into a dictionary of DataFrames.

    Returns:
        dict with keys: customers, orders, items, payments, reviews,
                        products, sellers, category_translation
    """
    files = {
        "customers":            "olist_customers_dataset.csv",
        "orders":               "olist_orders_dataset.csv",
        "items":                "olist_order_items_dataset.csv",
        "payments":             "olist_order_payments_dataset.csv",
        "reviews":              "olist_order_reviews_dataset.csv",
        "products":             "olist_products_dataset.csv",
        "sellers":              "olist_sellers_dataset.csv",
        "category_translation": "product_category_name_translation.csv",
    }

    dataframes = {}
    for key, filename in files.items():
        filepath = os.path.join(data_dir, filename)
        if os.path.exists(filepath):
            dataframes[key] = pd.read_csv(filepath)
            print(f"  [OK] Loaded {key}: {dataframes[key].shape}")
        else:
            print(f"  [MISSING] {key} at {filepath}")
            dataframes[key] = pd.DataFrame()

    return dataframes


def build_master_df(dfs: dict) -> pd.DataFrame:
    """
    Merge all tables into a single analytical DataFrame.

    Join path:
        orders → customers (customer_id)
        orders → items (order_id)
        items  → products (product_id)
        items  → sellers (seller_id)
        orders → payments (order_id)
        orders → reviews (order_id)
        products → category_translation (product_category_name)

    Returns:
        pd.DataFrame — one row per order-item with all dimensions attached.
    """
    # Start with orders + customers
    master = dfs["orders"].merge(dfs["customers"], on="customer_id", how="left")

    # Add order items
    master = master.merge(dfs["items"], on="order_id", how="left")

    # Add product info with English category names
    products = dfs["products"].merge(
        dfs["category_translation"],
        on="product_category_name",
        how="left"
    )
    master = master.merge(products, on="product_id", how="left")

    # Add seller info
    master = master.merge(dfs["sellers"], on="seller_id", how="left", suffixes=("", "_seller"))

    # Add payments (aggregate to order level first to avoid duplication)
    payments_agg = dfs["payments"].groupby("order_id").agg(
        payment_value=("payment_value", "sum"),
        payment_type=("payment_type", "first"),
        payment_installments=("payment_installments", "max"),
    ).reset_index()
    master = master.merge(payments_agg, on="order_id", how="left")

    # Add reviews
    master = master.merge(dfs["reviews"], on="order_id", how="left")

    print(f"\n  ✓ Master DataFrame: {master.shape[0]:,} rows × {master.shape[1]} columns")
    return master
