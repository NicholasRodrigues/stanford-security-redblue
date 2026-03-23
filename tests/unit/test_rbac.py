"""Tests for core/rbac.py."""

import pytest

from src.core.rbac import Role, check_permission, parse_role, requires_role


class TestParseRole:
    def test_public(self):
        assert parse_role("public") == Role.PUBLIC

    def test_internal(self):
        assert parse_role("internal") == Role.INTERNAL

    def test_admin(self):
        assert parse_role("admin") == Role.ADMIN

    def test_case_insensitive(self):
        assert parse_role("ADMIN") == Role.ADMIN
        assert parse_role("Internal") == Role.INTERNAL

    def test_unknown_defaults_public(self):
        assert parse_role("unknown") == Role.PUBLIC


class TestCheckPermission:
    def test_public_can_query_public_notes(self):
        assert check_permission("public", "query_database", "public_notes") is True

    def test_public_cannot_query_private_records(self):
        assert check_permission("public", "query_database", "private_records") is False

    def test_admin_can_query_private_records(self):
        assert check_permission("admin", "query_database", "private_records") is True

    def test_internal_can_query_users(self):
        assert check_permission("internal", "query_database", "users") is True

    def test_public_cannot_query_users(self):
        assert check_permission("public", "query_database", "users") is False

    def test_public_can_read_public_files(self):
        assert check_permission("public", "read_file", "public") is True

    def test_public_cannot_read_private_files(self):
        assert check_permission("public", "read_file", "private") is False

    def test_internal_can_read_private_files(self):
        assert check_permission("internal", "read_file", "private") is True

    def test_public_cannot_write_files(self):
        assert check_permission("public", "write_file") is False

    def test_internal_can_write_files(self):
        assert check_permission("internal", "write_file") is True

    def test_unknown_tool_requires_admin(self):
        assert check_permission("public", "unknown_tool", "resource") is False
        assert check_permission("admin", "unknown_tool", "resource") is True


class TestRequiresRole:
    def test_admin_function_allows_admin(self):
        @requires_role(Role.ADMIN)
        def secret_func(state):
            return "secret"

        result = secret_func({"user_role": "admin"})
        assert result == "secret"

    def test_admin_function_blocks_public(self):
        @requires_role(Role.ADMIN)
        def secret_func(state):
            return "secret"

        with pytest.raises(PermissionError, match="Access denied"):
            secret_func({"user_role": "public"})

    def test_internal_function_allows_internal(self):
        @requires_role(Role.INTERNAL)
        def internal_func(state):
            return "internal data"

        result = internal_func({"user_role": "internal"})
        assert result == "internal data"

    def test_internal_function_allows_admin(self):
        @requires_role(Role.INTERNAL)
        def internal_func(state):
            return "internal data"

        result = internal_func({"user_role": "admin"})
        assert result == "internal data"

    def test_internal_function_blocks_public(self):
        @requires_role(Role.INTERNAL)
        def internal_func(state):
            return "internal data"

        with pytest.raises(PermissionError):
            internal_func({"user_role": "public"})
