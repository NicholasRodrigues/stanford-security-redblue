"""SQLite DDL schema definitions."""

CREATE_PUBLIC_NOTES = """
CREATE TABLE IF NOT EXISTS public_notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now'))
);
"""

CREATE_PRIVATE_RECORDS = """
CREATE TABLE IF NOT EXISTS private_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_name TEXT NOT NULL,
    ssn TEXT NOT NULL,
    salary REAL NOT NULL,
    medical_notes TEXT NOT NULL
);
"""

CREATE_USERS = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('public', 'internal', 'admin'))
);
"""

ALL_TABLES = [CREATE_PUBLIC_NOTES, CREATE_PRIVATE_RECORDS, CREATE_USERS]
