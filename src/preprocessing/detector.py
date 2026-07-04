import pandas as pd
from src.utils.logger import get_logger

logger = get_logger(__name__)

def detect_features(df: pd.DataFrame, target_col: str, drop_cols: list = None) -> dict:
    """
    Automatically detect feature types (numeric, categorical, boolean) from a DataFrame.
    
    Args:
        df: The pandas DataFrame to inspect.
        target_col: The target column to exclude from features.
        drop_cols: List of ID or metadata columns to exclude.
        
    Returns:
        dict: A dictionary containing lists of column names for each type.
    """
    if drop_cols is None:
        drop_cols = []
        
    logger.info("  [Auto-Detector] Inspecting DataFrame schema...")
    
    # Exclude target and metadata columns
    exclude = set(drop_cols + [target_col])
    cols_to_evaluate = [col for col in df.columns if col not in exclude]
    
    numeric_features = []
    categorical_features = []
    boolean_features = []
    
    for col in cols_to_evaluate:
        # Check boolean
        if pd.api.types.is_bool_dtype(df[col]) or set(df[col].dropna().unique()).issubset({0, 1, 0.0, 1.0}):
            # If it strictly has 2 unique values (0/1), treat as boolean/binary numeric
            boolean_features.append(col)
        # Check numeric
        elif pd.api.types.is_numeric_dtype(df[col]):
            numeric_features.append(col)
        # Check categorical
        elif pd.api.types.is_object_dtype(df[col]) or pd.api.types.is_categorical_dtype(df[col]):
            # Check cardinality to avoid treating unique IDs as categories
            if df[col].nunique() < 50:
                categorical_features.append(col)
            else:
                logger.warning(f"  [Auto-Detector] Dropping high-cardinality string column: {col}")
        else:
            logger.warning(f"  [Auto-Detector] Ignored unsupported type in column: {col}")
            
    logger.info(f"  [Auto-Detector] Detected {len(numeric_features)} Numeric, {len(categorical_features)} Categorical, {len(boolean_features)} Boolean features.")
    
    return {
        "numeric": numeric_features,
        "categorical": categorical_features,
        "boolean": boolean_features
    }
