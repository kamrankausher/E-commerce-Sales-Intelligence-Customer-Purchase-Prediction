# E-Commerce Growth Intelligence & Churn Prediction Platform

![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Scikit-Learn](https://img.shields.io/badge/scikit--learn-%23F7931E.svg?style=for-the-badge&logo=scikit-learn&logoColor=white)
![DuckDB](https://img.shields.io/badge/DuckDB-FFF000?style=for-the-badge&logo=duckdb&logoColor=black)

An end-to-end Data Science and Machine Learning platform designed to identify high-risk e-commerce customers, explain the drivers behind customer churn, and provide actionable business intelligence.

This repository features a fully interactive **Machine Learning Workbench** deployed on Streamlit.

---

## 🚀 Live Application
Launch the interactive Streamlit Workbench locally:
```bash
python -m streamlit run streamlit_app/app.py
```


---

## 📖 Project Overview

Customer churn is one of the most expensive problems in e-commerce. It costs 5x more to acquire a new customer than to retain an existing one. This project solves that problem by building a **Machine Learning Pipeline** capable of ingesting raw transactional data, generating predictive features (RFM metrics), and deploying models that accurately predict which customers will stop purchasing.

### Key Features
1. **Interactive ML Workbench:** Upload any generic tabular dataset. The platform will auto-profile the data, visualize it, and train models dynamically.
2. **Automated ML Pipeline:** Includes auto-detection for Classification/Regression, dynamic imputation, scaling, and hyperparameter tuning.
3. **In-Browser SQL Analytics:** Integrated with **DuckDB** to allow live SQL querying of your datasets directly in the dashboard.
4. **Explainable AI (XAI):** Utilizes **SHAP** and **Permutation Importance** to explain *why* a customer is churning in plain English.
5. **Data Leakage Prevention:** Built heavily on `sklearn.pipeline.Pipeline` and `ColumnTransformer` to guarantee zero data leakage during evaluation.

---

## 🛠️ Architecture & Tech Stack

- **Data Validation:** `pandera`
- **Data Engineering:** `pandas`, `duckdb`
- **Machine Learning:** `scikit-learn`, `xgboost`, `lightgbm`
- **Explainability:** `shap`
- **Visualization:** `plotly`, `seaborn`, `matplotlib`
- **Deployment:** `streamlit`, `docker`

---

## 📁 Repository Structure

```text
├── Dockerfile                  # Containerization for cloud deployment
├── README.md                   # Project documentation
├── requirements.txt            # Python dependencies
├── run_pipeline.py             # CLI backend execution script
├── data/                       # (Ignored) Raw and processed datasets
├── models/                     # (Ignored) Serialized ML models (.pkl)
├── reports/                    # Auto-generated markdown reports and SHAP plots
├── src/                        # Core Python Modules
│   ├── analytics/              # DuckDB SQL execution
│   ├── data/                   # Data validation and loading
│   ├── evaluation/             # Leaderboards and Explainability
│   ├── features/               # RFM engineering and feature extraction
│   ├── models/                 # Model training and hyperparameter tuning
│   └── preprocessing/          # Dynamic scikit-learn ColumnTransformers
└── streamlit_app/              # Interactive UI application
```

---

## ⚙️ Quick Start (Local Setup)

**1. Clone the repository**
```bash
git clone https://github.com/kamrankausher/E-commerce-Sales-Intelligence-Customer-Purchase-Prediction.git
cd E-commerce-Sales-Intelligence-Customer-Purchase-Prediction
```

**2. Install Dependencies**
```bash
pip install -r requirements.txt
```

**3. Run the Backend Pipeline (Optional)**
If you want to train the models locally via CLI and generate the Markdown reports:
```bash
python run_pipeline.py
```

**4. Launch the Streamlit App**
```bash
python -m streamlit run streamlit_app/app.py
```

---

## 📊 Business Insights

Through our Exploratory Data Analysis and ML Explainability, we identified several critical business drivers:
- **Delivery Experience is Crucial:** Late deliveries exponentially increase the likelihood of customer churn.
- **The First 60 Days:** The probability of a repeat purchase drops significantly if the customer has not returned within 60 days.
- **Actionable Retention:** By integrating these predictions into CRM tools, automated marketing campaigns can target high-risk customers *before* they officially churn.

---

## 🧑‍💻 Author

Built as a demonstration of professional Data Science and MLOps practices for Entry-Level Data Scientist and Machine Learning Engineer roles. 
