import pandas as pd
import numpy as np
from src.utils.logger import get_logger

logger = get_logger(__name__)

def detect_task_type(y: pd.Series) -> str:
    """
    Automatically determine if the target variable represents a Classification
    or Regression task.
    
    Rules:
    - If dtype is boolean or object/category -> Classification
    - If numeric and unique values <= 10 -> Classification
    - Otherwise -> Regression
    
    Returns:
        "Classification" or "Regression"
    """
    logger.info(f"  [Auto-Detector] Inspecting target variable '{y.name}'...")
    
    unique_vals = y.nunique()
    dtype = y.dtype
    
    logger.info(f"  [Auto-Detector] Target dtype: {dtype}, Unique values: {unique_vals}")
    
    if pd.api.types.is_bool_dtype(dtype) or pd.api.types.is_object_dtype(dtype) or isinstance(dtype, pd.CategoricalDtype):
        logger.info("  [Auto-Detector] Detected Task: Classification (Categorical/Boolean target)")
        return "Classification"
        
    if pd.api.types.is_numeric_dtype(dtype):
        if unique_vals <= 10:
            logger.info("  [Auto-Detector] Detected Task: Classification (Low cardinality numeric target)")
            return "Classification"
        else:
            logger.info("  [Auto-Detector] Detected Task: Regression (Continuous numeric target)")
            return "Regression"
            
    # Default fallback
    logger.warning("  [Auto-Detector] Could not definitively determine task type. Defaulting to Regression.")
    return "Regression"
