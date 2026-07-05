from src.utils.logger import get_logger
logger = get_logger(__name__)

"""
model_trainer.py — Train, compare, and evaluate ML models for churn prediction.

WHY THIS EXISTS:
    This module encapsulates the entire model training workflow: splitting data,
    training multiple models, evaluating them with consistent metrics, selecting
    the best one, and performing hyperparameter tuning. Extracted from notebooks
    so the Streamlit app can reuse the trained model.

INTERVIEW EXPLANATION:
    "I compared 5 models — from simple (Logistic Regression) to advanced
    (XGBoost, LightGBM). I used stratified train-test split because the
    churn classes were imbalanced. Each model was evaluated on Accuracy,
    Precision, Recall, F1, and ROC-AUC. XGBoost gave the best ROC-AUC,
    so I tuned its hyperparameters with RandomizedSearchCV."

MODELS COMPARED:
    1. Logistic Regression — interpretable baseline
    2. Decision Tree       — non-linear, visual, prone to overfitting
    3. Random Forest       — ensemble of trees, reduces variance
    4. XGBoost             — gradient boosting, handles imbalance well
    5. LightGBM            — faster gradient boosting, memory efficient
"""

import os
import time
import numpy as np
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split, RandomizedSearchCV, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier, XGBRegressor
from lightgbm import LGBMClassifier, LGBMRegressor
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, mean_squared_error, mean_absolute_error, r2_score
)
import config

TARGET_COL = config.TARGET_COL
MODEL_DIR = config.MODELS_DIR


def split_data(df: pd.DataFrame, test_size: float = 0.2, random_state: int = 42):
    """
    Split the dataset into training and testing sets.
    """
    logger.info("  Splitting data into train and test sets...")
    
    X = df.drop(columns=[config.TARGET_COL, config.ID_COL], errors='ignore')
    y = df[config.TARGET_COL]
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )

    logger.info(f"  Train: {X_train.shape[0]:,} samples | Test: {X_test.shape[0]:,} samples")
    logger.info(f"  Train churn rate: {y_train.mean()*100:.1f}% | Test churn rate: {y_test.mean()*100:.1f}%")
    return X_train, X_test, y_train, y_test


def get_models(task_type: str = "Classification") -> dict:
    """
    Return a dictionary of model instances based on task_type.
    """
    if task_type == "Classification":
        return {
            "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42, class_weight="balanced"),
            "Decision Tree": DecisionTreeClassifier(max_depth=5, random_state=42, class_weight="balanced"),
            "Random Forest": RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, class_weight="balanced", n_jobs=-1),
            "XGBoost": XGBClassifier(n_estimators=100, max_depth=6, learning_rate=0.1, random_state=42, eval_metric="logloss", scale_pos_weight=1),
            "LightGBM": LGBMClassifier(n_estimators=100, max_depth=8, learning_rate=0.1, random_state=42, class_weight="balanced", verbose=-1),
        }
    else:
        return {
            "Linear Regression": LinearRegression(),
            "Decision Tree": DecisionTreeRegressor(max_depth=5, random_state=42),
            "Random Forest": RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1),
            "XGBoost": XGBRegressor(n_estimators=100, max_depth=6, learning_rate=0.1, random_state=42),
            "LightGBM": LGBMRegressor(n_estimators=100, max_depth=8, learning_rate=0.1, random_state=42, verbose=-1),
        }


def evaluate_model(model, X_test, y_test, task_type: str = "Classification") -> dict:
    """Evaluate a trained model on the test set."""
    y_pred = model.predict(X_test)
    
    if task_type == "Classification":
        y_proba = model.predict_proba(X_test)[:, 1] if hasattr(model, "predict_proba") else y_pred
        return {
            "accuracy":  round(accuracy_score(y_test, y_pred), 4),
            "precision": round(precision_score(y_test, y_pred, zero_division=0, average='weighted'), 4),
            "recall":    round(recall_score(y_test, y_pred, zero_division=0, average='weighted'), 4),
            "f1_score":  round(f1_score(y_test, y_pred, zero_division=0, average='weighted'), 4),
            "roc_auc":   round(roc_auc_score(y_test, y_proba), 4) if len(np.unique(y_test)) == 2 else np.nan,
        }
    else:
        return {
            "rmse": round(np.sqrt(mean_squared_error(y_test, y_pred)), 4),
            "mae":  round(mean_absolute_error(y_test, y_pred), 4),
            "r2":   round(r2_score(y_test, y_pred), 4),
        }

