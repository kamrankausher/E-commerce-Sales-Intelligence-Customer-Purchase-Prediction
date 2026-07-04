# Project Story — 10-15 Minute Interview Walkthrough

Use this script to explain your project naturally in interviews. Read through it, internalize the flow, and practice until you can tell it conversationally without memorizing word-for-word.

---

## Opening (30 seconds)

> "I built an end-to-end customer analytics and churn prediction project for e-commerce. The goal was to analyze customer behavior from a Brazilian e-commerce dataset and predict which customers are likely to stop buying — so the business can take proactive retention actions."

---

## Business Problem (1 minute)

> "The core problem was low repeat purchase rates — only about 15% of customers come back for a second purchase. The business needed to understand: **who is likely to churn, why, and what can we do about it?**"

> "I defined churn as a customer who hasn't purchased in the last 90 days, which is an industry standard for e-commerce."

---

## Dataset (1-2 minutes)

> "I used the Brazilian E-Commerce dataset — it has 8 relational tables covering customers, orders, order items, payments, reviews, products, sellers, and category translations. About 8,500 customers, 18,000 orders, 5,000 products, and 220 sellers."

> "The data is relational — connected by foreign keys like customer_id and order_id. I had to merge all 8 tables into a single analytical DataFrame to work with."

**If asked about the data source:**
> "It's based on real Brazilian e-commerce patterns. The original dataset is from Olist, available on Kaggle."

---

## Data Cleaning (1-2 minutes)

> "I found about 2% of delivery dates were null — those were undelivered orders. I also had about 10% missing review scores. For reviews, I filled with the median because it's ordinal data. For missing delivery dates, I simply filtered to delivered orders only since those are the only ones valid for revenue and delivery analysis."

> "For outliers, I used the **IQR method** on order prices. E-commerce data is naturally right-skewed — most orders are small but a few are very large. Instead of removing them, I **capped** the values to preserve the signal while reducing extreme influence on the models."

**If asked: Why IQR instead of z-score?**
> "Z-score assumes a normal distribution, which e-commerce prices are not — they're right-skewed. IQR is robust to non-normal distributions."

**If asked: Why cap instead of remove?**
> "High-value orders are real business events. Removing them would lose revenue information. Capping preserves the data point while limiting its extreme influence."

---

## EDA (2-3 minutes)

> "My EDA revealed several important patterns:"

> "**Geographically**, São Paulo alone drives about 35% of total revenue. That's a huge concentration."

> "**Payment methods** — credit cards dominate at 73%, and the average number of installments is about 3. This is a Brazilian market pattern where installment purchases are very common."

> "**Reviews** follow a J-shaped distribution — most are 4-5 stars, but the 1-star reviews are the second most common. This means dissatisfied customers feel strongly enough to leave bad reviews."

> "**Delivery performance** — about 15-20% of orders arrive late. And I found a correlation between late deliveries and lower review scores. This directly impacts churn."

> "**Repeat purchases** — only 15% of customers come back. This validated the churn prediction problem."

**If asked: What visualization tool did you use?**
> "Matplotlib and Seaborn for the notebooks — they give publication-quality static charts. Plotly for the Streamlit dashboard — it provides interactive charts."

---

## Feature Engineering (2-3 minutes)

> "This was the most critical step. I engineered **12 customer-level features** from the raw transactional data."

> "The key features were:
> - **Recency** — days since last purchase (strongest churn predictor)
> - **Frequency** — number of orders
> - **Monetary** — total spend
> - **Average order value**
> - **Review scores** — both average and count
> - **Tenure** — days between first and last purchase
> - **Late delivery rate** — proportion of orders that arrived late
> - **Category diversity** — how many product categories they explored"

> "The most important decision was the **churn definition**: a customer who hasn't purchased in 90 days is labeled as churned. This gave us roughly a 60-70% churn rate, which reflects the reality of low repeat purchase behavior in this dataset."

