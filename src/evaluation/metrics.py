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
        "missing_values_removed_or_imputed": True,
        "duplicates_removed": len(master_raw) - len(master_clean),
        "features_engineered": len(ml_data.columns) - 2,
        "final_samples": len(ml_data)
    }

def generate_leaderboard(results: list, task_type: str = "Classification") -> dict:
    """
    Generate a leaderboard from a list of result dictionaries.
    Identifies Best, Fastest, and Most Interpretable models.
    """
    if not results:
        return {}

    df = pd.DataFrame(results)
    
    # Sort
    if task_type == "Classification":
        df = df.sort_values("roc_auc", ascending=False)
        best_metric = "roc_auc"
    else:
        df = df.sort_values("rmse", ascending=True)
        best_metric = "rmse"
        
    best_model = df.iloc[0]["model"]
    
    # Fastest
    fastest_model = df.sort_values("inference_time_sec").iloc[0]["model"]
    
    # Interpretable
    interpretable_models = ["Logistic Regression", "Decision Tree", "Linear Regression"]
    df_interp = df[df["model"].isin(interpretable_models)]
    if not df_interp.empty:
        most_interpretable = df_interp.iloc[0]["model"]
    else:
        most_interpretable = best_model
        
    leaderboard_info = {
        "best_model": best_model,
        "fastest_model": fastest_model,
        "most_interpretable": most_interpretable,
        "all_results": df.to_dict(orient="records")
    }
    
    return leaderboard_info
