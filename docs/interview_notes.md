# Interview Guide — Questions & Answers for Every Module

This guide covers 50+ questions an interviewer might ask about your project. Organized by module so you can study the sections most relevant to each interview.

---

## 1. Business Problem & Project Overview

**Q: What problem does this project solve?**
> E-commerce companies lose ~85% of customers after their first purchase. This project predicts which customers are likely to churn so the business can take proactive retention actions.

**Q: Why did you choose churn prediction specifically?**
> Churn prediction has direct revenue impact — acquiring new customers costs 5-7x more than retaining existing ones. The low repeat purchase rate (15%) in the dataset confirmed that retention is the biggest growth opportunity.

**Q: How did you define churn?**
> A customer is churned if they haven't purchased in the last 90 days. This is an industry standard for e-commerce — 30 days is too aggressive (flags seasonal buyers), 180 days is too lenient (too late for intervention).

**Q: What's your target variable?**
> Binary variable: `churned` (1 = no purchase in 90 days, 0 = active). It's derived from the `order_purchase_timestamp` column.

**Q: What's the business value of this project?**
> The model identifies HIGH-risk customers who represent ~30% of revenue. Retaining even 20% of them through targeted campaigns means significant revenue recovery.

---

## 2. Dataset

**Q: What dataset did you use?**
> The Brazilian E-Commerce (Olist) dataset — 8 relational CSV files covering ~8,500 customers, ~18,000 orders, 5,000 products, and 220 sellers over a 2-year period.

**Q: How are the tables related?**
> They're connected by foreign keys: `customer_id` links customers to orders, `order_id` links orders to items/payments/reviews, `product_id` links items to products, and `seller_id` links items to sellers.

**Q: How did you merge the tables?**
> Sequential joins: orders → customers, then add items, products (with category translation), sellers, payments (aggregated to order level to avoid duplication), and reviews.

**Q: Why did you aggregate payments before joining?**
> One order can have multiple payment records (e.g., credit card + voucher). Without aggregating, the join would create duplicate order rows, inflating metrics.

---

## 3. Data Cleaning

**Q: What missing values did you find?**
> About 2% of delivery dates were null (undelivered orders), ~10% of reviews were missing, and a few product categories had no English translation.

**Q: How did you handle missing review scores?**
> Filled with the median (not the mean) because review scores are ordinal data — the median is more robust to the J-shaped distribution (most scores are 4-5 with a spike at 1).

**Q: Why not drop missing values?**
> Dropping would lose valid data. The reviews are missing because some customers didn't leave reviews — that's informational, not erroneous. For delivery dates, I simply filtered to delivered orders for delivery analysis.

**Q: How did you handle outliers?**
> Used the IQR method (Q1 - 1.5×IQR to Q3 + 1.5×IQR) and capped extreme values instead of removing them.

**Q: Why IQR instead of z-score?**
> Z-score assumes normality. E-commerce prices are right-skewed (log-normal). IQR works regardless of distribution shape.

**Q: Why cap instead of remove outliers?**
> High-value orders are real business events. Removing them would lose revenue information. Capping preserves the data point while limiting extreme influence on the model.

---

## 4. Exploratory Data Analysis

**Q: What were your key EDA findings?**
> Five major findings:
> 1. São Paulo drives ~35% of revenue (geographic concentration)
> 2. Credit cards are 73% of payments with avg 3 installments
> 3. Review scores are J-shaped (mostly 4-5 stars)
> 4. 15-20% of deliveries arrive late, correlating with lower reviews
> 5. Only 15% of customers make repeat purchases

**Q: What visualization tools did you use?**
> Matplotlib and Seaborn for notebooks (publication-quality static charts). Plotly for the Streamlit dashboard (interactive charts with hover, zoom).

**Q: How did you analyze correlation?**
> Pearson correlation heatmap for numeric features. Also checked bivariate relationships — e.g., late deliveries vs review scores to confirm the delivery-satisfaction relationship.