**If asked: Why 90 days?**
> "It's the industry standard for e-commerce. 30 days is too aggressive — it would flag seasonal buyers. 180 days is too lenient — by then it's too late for intervention."

**If asked: Why these specific features?**
> "They map to the RFM framework — Recency, Frequency, Monetary — which is a proven customer segmentation approach. I extended it with behavioral features like review engagement and delivery experience."

---

## Model Building (2-3 minutes)

> "I compared **5 classification models**: Logistic Regression as a baseline, Decision Tree for non-linear patterns, Random Forest as an ensemble method, and XGBoost and LightGBM as gradient boosting methods."

> "I used a **stratified 80/20 train-test split** — stratified because the churn classes were imbalanced, and I needed both training and test sets to maintain the same churn ratio."

> "All models were evaluated on **5 metrics**: Accuracy, Precision, Recall, F1-Score, and ROC-AUC. I chose **ROC-AUC as the primary metric** because it's threshold-independent and handles class imbalance better than accuracy."

> "XGBoost gave the best ROC-AUC, so I selected it and tuned its hyperparameters using **RandomizedSearchCV with 5-fold cross-validation**."

**If asked: Why not GridSearchCV?**
> "GridSearch tests every combination, which is exponentially expensive. RandomSearch samples randomly and research has shown it finds comparably good parameters with fewer iterations."

**If asked: Why not Logistic Regression?**
> "Logistic Regression is a good baseline and I did include it. But tree-based models like XGBoost handle non-linear relationships, feature interactions, and class imbalance better — which are all present in this data."

**If asked: How did you handle class imbalance?**
> "I used class_weight='balanced' for scikit-learn models and scale_pos_weight for XGBoost. I also used stratified splitting and evaluated with metrics that account for imbalance (F1, ROC-AUC) rather than just accuracy."

---

## Model Evaluation (1 minute)

> "The tuned XGBoost model achieved approximately 0.85-0.90 ROC-AUC. The confusion matrix showed high recall for churned customers — we're catching most actual churners, which is what matters for a retention campaign."

> "**Feature importance** confirmed business intuition: recency was the strongest predictor, followed by frequency and monetary value. This is consistent with RFM theory — customers who haven't bought recently, don't buy often, and haven't spent much are the most likely to churn."

---

## Business Insights (1-2 minutes)

> "I translated the model results into 5 actionable recommendations:"

> "First, an **early warning system** — when a customer crosses 60 days without a purchase, trigger a retention email."

> "Second, **fix delivery performance** in states with high late delivery rates — this directly reduces churn."

> "Third, a **first-to-second purchase program** — an automated email sequence to convert one-time buyers."

> "Fourth, **service recovery** — proactively reach out after 1-2 star reviews."

> "And fifth, **risk-tiered marketing** — different strategies for LOW, MEDIUM, and HIGH risk customers."

> "I also quantified the revenue at risk — HIGH-risk customers represent about 30% of total revenue. If we retain just 20% of them through these campaigns, that's a significant revenue save."

---

## Deployment (30 seconds)

> "I deployed the model in a **Streamlit dashboard** with 4 pages: KPI overview, EDA explorer, a churn predictor where you can adjust customer features and get real-time predictions, and a business insights page with recommendations."

> "Streamlit was the right choice because it's pure Python — no frontend engineering required — and it's fast to build and easy to share."

---

## Closing (30 seconds)

> "So in summary — this project covers the full data science lifecycle: problem definition, data understanding, cleaning, EDA, feature engineering, model comparison, evaluation, business insights, and deployment. Every decision — from the churn definition to the model choice to the evaluation metric — has a clear business justification."

---

## Total Time: ~12-15 minutes

Practice this until you can explain it naturally, adjusting depth based on interviewer reactions. If they're technical, go deeper on model comparison. If they're business-focused, emphasize the EDA findings and recommendations.
