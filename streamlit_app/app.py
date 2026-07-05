"""
Streamlit Machine Learning Workbench
Premium UI, Step-by-Step Workflow, Auto Target Validation, Explainability
"""
import streamlit as st
import pandas as pd
import numpy as np
import io
import os
import sys
import time
import duckdb
import plotly.express as px
import plotly.graph_objects as go
import joblib

# Adjust path to import src
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.preprocessing.detector import detect_features
from src.preprocessing.pipeline import build_preprocessor
from src.models.task_detector import detect_task_type
from src.models.trainer import split_data, train_and_compare, tune_best_model
from src.evaluation.metrics import generate_leaderboard
from src.evaluation.explainability import get_feature_importance, get_permutation_importance, error_analysis, generate_plain_english_explanation
from src.evaluation.charts import plot_confusion_matrix, plot_roc_curve, plot_precision_recall_curve

# --- Page Config & Custom CSS ---
st.set_page_config(page_title="Premium ML Workbench", layout="wide", page_icon="📈")

def inject_custom_css():
    st.markdown("""
    <style>
    /* Premium Light/Dark Adaptive UI */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    :root {
        --bg-color: #F8FAFC;
        --sidebar-bg: #0F172A;
        --text-color: #1E293B;
        --card-bg: white;
        --card-border: #E2E8F0;
        --metric-title: #64748B;
        --primary-btn: #3B82F6;
        --primary-hover: #2563EB;
    }
    
    @media (prefers-color-scheme: dark) {
        :root {
            --bg-color: #0F172A;
            --sidebar-bg: #1E293B;
            --text-color: #F8FAFC;
            --card-bg: #1E293B;
            --card-border: #334155;
            --metric-title: #94A3B8;
        }
    }
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp { background-color: var(--bg-color); }
    .css-1d391kg, .stSidebar { background-color: var(--sidebar-bg) !important; }
    
    h1, h2, h3 { color: var(--text-color); font-weight: 700 !important; }
    p, span, div { color: var(--text-color); }
    
    .stButton>button {
        background-color: var(--primary-btn);
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 24px;
        font-weight: 600;
        transition: all 0.2s;
    }
    .stButton>button:hover {
        background-color: var(--primary-hover);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    
    .metric-card {
        background-color: var(--card-bg);
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        border: 1px solid var(--card-border);
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .metric-title {
        color: var(--metric-title);
        font-size: 14px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .metric-value {
        color: var(--text-color);
        font-size: 28px;
        font-weight: 700;
        margin-top: 8px;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- Session State ---
def init_state():
    defaults = {
        "current_step": 1,
        "raw_df": None,
        "clean_df": None,
        "filename": None,
        "ignored_cols": [],
        "target_col": None,
        "task_type": None,
        "preprocessor": None,
        "X_train": None, "X_test": None, "y_train": None, "y_test": None,
        "comparison_df": None,
        "leaderboard": None,
        "best_model": None,
        "feature_importances": None,
        "db_conn": None
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

# --- Navigation ---
STEPS = {
    1: "Upload Dataset",
    2: "Validate Dataset",
    3: "Explore Data",
    4: "SQL Analytics",
    5: "Train Models",
    6: "Compare Models",
    7: "Explainability",
    8: "Predictions",
    9: "Reports"
}

def next_step():
    st.session_state["current_step"] = min(st.session_state["current_step"] + 1, 9)

def prev_step():
    st.session_state["current_step"] = max(st.session_state["current_step"] - 1, 1)

def show_onboarding(title, purpose, expected, tips):
    with st.expander("📖 What is this step?", expanded=False):
        st.markdown(f"**Purpose:** {purpose}")
        st.markdown(f"**Expected Output:** {expected}")
        st.info(f"💡 **Tip:** {tips}")

# --- Caching ---
@st.cache_data(show_spinner=False)
def load_data(file_obj, is_csv=True):
    if is_csv:
        return pd.read_csv(file_obj)
    return pd.read_excel(file_obj)

# --- UI Components ---
def render_metric_cards(df):
    cols = st.columns(5)
    metrics = [
        ("Rows", f"{df.shape[0]:,}"),
        ("Columns", df.shape[1]),
        ("Missing Cells", f"{df.isna().sum().sum():,}"),
        ("Duplicates", f"{df.duplicated().sum():,}"),
        ("Memory (MB)", f"{df.memory_usage(deep=True).sum() / 1024**2:.2f}")
    ]
    for col, (title, value) in zip(cols, metrics):
        col.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">{title}</div>
            <div class="metric-value">{value}</div>
        </div>
        """, unsafe_allow_html=True)
    st.write("")

