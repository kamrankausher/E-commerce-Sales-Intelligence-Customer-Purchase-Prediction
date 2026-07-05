import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import shap
from sklearn.inspection import permutation_importance
from src.utils.logger import get_logger
import config

logger = get_logger(__name__)

def get_feature_importance(model, feature_names: list) -> pd.DataFrame:
    """Extract feature importance from a trained model if available."""
    # model is a Pipeline. Step 1 is classifier/regressor.
    if hasattr(model, 'steps'):
        estimator = model.steps[-1][1]
    else:
        estimator = model

    if hasattr(estimator, "feature_importances_"):
        importances = estimator.feature_importances_
    elif hasattr(estimator, "coef_"):
        importances = np.abs(estimator.coef_[0]) if len(estimator.coef_.shape) > 1 else np.abs(estimator.coef_)
    else:
        return pd.DataFrame()

    # Match lengths
    if len(importances) != len(feature_names):
        logger.warning(f"Feature importance length ({len(importances)}) does not match feature names ({len(feature_names)})")
        return pd.DataFrame()

    fi = pd.DataFrame({
        "feature": feature_names,
        "importance": importances
    }).sort_values("importance", ascending=False).reset_index(drop=True)

    if fi["importance"].sum() > 0:
        fi["importance_pct"] = (fi["importance"] / fi["importance"].sum() * 100).round(1)
    else:
        fi["importance_pct"] = 0

    return fi

def get_permutation_importance(model, X_test, y_test, feature_names, task_type="Classification") -> pd.DataFrame:
    """Calculate permutation importance on the test set."""
    scoring = 'roc_auc' if task_type == 'Classification' else 'neg_mean_squared_error'
    
    # Calculate permutation importance
    r = permutation_importance(model, X_test, y_test, n_repeats=5, random_state=42, scoring=scoring)
    
    pi = pd.DataFrame({
        "feature": feature_names,
        "importance": r.importances_mean,
        "std": r.importances_std
    }).sort_values("importance", ascending=False).reset_index(drop=True)
    
    return pi

def generate_shap_explanations(model, X_test, output_dir=config.REPORTS_DIR):
    """
    Generate SHAP summary and bar plots.
    Saves the plots to reports/images/
    """
    logger.info("  Generating SHAP Explanations...")
    images_dir = os.path.join(output_dir, "images")
    os.makedirs(images_dir, exist_ok=True)
    
    # Get the estimator and the preprocessor from the pipeline
    try:
        preprocessor = model.steps[0][1]
        estimator = model.steps[-1][1]
        
        # Transform the test data for SHAP
        X_test_transformed = preprocessor.transform(X_test)
        
        # Retrieve feature names out of the preprocessor if possible
        # This requires Scikit-Learn 1.2+ for get_feature_names_out on ColumnTransformer
        try:
            feature_names = preprocessor.get_feature_names_out()
            # Clean up the names from pipeline prefixes (e.g. "num__", "cat__")
            feature_names = [name.split("__")[-1] for name in feature_names]
        except Exception:
            feature_names = X_test.columns.tolist()
        
        # Create an Explainer
        # TreeExplainer is faster for Tree models
        if type(estimator).__name__ in ["RandomForestClassifier", "RandomForestRegressor", 
                                        "XGBClassifier", "XGBRegressor", 
                                        "LGBMClassifier", "LGBMRegressor", 
                                        "DecisionTreeClassifier", "DecisionTreeRegressor"]:
            explainer = shap.TreeExplainer(estimator)
        else:
            explainer = shap.LinearExplainer(estimator, X_test_transformed)
            
        shap_values = explainer.shap_values(X_test_transformed)
        
        # In classification, shap_values might be a list (one for each class)
        if isinstance(shap_values, list):
            shap_values = shap_values[1] # Use positive class
            
        # Summary Plot
        plt.figure(figsize=(10, 6))
        shap.summary_plot(shap_values, X_test_transformed, feature_names=feature_names, show=False)
        plt.tight_layout()
        summary_path = os.path.join(images_dir, "shap_summary.png")
        plt.savefig(summary_path)
        plt.close()
        
        # Bar Plot (Global Importance)
        plt.figure(figsize=(10, 6))
        shap.summary_plot(shap_values, X_test_transformed, feature_names=feature_names, plot_type="bar", show=False)
        plt.tight_layout()
        bar_path = os.path.join(images_dir, "shap_bar.png")
        plt.savefig(bar_path)
        plt.close()
        
        logger.info(f"  [OK] SHAP plots saved to {images_dir}")
        return summary_path, bar_path
        
    except Exception as e:
        logger.warning(f"  [SKIPPED] SHAP explanations could not be generated: {str(e)}")
        return None, None

def generate_plain_english_explanation(prediction, feature_importances: pd.DataFrame, X_instance: pd.Series) -> str:
    """
    Generate a simple, plain-English explanation of why the prediction was made.
    """
    if feature_importances.empty:
        return f"The model predicted {prediction} based on the overall data patterns."
        
    top_features = feature_importances.head(3)["feature"].tolist()
    
    explanation = f"The model predicted {'Churn' if prediction == 1 else 'Active'} primarily because of these factors:\n"
    for feature in top_features:
        val = X_instance.get(feature, "Unknown")
        explanation += f"- The customer's {feature} is {val}.\n"
        
    explanation += "\nThese features historically have the highest impact on customer behavior in our dataset."
    return explanation

def error_analysis(model, X_test, y_test, task_type="Classification"):
    """
    Perform simple error analysis.
    Classification: Identify False Positives and False Negatives.
    Regression: Identify top residuals.
    """
    y_pred = model.predict(X_test)
    
    df = X_test.copy()
    df["Actual"] = y_test
    df["Predicted"] = y_pred
    
    if task_type == "Classification":
        df["Error_Type"] = "Correct"
        df.loc[(df["Actual"] == 1) & (df["Predicted"] == 0), "Error_Type"] = "False Negative (Missed Churn)"
        df.loc[(df["Actual"] == 0) & (df["Predicted"] == 1), "Error_Type"] = "False Positive (False Alarm)"
        
        counts = df["Error_Type"].value_counts().to_dict()
        return counts, df[df["Error_Type"] != "Correct"].head(5)
    else:
        df["Residual"] = np.abs(df["Actual"] - df["Predicted"])
        top_errors = df.sort_values("Residual", ascending=False).head(5)
        return {"mean_absolute_error": df["Residual"].mean()}, top_errors
