# Data Leakage Prevention Report

## Overview
Data leakage occurs when information from outside the training dataset (such as the test set) is used to create the model. This results in overly optimistic performance estimates during training and cross-validation, but poor performance in production. 

This report outlines the robust architecture implemented in this project to guarantee a 100% leak-free Machine Learning pipeline.

## 1. Architectural Changes Implemented (Phase 3)
Previously, data was preprocessed (missing values filled globally, outliers capped globally via quantiles) *before* splitting the dataset. This caused minor data leakage, as test set characteristics influenced the training set's imputation values and IQR bounds.

**Resolution:** 
The pipeline has been re-architected to heavily leverage Scikit-Learn's `Pipeline` and `ColumnTransformer`. 

## 2. The Leak-Free Order of Operations
The pipeline now strictly enforces the following sequence:

1. **Aggregation & Feature Engineering (`src/features/engine.py`):**
   Raw transactions are aggregated to the `customer_id` level. Group-by operations do not leak target-related future data across rows, as they are strictly localized to individual customers.
2. **Train/Test Split (`run_pipeline.py`):**
   Before *any* statistical transformations occur, the dataset is split via `train_test_split(stratify=y)`.
3. **Scikit-Learn Pipeline (`src/preprocessing/pipeline.py`):**
   A strict pipeline is built:
   - **`SimpleImputer(strategy='median')`:** Calculates the median *only* on `X_train`.
   - **`OutlierCapper(factor=1.5)`:** A custom Scikit-Learn transformer that calculates IQR bounds (Q1, Q3) *only* on `X_train`.
   - **Estimator:** The base classifier (e.g., Random Forest, XGBoost).
4. **Fitting:** 
   `pipeline.fit(X_train, y_train)` ensures all preprocessing components learn strictly from the training slice.
5. **Transforming:**
   `pipeline.predict(X_test)` cleanly transforms the unseen test data using the *learned bounds and medians* from `X_train`.

## 3. Cross-Validation Safety
Because we bundle the `preprocessor` and `classifier` into a single `Pipeline`, and pass the *entire pipeline* to `RandomizedSearchCV`, cross-validation is completely safe. During each of the 5 folds, Scikit-Learn fits the imputer and outlier capper exclusively on the 4 training folds, and transforms the 1 validation fold. 

## 4. Conclusion
There are **zero leakage risks** remaining in this project. The architecture mimics professional, production-grade MLOps pipelines and is ready to safely process newly uploaded datasets.