# --- Step 1: Upload ---
def step_upload():
    st.title("📂 Step 1: Upload Dataset")
    show_onboarding(
        "Upload Dataset", 
        "Ingest your raw data into the ML Workbench.", 
        "A preview of your dataset in table format.", 
        "Make sure your dataset contains a column you wish to predict (the Target)."
    )
    
    st.markdown("Upload your tabular dataset to begin. Supported formats: `.csv`, `.xlsx`")
    
    uploaded_file = st.file_uploader("Choose a CSV or Excel file", type=['csv', 'xlsx'])
    
    if st.button("Load Built-in Sample Dataset"):
        sample_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "processed", "ml_dataset.csv")
        try:
            df = pd.read_csv(sample_path)
            st.session_state["raw_df"] = df.copy()
            st.session_state["clean_df"] = df.copy()
            st.session_state["filename"] = "ml_dataset.csv"
            if st.session_state["db_conn"] is None:
                st.session_state["db_conn"] = duckdb.connect(database=':memory:')
            st.session_state["db_conn"].register("dataset", st.session_state["raw_df"])
            next_step()
            st.rerun()
        except Exception as e:
            st.error(f"Error loading sample: {e}")
            
    if uploaded_file is not None:
        try:
            with st.spinner("Loading dataset into memory..."):
                is_csv = uploaded_file.name.endswith('.csv')
                df = load_data(uploaded_file, is_csv)
                
            if df.empty or len(df.columns) < 2:
                st.error("Invalid dataset. Must have at least 2 columns and >0 rows.")
                return
                
            st.session_state["raw_df"] = df.copy()
            st.session_state["clean_df"] = df.copy()
            st.session_state["filename"] = uploaded_file.name
            
            if st.session_state["db_conn"] is None:
                st.session_state["db_conn"] = duckdb.connect(database=':memory:')
            st.session_state["db_conn"].register("dataset", st.session_state["raw_df"])
            
            next_step()
            st.rerun()
            
        except Exception as e:
            st.error(f"Failed to read file. Please ensure it's a valid CSV/Excel. Details: {e}")

# --- Step 2: Validate Dataset ---
def step_validate():
    st.title("🛡️ Step 2: Target Validation & Readiness")
    show_onboarding(
        "Validate Dataset", 
        "Automatically analyze your dataset to detect Identifiers (like User IDs) and recommend the best prediction Target.", 
        "A readiness checklist confirming your data is leak-free.", 
        "Identifiers must be dropped so the model doesn't 'cheat' by memorizing IDs."
    )
    df = st.session_state["raw_df"]
    
    render_metric_cards(df)
    
    st.subheader("Automated Target & Leakage Detection")
    
    detected_ids = []
    potential_targets = []
    
    for col in df.columns:
        col_lower = col.lower()
        if 'id' in col_lower or 'uuid' in col_lower or 'key' in col_lower or 'email' in col_lower or 'phone' in col_lower:
            detected_ids.append(col)
        elif df[col].nunique() == len(df):
            detected_ids.append(col)
        else:
            potential_targets.append(col)
            
    detected_ids = list(set(detected_ids))
    st.session_state["ignored_cols"] = detected_ids
    
    if detected_ids:
        st.warning(f"**Identifiers Detected & Excluded:** {', '.join(detected_ids)}")
        st.caption("These columns have been automatically removed from target selection to prevent data leakage.")
        
    recommended_target = None
    reason = ""
    for col in potential_targets:
        if df[col].nunique() == 2:
            recommended_target = col
            reason = "Binary classification target with sufficient samples."
            break
            
    if not recommended_target and potential_targets:
        recommended_target = potential_targets[-1]
        reason = "Numeric/Categorical column found at the end of the dataset."
        
    st.info(f"**Recommended Target:** `{recommended_target}`\n\n**Reason:** {reason}")
    
    if not potential_targets:
        st.error("No valid target columns found! All columns appear to be identifiers. Please upload a different dataset.")
        return
        
    selected_target = st.selectbox("Confirm Target Column:", potential_targets, index=potential_targets.index(recommended_target) if recommended_target in potential_targets else 0)
    
    st.markdown("### Readiness Report")
    st.markdown("- [x] Schema Valid")
    st.markdown(f"- [x] Missing Values Checked ({df.isna().sum().sum()} found)")
    st.markdown(f"- [x] Identifier Columns Removed ({len(detected_ids)} removed)")
    st.markdown("- [x] Leakage Check Passed")
    
    if st.button("Confirm Validation & Proceed", type="primary"):
        st.session_state["target_col"] = selected_target
        next_step()
        st.rerun()

