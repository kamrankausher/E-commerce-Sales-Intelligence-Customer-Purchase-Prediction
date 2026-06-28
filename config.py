"""
Central configuration for the E-commerce Growth Intelligence Platform.
All paths use os.path for cross-platform compatibility.
"""
import os

# ─── Paths ───────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
SQL_DIR = os.path.join(BASE_DIR, "sql")
DASHBOARD_DIR = os.path.join(BASE_DIR, "dashboard")

# ─── Database (SQLite) ──────────────────────────────────────────────────────
DATABASE_PATH = os.path.join(DATA_DIR, "ecommerce.db")

# ─── API ─────────────────────────────────────────────────────────────────────
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", 8000))

# ─── Logging ─────────────────────────────────────────────────────────────────
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
