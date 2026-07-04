"""
metrics.py — Extract and save evaluation metrics.
"""
import pandas as pd
import os
import config
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def save_metrics(metrics_dict: dict):
    """
    Save extracted metrics to outputs/model_results.csv.
    Appends to the file if it exists.
    """
    df = pd.DataFrame([metrics_dict])
    df['timestamp'] = datetime.now().isoformat()
    
    file_path = config.MODEL_RESULTS_FILE
    
    if os.path.exists(file_path):
        existing_df = pd.read_csv(file_path)
        combined = pd.concat([existing_df, df], ignore_index=True)
    else:
        combined = df
        
    combined.to_csv(file_path, index=False)
    logger.info(f"Metrics saved to {file_path}")

def extract_dataset_metrics(master_raw: pd.DataFrame, master_clean: pd.DataFrame, ml_data: pd.DataFrame) -> dict:
    """Extract metrics related to data processing."""
    return {
        "raw_rows": len(master_raw),
        "raw_columns": len(master_raw.columns),
        "cleaned_rows": len(master_clean),
        "cleaned_columns": len(master_clean.columns),
        "missing_values_removed_or_imputed": True, # Boolean flag for simplicity
        "duplicates_removed": len(master_raw) - len(master_clean),
        "features_engineered": len(ml_data.columns) - 2, # Excluding customer_id and target
        "final_samples": len(ml_data)
    }
