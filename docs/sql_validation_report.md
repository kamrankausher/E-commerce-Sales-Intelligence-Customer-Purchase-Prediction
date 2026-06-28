# SQL Validation Report

## 1. Overview
The platform generates analytics via 12 sophisticated SQL queries stored in `sql/analytics_queries.sql`, queried against an SQLite database.

## 2. Advanced Techniques Utilized
The resume states the project uses "CTEs, window functions, and cohort retention logic."
- **Common Table Expressions (CTEs):** Used heavily in 6 of the 12 queries to modularize complex sub-selections (e.g., Query 3 Cohort Analysis, Query 6 Monthly Retention, Query 9 RFM).
- **Window Functions:** Implemented multiple times:
  - `LAG()` for month-over-month growth.
  - `NTILE(5)` for RFM scoring segmentation.
  - `RANK()` and `ROW_NUMBER()` for lifetime value distributions.
- **Date Manipulations:** `strftime` and `julianday` are properly utilized for accurate monthly offsets and day-diffs.

## 3. Performance & Indexing
Executing window functions and multiple JOINs over 18,000+ records can result in full table scans.
- **Validation:** The ingestion pipeline in `data/load_data.py` injects critical indexes (`idx_orders_customer`, `idx_items_order`, `idx_payments_order`, `idx_customers_state`). 
- **Result:** These indexes enable the queries to run efficiently without lagging the FastAPI responses.

## 4. Conclusion
The SQL layer is advanced, meticulously written, and clearly designed to demonstrate high-level data engineering and analytical skills suitable for interviews.
