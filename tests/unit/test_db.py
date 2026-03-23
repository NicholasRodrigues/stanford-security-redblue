"""Tests for data/db.py — DatabaseManager."""

import pytest

from src.data.db import DatabaseManager


@pytest.fixture
def db():
    """Fresh in-memory database, initialized and seeded."""
    manager = DatabaseManager(":memory:")
    manager.initialize()
    manager.seed()
    yield manager
    manager.close()


class TestDatabaseManager:
    def test_initialize_creates_tables(self):
        manager = DatabaseManager(":memory:")
        manager.initialize()
        tables = manager.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        table_names = [t["name"] for t in tables]
        assert "public_notes" in table_names
        assert "private_records" in table_names
        assert "users" in table_names
        manager.close()

    def test_seed_populates_public_notes(self, db):
        notes = db.execute("SELECT COUNT(*) as cnt FROM public_notes")
        assert notes[0]["cnt"] == 20

    def test_seed_populates_private_records(self, db):
        records = db.execute("SELECT COUNT(*) as cnt FROM private_records")
        assert records[0]["cnt"] == 10

    def test_seed_populates_users(self, db):
        users = db.execute("SELECT COUNT(*) as cnt FROM users")
        assert users[0]["cnt"] == 3

    def test_query_public_notes(self, db):
        notes = db.execute("SELECT title FROM public_notes WHERE title LIKE '%Holiday%'")
        assert len(notes) == 1
        assert "Holiday" in notes[0]["title"]

    def test_query_private_records(self, db):
        records = db.execute("SELECT ssn FROM private_records WHERE employee_name = 'Alice Johnson'")
        assert len(records) == 1
        assert records[0]["ssn"] == "123-45-6789"

    def test_execute_readonly_select(self, db):
        result = db.execute_readonly("SELECT COUNT(*) as cnt FROM public_notes")
        assert result[0]["cnt"] == 20

    def test_execute_readonly_rejects_insert(self, db):
        with pytest.raises(ValueError, match="Only SELECT"):
            db.execute_readonly("INSERT INTO public_notes (title, content) VALUES ('x', 'y')")

    def test_execute_readonly_rejects_delete(self, db):
        with pytest.raises(ValueError, match="Only SELECT"):
            db.execute_readonly("DELETE FROM public_notes")

    def test_execute_readonly_rejects_update(self, db):
        with pytest.raises(ValueError, match="Only SELECT"):
            db.execute_readonly("UPDATE public_notes SET title = 'x'")

    def test_execute_readonly_rejects_drop(self, db):
        with pytest.raises(ValueError, match="Only SELECT"):
            db.execute_readonly("DROP TABLE public_notes")

    def test_reset_clears_all_data(self, db):
        db.reset()
        notes = db.execute("SELECT COUNT(*) as cnt FROM public_notes")
        records = db.execute("SELECT COUNT(*) as cnt FROM private_records")
        users = db.execute("SELECT COUNT(*) as cnt FROM users")
        assert notes[0]["cnt"] == 0
        assert records[0]["cnt"] == 0
        assert users[0]["cnt"] == 0

    def test_context_manager(self):
        with DatabaseManager(":memory:") as db:
            db.initialize()
            db.seed()
            notes = db.execute("SELECT COUNT(*) as cnt FROM public_notes")
            assert notes[0]["cnt"] == 20
