"""
config.py — Centralized configuration for the E-commerce Customer Analytics project.
"""
import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Data paths
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "processed")
OUTPUTS_DIR = os.path.join(PROJECT_ROOT, "outputs")
REPORTS_DIR = os.path.join(PROJECT_ROOT, "reports")
MODELS_DIR = os.path.join(PROJECT_ROOT, "models")

# Data files
MASTER_CLEANED_FILE = os.path.join(PROCESSED_DATA_DIR, "master_cleaned.csv")
ML_DATASET_FILE = os.path.join(PROCESSED_DATA_DIR, "ml_dataset.csv")
MODEL_RESULTS_FILE = os.path.join(OUTPUTS_DIR, "model_results.csv")
BEST_MODEL_FILE = os.path.join(MODELS_DIR, "best_model.pkl")

# ML Parameters
TARGET_COL = "churned"
CHURN_THRESHOLD_DAYS = 90
TEST_SIZE = 0.2
RANDOM_SEED = 42

FEATURE_COLS = [
    "frequency", "monetary", "recency_days", "avg_order_value",
    "avg_review_score", "review_count", "tenure_days",
    "avg_days_between_orders", "avg_installments",
    "payment_type_diversity", "late_delivery_rate", "category_diversity"
]

# Create directories if they don't exist
for d in [RAW_DATA_DIR, PROCESSED_DATA_DIR, OUTPUTS_DIR, REPORTS_DIR, MODELS_DIR]:
    os.makedirs(d, exist_ok=True)
