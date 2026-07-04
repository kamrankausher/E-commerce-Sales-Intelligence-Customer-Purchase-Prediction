"""
schema.py — Data validation using Pandera.
"""
import pandera as pa
import pandas as pd
import logging
import os
import config

logger = logging.getLogger(__name__)

# Define schemas for raw tables
customers_schema = pa.DataFrameSchema({
    "customer_id": pa.Column(str, nullable=False),
    "customer_unique_id": pa.Column(str, nullable=False),
    "customer_zip_code_prefix": pa.Column(int, nullable=False),
    "customer_city": pa.Column(str, nullable=False),
    "customer_state": pa.Column(str, nullable=False, checks=pa.Check.str_length(2, 2)),
})

orders_schema = pa.DataFrameSchema({
    "order_id": pa.Column(str, nullable=False),
    "customer_id": pa.Column(str, nullable=False),
    "order_status": pa.Column(str, nullable=False),
    "order_purchase_timestamp": pa.Column(str, nullable=False),
})

# We can define more schemas, but for brevity we validate a few key tables.
schemas = {
    "customers": customers_schema,
    "orders": orders_schema
}

def validate_raw_data(dfs: dict):
    """Validate dataframes against their Pandera schemas."""
    logger.info("Starting Data Validation...")
    report_lines = ["# Data Validation Report\n"]
    
    for name, schema in schemas.items():
        if name in dfs:
            try:
                schema.validate(dfs[name])
                msg = f"[OK] {name}: Schema validation passed."
                logger.info(msg)
                report_lines.append(f"- {msg}")
            except pa.errors.SchemaError as e:
                msg = f"[FAIL] {name}: Schema validation failed. {e}"
                logger.error(msg)
                report_lines.append(f"- {msg}")
                
    # Save report
    os.makedirs(config.REPORTS_DIR, exist_ok=True)
    report_path = os.path.join(config.REPORTS_DIR, "validation_report.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
        
    logger.info(f"Validation report saved to {report_path}")
