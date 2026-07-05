import pytest
import pandas as pd
import numpy as np
from src.models.task_detector import detect_task_type
from src.evaluation.metrics import generate_leaderboard

def test_task_detection_classification():
    y = pd.Series([0, 1, 0, 1, 1], name="churned")
    assert detect_task_type(y) == "Classification"
    
    y = pd.Series(["A", "B", "A", "C"], name="category")
    assert detect_task_type(y) == "Classification"
    
def test_task_detection_regression():
    y = pd.Series(np.random.rand(100), name="price")
    assert detect_task_type(y) == "Regression"

def test_generate_leaderboard_classification():
    results = [
        {"model": "Logistic Regression", "roc_auc": 0.8, "inference_time_sec": 0.1},
        {"model": "XGBoost", "roc_auc": 0.9, "inference_time_sec": 0.5},
        {"model": "LightGBM", "roc_auc": 0.85, "inference_time_sec": 0.3},
    ]
    
    leaderboard = generate_leaderboard(results, task_type="Classification")
    assert leaderboard["best_model"] == "XGBoost"
    assert leaderboard["fastest_model"] == "Logistic Regression"
    assert leaderboard["most_interpretable"] == "Logistic Regression"