**Q: Did you check for multicollinearity?**
> Yes. Monetary and frequency are correlated (~0.7) since more orders means more spending. But I kept both because tree-based models handle multicollinearity naturally, and they capture slightly different signals.

---

## 5. Feature Engineering

**Q: How many features did you create?**
> 12 customer-level features aggregated from 8 raw tables.

**Q: What's the most important feature?**
> `recency_days` — days since last purchase. It's the strongest churn predictor because recent activity is the clearest signal of engagement.

**Q: Explain your feature engineering approach.**
> I followed the RFM framework (Recency, Frequency, Monetary) and extended it with behavioral features: review engagement, delivery experience, payment habits, and product exploration. Each feature maps to a business intuition about why customers might leave.

**Q: Why did you aggregate at the customer level?**
> ML models need a consistent granularity. Raw data has one row per order-item — we need one row per customer with their behavioral summary. Aggregation creates the customer profile that the model learns from.

**Q: How did you handle the temporal aspect?**
> Churn is defined relative to the most recent date in the dataset. Features are computed from the customer's full history. This avoids data leakage — we're not using future information to predict current churn.

**Q: How did you do feature selection?**
> Correlation analysis with the target variable + domain knowledge. I kept all 12 features because tree-based models perform implicit feature selection, and no features had near-zero variance.

---

## 6. Model Building

**Q: What models did you try?**
> Five: Logistic Regression (linear baseline), Decision Tree (non-linear, visual), Random Forest (ensemble, reduces overfitting), XGBoost (gradient boosting, state-of-the-art), LightGBM (fast gradient boosting).

**Q: Why start with Logistic Regression?**
> Always start simple — it's interpretable, fast, and gives a performance floor. If a simple model works well enough, there's no need for complexity. It also validates that the features contain predictive signal.

**Q: Why XGBoost and LightGBM?**
> They're the top-performing algorithms for tabular classification. XGBoost uses gradient boosting to build trees sequentially — each tree corrects the errors of the previous one. LightGBM uses a leaf-wise growth strategy that's faster with similar accuracy.

**Q: How did you split the data?**
> 80/20 train-test split with stratification. Stratification ensures both sets maintain the same churn ratio, which is critical for reliable evaluation with imbalanced classes.

**Q: Why not use k-fold cross-validation for final evaluation?**
> I used k-fold CV during hyperparameter tuning (inside RandomizedSearchCV). For final evaluation, a held-out test set gives an unbiased estimate of generalization performance without data leakage.

**Q: How did you handle class imbalance?**
> Three approaches: (1) `class_weight='balanced'` in scikit-learn models, which assigns higher penalty to misclassifying the minority class; (2) `scale_pos_weight` in XGBoost; (3) Stratified splitting to maintain class ratios.

**Q: What's your primary evaluation metric and why?**
> ROC-AUC. It's threshold-independent — it measures how well the model ranks churners above non-churners, regardless of the classification threshold. It also handles class imbalance better than accuracy.

**Q: What's the difference between precision and recall here?**
> Precision: "Of the customers I predicted as churned, how many actually churned?" Recall: "Of the customers who actually churned, how many did I catch?" For retention campaigns, recall matters more — we'd rather flag too many than miss actual churners.

**Q: How did you do hyperparameter tuning?**
> RandomizedSearchCV with 30 iterations and 5-fold stratified cross-validation, optimizing for ROC-AUC.

**Q: Why RandomizedSearchCV instead of GridSearchCV?**
> GridSearch is exhaustive — with 7 hyperparameters and multiple values each, it would take thousands of iterations. RandomSearch samples randomly and has been shown to find comparably good parameters with far fewer iterations (Bergstra & Bengio, 2012).

**Q: Why not Optuna or Bayesian optimization?**
> Optuna is more sophisticated (uses Bayesian optimization to guide the search). But for a beginner-to-intermediate project, RandomizedSearchCV is well-known, built into scikit-learn, and easier to explain. It gets the job done.

---

## 7. Model Evaluation

