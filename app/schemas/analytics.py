from pydantic import BaseModel
from typing import Optional

class RevenueByState(BaseModel):
    state: str
    total_orders: int
    total_revenue: float
    avg_order_value: float

class MonthlyRevenueTrend(BaseModel):
    month: str
    revenue: float
    prev_month_revenue: Optional[float] = None
    growth_pct: Optional[float] = None

class CohortAnalysis(BaseModel):
    cohort_month: str
    month_offset: int
    active_customers: int

class RepeatPurchaseRate(BaseModel):
    total_customers: int
    repeat_customers: int
    repeat_purchase_rate_pct: float

class TopSeller(BaseModel):
    seller_id: str
    seller_city: str
    seller_state: str
    orders_fulfilled: int
    total_revenue: float
    avg_item_price: float

class MonthlyRetentionRate(BaseModel):
    active_month: str
    active_count: int
    retained_count: Optional[int] = 0
    retention_rate_pct: Optional[float] = 0.0

class CategoryPerformance(BaseModel):
    category: str
    total_orders: int
    total_items_sold: int
    total_revenue: float
    avg_price: float
    avg_review_score: Optional[float] = None

class DeliveryPerformance(BaseModel):
    customer_state: str
    total_orders: int
    late_orders: int
    late_pct: float
    avg_delivery_days: float

class RFMSegmentation(BaseModel):
    segment: str
    customer_count: int

class PaymentMethodAnalysis(BaseModel):
    payment_type: str
    transaction_count: int
    total_value: float
    avg_value: float
    avg_installments: float
    revenue_rank: int

class CLVDistribution(BaseModel):
    total_customers: int
    avg_clv: float
    median_clv: float
    min_clv: float
    max_clv: float

class ReviewSentiment(BaseModel):
    category: str
    total_reviews: int
    avg_score: float
    positive_reviews: int
    negative_reviews: int
    positive_rate_pct: float
