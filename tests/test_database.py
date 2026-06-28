import os
import sqlite3
import pytest
from app.database import get_connection, run_query, parse_sql_file
from config import SQL_DIR

def test_get_connection():
    """Test that get_connection returns a valid SQLite connection."""
    conn = get_connection()
    assert isinstance(conn, sqlite3.Connection)
    conn.close()

def test_run_query_success():
    """Test executing a simple SQL query."""
    res = run_query("SELECT 1 AS test_val")
    assert len(res) == 1
    assert res[0]["test_val"] == 1

def test_run_query_failure():
    """Test executing an invalid SQL query raises an exception."""
    with pytest.raises(Exception):
        run_query("SELECT * FROM non_existent_table_xyz123")

def test_parse_sql_file_exists():
    """Test parsing the main analytics SQL file."""
    filepath = os.path.join(SQL_DIR, "analytics_queries.sql")
    queries = parse_sql_file(filepath)
    assert len(queries) == 12
    # Ensure they look like queries
    assert "SELECT" in queries[0].upper()

def test_parse_sql_file_not_found():
    """Test parsing a non-existent file returns empty list."""
    queries = parse_sql_file("fake_path_does_not_exist.sql")
    assert queries == []
