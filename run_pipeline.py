"""
run_pipeline.py — Orchestrate the entire Data Science pipeline.
"""
import os
import time
import logging
import warnings
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
import joblib

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
warnings.filterwarnings('ignore')

import config
from src.data.loader import load_all
from src.validation.schema import validate_raw_data
from src.preprocessing.clean_orchestrator import build_master_dataset
from src.features.engine import prepare_ml_dataset
from src.models.trainer import split_data, get_models, save_model
from src.evaluation.metrics import save_metrics, extract_dataset_metrics

def main():
    logger.info("=== Starting Data Science Pipeline ===")
    
    # 1. Load Data
    t0 = time.time()
    dfs = load_all()
    logger.info(f"Loaded {len(dfs)} raw tables in {time.time()-t0:.2f}s")
    
    # 2. Data Validation
    validate_raw_data(dfs)
    
    # 3. Data Cleaning
    t0 = time.time()
    master_clean = build_master_dataset(dfs)
    logger.info(f"Cleaned and merged data into {master_clean.shape} in {time.time()-t0:.2f}s")
    master_clean.to_csv(config.MASTER_CLEANED_FILE, index=False)
    
    # 4. Feature Engineering
    t0 = time.time()
    ml_data = prepare_ml_dataset(master_clean, churn_threshold_days=config.CHURN_THRESHOLD_DAYS)
    logger.info(f"Engineered {len(ml_data.columns)} features for {len(ml_data)} customers in {time.time()-t0:.2f}s")
    ml_data.to_csv(config.ML_DATASET_FILE, index=False)
    
    # 5. Extract Dataset Metrics
    dataset_metrics = extract_dataset_metrics(dfs['customers'], master_clean, ml_data)
    
    # 6. Model Training & Evaluation
    X_train, X_test, y_train, y_test = split_data(ml_data, test_size=config.TEST_SIZE, random_state=config.RANDOM_SEED)
    
    models = get_models()
    
    best_auc = 0
    best_model_name = ""
    best_model = None
    
    # Clear out old metrics
    if os.path.exists(config.MODEL_RESULTS_FILE):
        os.remove(config.MODEL_RESULTS_FILE)
    
    for name, model_pipeline in models.items():
        logger.info(f"Training {name}...")
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
    
    # 7. Hyperparameter Tuning
    if best_model_name in ["XGBoost", "LightGBM", "Random Forest"]:
        logger.info(f"Tuning {best_model_name} with RandomizedSearchCV...")
        from src.models.trainer import tune_best_model
        best_model = tune_best_model(X_train, y_train, model_name=best_model_name, n_iter=10)
    
    # 8. Save Best Model
    save_model(best_model, filename="best_model.pkl")
    logger.info(f"Saved best model to {config.BEST_MODEL_FILE}")
    
    logger.info("=== Pipeline Complete ===")

if __name__ == "__main__":
    main()
