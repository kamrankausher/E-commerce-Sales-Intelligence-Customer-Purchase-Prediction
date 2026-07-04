import os
import duckdb
import pandas as pd
from src.utils.logger import get_logger

logger = get_logger(__name__)

def run_sql_file(conn: duckdb.DuckDBPyConnection, sql_file_path: str) -> pd.DataFrame:
    """Read a SQL file and execute it in DuckDB, returning a DataFrame."""
    with open(sql_file_path, "r", encoding="utf-8") as f:
        query = f.read()
    return conn.execute(query).df()

def execute_all_business_queries(dfs: dict) -> dict:
    """
    Load raw DataFrames into DuckDB and execute all SQL analytics queries.
    Returns a dictionary of DataFrames containing the results.
    """
    logger.info("  Executing Business SQL Analytics...")
    conn = duckdb.connect(database=':memory:')
    
    # Load all tables into DuckDB
    # We rename 'category_translation' to match the SQL query exactly
    for name, df in dfs.items():
        table_name = name
        # Register the dataframe as a view in duckdb
        conn.register(table_name, df)
        
    results = {}
    sql_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "sql")
    
    if not os.path.exists(sql_dir):
        logger.warning(f"  SQL directory not found at {sql_dir}")
        return results
        
    for file in os.listdir(sql_dir):
        if file.endswith(".sql"):
            query_name = file.replace(".sql", "")
            file_path = os.path.join(sql_dir, file)
            try:
                res_df = run_sql_file(conn, file_path)
                results[query_name] = res_df
                logger.info(f"    [OK] Executed {file}")
            except Exception as e:
                logger.error(f"    [ERROR] Failed to execute {file}: {e}")
                
    conn.close()
    return results
