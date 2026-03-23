"""Shared test fixtures."""

import pytest
from pathlib import Path

from src.data.db import DatabaseManager
from src.core.sandbox import Sandbox
from src.core.llm import LLMResponse


@pytest.fixture
def in_memory_db():
    """Fresh in-memory database, initialized and seeded."""
    db = DatabaseManager(":memory:")
    db.initialize()
    db.seed()
    yield db
    db.close()


@pytest.fixture
def sandbox(tmp_path):
    """Temporary directory sandbox with test files."""
    sb = Sandbox(tmp_path)
    # Create public files
    public_dir = tmp_path / "public"
    public_dir.mkdir()
    (public_dir / "note1.txt").write_text("Public company policy document.")
    (public_dir / "readme.txt").write_text("Welcome to the company file system.")
    # Create private files
    private_dir = tmp_path / "private"
    private_dir.mkdir()
    (private_dir / "salaries.txt").write_text("Alice Johnson: $145,000\nBob Smith: $132,000")
    (private_dir / "ssn_list.txt").write_text("Alice: 123-45-6789\nBob: 234-56-7890")
    return sb


@pytest.fixture
def mock_llm_response():
    """Factory for creating mock LLM responses."""

    def _make(content: str = "", tool_calls: list = None) -> LLMResponse:
        return LLMResponse(
            content=content,
            tool_calls=tool_calls or [],
            model="mock-model",
            usage={"prompt_tokens": 10, "completion_tokens": 20},
        )

    return _make
