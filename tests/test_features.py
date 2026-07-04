import pandas as pd
import numpy as np
import pytest
from src.features.engine import define_churn, build_customer_features

def test_define_churn():
    df = pd.DataFrame({
        "customer_unique_id": [1, 2, 3],
        "order_purchase_timestamp": pd.to_datetime([
            "2023-12-01",  # Recent
            "2023-01-01",  # Very old (churned)
            "2023-11-15"   # Inside threshold
        ])
    })
    
    churn_df = define_churn(df, churn_threshold_days=90)
    
    assert len(churn_df) == 3
    
    # customer 1: active (0)
    # customer 2: churned (1)
    # customer 3: active (0)
    assert churn_df.loc[churn_df["customer_unique_id"] == 1, "churned"].values[0] == 0
    assert churn_df.loc[churn_df["customer_unique_id"] == 2, "churned"].values[0] == 1
    assert churn_df.loc[churn_df["customer_unique_id"] == 3, "churned"].values[0] == 0

def test_build_customer_features():
    df = pd.DataFrame({
        "customer_unique_id": [1, 1, 2],
        "order_id": [101, 102, 201],
        "order_purchase_timestamp": pd.to_datetime(["2023-12-01", "2023-12-10", "2023-11-01"]),
        "payment_value": [50.0, 150.0, 300.0],
        "review_score": [4, 5, 2],
        "payment_installments": [1, 3, 5],
        "payment_type_diversity": [1, 1, 2],
        "product_category_name_english": ["toys", "books", "games"]
    })
    
    features = build_customer_features(df)
    
    assert len(features) == 2
    
    # Customer 1 stats
    c1 = features[features["customer_unique_id"] == 1].iloc[0]
    assert c1["frequency"] == 2
    assert c1["monetary"] == 200.0
    assert c1["avg_order_value"] == 100.0
    assert c1["avg_review_score"] == 4.5
    assert c1["review_count"] == 2
    assert c1["tenure_days"] == 9 # 10th minus 1st
    assert c1["category_diversity"] == 2
    
    # Customer 2 stats
    c2 = features[features["customer_unique_id"] == 2].iloc[0]
    assert c2["frequency"] == 1
    assert c2["monetary"] == 300.0
    assert c2["category_diversity"] == 1
