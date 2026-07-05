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
from src.models.trainer import split_data, get_models, save_model, train_and_compare, tune_best_model
from src.models.task_detector import detect_task_type
from src.evaluation.metrics import save_metrics, extract_dataset_metrics, generate_leaderboard
from src.evaluation.explainability import (
    get_feature_importance, get_permutation_importance,
    generate_shap_explanations, generate_plain_english_explanation, error_analysis
)

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
    
    # 11. Automatic Task Detection
    task_type = detect_task_type(y)
    
    # 12. Model Comparison
    comparison_df = train_and_compare(X_train, X_test, y_train, y_test, task_type=task_type)
    
    # Save the results of the model comparison
    results_list = comparison_df.to_dict(orient="records")
    leaderboard = generate_leaderboard(results_list, task_type=task_type)
    best_model_name = leaderboard["best_model"]
    
    logger.info(f"Leaderboard best model: {best_model_name}")
    
    # 13. Hyperparameter Tuning on Best Model
    logger.info(f"Tuning {best_model_name} with RandomizedSearchCV...")
    best_model = tune_best_model(X_train, y_train, preprocessor=preprocessor, model_name=best_model_name, n_iter=10, task_type=task_type)
    
    # 14. Explainability & Feature Importance
    try:
        feature_names_out = preprocessor.get_feature_names_out()
        feature_names_clean = [f.split("__")[-1] for f in feature_names_out]
    except Exception:
        feature_names_clean = X_train.columns.tolist()

    logger.info("Extracting Feature Importance...")
    fi = get_feature_importance(best_model, feature_names_clean)
    
    logger.info("Calculating Permutation Importance...")
    pi = get_permutation_importance(best_model, X_test, y_test, feature_names_clean, task_type=task_type)
    
    logger.info("Generating SHAP Explanations...")
    shap_summary, shap_bar = generate_shap_explanations(best_model, X_test, output_dir=config.REPORTS_DIR)
    
    logger.info("Performing Error Analysis...")
    error_summary, top_errors = error_analysis(best_model, X_test, y_test, task_type=task_type)
    
    # 15. Plain-English Prediction Example
    sample_instance = X_test.iloc[0]
    sample_prediction = best_model.predict(X_test.iloc[[0]])[0]
    plain_english = generate_plain_english_explanation(sample_prediction, fi, sample_instance)
    logger.info(f"Sample Explanation: {plain_english}")

    # 16. Save Best Complete Pipeline
    save_model(best_model, filename="best_model.pkl")
    logger.info(f"Saved best complete pipeline to {config.BEST_MODEL_FILE}")
    
    # 17. Generate Phase 6 Modeling Report
    logger.info("Generating Phase 6 Modeling Report...")
    report_path = os.path.join(config.REPORTS_DIR, "Phase6_Modeling_Report.md")
    with open(report_path, "w") as f:
        f.write("# Phase 6: Model Training & Evaluation Report\n\n")
        f.write(f"## 1. Detected ML Task Type\n- **Task Type**: {task_type}\n\n")
        f.write("## 2. Model Leaderboard\n")
        f.write(comparison_df.to_markdown(index=False))
        f.write(f"\n\n- **Best Model**: {leaderboard['best_model']}\n")
        f.write(f"- **Fastest Inference**: {leaderboard['fastest_model']}\n")
        f.write(f"- **Most Interpretable**: {leaderboard['most_interpretable']}\n\n")
        f.write("## 3. Feature Importance\n")
        if not fi.empty:
            f.write(fi.head(10).to_markdown(index=False))
        f.write("\n\n## 4. Permutation Importance\n")
        f.write(pi.head(10).to_markdown(index=False))
        f.write("\n\n## 5. Error Analysis\n")
        f.write(f"Summary: {error_summary}\n\n")
        f.write("## 6. Plain-English Explanation Example\n")
        f.write(f"```text\n{plain_english}\n```\n")
        if shap_summary:
            f.write("\n## 7. SHAP Explanations\n")
            f.write("![SHAP Summary](images/shap_summary.png)\n")
    
    logger.info("=== Pipeline Complete ===")

if __name__ == "__main__":
    main()
