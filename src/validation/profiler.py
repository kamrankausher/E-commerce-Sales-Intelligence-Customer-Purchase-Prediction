import os
import pandas as pd
from src.utils.logger import get_logger
import config

logger = get_logger(__name__)

def generate_data_profile(df: pd.DataFrame, report_name: str = "dataset_profile.md"):
    """
    Automatically generate a data profile containing schema, missing values, 
    and descriptive statistics.
    
    Why: Instead of using heavy libraries like ydata-profiling (which can crash 
    on large datasets and take a long time), a manual profiling script gives 
    total control and demonstrates a solid understanding of basic EDA in 
    interviews.
    """
    logger.info("  Generating Data Profile...")
    
    os.makedirs(config.REPORTS_DIR, exist_ok=True)
    report_path = os.path.join(config.REPORTS_DIR, report_name)
    
    lines = [f"# Dataset Profile: {report_name}\n"]
    
    # 1. Shape
    lines.append("## 1. Dataset Shape")
    lines.append(f"- **Rows:** {df.shape[0]:,}")
    lines.append(f"- **Columns:** {df.shape[1]:,}\n")
    
    # 2. Data Types & Missing Values
    lines.append("## 2. Column Summary & Missing Values")
    lines.append("| Column | Type | Missing Count | Missing % |")
    lines.append("|---|---|---|---|")
    
    missing = df.isnull().sum()
    for col in df.columns:
        dtype = str(df[col].dtype)
        miss_count = missing[col]
        miss_pct = (miss_count / len(df)) * 100
        lines.append(f"| {col} | `{dtype}` | {miss_count:,} | {miss_pct:.2f}% |")
        
    lines.append("\n## 3. Numeric Summary")
    numeric_df = df.select_dtypes(include='number')
    if not numeric_df.empty:
        desc = numeric_df.describe().T
        
        # Build markdown table manually to avoid 'tabulate' dependency
        header = "| Column | " + " | ".join(desc.columns) + " |"
        sep = "|---|" + "|".join(["---"] * len(desc.columns)) + "|"
        lines.append(header)
        lines.append(sep)
        
        for idx, row in desc.iterrows():
            row_str = " | ".join([f"{val:.4f}" for val in row.values])
            lines.append(f"| {idx} | {row_str} |")
    else:
        lines.append("No numeric columns found.")
        
    # Write to file
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
        
    logger.info(f"  [OK] Data profile saved to {report_path}")
