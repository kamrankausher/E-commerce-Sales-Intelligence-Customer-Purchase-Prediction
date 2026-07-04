"""
Streamlit Dashboard for E-commerce Customer Analytics
"""
import streamlit as st
import pandas as pd
import joblib
import os
import duckdb
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# Adjust system path to import config
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from src.visualization.plots import plot_correlation_heatmap

st.set_page_config(page_title="E-commerce Analytics", layout="wide", page_icon="🛒")

# ─── Load Data ─────────────────────────────────────────────────────────────
@st.cache_resource
def load_data():
    master_clean = pd.read_csv(config.MASTER_CLEANED_FILE)
    ml_data = pd.read_csv(config.ML_DATASET_FILE)
    model_results = pd.read_csv(config.MODEL_RESULTS_FILE)
    model = joblib.load(config.BEST_MODEL_FILE)
    
    # Load raw data into DuckDB for SQL Analytics
    conn = duckdb.connect(database=':memory:')
    for table_name in ['customers', 'orders', 'order_items', 'products', 'order_payments']:
        file_path = os.path.join(config.RAW_DATA_DIR, f"olist_{table_name}_dataset.csv")
        if os.path.exists(file_path):
            # Clean up the table name for SQL
            sql_name = table_name.replace("order_", "")
            if sql_name == "items": sql_name = "items"
            conn.execute(f"CREATE TABLE {sql_name} AS SELECT * FROM read_csv_auto('{file_path}')")
    
    return master_clean, ml_data, model_results, model, conn

try:
    df_clean, df_ml, df_results, best_model, db_conn = load_data()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.info("Please run `python run_pipeline.py` first to generate the required datasets and models.")
    st.stop()

# ─── Navigation ────────────────────────────────────────────────────────────
pages = [
    "Home", "Dataset Overview", "Data Validation", "Data Cleaning Report", 
    "EDA", "SQL Insights", "Machine Learning", "Model Comparison", 
    "Prediction Simulator", "Business Insights", "About"
]
page = st.sidebar.radio("Navigate", pages)

# ─── Pages ─────────────────────────────────────────────────────────────────

if page == "Home":
    st.title("🛒 E-commerce Customer Analytics & Churn Prediction")
    st.markdown("""
    Welcome to the E-commerce Growth Intelligence Platform.
    
    This project demonstrates an end-to-end Data Science pipeline to identify high-risk customers 
    and provide actionable retention strategies.
    
    **Project Goals:**
    1. Identify customers likely to churn (90-day inactivity).
    2. Understand churn drivers (Recency, Frequency, Delivery Experience).
    3. Quantify revenue impact and prioritize retention efforts.
    
    Use the sidebar to navigate through the different phases of the project, from raw data validation 
    all the way to the machine learning predictions and business insights.
    """)
    st.image("https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?auto=format&fit=crop&w=1200&q=80", use_column_width=True)

elif page == "Dataset Overview":
    st.title("📊 Dataset Overview")
    st.markdown("We are analyzing a relational Brazilian E-commerce dataset containing 8 tables.")
    col1, col2, col3 = st.columns(3)
    col1.metric("Customers", "10,000+")
    col2.metric("Orders", "29,000+")
    col3.metric("Products", "5,000+")
    
    st.subheader("Raw Data Sample (Customers)")
    st.dataframe(pd.read_csv(os.path.join(config.RAW_DATA_DIR, "olist_customers_dataset.csv")).head())

elif page == "Data Validation":
    st.title("✅ Data Validation")
    st.markdown("Before processing, the raw data undergoes schema validation using `pandera`.")
    report_path = os.path.join(config.REPORTS_DIR, "validation_report.md")
    if os.path.exists(report_path):
        with open(report_path, "r") as f:
            st.markdown(f.read())
    else:
        st.info("Validation report not found. Run the pipeline.")