def train_and_compare(X_train, X_test, y_train, y_test, task_type="Classification") -> pd.DataFrame:
    """Train all models, evaluate on test set, return comparison table."""
    models = get_models(task_type)
    results = []

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    for name, model in models.items():
        logger.info(f"  Training {name}...")
        
        t_start = time.time()
        if name in ["Logistic Regression", "Linear Regression"]:
            model.fit(X_train_scaled, y_train)
            train_time = time.time() - t_start
            
            t_inf = time.time()
            metrics = evaluate_model(model, X_test_scaled, y_test, task_type)
            inf_time = time.time() - t_inf
        else:
            model.fit(X_train, y_train)
            train_time = time.time() - t_start
            
            t_inf = time.time()
            metrics = evaluate_model(model, X_test, y_test, task_type)
            inf_time = time.time() - t_inf

        metrics["model"] = name
        metrics["training_time_sec"] = train_time
        metrics["inference_time_sec"] = inf_time
        results.append(metrics)
        if task_type == "Classification":
            logger.info(f"    ROC-AUC: {metrics.get('roc_auc')} | F1: {metrics.get('f1_score')}")
        else:
            logger.info(f"    RMSE: {metrics.get('rmse')} | R2: {metrics.get('r2')}")

    comparison = pd.DataFrame(results)
    
    if task_type == "Classification":
        comparison = comparison[["model", "accuracy", "precision", "recall", "f1_score", "roc_auc", "training_time_sec", "inference_time_sec"]]
        comparison = comparison.sort_values("roc_auc", ascending=False).reset_index(drop=True)
    else:
        comparison = comparison[["model", "rmse", "mae", "r2", "training_time_sec", "inference_time_sec"]]
        comparison = comparison.sort_values("rmse", ascending=True).reset_index(drop=True)

    print("\n" + "=" * 70)
    logger.info(f"  MODEL COMPARISON ({task_type})")
    print("=" * 70)
    print(comparison.to_string(index=False))

    return comparison


def tune_best_model(X_train, y_train, preprocessor, model_name: str = "XGBoost", n_iter: int = 30, task_type="Classification"):
    """Hyperparameter tuning with RandomizedSearchCV."""
    from sklearn.pipeline import Pipeline
    from sklearn.model_selection import KFold
    
    # Simple param grids
    param_distributions = {
        "XGBoost": {
            "classifier__n_estimators": [50, 100, 200],
            "classifier__max_depth": [3, 5, 8],
            "classifier__learning_rate": [0.01, 0.1, 0.2],
        },
        "LightGBM": {
            "classifier__n_estimators": [50, 100, 200],
            "classifier__max_depth": [3, 5, 8],
            "classifier__learning_rate": [0.01, 0.1, 0.2],
        },
        "Random Forest": {
            "classifier__n_estimators": [50, 100, 200],
            "classifier__max_depth": [5, 10, None],
        },
    }

    if model_name not in param_distributions:
        logger.info(f"  ⚠ No tuning config for '{model_name}'. Using default params.")
        return Pipeline([('preprocessor', preprocessor), ('classifier', get_models(task_type)[model_name])])

    base_models = get_models(task_type)
    model = base_models[model_name]
    
    pipeline = Pipeline([
        ('preprocessor', preprocessor),
        ('classifier', model)
    ])

    logger.info(f"  Tuning {model_name} with RandomizedSearchCV ({n_iter} iterations)...")
    
    if task_type == "Classification":
        cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
        scoring = "roc_auc"
    else:
        cv = KFold(n_splits=3, shuffle=True, random_state=42)
        scoring = "neg_mean_squared_error"

    search = RandomizedSearchCV(
        pipeline,
        param_distributions[model_name],
        n_iter=n_iter,
        cv=cv,
        scoring=scoring,
        random_state=42,
        n_jobs=-1,
        verbose=0,
    )
    search.fit(X_train, y_train)

    best_score = search.best_score_ if task_type == "Classification" else -search.best_score_
    logger.info(f"  [OK] Best Score (CV): {best_score:.4f}")
    logger.info(f"  [OK] Best params: {search.best_params_}")

    return search.best_estimator_


def get_feature_importance(model, feature_names: list) -> pd.DataFrame:
    """
    Extract feature importance from a trained model.

    Works with tree-based models (Decision Tree, Random Forest, XGBoost, LightGBM)
    and linear models (Logistic Regression — uses absolute coefficient values).
    """
    if hasattr(model, "feature_importances_"):
        importances = model.feature_importances_
    elif hasattr(model, "coef_"):
        importances = np.abs(model.coef_[0])
    else:
        return pd.DataFrame()

    fi = pd.DataFrame({
        "feature": feature_names,
        "importance": importances
    }).sort_values("importance", ascending=False).reset_index(drop=True)

    # Normalize to percentages
    fi["importance_pct"] = (fi["importance"] / fi["importance"].sum() * 100).round(1)

    return fi


def save_model(model, filename: str = "best_model.pkl"):
    """Save a trained model to the models/ directory using joblib."""
    os.makedirs(MODEL_DIR, exist_ok=True)
    filepath = os.path.join(MODEL_DIR, filename)
    joblib.dump(model, filepath)
    logger.info(f"  [OK] Model saved to {filepath}")
    return filepath


def load_model(filename: str = "best_model.pkl"):
    """Load a trained model from the models/ directory."""
    filepath = os.path.join(MODEL_DIR, filename)
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Model file not found: {filepath}")
    model = joblib.load(filepath)
    logger.info(f"  [OK] Model loaded from {filepath}")
    return model
