import os
from fastapi import APIRouter, HTTPException
from app.database import run_query, parse_sql_file
from config import SQL_DIR

router = APIRouter(tags=["Analytics"])

def _get_query(index: int) -> str:
    """Helper to fetch a specific query by its 0-based index."""
    queries = parse_sql_file(os.path.join(SQL_DIR, "analytics_queries.sql"))
    if not queries or index >= len(queries):
        raise HTTPException(status_code=500, detail="SQL query not found.")
    return queries[index]

@router.get("/revenue-by-state")
def get_revenue_by_state():
    """1. Revenue by State (Top 10)"""
    return run_query(_get_query(0))

@router.get("/monthly-revenue-trend")
def get_monthly_revenue_trend():
    """2. Monthly Revenue Trend"""
    return run_query(_get_query(1))

@router.get("/cohort-analysis")
def get_cohort_analysis():
    """3. Customer Cohort Analysis"""
    return run_query(_get_query(2))

@router.get("/repeat-purchase-rate")
def get_repeat_purchase_rate():
    """4. Repeat Purchase Rate"""
    return run_query(_get_query(3))

@router.get("/top-sellers")
def get_top_sellers():
    """5. Top 10 Sellers by Revenue"""
    return run_query(_get_query(4))

@router.get("/monthly-retention-rate")
def get_monthly_retention_rate():
    """6. Monthly Retention Rate"""
    return run_query(_get_query(5))

@router.get("/category-performance")
def get_category_performance():
    """7. Product Category Performance"""
    return run_query(_get_query(6))

@router.get("/delivery-performance")
def get_delivery_performance():
    """8. Delivery Performance Analysis"""
    return run_query(_get_query(7))

@router.get("/rfm-segmentation")
def get_rfm_segmentation():
    """9. RFM Segmentation (Aggregated to avoid huge payload)"""
    # Wrap the query in an aggregate to just return segment counts
    base_query = _get_query(8).rstrip(";")
    agg_query = f"WITH rfm_data AS ({base_query}) SELECT segment, COUNT(*) as customer_count FROM rfm_data GROUP BY segment ORDER BY customer_count DESC;"
    return run_query(agg_query)

@router.get("/payment-method-analysis")
def get_payment_method_analysis():
    """10. Payment Method Analysis"""
    return run_query(_get_query(9))

@router.get("/clv-distribution")
def get_clv_distribution():
    """11. Customer Lifetime Value (CLV) Distribution"""
    return run_query(_get_query(10))

@router.get("/review-sentiment")
def get_review_sentiment():
    """12. Review Sentiment by Category"""
    return run_query(_get_query(11))
