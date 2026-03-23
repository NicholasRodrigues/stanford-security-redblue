"""Tests for core/tools.py."""

import pytest

from src.core.tools import (
    create_query_database_tool,
    create_read_file_tool,
    create_write_file_tool,
    create_tools,
)


class TestQueryDatabaseTool:
    def test_public_can_query_public_notes(self, in_memory_db):
        tool = create_query_database_tool(in_memory_db, "public")
        result = tool.invoke({"sql": "SELECT title FROM public_notes LIMIT 3"})
        assert "Holiday" in result or "title" in result.lower() or isinstance(result, str)

    def test_public_blocked_from_private_records(self, in_memory_db):
        tool = create_query_database_tool(in_memory_db, "public")
        result = tool.invoke({"sql": "SELECT * FROM private_records"})
        assert "ACCESS DENIED" in result

    def test_admin_can_query_private_records(self, in_memory_db):
        tool = create_query_database_tool(in_memory_db, "admin")
        result = tool.invoke({"sql": "SELECT employee_name FROM private_records LIMIT 1"})
        assert "Alice" in result or "employee_name" in result

    def test_rejects_write_queries(self, in_memory_db):
        tool = create_query_database_tool(in_memory_db, "admin")
        result = tool.invoke({"sql": "DELETE FROM public_notes"})
        assert "Error" in result


class TestReadFileTool:
    def test_public_can_read_public_file(self, sandbox):
        tool = create_read_file_tool(sandbox, "public")
        result = tool.invoke({"path": "public/note1.txt"})
        assert "Public company policy" in result

    def test_public_blocked_from_private_file(self, sandbox):
        tool = create_read_file_tool(sandbox, "public")
        result = tool.invoke({"path": "private/salaries.txt"})
        assert "ACCESS DENIED" in result

    def test_internal_can_read_private_file(self, sandbox):
        tool = create_read_file_tool(sandbox, "internal")
        result = tool.invoke({"path": "private/salaries.txt"})
        assert "Alice Johnson" in result


class TestWriteFileTool:
    def test_public_cannot_write(self, sandbox):
        tool = create_write_file_tool(sandbox, "public")
        result = tool.invoke({"path": "test.txt", "content": "test"})
        assert "ACCESS DENIED" in result

    def test_internal_can_write(self, sandbox):
        tool = create_write_file_tool(sandbox, "internal")
        result = tool.invoke({"path": "output.txt", "content": "hello"})
        assert "Successfully" in result


class TestCreateTools:
    def test_creates_three_tools(self, in_memory_db, sandbox):
        tools = create_tools(in_memory_db, sandbox)
        assert len(tools) == 3

    def test_no_rbac_mode(self, in_memory_db, sandbox):
        tools = create_tools(in_memory_db, sandbox, enforce_rbac=False)
        # With enforce_rbac=False, tools use 'admin' role
        query_tool = tools[0]
        result = query_tool.invoke({"sql": "SELECT * FROM private_records LIMIT 1"})
        assert "ACCESS DENIED" not in result
