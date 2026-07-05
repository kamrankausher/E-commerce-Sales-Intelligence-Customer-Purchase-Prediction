import pandas as pd
import numpy as np
from sklearn.datasets import make_classification, make_regression
from src.preprocessing.detector import detect_features
from src.preprocessing.pipeline import build_preprocessor
from src.models.trainer import train_and_compare

print("--- Testing Binary Classification (Edge cases) ---")
X, y = make_classification(n_samples=100, n_features=5, n_classes=2, random_state=42)
df_bin = pd.DataFrame(X, columns=[f"feat_{i}" for i in range(5)])
df_bin["target"] = y
df_bin["date_col"] = pd.date_range("2020-01-01", periods=100) # Datetime
df_bin["id_col"] = range(100) # High cardinality

print("1. Detection")
feat_dict = detect_features(df_bin.drop(columns=["target"]), target_col="")
print("   ", feat_dict)

print("2. Preprocessing")
try:
    prep = build_preprocessor(feat_dict)
    X_trans = prep.fit_transform(df_bin.drop(columns=["target"]))
    print("    Preprocessed shape:", X_trans.shape)
except Exception as e:
    print("    PREPROCESSING FAILED:", e)

print("3. Training")
try:
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(df_bin.drop(columns=["target", "date_col", "id_col"]), df_bin["target"], test_size=0.2, stratify=df_bin["target"])
    train_and_compare(X_train, X_test, y_train, y_test, task_type="Classification")
    print("    Training OK")
except Exception as e:
    print("    TRAINING FAILED:", e)

print("\n--- Testing Multi-Class Classification ---")
X, y = make_classification(n_samples=100, n_features=5, n_classes=3, n_informative=3, random_state=42)
df_multi = pd.DataFrame(X, columns=[f"feat_{i}" for i in range(5)])
df_multi["target"] = y

try:
    X_train, X_test, y_train, y_test = train_test_split(df_multi.drop(columns=["target"]), df_multi["target"], test_size=0.2, stratify=df_multi["target"])
    train_and_compare(X_train, X_test, y_train, y_test, task_type="Classification")
    print("    Training OK")
except Exception as e:
    print("    TRAINING FAILED:", e)

print("\n--- Testing Regression ---")
X, y = make_regression(n_samples=100, n_features=5, random_state=42)
df_reg = pd.DataFrame(X, columns=[f"feat_{i}" for i in range(5)])
df_reg["target"] = y

try:
    X_train, X_test, y_train, y_test = train_test_split(df_reg.drop(columns=["target"]), df_reg["target"], test_size=0.2)
    train_and_compare(X_train, X_test, y_train, y_test, task_type="Regression")
    print("    Training OK")
except Exception as e:
    print("    TRAINING FAILED:", e)
