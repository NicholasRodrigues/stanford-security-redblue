"""LangGraph agent state definitions."""

from __future__ import annotations

import operator
from typing import Annotated, Any


class AgentState(dict):
    """State that flows through the LangGraph agent.

    Used as a TypedDict-like structure for LangGraph StateGraph.
    Keys:
        messages: Chat message history (append-only via operator.add).
        user_role: Current user's role ('public', 'internal', 'admin').
        db_path: Path to SQLite database (or ':memory:').
        sandbox_path: Root path for file sandbox.
        defense_enabled: Whether blue team defenses are active.
        metadata: Arbitrary metadata dict.
    """

    pass


# LangGraph state schema using Annotated for reducer
from typing import TypedDict


class AgentStateSchema(TypedDict):
    messages: Annotated[list, operator.add]
    user_role: str
    db_path: str
    sandbox_path: str
    defense_enabled: bool
    metadata: dict[str, Any]


def create_initial_state(
    user_role: str = "public",
    db_path: str = ":memory:",
    sandbox_path: str = "/tmp/sandbox",
    defense_enabled: bool = False,
) -> dict:
    """Create an initial agent state dict."""
    return {
        "messages": [],
        "user_role": user_role,
        "db_path": db_path,
        "sandbox_path": sandbox_path,
        "defense_enabled": defense_enabled,
        "metadata": {},
    }
