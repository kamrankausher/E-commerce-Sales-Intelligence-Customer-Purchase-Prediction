import os
from src.utils.logger import get_logger

logger = get_logger(__name__)

def generate_eda_report(sql_results: dict, insights: dict, output_path: str):
    """Compile all EDA findings and business insights into a single Markdown report."""
    logger.info(f"  Generating final EDA Report at {output_path}...")
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    lines = [
        "# Phase 4: Exploratory Data Analysis & Business Insights\n",
        "## 1. Automated Business Insights from SQL Analytics\n"
    ]
    
    # Add Insights
    for query_name, insight in insights.items():
        lines.append(f"### {query_name.replace('_', ' ').title()}")
        lines.append(f"**Observation:** {insight['Observation']}")
        lines.append(f"**Business Impact:** {insight['Business Impact']}")
        lines.append(f"**Recommendation:** {insight['Recommendation']}\n")
        
    # Add Data frames
    lines.append("## 2. SQL Query Results\n")
    for query_name, df in sql_results.items():
        lines.append(f"### {query_name}.sql")
        
        # Build markdown table manually to avoid 'tabulate' dependency
        if not df.empty:
            header = "| " + " | ".join(df.columns) + " |"
            sep = "|" + "|".join(["---"] * len(df.columns)) + "|"
            lines.append(header)
            lines.append(sep)
            
            for _, row in df.head(10).iterrows():
                row_str = " | ".join([str(val) for val in row.values])
                lines.append(f"| {row_str} |")
        lines.append("\n")
        
    lines.append("## 3. Visualization Artifacts\n")
    lines.append("Static visualizations have been saved to `reports/images/`.\n")
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
        
    logger.info("  [OK] EDA Report successfully generated.")
