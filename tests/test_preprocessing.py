import pandas as pd
import numpy as np
import pytest
from src.preprocessing.cleaner import handle_missing_values, cap_outliers, filter_delivered_orders

def test_handle_missing_values():
    df = pd.DataFrame({
        "review_score": [1, 5, np.nan, 3],
        "product_category_name_english": ["toys", np.nan, "books", "games"],
        "freight_value": [10.0, np.nan, 20.0, 5.0]
    })
    
    cleaned_df = handle_missing_values(df)
    
    # review_score median of [1, 5, 3] is 3
    assert cleaned_df["review_score"].isnull().sum() == 0
    assert cleaned_df.loc[2, "review_score"] == 3.0
    
    # category should be filled with 'other'
    assert cleaned_df["product_category_name_english"].isnull().sum() == 0
    assert cleaned_df.loc[1, "product_category_name_english"] == "other"
    
    # freight should be filled with 0
    assert cleaned_df["freight_value"].isnull().sum() == 0
    assert cleaned_df.loc[1, "freight_value"] == 0.0

def test_cap_outliers():
    df = pd.DataFrame({
        "price": [10, 12, 11, 15, 1000] # 1000 is an outlier
    })
    
    capped_df = cap_outliers(df, "price", factor=1.5)
    
    assert capped_df["price"].max() < 1000

def test_filter_delivered_orders():
    df = pd.DataFrame({
        "order_id": [1, 2, 3],
        "order_status": ["delivered", "canceled", "delivered"]
    })
    
    filtered_df = filter_delivered_orders(df)
    assert len(filtered_df) == 2
    assert "canceled" not in filtered_df["order_status"].values
