import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from src.utils.logger import get_logger

logger = get_logger(__name__)

class OutlierCapper(BaseEstimator, TransformerMixin):
    """
    Custom Scikit-Learn Transformer to cap outliers using the IQR method.
    
    Why this is leak-free:
    - fit() calculates the Q1, Q3, and IQR *only* on the training data.
    - transform() applies those learned bounds to both training and test data.
    """
    def __init__(self, factor=1.5):
        self.factor = factor
        self.bounds_ = {}

    def fit(self, X, y=None):
        if not isinstance(X, pd.DataFrame):
            X = pd.DataFrame(X)
            
        for col in X.columns:
            if pd.api.types.is_numeric_dtype(X[col]):
                q1 = X[col].quantile(0.25)
                q3 = X[col].quantile(0.75)
                iqr = q3 - q1
                lower = q1 - self.factor * iqr
                upper = q3 + self.factor * iqr
                self.bounds_[col] = (lower, upper)
        
        logger.info(f"  [OK] OutlierCapper fitted bounds on {len(self.bounds_)} numeric columns.")
        return self

    def transform(self, X):
        X_capped = X.copy()
        if not isinstance(X_capped, pd.DataFrame):
            X_capped = pd.DataFrame(X_capped)
            
        capped_count = 0
        for col, (lower, upper) in self.bounds_.items():
            if col in X_capped.columns:
                outliers = ((X_capped[col] < lower) | (X_capped[col] > upper)).sum()
                capped_count += outliers
                X_capped[col] = X_capped[col].clip(lower=lower, upper=upper)
                
        logger.info(f"  [OK] OutlierCapper transformed dataset, capping {capped_count} values globally.")
        return X_capped


from sklearn.feature_selection import VarianceThreshold
from sklearn.preprocessing import StandardScaler, OneHotEncoder
import numpy as np

def cast_to_float(X):
    return X.astype(float)

def build_preprocessor(feature_metadata: dict) -> Pipeline:
    """
    Build a dynamic Scikit-Learn preprocessing pipeline based on detected feature types.
    
    Args:
        feature_metadata: Dictionary containing 'numeric', 'categorical', 'boolean' lists.
        
    Returns:
        A complete preprocessing Pipeline.
    """
    transformers = []
    
    if feature_metadata.get("numeric"):
        numeric_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='median')),
            ('outliers', OutlierCapper(factor=1.5)),
            ('scaler', StandardScaler())  # Standard scaling for all numeric features
        ])
        transformers.append(('num', numeric_transformer, feature_metadata["numeric"]))
        
    if feature_metadata.get("categorical"):
        categorical_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='most_frequent')),
            ('encoder', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
        ])
        transformers.append(('cat', categorical_transformer, feature_metadata["categorical"]))
        
    if feature_metadata.get("boolean"):
        from sklearn.preprocessing import FunctionTransformer
        import numpy as np
        
        # SimpleImputer does not accept bool directly, so we cast to int (0/1) or float first
        boolean_transformer = Pipeline(steps=[
            ('cast', FunctionTransformer(func=cast_to_float, validate=False)),
            ('imputer', SimpleImputer(strategy='most_frequent'))
        ])
        transformers.append(('bool', boolean_transformer, feature_metadata["boolean"]))

    # Combine transformers
    preprocessor = ColumnTransformer(
        transformers=transformers,
        remainder='drop'  # Automatically drop any column not explicitly detected to prevent errors
    )
    
    # Bundle into a final preprocessing pipeline with Feature Selection
    # VarianceThreshold automatically removes features with zero variance (e.g. constant values)
    full_preprocessing_pipeline = Pipeline(steps=[
        ('col_transformer', preprocessor),
        ('feature_selector', VarianceThreshold(threshold=0.0))
    ])
    
    logger.info("  [OK] Built Dynamic Scikit-Learn Preprocessing Pipeline with Feature Selection.")
    return full_preprocessing_pipeline
