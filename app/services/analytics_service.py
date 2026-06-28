import os
import logging
from typing import List, Dict, Any
from app.database.connection import run_query
from config import SQL_DIR

logger = logging.getLogger(__name__)

class AnalyticsService:
    @staticmethod
    def parse_sql_file(filepath: str) -> List[str]:
        """Parses a SQL file containing multiple queries separated by semicolons."""
        if not os.path.exists(filepath):
            logger.warning(f"SQL file not found at {filepath}")
            return []
        with open(filepath, 'r', encoding='utf-8') as f:
            sql = f.read()
        
        # Split by semicolon and remove empty queries
        queries = [q.strip() + ";" for q in sql.split(';') if q.strip()]
        return queries

    @classmethod
    def get_query(cls, index: int) -> str:
        """Fetch a specific query by its 0-based index."""
        queries = cls.parse_sql_file(os.path.join(SQL_DIR, "analytics_queries.sql"))
        if not queries or index >= len(queries):
            raise ValueError(f"SQL query at index {index} not found.")
        return queries[index]

    @classmethod
    def execute_analytics_query(cls, index: int) -> List[Dict[str, Any]]:
        """Executes the analytics query at the given index."""
        query = cls.get_query(index)
        
        # If it's RFM segmentation (index 8), we aggregate it to avoid a huge payload
        if index == 8:
            base_query = query.rstrip(";")
            query = f"WITH rfm_data AS ({base_query}) SELECT segment, COUNT(*) as customer_count FROM rfm_data GROUP BY segment ORDER BY customer_count DESC;"
            
        return run_query(query)
