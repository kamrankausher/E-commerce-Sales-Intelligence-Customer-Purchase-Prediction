import os
import time
import logging
import warnings
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from sklearn.pipeline import Pipeline
import joblib

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
from src.utils.logger import get_logger
logger = get_logger(__name__)
warnings.filterwarnings('ignore')

import config
from src.data.loader import load_all
from src.validation.schema import validate_raw_data
from src.validation.profiler import generate_data_profile
from src.preprocessing.clean_orchestrator import build_master_dataset
from src.preprocessing.detector import detect_features
from src.preprocessing.pipeline import build_preprocessor
from src.features.engine import prepare_ml_dataset
from src.models.trainer import split_data, get_models, save_model
from src.evaluation.metrics import save_metrics, extract_dataset_metrics

def main():
    logger.info("=== Starting Data Science Pipeline (Phase 5 Architecture) ===")
    
    # 1. Load Data
    t0 = time.time()
    dfs = load_all()
    logger.info(f"Loaded {len(dfs)} raw tables in {time.time()-t0:.2f}s")
    
    # 2. Data Validation
    validate_raw_data(dfs)
    
    # 3. Data Cleaning (Aggregation & Joins)
    t0 = time.time()
    master_clean = build_master_dataset(dfs)
    logger.info(f"Cleaned and merged data into {master_clean.shape} in {time.time()-t0:.2f}s")
    master_clean.to_csv(config.MASTER_CLEANED_FILE, index=False)
    
    # 4. Feature Engineering
    t0 = time.time()
    ml_data = prepare_ml_dataset(master_clean, churn_threshold_days=config.CHURN_THRESHOLD_DAYS)
    logger.info(f"Engineered features for {len(ml_data)} customers in {time.time()-t0:.2f}s")
    ml_data.to_csv(config.ML_DATASET_FILE, index=False)
    
    # 5. Automated Feature Detection (PHASE 5)
    feature_metadata = detect_features(ml_data, target_col=config.TARGET_COL, drop_cols=[config.ID_COL])
    
    # 6. Data Profiling
    generate_data_profile(ml_data, report_name="ml_dataset_profile.md")
    
    # 7. Extract Dataset Metrics (for Streamlit dashboard)
    dataset_metrics = extract_dataset_metrics(dfs['customers'], master_clean, ml_data)
    
    # 8. Train/Test Split (CRITICAL LEAKAGE PREVENTION - Must happen BEFORE preprocessing)
    logger.info("Splitting data into train/test sets...")
    X = ml_data.drop(columns=[config.TARGET_COL, config.ID_COL], errors='ignore')
    y = ml_data[config.TARGET_COL]
    
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=config.TEST_SIZE, random_state=config.RANDOM_SEED, stratify=y)
    
    # 9. Build Preprocessing Pipeline dynamically
    preprocessor = build_preprocessor(feature_metadata)
    
    # 10. Fit and Serialize Preprocessing Pipeline
    logger.info("Fitting Preprocessing Pipeline on training data...")
    preprocessor.fit(X_train, y_train)
    
    # Save the standalone preprocessing pipeline for production use
    os.makedirs(os.path.dirname(config.BEST_MODEL_FILE), exist_ok=True)
    preprocessing_path = os.path.join(os.path.dirname(config.BEST_MODEL_FILE), "preprocessing_pipeline.pkl")
    joblib.dump(preprocessor, preprocessing_path)
    logger.info(f"Saved preprocessing pipeline to {preprocessing_path}")
    
    # 11. Model Training & Evaluation
    models = get_models()
    
    best_auc = 0
    best_model_name = ""
    best_model = None
    
    if os.path.exists(config.MODEL_RESULTS_FILE):
        os.remove(config.MODEL_RESULTS_FILE)
    
    for name, clf in models.items():
        logger.info(f"Training {name}...")
        
        # Bundle preprocessing and modeling
        model_pipeline = Pipeline(steps=[
            ('preprocessor', preprocessor),
            ('classifier', clf)
        ])
        
        t_start = time.time()
        model_pipeline.fit(X_train, y_train)
        train_time = time.time() - t_start
        
        t_inf = time.time()
        y_pred = model_pipeline.predict(X_test)
        y_prob = model_pipeline.predict_proba(X_test)[:, 1]
        inference_time = time.time() - t_inf
        
        auc = roc_auc_score(y_test, y_prob)
        
        if auc > best_auc:
            best_auc = auc
            best_model_name = name
            best_model = model_pipeline
            
        metrics = {
            "model": name,
            "accuracy": accuracy_score(y_test, y_pred),
            "precision": precision_score(y_test, y_pred, zero_division=0),
            "recall": recall_score(y_test, y_pred, zero_division=0),
            "f1_score": f1_score(y_test, y_pred, zero_division=0),
            "roc_auc": auc,
            "training_time_sec": train_time,
            "inference_time_sec": inference_time,
            **dataset_metrics
        }
        
        save_metrics(metrics)
        
    logger.info(f"Best base model found: {best_model_name} with AUC = {best_auc:.4f}")
    
    # 12. Hyperparameter Tuning
    if best_model_name in ["XGBoost", "LightGBM", "Random Forest"]:
        logger.info(f"Tuning {best_model_name} with RandomizedSearchCV...")
        from src.models.trainer import tune_best_model
        best_model = tune_best_model(X_train, y_train, preprocessor=preprocessor, model_name=best_model_name, n_iter=10)
    
    # 13. Save Best Complete Pipeline
    save_model(best_model, filename="best_model.pkl")
    logger.info(f"Saved best complete pipeline to {config.BEST_MODEL_FILE}")
    
    logger.info("=== Pipeline Complete ===")

if __name__ == "__main__":
    main()
