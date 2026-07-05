# Phase 7: Interactive Machine Learning Workbench

## Overview
In this phase, we transformed the static, backend-only Data Science pipeline into a professional, interactive Machine Learning Workbench using Streamlit. The application allows users to dynamically upload tabular datasets, validate schemas, visualize data, and train predictive models all through a user-friendly interface.

## Key Features Implemented

1. **State-Driven Workflow:**
   - Implemented `st.session_state` management to ensure users follow a logical progression (Upload -> Clean -> Train -> Evaluate).
   - Sidebar navigation dynamically updates based on the user's progress.

2. **Dynamic Data Ingestion & Profiling:**
   - Supports CSV and Excel formats.
   - Automatically generates statistical summaries, missing value heatmaps, and schema overviews using Pandas and Plotly.

3. **Real-time EDA & SQL Analytics:**
   - Built a dynamic Exploratory Data Analysis module rendering Plotly charts for both numerical and categorical features.
   - Integrated **DuckDB** in-memory to allow users to write and execute live SQL queries directly against their uploaded dataset in the browser.

4. **Automated Machine Learning Pipeline:**
   - Integrated the auto-detection modules from Phase 6 (`detect_task_type`, `detect_features`).
   - The user selects a target column; the app automatically builds a generic `ColumnTransformer`, splits the data, trains 5 models (Logistic Regression, Decision Tree, Random Forest, XGBoost, LightGBM for classification), and generates a leaderboard.

5. **Explainability & Predictions:**
   - Computes Feature Importances dynamically.
   - Includes an interactive **Predictions Simulator** that generates UI inputs based on the original feature data types, allowing live inference through the trained `Pipeline`.
   - Generates Plain-English business translations of the predictions.

6. **Download Center:**
   - Users can download the `best_model.pkl` pipeline and the model comparison leaderboard.

## Design Principles Addressed
- **No Hardcoding:** The app dynamically infers data types and targets without relying on the specific e-commerce dataset (though it is fully compatible with it).
- **No Fabrication:** Every metric, prediction, and plot shown in the UI is a direct result of real-time execution on the user's dataset.
- **Professional Polish:** Utilized Streamlit metrics, success banners, spinners, and tabs for a clean, interview-ready presentation.

## Usage
Start the workbench using:
```bash
python -m streamlit run streamlit_app/app.py
```
