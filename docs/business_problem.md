# Business Problem Statement

## Context

An e-commerce company operating in Brazil wants to **reduce customer churn** and **increase repeat purchase rates**. The company has transactional data covering customers, orders, products, payments, reviews, and delivery information across all 27 Brazilian states over a 2-year period.

## The Problem

The company's **repeat purchase rate is only ~15%** — meaning 85% of customers make a single purchase and never return. The company has no systematic way to:

1. **Identify** which customers are likely to churn
2. **Understand** why customers stop buying
3. **Prioritize** which customers to target with retention campaigns
4. **Measure** the revenue impact of customer churn

## The Solution

Build an end-to-end data science pipeline that:

1. **Analyzes** historical e-commerce data to understand customer behavior
2. **Predicts** which customers are at risk of churning using machine learning
3. **Identifies** the key drivers of churn (feature importance)
4. **Recommends** data-driven retention strategies
5. **Deploys** an interactive dashboard for business stakeholders

## Churn Definition

> A customer is considered **"churned"** if they have not made a purchase in the **last 90 days** relative to the most recent date in the dataset.

This 90-day threshold is an industry standard for e-commerce platforms. It balances between:
- Too short (30 days): Would flag seasonal buyers as churned
- Too long (180 days): Would miss early intervention opportunities

## Success Metrics

| Metric | Target | Why |
|--------|--------|-----|
| ROC-AUC | > 0.80 | Model should rank churners higher than active customers |
| Recall | > 0.70 | We should catch at least 70% of actual churners |
| Precision | > 0.60 | At least 60% of predicted churners should be real churners |
| Business Impact | Quantified | Revenue at risk from high-probability churners |

## Stakeholders

- **Marketing Team**: Needs customer segments for targeted campaigns
- **Operations Team**: Needs delivery performance insights
- **Product Team**: Needs review analysis for product improvement
- **Management**: Needs KPI dashboard and revenue impact analysis

## Constraints

- Budget-friendly: Use open-source tools only (Python, scikit-learn, Streamlit)
- Interpretable: Business stakeholders need to understand why a customer is flagged
- Actionable: Every insight must map to a concrete business action
