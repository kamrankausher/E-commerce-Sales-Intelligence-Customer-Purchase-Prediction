import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    """Test health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

# ─── Analytics Endpoint Tests ───────────────────────────────────────────────

def test_revenue_by_state():
    response = client.get("/api/v1/revenue-by-state")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "state" in data[0]
        assert "total_revenue" in data[0]

def test_monthly_revenue_trend():
    response = client.get("/api/v1/monthly-revenue-trend")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "month" in data[0]
        assert "revenue" in data[0]

def test_cohort_analysis():
    response = client.get("/api/v1/cohort-analysis")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "cohort_month" in data[0]
        assert "month_offset" in data[0]

def test_repeat_purchase_rate():
    response = client.get("/api/v1/repeat-purchase-rate")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "total_customers" in data[0]
        assert "repeat_purchase_rate_pct" in data[0]

def test_top_sellers():
    response = client.get("/api/v1/top-sellers")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "seller_id" in data[0]
        assert "total_revenue" in data[0]

def test_monthly_retention_rate():
    response = client.get("/api/v1/monthly-retention-rate")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "active_month" in data[0]
        assert "retention_rate_pct" in data[0]

def test_category_performance():
    response = client.get("/api/v1/category-performance")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "category" in data[0]
        assert "total_revenue" in data[0]

def test_delivery_performance():
    response = client.get("/api/v1/delivery-performance")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "customer_state" in data[0]
        assert "late_pct" in data[0]

def test_rfm_segmentation():
    response = client.get("/api/v1/rfm-segmentation")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "segment" in data[0]
        assert "customer_count" in data[0]

def test_payment_method_analysis():
    response = client.get("/api/v1/payment-method-analysis")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "payment_type" in data[0]
        assert "total_value" in data[0]

def test_clv_distribution():
    response = client.get("/api/v1/clv-distribution")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "avg_clv" in data[0]
        assert "median_clv" in data[0]

def test_review_sentiment():
    response = client.get("/api/v1/review-sentiment")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "category" in data[0]
        assert "positive_rate_pct" in data[0]

# ─── Negative & Edge Cases ──────────────────────────────────────────────────

def test_invalid_endpoint():
    """Test 404 response for non-existent endpoint."""
    response = client.get("/api/v1/invalid-endpoint-1234")
    assert response.status_code == 404

def test_method_not_allowed():
    """Test 405 response for incorrect HTTP method."""
    response = client.post("/api/v1/revenue-by-state")
    assert response.status_code == 405

def test_cors_headers():
    """Test CORS headers are present."""
    response = client.options(
        "/api/v1/revenue-by-state",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "X-Requested-With",
        },
    )
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers
