from src.utils.logger import get_logger
logger = get_logger(__name__)

"""
feature_engine.py — Create ML-ready features from raw e-commerce data.

WHY THIS EXISTS:
    Raw transactional data (orders, payments, reviews) isn't suitable for ML.
    We need to aggregate it to the CUSTOMER level and engineer meaningful
    features that capture purchasing behavior, engagement, and satisfaction.

INTERVIEW EXPLANATION:
    "I engineered 12 features at the customer level. The key insight was
    defining churn as 'no purchase in the last 90 days.' I then built features
    like recency, frequency, monetary value, average review score, tenure,
    and delivery experience. These map directly to business intuition —
    customers who haven't bought recently, buy infrequently, or had bad
    delivery experiences are more likely to churn."

FEATURE LIST:
    1.  frequency                — Number of orders placed
    2.  monetary                 — Total amount spent (R$)
    3.  recency_days             — Days since last purchase
    4.  avg_order_value          — Average spend per order
    5.  avg_review_score         — Mean review score given
    6.  review_count             — Number of reviews submitted
    7.  tenure_days              — Days between first and last purchase
    8.  avg_days_between_orders  — Average gap between consecutive orders
    9.  avg_installments         — Average payment installments used
    10. payment_type_diversity   — Number of distinct payment methods
    11. late_delivery_rate       — Proportion of orders delivered late
    12. category_diversity       — Number of unique product categories bought
"""

import pandas as pd
import numpy as np


def define_churn(df: pd.DataFrame, churn_threshold_days: int = 90) -> pd.DataFrame:
    """
    Define the churn label for each customer.

    Definition: A customer is 'churned' if they have NOT made a purchase
    in the last `churn_threshold_days` days (relative to the most recent
    date in the dataset).

    Why 90 days: Industry standard for e-commerce. Most platforms consider
    a customer inactive after 3 months without a purchase.

    Args:
        df: Master DataFrame with customer_unique_id and order_purchase_timestamp
        churn_threshold_days: Number of inactive days to define churn (default: 90)

    Returns:
        DataFrame with customer_unique_id and churn label (1=churned, 0=active)
    """
    reference_date = df["order_purchase_timestamp"].max()
    cutoff_date = reference_date - pd.Timedelta(days=churn_threshold_days)

    last_purchase = df.groupby("customer_unique_id")["order_purchase_timestamp"].max()
    churn_labels = (last_purchase < cutoff_date).astype(int)
    churn_labels.name = "churned"

    logger.info(f"  Reference date: {reference_date.date()}")
    logger.info(f"  Churn cutoff:   {cutoff_date.date()} ({churn_threshold_days} days before)")
    logger.info(f"  Churned: {churn_labels.sum()} ({churn_labels.mean()*100:.1f}%)")
    logger.info(f"  Active:  {(~churn_labels.astype(bool)).sum()} ({(1-churn_labels.mean())*100:.1f}%)")

    return churn_labels.reset_index()


