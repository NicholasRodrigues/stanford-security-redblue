"""Application settings loaded from environment variables."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Project-wide settings loaded from .env or environment."""

    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    default_model: str = "openai/gpt-4.1-nano"
    db_path: str = ":memory:"
    sandbox_root: Path = Path("data/sandbox")

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}

    def has_any_api_key(self) -> bool:
        return bool(self.openai_api_key or self.anthropic_api_key)


_settings: Optional[Settings] = None


def get_settings(**overrides) -> Settings:
    """Return singleton settings instance (or create with overrides)."""
    global _settings
    if _settings is None or overrides:
        _settings = Settings(**overrides)
    return _settings