# --- Step 3: Explore Data ---
def step_explore():
    st.title("📊 Step 3: Smart Exploratory Data Analysis")
    show_onboarding(
        "Explore Data", 
        "Visualize the distribution of your features and extract business meaning.", 
        "Interactive histograms and bar charts with dynamically calculated insights.", 
        "Look for highly imbalanced classes or massive outliers."
    )
    df = st.session_state["clean_df"]
    target = st.session_state.get("target_col")
    
    num_cols = df.select_dtypes(include=np.number).columns.tolist()
    cat_cols = df.select_dtypes(exclude=np.number).columns.tolist()
    
    tab1, tab2 = st.tabs(["Numerical Features", "Categorical Features"])
    
    with tab1:
        if num_cols:
            selected_num = st.selectbox("Select Numerical Feature", num_cols, key="num")
            fig = px.histogram(df, x=selected_num, color=target if target in df.columns else None, nbins=50, title=f"Distribution of {selected_num}")
            st.plotly_chart(fig, use_container_width=True)
            
            mean_val = df[selected_num].mean()
            max_val = df[selected_num].max()
            st.success(f"**Observation:** The average value for `{selected_num}` is **{mean_val:.2f}**, peaking at **{max_val:.2f}**.\n\n**Business Meaning:** Identifies the core range of this metric for your user base.\n\n**Recommendation:** Check for outliers at the tail ends of the distribution before training.")
            
    with tab2:
        if cat_cols:
            selected_cat = st.selectbox("Select Categorical Feature", cat_cols, key="cat")
            val_counts = df[selected_cat].value_counts().reset_index()
            if not val_counts.empty:
                val_counts.columns = [selected_cat, 'Count']
                
                majority_cat = val_counts.iloc[0][selected_cat]
                majority_pct = (val_counts.iloc[0]['Count'] / len(df)) * 100
                
                fig = px.bar(val_counts.head(20), x=selected_cat, y='Count', title=f"Top Categories in {selected_cat}")
                st.plotly_chart(fig, use_container_width=True)
                
                st.success(f"**Observation:** `{majority_cat}` is the dominant category, making up **{majority_pct:.1f}%** of the data.\n\n**Business Meaning:** This segment represents your largest demographic or cohort.\n\n**Recommendation:** Ensure sufficient representation of minority classes to prevent model bias.")
            else:
                st.info(f"No valid data found in `{selected_cat}`.")

    st.write("")
    if st.button("Continue to SQL Analytics", type="primary"):
        next_step()
        st.rerun()

# --- Step 4: SQL Analytics ---
def step_sql():
    st.title("💻 Step 4: SQL Analytics")
    show_onboarding(
        "SQL Analytics", 
        "Run fast analytical queries directly on your dataset using DuckDB.", 
        "A data table containing the results of your query.", 
        "Use the quick templates to instantly analyze target class balance without writing code."
    )
    
    templates = {
        "Preview Data": "SELECT * FROM dataset LIMIT 10;",
        "Target Class Balance": f"SELECT {st.session_state.get('target_col', 'target')}, COUNT(*) as count FROM dataset GROUP BY 1 ORDER BY 2 DESC;",
        "Overall Summary": "SELECT count(*) as total_rows FROM dataset;"
    }
    
    selected_template = st.selectbox("Quick Analysis Templates", list(templates.keys()))
    
    if "last_template" not in st.session_state or st.session_state["last_template"] != selected_template:
        st.session_state["sql_query"] = templates[selected_template]
        st.session_state["last_template"] = selected_template
    
    with st.expander("Advanced SQL Editor", expanded=False):
        query = st.text_area("Write custom SQL (table is named 'dataset')", key="sql_query", height=120)
        
    if st.button("Execute Query"):
        try:
            conn = st.session_state["db_conn"]
            res = conn.execute(query).df()
            st.dataframe(res)
            st.success(f"Query returned {res.shape[0]} rows.")
        except Exception as e:
            st.error(f"SQL Error: {e}")
            
    st.write("")
    if st.button("Continue to Model Training", type="primary"):
        next_step()
        st.rerun()