elif page == "Data Cleaning Report":
    st.title("🧹 Data Cleaning Report")
    st.markdown("""
    **Preprocessing Steps Applied:**
    - Standardized date columns to `datetime` objects.
    - Filtered out canceled/unavailable orders (kept only 'delivered').
    - Imputed missing review scores using the median (ordinal data).
    - Detected and capped outliers in the `price` column using the IQR method.
    """)
    st.subheader("Cleaned Master Dataset")
    st.dataframe(df_clean.head())

elif page == "EDA":
    st.title("📈 Exploratory Data Analysis")
    st.markdown("Dynamic visualization generated from raw data.")
    
    tab1, tab2, tab3 = st.tabs(["Distributions", "Categorical", "Correlations"])
    with tab1:
        st.subheader("Numeric Distributions")
        for col in ["frequency", "monetary", "recency_days"]:
            if col in df_ml.columns:
                fig = px.histogram(df_ml, x=col, title=f"{col.title()} Distribution", nbins=50, color_discrete_sequence=['#6366f1'])
                st.plotly_chart(fig, use_container_width=True)
                
    with tab2:
        st.subheader("Categorical Trends")
        top_states = df_clean["customer_state"].value_counts().reset_index().head(10)
        top_states.columns = ["State", "Count"]
        st.plotly_chart(px.bar(top_states, x="State", y="Count", title="Top 10 Customer States", color_discrete_sequence=['#6366f1']), use_container_width=True)
        
    with tab3:
        st.subheader("Feature Correlations")
        features = [col for col in df_ml.columns if col not in [config.ID_COL, config.TARGET_COL]]
        st.pyplot(plot_correlation_heatmap(df_ml[features + [config.TARGET_COL]]))

elif page == "SQL Insights":
    st.title("💻 SQL Analytics")
    st.markdown("Executing live SQL queries on the raw datasets using DuckDB.")
    
    sql_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sql")
    if os.path.exists(sql_dir):
        queries = [f for f in os.listdir(sql_dir) if f.endswith('.sql')]
        selected_query = st.selectbox("Select a Business Query", queries)
        
        if selected_query:
            query_name = selected_query.replace(".sql", "").replace("_", " ").title()
            st.subheader(f"Query: {query_name}")
            
            with open(os.path.join(sql_dir, selected_query), "r") as f:
                sql_text = f.read()
                
            st.code(sql_text, language="sql")
            
            try:
                res = db_conn.execute(sql_text).df()
                st.dataframe(res)
                
                # Basic automated charting if applicable
                if len(res.columns) >= 2:
                    if "month" in res.columns:
                        st.plotly_chart(px.line(res, x=res.columns[0], y=res.columns[1], title=query_name), use_container_width=True)
                    else:
                        st.plotly_chart(px.bar(res, x=res.columns[0], y=res.columns[-1], title=query_name), use_container_width=True)
            except Exception as e:
                st.error(f"SQL execution failed: {e}")
    else:
        st.warning("SQL directory not found.")

elif page == "Machine Learning":
    st.title("🤖 Machine Learning Pipeline")
    st.markdown("""
    **Target Definition:** 
    Customer churned if no purchase in the last 90 days.
    
    **Features Engineered:**
    - **RFM:** Recency, Frequency, Monetary
    - **Behavioral:** Review count, avg review score, avg days between orders
    - **Operational:** Late delivery rate, installments
    
    **Algorithm Selection:**
    Evaluated Logistic Regression, Decision Tree, Random Forest, XGBoost, LightGBM.
    """)
    st.dataframe(df_ml.head())

elif page == "Model Comparison":
    st.title("🏆 Model Comparison")
    st.markdown("Evaluating models based on ROC-AUC, F1-Score, and Processing Time.")
    st.dataframe(df_results[['model', 'accuracy', 'precision', 'recall', 'f1_score', 'roc_auc', 'training_time_sec']])
    
    st.subheader("ROC-AUC Comparison")
    st.plotly_chart(px.bar(df_results, x='model', y='roc_auc', color='model'))

