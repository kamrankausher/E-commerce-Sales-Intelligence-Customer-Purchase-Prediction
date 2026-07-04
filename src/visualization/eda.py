import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from src.utils.logger import get_logger

logger = get_logger(__name__)

def generate_sql_charts(sql_results: dict, output_dir: str):
    """Generate static charts from SQL results and save them."""
    os.makedirs(output_dir, exist_ok=True)
    logger.info("  Generating Visualizations from SQL Data...")
    
    # 1. Top Categories
    if "top_categories_revenue" in sql_results:
        df = sql_results["top_categories_revenue"]
        plt.figure(figsize=(10, 6))
        sns.barplot(data=df, x="total_revenue", y="category", palette="viridis")
        plt.title("Top 10 Categories by Revenue")
        plt.xlabel("Total Revenue (BRL)")
        plt.ylabel("Category")
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, "top_categories_revenue.png"))
        plt.close()
        
    # 2. Monthly Revenue
    if "monthly_revenue" in sql_results:
        df = sql_results["monthly_revenue"]
        plt.figure(figsize=(12, 5))
        sns.lineplot(data=df, x="month", y="total_revenue", marker="o", color="blue")
        plt.title("Monthly Revenue Trend")
        plt.xlabel("Month")
        plt.ylabel("Revenue (BRL)")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, "monthly_revenue.png"))
        plt.close()
        
    # 3. Revenue by State
    if "revenue_by_state" in sql_results:
        df = sql_results["revenue_by_state"]
        plt.figure(figsize=(10, 6))
        sns.barplot(data=df, x="total_revenue", y="state", palette="magma")
        plt.title("Top 10 States by Revenue")
        plt.xlabel("Total Revenue (BRL)")
        plt.ylabel("State")
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, "revenue_by_state.png"))
        plt.close()

def generate_business_insights(sql_results: dict) -> dict:
    """Automated Business Insight Generation based on raw data dynamically."""
    insights = {}
    
    if "top_categories_revenue" in sql_results:
        df = sql_results["top_categories_revenue"]
        top_cat = df.iloc[0]['category']
        top_rev = df.iloc[0]['total_revenue']
        insights["top_categories_revenue"] = {
            "Observation": f"The '{top_cat}' category generates the highest revenue at R$ {top_rev:,.2f}.",
            "Business Impact": "Revenue is heavily concentrated in this category, representing a strong market fit but also a vulnerability if demand shifts.",
            "Recommendation": f"Capitalize on '{top_cat}' with premium cross-selling, while simultaneously diversifying marketing efforts to underperforming categories."
        }
        
    if "monthly_revenue" in sql_results:
        df = sql_results["monthly_revenue"]
        best_month = df.loc[df['total_revenue'].idxmax(), 'month']
        insights["monthly_revenue"] = {
            "Observation": f"Revenue peaked during {best_month}.",
            "Business Impact": "Seasonality plays a significant role in customer purchasing behavior, likely tied to promotional events like Black Friday or holidays.",
            "Recommendation": "Allocate higher marketing budgets 30 days prior to the peak month to maximize customer acquisition during high-intent periods."
        }
        
    if "average_order_value" in sql_results:
        df = sql_results["average_order_value"]
        aov = df.iloc[0]['average_order_value']
        insights["average_order_value"] = {
            "Observation": f"The Average Order Value (AOV) across all delivered orders is R$ {aov:,.2f}.",
            "Business Impact": "AOV indicates the baseline profitability per transaction before operational costs.",
            "Recommendation": f"Introduce free-shipping thresholds at R$ {aov * 1.2:,.0f} to incentivize customers to add more items to their cart."
        }
        
    return insights