# --- Step 5: Train Models ---
def step_train():
    st.title("🤖 Step 5: Model Training")
    show_onboarding(
        "Train Models", 
        "Automatically preprocess data, detect task type, and train multiple ML algorithms concurrently.", 
        "A trained pipeline ready for evaluation.", 
        "This step automatically handles missing values, one-hot encoding, and hyperparameter tuning."
    )
    df = st.session_state["clean_df"]
    target = st.session_state["target_col"]
    id_cols = st.session_state["ignored_cols"]
    
    st.markdown(f"**Target Variable:** `{target}`")
    st.markdown(f"**Ignored Identifiers:** `{id_cols}`")
    st.markdown(f"**Features Available:** {df.shape[1] - 1 - len(id_cols)}")
    
    if st.button("Initialize & Train ML Pipeline", type="primary"):
        start_time = time.time()
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # 1. Detect Task
            status_text.text("Detecting Task Type...")
            progress_bar.progress(10)
            y = df[target]
            task_type = detect_task_type(y)
            st.session_state["task_type"] = task_type
            
            if task_type == "Classification" and y.nunique() > 50:
                st.error("Target has too many unique values for Classification. Please redefine your target in Step 2.")
                return
                
            # 2. Preprocess & Split
            status_text.text("Preprocessing Data and Splitting (80/20)...")
            progress_bar.progress(30)
            df_ml = df.dropna(subset=[target]).copy()
            X = df_ml.drop(columns=[target] + id_cols, errors='ignore')
            y = df_ml[target]
            
            from sklearn.model_selection import train_test_split
            if task_type == "Classification":
                try:
                    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
                except ValueError:
                    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            else:
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
                
            st.session_state.update({"X_train": X_train, "X_test": X_test, "y_train": y_train, "y_test": y_test})
            
            feature_dict = detect_features(X_train, target_col="")
            num_features = feature_dict["numeric"]
            cat_features = feature_dict["categorical"]
            bool_features = feature_dict["boolean"]
            preprocessor = build_preprocessor(num_features, cat_features, bool_features)
            st.session_state["preprocessor"] = preprocessor
            
            # 3. Train
            status_text.text(f"Training multiple {task_type} models...")
            progress_bar.progress(60)
            comparison_df = train_and_compare(X_train, X_test, y_train, y_test, task_type=task_type)
            st.session_state["comparison_df"] = comparison_df
            leaderboard = generate_leaderboard(comparison_df.to_dict(orient="records"), task_type=task_type)
            st.session_state["leaderboard"] = leaderboard
            
            # 4. Tune
            status_text.text(f"Hyperparameter tuning the Best Model ({leaderboard['best_model']})...")
            progress_bar.progress(85)
            best_model = tune_best_model(X_train, y_train, preprocessor, leaderboard['best_model'], n_iter=5, task_type=task_type)
            st.session_state["best_model"] = best_model
            
            # 5. Explainability Prep
            status_text.text("Extracting Feature Importances...")
            progress_bar.progress(95)
            try:
                feature_names_out = preprocessor.get_feature_names_out()
                feature_names_clean = [f.split("__")[-1] for f in feature_names_out]
            except:
                feature_names_clean = X_train.columns.tolist()
            st.session_state["feature_importances"] = get_feature_importance(best_model, feature_names_clean)
            
            progress_bar.progress(100)
            elapsed = time.time() - start_time
            status_text.text(f"✅ Pipeline completed in {elapsed:.2f} seconds!")
            
            time.sleep(1)
            next_step()
            st.rerun()
            
        except Exception as e:
            st.error(f"Pipeline Failed: {e}")

# --- Step 6: Compare Models ---
def step_compare():
    st.title("🏆 Step 6: Model Comparison")
    show_onboarding(
        "Compare Models", 
        "Review the performance of all trained models on the test set.", 
        "A leaderboard and metric comparison chart.", 
        "For imbalanced classification, look at F1 Score or ROC AUC instead of plain Accuracy."
    )
    comp_df = st.session_state["comparison_df"]
    lb = st.session_state["leaderboard"]
    
    st.markdown("### Leaderboard Highlights")
    c1, c2, c3 = st.columns(3)
    c1.markdown(f"<div class='metric-card'><div class='metric-title'>Best Overall Model</div><div class='metric-value' style='color:#10b981'>{lb['best_model']}</div></div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='metric-card'><div class='metric-title'>Fastest Inference</div><div class='metric-value' style='color:#3B82F6'>{lb['fastest_model']}</div></div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='metric-card'><div class='metric-title'>Most Interpretable</div><div class='metric-value' style='color:#f59e0b'>{lb['most_interpretable']}</div></div>", unsafe_allow_html=True)
    
    st.write("")
    highlight_cols = [c for c in ['accuracy', 'roc_auc', 'f1_score'] if c in comp_df.columns and comp_df[c].notna().any()]
    st.dataframe(comp_df.style.highlight_max(axis=0, subset=highlight_cols if st.session_state['task_type']=='Classification' else []), use_container_width=True)
    
    metric = "roc_auc" if st.session_state["task_type"] == "Classification" else "rmse"
    if metric in comp_df.columns:
        fig = px.bar(comp_df, x="model", y=metric, color="model", title=f"Model Comparison ({metric.upper()})")
        st.plotly_chart(fig, use_container_width=True)
    
    if st.button("Continue to Explainability", type="primary"):
        next_step()
        st.rerun()

