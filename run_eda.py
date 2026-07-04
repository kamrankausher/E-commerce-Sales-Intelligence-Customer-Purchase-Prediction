import os
import time
import logging
import warnings
from src.utils.logger import get_logger
import config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = get_logger(__name__)
warnings.filterwarnings('ignore')

from src.data.loader import load_all
from src.analytics.queries import execute_all_business_queries
from src.visualization.eda import generate_sql_charts, generate_business_insights
from src.analytics.reporter import generate_eda_report

def main():
    logger.info("=== Starting Phase 4: Exploratory Data Analysis & SQL ===")
    
    # 1. Load raw data for SQL queries
    t0 = time.time()
    dfs = load_all()
    logger.info(f"Loaded raw tables in {time.time()-t0:.2f}s")
    
    # 2. Execute SQL Queries
    sql_results = execute_all_business_queries(dfs)
    
    if not sql_results:
        logger.error("No SQL results generated. Check sql/ directory.")
        return
        
    # 3. Generate Charts
    images_dir = os.path.join(config.REPORTS_DIR, "images")
    generate_sql_charts(sql_results, images_dir)
    
    # 4. Automated Insights
    insights = generate_business_insights(sql_results)
    
    # 5. Export Report
    report_path = os.path.join(config.REPORTS_DIR, "Phase4_EDA_Report.md")
    generate_eda_report(sql_results, insights, report_path)
    
    logger.info("=== Phase 4 Complete ===")

if __name__ == "__main__":
    main()
