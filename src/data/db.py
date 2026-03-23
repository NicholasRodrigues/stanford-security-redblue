"""Database manager for SQLite with in-memory and file-based modes."""

from __future__ import annotations

import sqlite3
from typing import Optional

from src.data.schema import ALL_TABLES
from src.data.seed import get_private_records, get_public_notes, get_users


class DatabaseManager:
    """Manages SQLite database lifecycle: create, seed, query, reset."""

    def __init__(self, path: str = ":memory:"):
        self.path = path
        self.conn: Optional[sqlite3.Connection] = None

    def connect(self) -> sqlite3.Connection:
        if self.conn is None:
            self.conn = sqlite3.connect(self.path)
            self.conn.row_factory = sqlite3.Row
        return self.conn

    def initialize(self) -> None:
        """Create all tables."""
        conn = self.connect()
        for ddl in ALL_TABLES:
            conn.execute(ddl)
        conn.commit()

    def seed(self) -> None:
        """Insert seed data into all tables."""
        conn = self.connect()
        for note in get_public_notes():
            conn.execute(
                "INSERT INTO public_notes (title, content) VALUES (?, ?)",
                (note["title"], note["content"]),
            )
        for record in get_private_records():
            conn.execute(
                "INSERT INTO private_records (employee_name, ssn, salary, medical_notes) VALUES (?, ?, ?, ?)",
                (record["employee_name"], record["ssn"], record["salary"], record["medical_notes"]),
            )
        for user in get_users():
            conn.execute(
                "INSERT INTO users (name, role) VALUES (?, ?)",
                (user["name"], user["role"]),
            )
        conn.commit()

    def reset(self) -> None:
        """Drop all data and re-create tables."""
        conn = self.connect()
        conn.execute("DELETE FROM public_notes")
        conn.execute("DELETE FROM private_records")
        conn.execute("DELETE FROM users")
        conn.commit()

    def execute(self, sql: str, params: tuple = ()) -> list[dict]:
        """Execute any SQL statement and return results as list of dicts."""
        conn = self.connect()
        cursor = conn.execute(sql, params)
        if cursor.description is None:
            conn.commit()
            return []
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def execute_readonly(self, sql: str, params: tuple = ()) -> list[dict]:
        """Execute read-only SQL. Raises ValueError for non-SELECT statements."""
        normalized = sql.strip().upper()
        if not normalized.startswith("SELECT"):
            raise ValueError(f"Only SELECT statements allowed. Got: {sql[:50]}")
        return self.execute(sql, params)

    def close(self) -> None:
        if self.conn:
            self.conn.close()
            self.conn = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, *args):
        self.close()