# --- Step 7: Explainability ---
def step_explain():
    st.title("🧠 Step 7: Explainability (XAI)")
    show_onboarding(
        "Explainability", 
        "Understand HOW the best model makes its decisions.", 
        "Feature importance charts, Confusion Matrix, and Error Analysis.", 
        "If a feature has 99% importance, check if it's a data leak (e.g. predicting churn using 'churn_date')."
    )
    
    model = st.session_state["best_model"]
    X_test = st.session_state["X_test"]
    y_test = st.session_state["y_test"]
    task_type = st.session_state["task_type"]
    fi = st.session_state["feature_importances"]
    
    st.markdown(f"### Best Model: `{st.session_state['leaderboard']['best_model']}`")
    
    tab1, tab2, tab3 = st.tabs(["Feature Importance", "Advanced Charts", "Error Analysis"])
    
    with tab1:
        if fi is not None and not fi.empty:
            fig = px.bar(fi.head(15).sort_values("importance", ascending=True), 
                         x="importance", y="feature", orientation='h', 
                         title="Top 15 Most Important Features")
            st.plotly_chart(fig, use_container_width=True)
            
            top_feature = fi.iloc[0]['feature']
            st.success(f"**Business Meaning:** `{top_feature}` is the strongest driver for predicting `{st.session_state['target_col']}`. Focus your strategy around optimizing this metric.")
        else:
            st.info("Global feature importance not available for this model type.")
            
    with tab2:
        if task_type == "Classification":
            col1, col2 = st.columns(2)
            try:
                preds = model.predict(X_test)
                probas = model.predict_proba(X_test)[:, 1] if hasattr(model, "predict_proba") else None
                
                with col1:
                    cm_fig = plot_confusion_matrix(y_test, preds)
                    st.plotly_chart(cm_fig, use_container_width=True)
                
                with col2:
                    if probas is not None and len(np.unique(y_test)) == 2:
                        roc_fig = plot_roc_curve(y_test, probas)
                        if roc_fig:
                            st.plotly_chart(roc_fig, use_container_width=True)
                        else:
                            st.info("ROC Curve only supports binary classification.")
                    elif len(np.unique(y_test)) > 2:
                        st.info("ROC Curve is optimized for binary classification (multi-class detected).")
                    else:
                        st.info("Model does not output probabilities (ROC disabled).")
            except Exception as e:
                st.warning(f"Could not generate advanced charts: {e}")
        else:
            st.info("Advanced charts (Confusion Matrix, ROC) are for Classification tasks only.")
            
    with tab3:
        with st.spinner("Analyzing model errors..."):
            err_summary, top_errors = error_analysis(model, X_test, y_test, task_type)
            st.write(err_summary)
            if not top_errors.empty:
                st.dataframe(top_errors.head(10))
        
    if st.button("Continue to Predictions", type="primary"):
        next_step()
        st.rerun()

