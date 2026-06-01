import sqlite3
import re #Regular Expressions library. Used to pattern-match text and query validation(for security checks)
import os
from typing import Any

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "movies.db")

_FORBIDDEN = re.compile( #Creates a compiled regex pattern and stores it in _FORBIDDEN
    r"\b(DROP|DELETE|UPDATE|INSERT|ALTER|CREATE|REPLACE|TRUNCATE)\b", #SQL keywords as whole words
    re.IGNORECASE, #case-insensitive
)

class SQLExecutionError(Exception): # Base error class for DB-related issues
    pass

class ForbiddenQueryError(SQLExecutionError): # Specific error when query is unsafe
    pass

def _validate(sql: str) -> None: #Function that checks if the SQL query is safe before execution
    if _FORBIDDEN.search(sql): #Uses regex pattern to check if query contains dangerous keywords (DROP, DELETE, etc.)
        raise ForbiddenQueryError("Only SELECT queries are allowed.")
    if not sql.strip().upper().startswith("SELECT"): #Ensures query starts with SELECT and removes spaces and ignores case
        raise ForbiddenQueryError("Only SELECT queries are allowed.")

def execute_query(sql: str, db_path: str = DB_PATH, max_rows: int = 200):
    _validate(sql)
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(sql)
        raw_rows = cur.fetchmany(max_rows)
        conn.close()
    except sqlite3.Error as exc:
        raise SQLExecutionError(f"Database error: {exc}") from exc

    if not raw_rows:
        return [], []

    columns = list(raw_rows[0].keys())
    rows = [tuple(r) for r in raw_rows]
    return columns, rows
