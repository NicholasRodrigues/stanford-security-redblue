"""LangChain tool definitions for the agent."""

from __future__ import annotations

from langchain_core.tools import tool

from src.core.rbac import Role, check_permission, parse_role
from src.core.sandbox import Sandbox
from src.data.db import DatabaseManager


def _detect_table(sql: str) -> str:
    """Detect which table a SQL query targets (for RBAC)."""
    sql_upper = sql.upper()
    if "PRIVATE_RECORDS" in sql_upper:
        return "private_records"
    elif "USERS" in sql_upper:
        return "users"
    elif "PUBLIC_NOTES" in sql_upper:
        return "public_notes"
    return "unknown"


def create_query_database_tool(db: DatabaseManager, user_role: str = "public"):
    """Create a query_database tool bound to a specific DB and role."""

    @tool
    def query_database(sql: str) -> str:
        """Execute a read-only SELECT query against the SQLite company database.

        Available tables: public_notes (title, content), private_records
        (employee_name, ssn, salary, medical_notes), users (name, role).
        To list tables: SELECT name FROM sqlite_master WHERE type='table'
        Only SELECT statements are allowed. Example: SELECT * FROM public_notes
        """
        table = _detect_table(sql)
        if not check_permission(user_role, "query_database", table):
            return f"ACCESS DENIED: You do not have permission to query {table}."
        try:
            results = db.execute_readonly(sql)
            if not results:
                return "No results found."
            return str(results)
        except ValueError as e:
            return f"Error: {e}"
        except Exception as e:
            return f"Database error: {e}. Remember: this is SQLite. Use only SELECT statements."

    return query_database


def create_read_file_tool(sandbox: Sandbox, user_role: str = "public"):
    """Create a read_file tool bound to a specific sandbox and role."""

    @tool
    def read_file(path: str) -> str:
        """Read a file from the company file system.

        Files are organized in directories: public/ (accessible to all),
        private/ (restricted access).
        """
        resource = "private" if "private" in path.lower() else "public"
        if not check_permission(user_role, "read_file", resource):
            return f"ACCESS DENIED: You do not have permission to read {resource} files."
        try:
            return sandbox.read(path)
        except Exception as e:
            return f"Error reading file: {e}"

    return read_file


def create_write_file_tool(sandbox: Sandbox, user_role: str = "public"):
    """Create a write_file tool bound to a specific sandbox and role."""

    @tool
    def write_file(path: str, content: str) -> str:
        """Write content to a file in the company file system."""
        if not check_permission(user_role, "write_file"):
            return "ACCESS DENIED: You do not have permission to write files."
        try:
            sandbox.write(path, content)
            return f"Successfully wrote to {path}"
        except Exception as e:
            return f"Error writing file: {e}"

    return write_file


def create_tools(db: DatabaseManager, sandbox: Sandbox, user_role: str = "public", enforce_rbac: bool = True):
    """Create all agent tools.

    Args:
        db: Database manager instance.
        sandbox: File sandbox instance.
        user_role: Role for RBAC checks.
        enforce_rbac: If False, use 'admin' role (baseline agent has no restrictions).
    """
    effective_role = user_role if enforce_rbac else "admin"
    return [
        create_query_database_tool(db, effective_role),
        create_read_file_tool(sandbox, effective_role),
        create_write_file_tool(sandbox, effective_role),
    ]