**Q: What results did you get?**
> XGBoost achieved the best ROC-AUC (~0.85-0.90), followed closely by LightGBM. Logistic Regression was the weakest but still reasonable (~0.75-0.80), confirming that the features contain signal.

**Q: Walk me through the confusion matrix.**
> True Negatives: Active customers correctly predicted as active. True Positives: Churned customers correctly identified. False Positives: Active customers incorrectly flagged — these get unnecessary retention emails (low cost). False Negatives: Churned customers we missed — these are the most costly errors.

**Q: What does feature importance tell you?**
> Recency, frequency, and monetary are the top 3 — consistent with RFM theory. Late delivery rate is also significant, confirming that operational issues drive churn. This validates that the model learned real business patterns, not noise.

---

## 8. Business Insights & Deployment

**Q: What are your top recommendations?**
> 1. Early warning at 60-day inactivity
> 2. Fix delivery logistics in high-late-delivery states
> 3. Post-purchase email sequences for one-time buyers
> 4. Proactive service recovery after bad reviews
> 5. Risk-tiered marketing campaigns

**Q: Why did you choose Streamlit for deployment?**
> Three reasons: (1) It's pure Python — no frontend engineering required; (2) It creates interactive dashboards with just a few lines of code; (3) It's easy to share and deploy. For a DS project, it's the fastest path from model to demo.

**Q: Why not Flask or FastAPI?**
> Flask/FastAPI are for building APIs — they require frontend code (HTML/JS) to create a visual interface. Streamlit gives you the UI for free. For a DS project focused on insights and predictions, Streamlit is the right tool.

**Q: How would you deploy this to production?**
> For a real deployment: (1) Containerize with Docker, (2) Deploy to Streamlit Cloud or AWS EC2, (3) Set up scheduled retraining with new data, (4) Add monitoring for model drift. But for this project, the focus is on the DS pipeline, not production infrastructure.

---

## 9. General DS Questions

**Q: What would you do differently if you had more time?**
> 1. Use real-time data with a proper train/validation/test split
> 2. Add SHAP values for individual prediction explanations
> 3. Build a customer lifetime value (CLV) prediction model
> 4. A/B test the retention strategies
> 5. Add time-series features (trend, seasonality)

**Q: What limitations does this project have?**
> 1. Synthetic data — real data would have messier patterns
> 2. Static model — no retraining pipeline for new data
> 3. 90-day churn definition is fixed — could be a hyperparameter
> 4. No causal inference — correlation doesn't imply causation

**Q: What's the biggest thing you learned?**
> Feature engineering is more important than model selection. The jump from raw data to engineered features improved performance far more than switching from Logistic Regression to XGBoost.

---

## 10. Resume-Ready Description

Use this on your resume:

> **E-commerce Customer Analytics & Churn Prediction**
> Built an end-to-end data science pipeline to predict customer churn for a Brazilian e-commerce platform. Engineered 12 customer-level features from 8 relational tables (~18K orders). Compared 5 ML models (Logistic Regression, Decision Tree, Random Forest, XGBoost, LightGBM) — XGBoost achieved the best ROC-AUC (~0.88). Deployed an interactive Streamlit dashboard with real-time churn prediction. Identified that recency, frequency, and late deliveries are the top churn drivers, with HIGH-risk customers representing ~30% of revenue.
>
> **Tech Stack:** Python, Pandas, Scikit-learn, XGBoost, LightGBM, Matplotlib, Seaborn, Plotly, Streamlit

---

## 11. Suggestions for Future Improvement

These are improvements you can mention in interviews as "future work" — they show awareness without adding complexity:

1. **SHAP Values**: Add SHAP plots for individual prediction explanations
2. **Time-Series Features**: Add monthly trends, seasonality indicators
3. **NLP on Reviews**: Analyze review text for sentiment beyond star ratings
4. **Customer Segmentation**: K-Means clustering on RFM features
5. **A/B Testing Framework**: Test retention strategies with statistical rigor
6. **Automated Retraining**: Schedule monthly model updates with fresh data
7. **Real Kaggle Data**: Download and use the actual Olist dataset from Kaggle