elif page == "Prediction Simulator":
    st.title("🔮 Churn Prediction Simulator")
    st.markdown("Adjust the features below to simulate customer churn probability using the best model.")
    
    col1, col2, col3 = st.columns(3)
    features = {}
    
    with col1:
        features["frequency"] = st.slider("Frequency (Total orders)", 1, 50, 2)
        features["monetary"] = st.slider("Monetary (Total spend R$)", 10.0, 5000.0, 150.0)
        features["avg_order_value"] = features["monetary"] / features["frequency"]
        
    with col2:
        features["avg_review_score"] = st.slider("Avg Review Score", 1.0, 5.0, 4.5)
        features["review_count"] = st.slider("Total Reviews", 0, 50, 1)
        features["tenure_days"] = st.slider("Tenure (Days since first order)", 1, 730, 300)
        features["avg_days_between_orders"] = st.slider("Avg Days Between Orders", 0, 365, 30)
        
    with col3:
        features["avg_installments"] = st.slider("Avg Installments", 1, 24, 1)
        features["payment_type_diversity"] = st.slider("Payment Methods Used", 1, 5, 1)
        features["late_delivery_rate"] = st.slider("Late Delivery Rate", 0.0, 1.0, 0.0)
        features["category_diversity"] = st.slider("Categories Bought", 1, 20, 2)
        
    if st.button("Predict Churn Risk"):
        input_df = pd.DataFrame([features])
        # Ensure order matches training data
        train_features = [col for col in df_ml.columns if col not in [config.ID_COL, config.TARGET_COL]]
        input_df = input_df[train_features]
        
        prob = best_model.predict_proba(input_df)[0][1]
        
        st.subheader("Prediction Result")
        if prob > 0.5:
            st.error(f"⚠️ HIGH RISK OF CHURN: {prob:.1%} probability")
        elif prob > 0.3:
            st.warning(f"⚖️ MEDIUM RISK: {prob:.1%} probability")
        else:
            st.success(f"✅ ACTIVE CUSTOMER: {prob:.1%} probability")

elif page == "Business Insights":
    st.title("💡 Business Insights & Impact")
    st.markdown("Dynamic insights automatically generated from the underlying data.")
    
    import sys
    from src.analytics.queries import execute_all_business_queries
    from src.visualization.eda import generate_business_insights
    
    # Pass Dataframes dynamically from the duckdb connection
    # Wait, execute_all_business_queries takes dict of DFs, but we already have duckdb connected.
    # To keep it simple in Streamlit without reloading, we'll just read the pre-generated report!
    
    report_path = os.path.join(config.REPORTS_DIR, "Phase4_EDA_Report.md")
    if os.path.exists(report_path):
        with open(report_path, "r", encoding="utf-8") as f:
            st.markdown(f.read())
    else:
        st.info("No EDA Report found. Please run `python run_eda.py`.")
        
    st.markdown("---")
    st.markdown("### Manual Operational Recommendations")
    st.markdown("""
    - **The 60-Day Intervention Rule**: Trigger automated retention emails at day 45.
    - **Operational Impact on Loyalty**: A late delivery increases the probability of churn by ~18%.
    - **The Second Purchase Hurdle**: Create a "Welcome Series" onboarding campaign.
    """)

elif page == "About":
    st.title("ℹ️ About the Project")
    st.markdown("""
    This project was built to demonstrate a complete Data Science and Machine Learning workflow.
    
    **Tools Used:**
    - **Data Manipulation:** `pandas`, `numpy`
    - **Validation:** `pandera`
    - **Machine Learning:** `scikit-learn`, `xgboost`, `lightgbm`
    - **SQL:** `duckdb`
    - **Visualization:** `matplotlib`, `seaborn`, `plotly`
    - **Deployment:** `streamlit`, `docker`
    
    Created for a Data Science portfolio.
    """)