def build_customer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate raw transactional data to customer-level features.

    Input: Master DataFrame (one row per order-item)
    Output: One row per customer_unique_id with 12 engineered features

    Feature Engineering Decisions:
    - We aggregate at customer_unique_id (not customer_id) because one
      person can have multiple customer_ids across sessions.
    - monetary uses payment_value (actual amount paid), not item price.
    - late_delivery_rate is a proportion [0, 1], not a count.
    """
    reference_date = df["order_purchase_timestamp"].max()

    # ─── Group by customer ──────────────────────────────────────────────
    # Deduplicate to order level first (items table creates multiple rows per order)
    orders = df.drop_duplicates(subset=["order_id", "customer_unique_id"])

    # 1. Frequency — number of distinct orders
    frequency = orders.groupby("customer_unique_id")["order_id"].nunique()
    frequency.name = "frequency"

    # 2. Monetary — total payment value
    monetary = orders.groupby("customer_unique_id")["payment_value"].sum().round(2)
    monetary.name = "monetary"

    # 3. Recency — days since last purchase
    last_purchase = orders.groupby("customer_unique_id")["order_purchase_timestamp"].max()
    recency = (reference_date - last_purchase).dt.days
    recency.name = "recency_days"

    # 4. Average order value
    avg_order_value = (monetary / frequency).round(2)
    avg_order_value.name = "avg_order_value"

    # 5. Average review score
    avg_review = orders.groupby("customer_unique_id")["review_score"].mean().round(2)
    avg_review.name = "avg_review_score"

    # 6. Review count
    review_count = orders.groupby("customer_unique_id")["review_score"].count()
    review_count.name = "review_count"

    # 7. Tenure — days between first and last purchase
    first_purchase = orders.groupby("customer_unique_id")["order_purchase_timestamp"].min()
    tenure = (last_purchase - first_purchase).dt.days
    tenure.name = "tenure_days"

    # 8. Average days between orders
    def calc_avg_days_between(group):
        dates = group.sort_values()
        if len(dates) < 2:
            return 0
        diffs = dates.diff().dt.days.dropna()
        return diffs.mean()

    avg_days_between = orders.groupby("customer_unique_id")["order_purchase_timestamp"].apply(
        calc_avg_days_between
    ).round(1)
    avg_days_between.name = "avg_days_between_orders"

    # 9. Average installments
    avg_installments = orders.groupby("customer_unique_id")["payment_installments"].mean().round(1)
    avg_installments.name = "avg_installments"

    # 10. Payment type diversity
    payment_diversity = orders.groupby("customer_unique_id")["payment_type_diversity"].max()
    payment_diversity.name = "payment_type_diversity"

    # 11. Late delivery rate
    if "order_delivered_customer_date" in df.columns and "order_estimated_delivery_date" in df.columns:
        orders_with_delivery = orders.dropna(subset=["order_delivered_customer_date", "order_estimated_delivery_date"])
        orders_with_delivery = orders_with_delivery.copy()
        orders_with_delivery["is_late"] = (
            orders_with_delivery["order_delivered_customer_date"] >
            orders_with_delivery["order_estimated_delivery_date"]
        ).astype(int)
        late_rate = orders_with_delivery.groupby("customer_unique_id")["is_late"].mean().round(3)
        late_rate.name = "late_delivery_rate"
    else:
        late_rate = pd.Series(0, index=frequency.index, name="late_delivery_rate")

    # 12. Category diversity
    category_diversity = df.groupby("customer_unique_id")["product_category_name_english"].nunique()
    category_diversity.name = "category_diversity"

    # ─── Combine all features ───────────────────────────────────────────
    features = pd.concat([
        frequency, monetary, recency, avg_order_value, avg_review,
        review_count, tenure, avg_days_between, avg_installments,
        payment_diversity, late_rate, category_diversity
    ], axis=1).reset_index()

    # Fill any remaining NaN (e.g., customers with no reviews)
    features = features.fillna(0)

    logger.info(f"  [OK] Built {len(features.columns)-1} features for {len(features):,} customers")
    logger.info(f"  Features: {list(features.columns[1:])}")

    return features


def prepare_ml_dataset(df: pd.DataFrame, churn_threshold_days: int = 90):
    """
    Complete pipeline: raw data → ML-ready dataset with features + labels.

    Returns:
        features_df: DataFrame with customer_unique_id + 12 features + churn label
    """
    print("=" * 60)
    logger.info("  FEATURE ENGINEERING PIPELINE")
    print("=" * 60)

    logger.info("[1/3] Defining churn labels...")
    churn = define_churn(df, churn_threshold_days)

    logger.info("[2/3] Building customer features...")
    features = build_customer_features(df)

    logger.info("[3/3] Merging features with labels...")
    dataset = features.merge(churn, on="customer_unique_id", how="inner")

    # CRITICAL: Drop 'recency_days' because it perfectly correlates with the target (churned = recency_days > 90)
    # This prevents extreme data leakage in Phase 5+
    dataset = dataset.drop(columns=["recency_days"], errors="ignore")

    logger.info(f"  [OK] Final ML dataset: {dataset.shape[0]:,} customers × {dataset.shape[1]} columns")
    logger.info(f"  Churn rate: {dataset['churned'].mean()*100:.1f}%")
    print("=" * 60)

    return dataset
