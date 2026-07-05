"""
Streamlit Machine Learning Workbench
A dynamic end-to-end ML platform for tabular data.
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
from src.evaluation.explainability import get_feature_importance, get_permutation_importance, error_analysis

# --- Page Config ---
st.set_page_config(page_title="ML Workbench", layout="wide", page_icon="⚙️")

# --- Session State Initialization ---
def init_state():
    defaults = {
        "raw_df": None,
        "clean_df": None,
        "filename": None,
        "target_col": None,
        "id_col": None,
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

init_state()

# --- Helper Functions ---
def reset_pipeline_state():
    """Resets everything downstream of data upload."""
    st.session_state["target_col"] = None
    st.session_state["task_type"] = None
    st.session_state["preprocessor"] = None
    st.session_state["comparison_df"] = None
    st.session_state["best_model"] = None
    st.session_state["feature_importances"] = None

# --- UI Pages ---

def render_welcome():
    st.title("⚙️ Interactive Machine Learning Workbench")
    st.markdown("""
    Welcome to the generic **Machine Learning Workbench**.
    
    This application allows you to upload **any structured tabular dataset** (CSV or Excel) and takes you through an entire end-to-end Machine Learning pipeline:
    
    1. **Upload Dataset**: Ingest your raw data.
    2. **Data Profiling**: Automatically inspect schema and statistics.
    3. **Data Cleaning & EDA**: Visualize distributions and prepare data.
    4. **SQL Analytics**: Query your uploaded data in real-time.
    5. **Model Training**: Auto-detect classification or regression and train multiple models.
    6. **Evaluation & Explainability**: Compare results and explain predictions.
    
    👈 **Get started by going to the 'Upload Dataset' tab in the sidebar.**
    """)
    st.info("Ensure your dataset has a clear target variable you want to predict.")

def render_upload():
    st.title("📂 Upload Dataset")
    st.markdown("Upload your tabular dataset to begin. Supported formats: **.csv**, **.xlsx**")
    
    uploaded_file = st.file_uploader("Choose a file", type=['csv', 'xlsx'])
    
    # FOR TESTING
    if st.button("Load Sample Dataset (ml_dataset.csv)"):
        sample_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "processed", "ml_dataset.csv")
        try:
            df = pd.read_csv(sample_path)
            st.session_state["raw_df"] = df.copy()
            st.session_state["clean_df"] = df.copy()
            st.session_state["filename"] = "ml_dataset.csv"
            
            if st.session_state["db_conn"] is None:
                st.session_state["db_conn"] = duckdb.connect(database=':memory:')
            st.session_state["db_conn"].register("dataset", st.session_state["raw_df"])
            reset_pipeline_state()
            st.success("Successfully loaded sample dataset!")
        except Exception as e:
            st.error(f"Error loading sample: {e}")
            
    if uploaded_file is not None:
        try:
            with st.spinner("Loading dataset..."):
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                
            if df.empty:
                st.error("The uploaded dataset is empty.")
                return
                
            if len(df.columns) < 2:
                st.error("The dataset must have at least 2 columns (features + target).")
                return
                
            # Basic validation check
            st.session_state["raw_df"] = df.copy()
            st.session_state["clean_df"] = df.copy() # Initial state
            st.session_state["filename"] = uploaded_file.name
            
            # Setup DuckDB
            if st.session_state["db_conn"] is None:
                st.session_state["db_conn"] = duckdb.connect(database=':memory:')
            # Register dataframe as a table
            raw_data = st.session_state["raw_df"]
            st.session_state["db_conn"].register("dataset", raw_data)
            
            st.success(f"Successfully loaded '{uploaded_file.name}' with {df.shape[0]} rows and {df.shape[1]} columns!")
            reset_pipeline_state()
            
            st.dataframe(df.head(10))
            
        except Exception as e:
            st.error(f"Error reading file: {e}")

def render_profiling():
    st.title("📊 Data Profiling & Schema")
    df = st.session_state["raw_df"]
    
    if df is None:
        st.warning("Please upload a dataset first.")
        return
        
    col1, col2, col3 = st.columns(3)
    col1.metric("Rows", df.shape[0])
    col2.metric("Columns", df.shape[1])
    col3.metric("Missing Cells", df.isna().sum().sum())
    
    st.subheader("Schema Validation")
    buffer = io.StringIO()
    df.info(buf=buffer)
    st.text(buffer.getvalue())
    
    st.subheader("Statistical Summary")
    st.dataframe(df.describe(include='all'))
    
    st.subheader("Missing Values Heatmap")
    missing = df.isna().sum()
    missing = missing[missing > 0]
    if not missing.empty:
        fig = px.bar(missing, x=missing.index, y=missing.values, title="Missing Values per Column")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.success("No missing values found in the dataset!")

def render_cleaning_eda():
    st.title("🧹 Data Cleaning & EDA")
    df = st.session_state["clean_df"]
    
    if df is None:
        st.warning("Please upload a dataset first.")
        return

    st.subheader("Exploratory Data Analysis")
    num_cols = df.select_dtypes(include=np.number).columns.tolist()
    cat_cols = df.select_dtypes(exclude=np.number).columns.tolist()
    
    tab1, tab2 = st.tabs(["Numerical Features", "Categorical Features"])
    
    with tab1:
        if num_cols:
            selected_num = st.selectbox("Select Numerical Feature", num_cols)
            fig = px.histogram(df, x=selected_num, nbins=50, title=f"Distribution of {selected_num}")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No numerical features found.")
            
    with tab2:
        if cat_cols:
            selected_cat = st.selectbox("Select Categorical Feature", cat_cols)
            val_counts = df[selected_cat].value_counts().reset_index()
            val_counts.columns = [selected_cat, 'Count']
            # Only show top 20 for readability
            fig = px.bar(val_counts.head(20), x=selected_cat, y='Count', title=f"Top 20 categories in {selected_cat}")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No categorical features found.")

def render_sql():
    st.title("💻 SQL Analytics")
    if st.session_state["raw_df"] is None:
        st.warning("Please upload a dataset first.")
        return
        
    st.markdown("Your uploaded data is available as a table named **`dataset`**.")
    query = st.text_area("Write your SQL query:", value="SELECT * FROM dataset LIMIT 10;", height=150)
    
    if st.button("Execute Query"):
        try:
            conn = st.session_state["db_conn"]
            res = conn.execute(query).df()
            st.success("Query executed successfully!")
            st.dataframe(res)
            
            csv = res.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Results as CSV",
                data=csv,
                file_name='query_results.csv',
                mime='text/csv',
            )
        except Exception as e:
            st.error(f"SQL Error: {str(e)}")

def render_training():
    st.title("🤖 Model Training & Comparison")
    df = st.session_state["clean_df"]
    
    if df is None:
        st.warning("Please upload a dataset first.")
        return
        
    st.subheader("1. Setup Machine Learning Task")
    
    cols = df.columns.tolist()
    target = st.selectbox("Select Target Column to Predict:", [None] + cols)
    id_cols = st.multiselect("Select Columns to Ignore (e.g. IDs):", cols)
    
    if target:
        if st.button("Start Training Pipeline"):
            with st.spinner("Detecting Task Type..."):
                y = df[target]
                task_type = detect_task_type(y)
                st.session_state["task_type"] = task_type
                st.session_state["target_col"] = target
                st.info(f"**Detected Task:** {task_type}")
                
            with st.spinner("Preparing Data & Preprocessing..."):
                # Drop NAs in target
                df_ml = df.dropna(subset=[target]).copy()
                X = df_ml.drop(columns=[target] + id_cols)
                y = df_ml[target]
                
                # Split
                X_train, X_test, y_train, y_test = split_data(X, y)
                st.session_state["X_train"] = X_train
                st.session_state["X_test"] = X_test
                st.session_state["y_train"] = y_train
                st.session_state["y_test"] = y_test
                
                # Detect features and build preprocessor
                num_features, cat_features, bool_features = detect_features(X_train)
                preprocessor = build_preprocessor(num_features, cat_features, bool_features)
                st.session_state["preprocessor"] = preprocessor
                
            with st.spinner(f"Training and Evaluating Models ({task_type})..."):
                comparison_df = train_and_compare(X_train, X_test, y_train, y_test, task_type=task_type)
                st.session_state["comparison_df"] = comparison_df
                
                leaderboard = generate_leaderboard(comparison_df.to_dict(orient="records"), task_type=task_type)
                st.session_state["leaderboard"] = leaderboard
                
            with st.spinner(f"Hyperparameter Tuning the Best Model ({leaderboard['best_model']})..."):
                best_model = tune_best_model(X_train, y_train, preprocessor, leaderboard['best_model'], n_iter=5, task_type=task_type)
                st.session_state["best_model"] = best_model
                
                # Extract Feature Importance
                try:
                    feature_names_out = preprocessor.get_feature_names_out()
                    feature_names_clean = [f.split("__")[-1] for f in feature_names_out]
                except Exception:
                    feature_names_clean = X_train.columns.tolist()
                
                fi = get_feature_importance(best_model, feature_names_clean)
                st.session_state["feature_importances"] = fi
                
            st.success("Training Complete! Proceed to the 'Evaluation' tab.")
            st.rerun()

    if st.session_state["comparison_df"] is not None:
        st.markdown("---")
        st.subheader("🏆 Model Leaderboard")
        comp_df = st.session_state["comparison_df"]
        st.dataframe(comp_df)
        
        lb = st.session_state["leaderboard"]
        c1, c2, c3 = st.columns(3)
        c1.success(f"**Best Model**: {lb['best_model']}")
        c2.info(f"**Fastest Inference**: {lb['fastest_model']}")
        c3.warning(f"**Most Interpretable**: {lb['most_interpretable']}")
        
        metric = "roc_auc" if st.session_state["task_type"] == "Classification" else "rmse"
        fig = px.bar(comp_df, x="model", y=metric, color="model", title=f"Model Comparison ({metric.upper()})")
        st.plotly_chart(fig, use_container_width=True)

def render_evaluation():
    st.title("📊 Detailed Evaluation & Explainability")
    if st.session_state["best_model"] is None:
        st.warning("Please train models first.")
        return
        
    st.subheader(f"Best Model: {st.session_state['leaderboard']['best_model']}")
    
    fi = st.session_state["feature_importances"]
    if fi is not None and not fi.empty:
        st.markdown("### Feature Importance")
        fig = px.bar(fi.head(15).sort_values("importance", ascending=True), 
                     x="importance", y="feature", orientation='h', 
                     title="Top 15 Most Important Features")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Feature importance not available for this model type.")
        
    st.markdown("### Error Analysis")
    with st.spinner("Analyzing errors..."):
        err_summary, top_errors = error_analysis(
            st.session_state["best_model"], 
            st.session_state["X_test"], 
            st.session_state["y_test"], 
            st.session_state["task_type"]
        )
        st.write(err_summary)
        st.dataframe(top_errors)

def render_predictions():
    st.title("🔮 Predictions Simulator")
    if st.session_state["best_model"] is None:
        st.warning("Please train models first.")
        return
        
    st.markdown("Adjust features below to generate live predictions using the trained pipeline.")
    
    X_train = st.session_state["X_train"]
    model = st.session_state["best_model"]
    task_type = st.session_state["task_type"]
    
    input_data = {}
    
    # Create an expander for input fields to save space
    with st.expander("Feature Inputs", expanded=True):
        # We will create 3 columns
        cols = st.columns(3)
        for i, col in enumerate(X_train.columns):
            c = cols[i % 3]
            dtype = X_train[col].dtype
            
            if pd.api.types.is_numeric_dtype(dtype):
                mean_val = float(X_train[col].mean())
                min_val = float(X_train[col].min())
                max_val = float(X_train[col].max())
                # Handle edge case where min == max
                if min_val == max_val:
                    input_data[col] = c.number_input(f"{col}", value=mean_val)
                else:
                    input_data[col] = c.slider(f"{col}", min_value=min_val, max_value=max_val, value=mean_val)
            elif pd.api.types.is_bool_dtype(dtype):
                input_data[col] = c.selectbox(f"{col}", [True, False])
            else:
                unique_vals = X_train[col].dropna().unique().tolist()
                if not unique_vals:
                    unique_vals = ["Unknown"]
                input_data[col] = c.selectbox(f"{col}", unique_vals)
                
    if st.button("Predict"):
        input_df = pd.DataFrame([input_data])
        try:
            if task_type == "Classification":
                prob = model.predict_proba(input_df)[0]
                pred = model.predict(input_df)[0]
                st.success(f"**Prediction:** {pred}")
                st.info(f"**Probabilities:** {dict(enumerate(prob))}")
            else:
                pred = model.predict(input_df)[0]
                st.success(f"**Prediction:** {pred:.4f}")
                
            from src.evaluation.explainability import generate_plain_english_explanation
            explanation = generate_plain_english_explanation(pred, st.session_state["feature_importances"], input_df.iloc[0])
            st.markdown("### Plain English Explanation")
            st.info(explanation)
            
        except Exception as e:
            st.error(f"Prediction Error: {e}")

def render_downloads():
    st.title("📥 Download Center")
    if st.session_state["best_model"] is None:
        st.warning("Please complete the pipeline to enable downloads.")
        return
        
    st.markdown("Download your trained artifacts and reports here.")
    
    # Best Model
    buffer = io.BytesIO()
    joblib.dump(st.session_state["best_model"], buffer)
    st.download_button(
        label="Download Best Model Pipeline (.pkl)",
        data=buffer.getvalue(),
        file_name="best_model_pipeline.pkl",
        mime="application/octet-stream"
    )
    
    # Leaderboard CSV
    csv = st.session_state["comparison_df"].to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Leaderboard (.csv)",
        data=csv,
        file_name="leaderboard.csv",
        mime="text/csv"
    )

# --- Sidebar Navigation ---
st.sidebar.title("Navigation")
# Control visibility of pages based on state
available_pages = ["Welcome", "Upload Dataset"]
if st.session_state["raw_df"] is not None:
    available_pages.extend(["Data Profiling & Schema", "Data Cleaning & EDA", "SQL Analytics", "Model Training"])
if st.session_state["best_model"] is not None:
    available_pages.extend(["Evaluation & Explainability", "Predictions Simulator", "Download Center"])

page = st.sidebar.radio("Go to:", available_pages)

# --- Router ---
if page == "Welcome":
    render_welcome()
elif page == "Upload Dataset":
    render_upload()
elif page == "Data Profiling & Schema":
    render_profiling()
elif page == "Data Cleaning & EDA":
    render_cleaning_eda()
elif page == "SQL Analytics":
    render_sql()
elif page == "Model Training":
    render_training()
elif page == "Evaluation & Explainability":
    render_evaluation()
elif page == "Predictions Simulator":
    render_predictions()
elif page == "Download Center":
    render_downloads()
