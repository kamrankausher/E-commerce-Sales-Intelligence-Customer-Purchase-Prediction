"""Unit tests for the SQLite connection and query utilities."""
import os
import sqlite3
import pandas as pd
import pytest
from src.utils.database import get_connection, run_query, execute_sql, load_df_to_table
from config import DATABASE_PATH

def test_get_connection():
    conn = get_connection()
    assert isinstance(conn, sqlite3.Connection)
    conn.close()

def test_execute_sql_and_run_query():
    # Create a temp table
    execute_sql("CREATE TABLE IF NOT EXISTS test_table (id INTEGER PRIMARY KEY, name TEXT)")
    execute_sql("INSERT INTO test_table (name) VALUES (?)", ("Alice",))
    
    # Query it
    df = run_query("SELECT * FROM test_table")
    assert isinstance(df, pd.DataFrame)
    assert len(df) >= 1
    assert df.iloc[-1]["name"] == "Alice"
    
    # Clean up
    execute_sql("DROP TABLE test_table")

def test_load_df_to_table():
    df = pd.DataFrame([{"col1": 1, "col2": "A"}, {"col1": 2, "col2": "B"}])
    load_df_to_table(df, "test_load_table", if_exists="replace")
    
    # Verify loaded data
    df_loaded = run_query("SELECT * FROM test_load_table")
    assert len(df_loaded) == 2
    assert df_loaded.iloc[0]["col2"] == "A"
    
    # Clean up
    execute_sql("DROP TABLE test_load_table")
