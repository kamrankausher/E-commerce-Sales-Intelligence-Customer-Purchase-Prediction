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
import numpy as np
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split, RandomizedSearchCV, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, classification_report, confusion_matrix
)
import config

FEATURE_COLS = config.FEATURE_COLS
TARGET_COL = config.TARGET_COL
MODEL_DIR = config.MODELS_DIR


def split_data(df: pd.DataFrame, test_size: float = 0.2, random_state: int = 42):
    """
    Split data into train and test sets with stratification.

    Why stratified: Churn is typically imbalanced (e.g., 70% churned, 30% active).
    Stratification ensures both train and test sets maintain the same class ratio,
    giving reliable evaluation metrics.
    """
    X = df[FEATURE_COLS]
    y = df[TARGET_COL]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )

    logger.info(f"  Train: {X_train.shape[0]:,} samples | Test: {X_test.shape[0]:,} samples")
    logger.info(f"  Train churn rate: {y_train.mean()*100:.1f}% | Test churn rate: {y_test.mean()*100:.1f}%")
    return X_train, X_test, y_train, y_test


def get_models() -> dict:
    """
    Return a dictionary of model instances to compare.

    Why these models:
    - LogisticRegression: Linear baseline — always start simple
    - DecisionTree: Non-linear, easy to visualize, shows overfitting risk
    - RandomForest: Ensemble of trees — reduces variance, strong baseline
    - XGBoost: Gradient boosting — state-of-the-art for tabular data
    - LightGBM: Faster boosting with comparable accuracy
    """
    return {
        "Logistic Regression": LogisticRegression(
            max_iter=1000, random_state=42, class_weight="balanced"
        ),
        "Decision Tree": DecisionTreeClassifier(
            max_depth=5, random_state=42, class_weight="balanced"
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=100, max_depth=10, random_state=42,
            class_weight="balanced", n_jobs=-1
        ),
        "XGBoost": XGBClassifier(
            n_estimators=100, max_depth=6, learning_rate=0.1,
            random_state=42, eval_metric="logloss",
            scale_pos_weight=1, use_label_encoder=False
        ),
        "LightGBM": LGBMClassifier(
            n_estimators=100, max_depth=8, learning_rate=0.1,
            random_state=42, class_weight="balanced", verbose=-1
        ),
    }


def evaluate_model(model, X_test, y_test) -> dict:
    """
    Evaluate a trained model on the test set.

    Metrics:
    - Accuracy:  Overall correctness (can be misleading with imbalance)
    - Precision: Of predicted churners, how many actually churned?
    - Recall:    Of actual churners, how many did we catch?
    - F1-Score:  Harmonic mean of Precision and Recall
    - ROC-AUC:   Model's ability to rank churners higher than non-churners
    """
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1] if hasattr(model, "predict_proba") else y_pred

    return {
        "accuracy":  round(accuracy_score(y_test, y_pred), 4),
        "precision": round(precision_score(y_test, y_pred, zero_division=0), 4),
        "recall":    round(recall_score(y_test, y_pred, zero_division=0), 4),
        "f1_score":  round(f1_score(y_test, y_pred, zero_division=0), 4),
        "roc_auc":   round(roc_auc_score(y_test, y_proba), 4),
    }


def train_and_compare(X_train, X_test, y_train, y_test) -> pd.DataFrame:
    """
    Train all models, evaluate on test set, return comparison table.

    Returns:
        pd.DataFrame — one row per model with all metrics, sorted by ROC-AUC
    """
    models = get_models()
    results = []

    # Scale features for Logistic Regression
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    for name, model in models.items():
        logger.info(f"  Training {name}...")

        # Use scaled data for Logistic Regression, raw for tree-based models
        if name == "Logistic Regression":
            model.fit(X_train_scaled, y_train)
            metrics = evaluate_model(model, X_test_scaled, y_test)
        else:
            model.fit(X_train, y_train)
            metrics = evaluate_model(model, X_test, y_test)

        metrics["model"] = name
        results.append(metrics)
        logger.info(f"    ROC-AUC: {metrics['roc_auc']:.4f} | F1: {metrics['f1_score']:.4f}")

    comparison = pd.DataFrame(results)
    comparison = comparison[["model", "accuracy", "precision", "recall", "f1_score", "roc_auc"]]
    comparison = comparison.sort_values("roc_auc", ascending=False).reset_index(drop=True)

    print("\n" + "=" * 70)
    logger.info("  MODEL COMPARISON (sorted by ROC-AUC)")
    print("=" * 70)
    print(comparison.to_string(index=False))

    return comparison


def tune_best_model(X_train, y_train, model_name: str = "XGBoost", n_iter: int = 30):
    """
    Hyperparameter tuning with RandomizedSearchCV.

    Why RandomizedSearchCV over GridSearchCV:
    - GridSearch tests every combination — exponentially expensive
    - RandomSearch samples randomly — finds good params faster
    - Research shows Random is often as effective as Grid with fewer iterations

    Why not Optuna:
    - Optuna is more sophisticated (Bayesian optimization)
    - But harder to explain in a fresher interview
    - RandomizedSearchCV is well-known, in scikit-learn, easy to discuss
    """
    param_distributions = {
        "XGBoost": {
            "n_estimators": [50, 100, 200, 300],
            "max_depth": [3, 4, 5, 6, 8, 10],
            "learning_rate": [0.01, 0.05, 0.1, 0.2],
            "subsample": [0.6, 0.7, 0.8, 0.9, 1.0],
            "colsample_bytree": [0.6, 0.7, 0.8, 0.9, 1.0],
            "min_child_weight": [1, 3, 5, 7],
            "gamma": [0, 0.1, 0.2, 0.3],
        },
        "LightGBM": {
            "n_estimators": [50, 100, 200, 300],
            "max_depth": [3, 5, 8, 10, -1],
            "learning_rate": [0.01, 0.05, 0.1, 0.2],
            "num_leaves": [15, 31, 63, 127],
            "subsample": [0.6, 0.7, 0.8, 0.9, 1.0],
            "colsample_bytree": [0.6, 0.7, 0.8, 0.9, 1.0],
        },
        "Random Forest": {
            "n_estimators": [50, 100, 200, 300],
            "max_depth": [5, 8, 10, 15, None],
            "min_samples_split": [2, 5, 10],
            "min_samples_leaf": [1, 2, 4],
            "max_features": ["sqrt", "log2"],
        },
    }

    if model_name not in param_distributions:
        logger.info(f"  ⚠ No tuning config for '{model_name}'. Using default params.")
        return get_models()[model_name]

    base_models = get_models()
    model = base_models[model_name]

    logger.info(f"  Tuning {model_name} with RandomizedSearchCV ({n_iter} iterations)...")

    search = RandomizedSearchCV(
        model,
        param_distributions[model_name],
        n_iter=n_iter,
        cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=42),
        scoring="roc_auc",
        random_state=42,
        n_jobs=-1,
        verbose=0,
    )
    search.fit(X_train, y_train)

    logger.info(f"  [OK] Best ROC-AUC (CV): {search.best_score_:.4f}")
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
