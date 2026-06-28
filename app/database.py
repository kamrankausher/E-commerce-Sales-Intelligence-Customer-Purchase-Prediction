import os
import sqlite3
import pandas as pd
from config import DATABASE_PATH

def get_connection():
    """Create a new SQLite connection."""
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

def run_query(query: str, params: tuple = None) -> list:
    """
    Execute a SQL query and return results as a list of dictionaries.
    """
    conn = get_connection()
    try:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"Query failed: {e}")
        raise
    finally:
        conn.close()

def parse_sql_file(filepath: str) -> list:
    """Parses a SQL file containing multiple queries separated by semicolons."""
    if not os.path.exists(filepath):
        return []
    with open(filepath, 'r', encoding='utf-8') as f:
        sql = f.read()
    
    # Split by semicolon and remove empty queries
    queries = [q.strip() + ";" for q in sql.split(';') if q.strip()]
    return queries
