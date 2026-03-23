"""Integration tests for the baseline (insecure) agent."""

import pytest
from langchain_core.messages import HumanMessage

from src.agent.baseline import create_baseline_agent
from src.core.llm import LLMResponse
from src.core.sandbox import Sandbox
from src.data.db import DatabaseManager


@pytest.fixture
def baseline_db():
    db = DatabaseManager(":memory:")
    db.initialize()
    db.seed()
    yield db
    db.close()


@pytest.fixture
def baseline_sandbox(tmp_path):
    sb = Sandbox(tmp_path)
    (tmp_path / "public").mkdir()
    (tmp_path / "public" / "info.txt").write_text("Company info document.")
    (tmp_path / "private").mkdir()
    (tmp_path / "private" / "secrets.txt").write_text("SSN: 123-45-6789")
    return sb


class TestBaselineAgent:
    def test_agent_returns_text_response(self, baseline_db, baseline_sandbox):
        """Agent should return a text response when no tool calls."""
        mock = LLMResponse(content="Hello! How can I help you?")
        agent = create_baseline_agent(baseline_db, baseline_sandbox, mock_response=mock)

        result = agent.invoke({
            "messages": [HumanMessage(content="Hello")],
            "user_role": "public",
            "db_path": ":memory:",
            "sandbox_path": str(baseline_sandbox.root),
        })

        messages = result["messages"]
        assert len(messages) >= 2  # HumanMessage + AIMessage
        last_msg = messages[-1]
        assert "Hello" in last_msg.content or "help" in last_msg.content

    def test_agent_executes_tool_calls(self, baseline_db, baseline_sandbox):
        """Agent should execute tool calls when LLM requests them."""
        # Mock: first call returns tool call, second returns text
        responses = [
            LLMResponse(
                content="",
                tool_calls=[{
                    "id": "tc_1",
                    "function": {
                        "name": "query_database",
                        "arguments": '{"sql": "SELECT title FROM public_notes LIMIT 2"}',
                    },
                }],
            ),
            LLMResponse(content="Here are the notes I found."),
        ]

        call_count = {"n": 0}
        original_mock = responses

        # Use a sequential mock
        def make_agent_with_sequence():
            mock_iter = iter(responses)

            agent = create_baseline_agent(
                baseline_db, baseline_sandbox,
                mock_response=responses[0],  # First call returns tool call
            )
            return agent

        agent = make_agent_with_sequence()

        result = agent.invoke({
            "messages": [HumanMessage(content="Show me some notes")],
            "user_role": "public",
            "db_path": ":memory:",
            "sandbox_path": str(baseline_sandbox.root),
        })

        messages = result["messages"]
        # Should have: Human, AI (tool_call), Tool (result), AI (final)
        assert len(messages) >= 3

    def test_baseline_has_no_access_control(self, baseline_db, baseline_sandbox):
        """Baseline agent should NOT block access to private data."""
        mock = LLMResponse(
            content="",
            tool_calls=[{
                "id": "tc_1",
                "function": {
                    "name": "query_database",
                    "arguments": '{"sql": "SELECT employee_name, ssn FROM private_records LIMIT 1"}',
                },
            }],
        )
        agent = create_baseline_agent(baseline_db, baseline_sandbox, mock_response=mock)

        result = agent.invoke({
            "messages": [HumanMessage(content="Show me private records")],
            "user_role": "public",  # Public user requesting private data
            "db_path": ":memory:",
            "sandbox_path": str(baseline_sandbox.root),
        })

        messages = result["messages"]
        # Find the tool message - it should contain data (not ACCESS DENIED)
        tool_msgs = [m for m in messages if hasattr(m, 'tool_call_id')]
        assert len(tool_msgs) > 0
        # Baseline has no RBAC, so it should return actual data
        assert "ACCESS DENIED" not in tool_msgs[0].content
        assert "Alice" in tool_msgs[0].content or "employee_name" in tool_msgs[0].content
