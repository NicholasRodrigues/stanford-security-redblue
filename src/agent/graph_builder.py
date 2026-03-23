"""Shared LangGraph construction helpers."""

from __future__ import annotations

from typing import Any, Callable, Literal

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langgraph.graph import StateGraph, END


def should_continue(state: dict) -> Literal["tools", "__end__"]:
    """Route based on whether the last AI message has tool calls."""
    messages = state.get("messages", [])
    if not messages:
        return "__end__"

    last_message = messages[-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return "__end__"


def create_system_message(prompt: str) -> SystemMessage:
    """Create a system message."""
    return SystemMessage(content=prompt)


def create_human_message(content: str) -> HumanMessage:
    """Create a human message."""
    return HumanMessage(content=content)
