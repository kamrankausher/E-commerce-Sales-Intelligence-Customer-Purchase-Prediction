import os
import sqlite3
import logging
from typing import List, Dict, Any, Tuple, Optional
from config import DATABASE_PATH

logger = logging.getLogger(__name__)

def get_connection() -> sqlite3.Connection:
    """Create and return a new SQLite connection."""
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

def run_query(query: str, params: Optional[Tuple] = None) -> List[Dict[str, Any]]:
    """
    Execute a SQL query and return results as a list of dictionaries.
    
    Args:
        query (str): The SQL query to execute.
        params (tuple, optional): Parameters for the query. Defaults to None.
        
    Returns:
        List[Dict[str, Any]]: The results of the query.
    """
    conn = get_connection()
    try:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Database query failed: {e}")
        raise
    finally:
        conn.close()