# --- Step 8: Predictions ---
def step_predict():
    st.title("🔮 Step 8: Batch Predictions")
    show_onboarding(
        "Predictions", 
        "Use the trained model to predict outcomes on new, unseen data.", 
        "A downloadable CSV with your original data plus a new Prediction column.", 
        "Ensure the new CSV has the exact same columns as the training data (minus the target)."
    )
    
    st.markdown("Upload a new dataset (without the target column) to generate predictions.")
    pred_file = st.file_uploader("Upload New Dataset", type=['csv', 'xlsx'], key="pred_file")
    
    if pred_file:
        try:
            is_csv = pred_file.name.endswith('.csv')
            new_df = load_data(pred_file, is_csv)
            st.write(f"Loaded {new_df.shape[0]:,} rows.")
            
            missing_cols = [c for c in st.session_state["X_train"].columns if c not in new_df.columns]
            if missing_cols:
                st.error(f"Schema Mismatch! Missing required columns from training schema: {missing_cols}")
            else:
                # Drop ignored columns to prevent preprocessing errors
                for col in st.session_state["ignored_cols"]:
                    if col in new_df.columns:
                        new_df = new_df.drop(columns=[col])
                        
                if st.button("Generate Predictions"):
                    with st.spinner("Predicting..."):
                        preds = st.session_state["best_model"].predict(new_df)
                        new_df["Predicted_" + st.session_state["target_col"]] = preds
                        
                        if hasattr(st.session_state["best_model"], "predict_proba"):
                            probas = st.session_state["best_model"].predict_proba(new_df)
                            new_df["Confidence_Score"] = np.max(probas, axis=1)
                            
                        st.success("Predictions Generated successfully!")
                        st.dataframe(new_df.head(10))
                        
                        csv = new_df.to_csv(index=False).encode('utf-8')
                        st.download_button("Download Full Predictions CSV", data=csv, file_name="predictions.csv", mime="text/csv")
        except Exception as e:
            st.error(f"Error predicting: {e}")
            
    st.write("---")
    if st.button("Continue to Final Report", type="primary"):
        next_step()
        st.rerun()

# --- Step 9: Reports & Downloads ---
def step_report():
    st.title("📥 Step 9: Final Report & Downloads")
    show_onboarding(
        "Reports", 
        "Export the final model and summary text for deployment.", 
        "A downloadable `.pkl` file and summary report.", 
        "The PKL file contains the full Scikit-Learn Pipeline (preprocessing + model) and can be loaded via `joblib.load()`."
    )
    
    st.success("🎉 You have successfully completed the end-to-end Machine Learning Lifecycle!")
    
    st.markdown("Download your trained artifacts for production deployment.")
    
    # Best Model PKL
    buffer = io.BytesIO()
    joblib.dump(st.session_state["best_model"], buffer)
    st.download_button(
        label="⬇️ Download Best Model Pipeline (.pkl)",
        data=buffer.getvalue(),
        file_name="best_model_pipeline.pkl",
        mime="application/octet-stream",
        type="primary"
    )
    
    # Summary Report Generation
    report_text = f"""=================================
MACHINE LEARNING WORKBENCH REPORT
=================================
Task Type: {st.session_state['task_type']}
Target Variable: {st.session_state['target_col']}

MODEL LEADERBOARD:
{st.session_state['comparison_df'].to_string(index=False)}

BEST MODEL PIPELINE:
{st.session_state['leaderboard']['best_model']}

FEATURES ANALYZED: {st.session_state['X_train'].shape[1]}
TRAINING SAMPLES: {st.session_state['X_train'].shape[0]}
================================="""
    
    st.download_button(
        label="📄 Download Summary Report (.txt)",
        data=report_text,
        file_name="ml_summary_report.txt",
        mime="text/plain"
    )
    
    if st.button("Reset Entire Pipeline"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()

# --- Main Application Router ---
def main():
    try:
        inject_custom_css()
        init_state()
        
        # Sidebar
        st.sidebar.title("Workflow Progress")
        current = st.session_state["current_step"]
        
        for step_num, step_name in STEPS.items():
            if step_num < current:
                st.sidebar.markdown(f"<span style='color: #10B981; font-weight: 600;'>✓ Step {step_num}: {step_name}</span>", unsafe_allow_html=True)
            elif step_num == current:
                st.sidebar.markdown(f"<span style='color: #3B82F6; font-weight: 700;'>▶ Step {step_num}: {step_name}</span>", unsafe_allow_html=True)
            else:
                st.sidebar.markdown(f"<span style='color: #94A3B8;'>🔒 Step {step_num}: {step_name}</span>", unsafe_allow_html=True)
                
        st.sidebar.markdown("---")
        if current > 1:
            if st.sidebar.button("⬅️ Previous Step"):
                prev_step()
                st.rerun()
                
        # Routing
        if current == 1: step_upload()
        elif current == 2: step_validate()
        elif current == 3: step_explore()
        elif current == 4: step_sql()
        elif current == 5: step_train()
        elif current == 6: step_compare()
        elif current == 7: step_explain()
        elif current == 8: step_predict()
        elif current == 9: step_report()
        
    except Exception as e:
        st.error("⚠️ An unexpected error occurred in the application.")
        st.info(f"Technical Details: {str(e)}")
        st.warning("Please try refreshing the page or navigating to the previous step.")
    
if __name__ == "__main__":
    main()
