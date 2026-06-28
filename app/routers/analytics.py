from fastapi import APIRouter, HTTPException
from typing import List
from app.services.analytics_service import AnalyticsService
from app.schemas.analytics import (
    RevenueByState, MonthlyRevenueTrend, CohortAnalysis, RepeatPurchaseRate,
    TopSeller, MonthlyRetentionRate, CategoryPerformance, DeliveryPerformance,
    RFMSegmentation, PaymentMethodAnalysis, CLVDistribution, ReviewSentiment
)

router = APIRouter(tags=["Analytics"])

@router.get("/revenue-by-state", response_model=List[RevenueByState])
def get_revenue_by_state():
    """1. Revenue by State (Top 10)"""
    try:
        return AnalyticsService.execute_analytics_query(0)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/monthly-revenue-trend", response_model=List[MonthlyRevenueTrend])
def get_monthly_revenue_trend():
    """2. Monthly Revenue Trend"""
    try:
        return AnalyticsService.execute_analytics_query(1)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cohort-analysis", response_model=List[CohortAnalysis])
def get_cohort_analysis():
    """3. Customer Cohort Analysis"""
    try:
        return AnalyticsService.execute_analytics_query(2)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/repeat-purchase-rate", response_model=List[RepeatPurchaseRate])
def get_repeat_purchase_rate():
    """4. Repeat Purchase Rate"""
    try:
        return AnalyticsService.execute_analytics_query(3)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/top-sellers", response_model=List[TopSeller])
def get_top_sellers():
    """5. Top 10 Sellers by Revenue"""
    try:
        return AnalyticsService.execute_analytics_query(4)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/monthly-retention-rate", response_model=List[MonthlyRetentionRate])
def get_monthly_retention_rate():
    """6. Monthly Retention Rate"""
    try:
        return AnalyticsService.execute_analytics_query(5)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/category-performance", response_model=List[CategoryPerformance])
def get_category_performance():
    """7. Product Category Performance"""
    try:
        return AnalyticsService.execute_analytics_query(6)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/delivery-performance", response_model=List[DeliveryPerformance])
def get_delivery_performance():
    """8. Delivery Performance Analysis"""
    try:
        return AnalyticsService.execute_analytics_query(7)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/rfm-segmentation", response_model=List[RFMSegmentation])
def get_rfm_segmentation():
    """9. RFM Segmentation (Aggregated to avoid huge payload)"""
    try:
        return AnalyticsService.execute_analytics_query(8)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/payment-method-analysis", response_model=List[PaymentMethodAnalysis])
def get_payment_method_analysis():
    """10. Payment Method Analysis"""
    try:
        return AnalyticsService.execute_analytics_query(9)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/clv-distribution", response_model=List[CLVDistribution])
def get_clv_distribution():
    """11. Customer Lifetime Value (CLV) Distribution"""
    try:
        return AnalyticsService.execute_analytics_query(10)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/review-sentiment", response_model=List[ReviewSentiment])
def get_review_sentiment():
    """12. Review Sentiment by Category"""
    try:
        return AnalyticsService.execute_analytics_query(11)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
