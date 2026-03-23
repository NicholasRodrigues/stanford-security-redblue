"""Tests for config/settings.py and config/models.py."""

import os

import pytest


class TestSettings:
    def test_default_model(self):
        # Reset singleton
        import src.config.settings as mod
        mod._settings = None
        s = mod.get_settings()
        assert s.default_model == "openai/gpt-4.1-nano"

    def test_override_model(self):
        import src.config.settings as mod
        mod._settings = None
        s = mod.get_settings(default_model="anthropic/claude-sonnet-4-20250514")
        assert s.default_model == "anthropic/claude-sonnet-4-20250514"
        mod._settings = None  # cleanup

    def test_has_any_api_key_false(self):
        import src.config.settings as mod
        mod._settings = None
        s = mod.get_settings(openai_api_key=None, anthropic_api_key=None)
        assert s.has_any_api_key() is False
        mod._settings = None

    def test_has_any_api_key_true(self):
        import src.config.settings as mod
        mod._settings = None
        s = mod.get_settings(openai_api_key="sk-test")
        assert s.has_any_api_key() is True
        mod._settings = None

    def test_db_path_default(self):
        import src.config.settings as mod
        mod._settings = None
        s = mod.get_settings()
        assert s.db_path == ":memory:"
        mod._settings = None


class TestModelRegistry:
    def test_resolve_fast(self):
        from src.config.models import resolve_model
        assert resolve_model("fast") == "openai/gpt-4.1-nano"

    def test_resolve_smart(self):
        from src.config.models import resolve_model
        assert resolve_model("smart") == "openai/gpt-4.1-mini"

    def test_resolve_local(self):
        from src.config.models import resolve_model
        assert resolve_model("local") == "ollama/llama3.2"

    def test_resolve_passthrough(self):
        from src.config.models import resolve_model
        assert resolve_model("openai/gpt-4o") == "openai/gpt-4o"
