from src.utils.logger import get_logger
logger = get_logger(__name__)

"""
data_cleaner.py — Handle missing values, outliers, and data type issues.

WHY THIS EXISTS:
    Raw data always has quality issues. This module provides reusable functions
    for missing value analysis, outlier detection (IQR method), date parsing,
    and duplicate removal. Each function explains what it does and why.

INTERVIEW EXPLANATION:
    "Before any analysis, I cleaned the data systematically. I checked for
    missing values — about 2% of delivery dates were null (undelivered orders)
    and 10% of reviews were missing. I handled missing dates by filtering to
    delivered orders only, imputed review scores with the median, and used
    IQR-based outlier detection on order values to cap extreme prices."
"""

import pandas as pd
import numpy as np


def analyze_missing(df: pd.DataFrame) -> pd.DataFrame:
    """
    Show missing value counts and percentages for all columns.

    Returns:
        DataFrame with columns: column, missing_count, missing_pct
    """
    missing = df.isnull().sum()
    pct = (missing / len(df) * 100).round(2)
    result = pd.DataFrame({
        "column": missing.index,
        "missing_count": missing.values,
        "missing_pct": pct.values
    })
    return result[result["missing_count"] > 0].sort_values("missing_pct", ascending=False).reset_index(drop=True)


def fix_date_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert all date/timestamp columns to datetime type.

    Why: Pandas reads dates as strings by default. We need datetime
    for time-based calculations (delivery time, recency, tenure).
    """
    date_cols = [c for c in df.columns if "timestamp" in c or "date" in c]
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
            logger.info(f"  [OK] Converted {col} to datetime")
    return df


def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Handle missing values with appropriate strategies per column.

    Strategy:
    - review_score: fill with median (ordinal data, median is robust)
    - delivery dates: leave NaN (filter later — only analyze delivered orders)
    - product_category_name_english: fill with 'other'
    - numeric columns: fill with 0 if clearly countable
    """
    df = df.copy()

    # Review scores — fill with median
    if "review_score" in df.columns:
        median_score = df["review_score"].median()
        filled = df["review_score"].isnull().sum()
        df["review_score"] = df["review_score"].fillna(median_score)
        logger.info(f"  [OK] Filled {filled} missing review_score values with median ({median_score})")

    # Category names — fill with 'other'
    if "product_category_name_english" in df.columns:
        filled = df["product_category_name_english"].isnull().sum()
        df["product_category_name_english"] = df["product_category_name_english"].fillna("other")
        logger.info(f"  [OK] Filled {filled} missing category names with 'other'")

    # Freight value — fill with 0
    if "freight_value" in df.columns:
        filled = df["freight_value"].isnull().sum()
        df["freight_value"] = df["freight_value"].fillna(0)
        if filled > 0:
            logger.info(f"  [OK] Filled {filled} missing freight_value with 0")

    return df


def detect_outliers_iqr(df: pd.DataFrame, column: str, factor: float = 1.5) -> pd.DataFrame:
    """
    Detect outliers using the IQR method.

    Why IQR: It's robust to extreme values (unlike z-score which assumes
    normality). Works well for skewed e-commerce price distributions.

    Args:
        df: DataFrame
        column: numeric column to check
        factor: IQR multiplier (1.5 = standard, 3.0 = extreme only)

    Returns:
        DataFrame of outlier rows
    """
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - factor * IQR
    upper = Q3 + factor * IQR
    outliers = df[(df[column] < lower) | (df[column] > upper)]
    logger.info(f"  Outliers in '{column}': {len(outliers)} ({len(outliers)/len(df)*100:.1f}%)")
    logger.info(f"  Bounds: [{lower:.2f}, {upper:.2f}]  |  Range: [{df[column].min():.2f}, {df[column].max():.2f}]")
    return outliers


def cap_outliers(df: pd.DataFrame, column: str, factor: float = 1.5) -> pd.DataFrame:
    """
    Cap outliers to IQR bounds (winsorization).

    Why cap instead of remove: In e-commerce, high-value orders are real
    business events. Removing them would lose revenue information. Capping
    preserves the signal while reducing extreme influence on models.
    """
    df = df.copy()
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - factor * IQR
    upper = Q3 + factor * IQR

    capped = ((df[column] < lower) | (df[column] > upper)).sum()
    df[column] = df[column].clip(lower=lower, upper=upper)
    logger.info(f"  [OK] Capped {capped} outliers in '{column}' to [{lower:.2f}, {upper:.2f}]")
    return df


def remove_duplicates(df: pd.DataFrame, subset: list = None) -> pd.DataFrame:
    """Remove duplicate rows, optionally by subset of columns."""
    before = len(df)
    df = df.drop_duplicates(subset=subset)
    removed = before - len(df)
    if removed > 0:
        logger.info(f"  [OK] Removed {removed} duplicate rows")
    else:
        logger.info(f"  [OK] No duplicates found")
    return df


def filter_delivered_orders(df: pd.DataFrame) -> pd.DataFrame:
    """
    Keep only delivered orders.

    Why: Non-delivered orders (canceled, processing, unavailable) shouldn't
    be included in revenue, delivery, or churn analysis — they represent
    incomplete transactions.
    """
    before = len(df)
    df = df[df["order_status"] == "delivered"].copy()
    removed = before - len(df)
    logger.info(f"  [OK] Filtered to delivered orders: {len(df):,} rows ({removed:,} non-delivered removed)")
    return df
