"""Phase 3: Defended agent with all blue team layers."""

from __future__ import annotations

import json
import operator
from typing import Annotated, Any, TypedDict

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage, ToolMessage
from langgraph.graph import StateGraph, END

from src.agent.baseline import _msg_to_dict
from src.blue_team.input_filter import InputFilter
from src.blue_team.output_filter import OutputFilter
from src.blue_team.context_separation import SandwichDefense
from src.blue_team.semantic_guard import SemanticGuard
from src.blue_team.instruction_hierarchy import enforce_hierarchy
from src.blue_team.permission_validator import PermissionValidator
from src.core.llm import LLMResponse, completion
from src.core.tools import create_tools
from src.core.sandbox import Sandbox
from src.data.db import DatabaseManager


class DefendedStateSchema(TypedDict):
    messages: Annotated[list[BaseMessage], operator.add]
    user_role: str
    db_path: str
    sandbox_path: str
    blocked: bool
    block_reason: str


def create_defended_agent(
    db: DatabaseManager,
    sandbox: Sandbox,
    model: str = "openai/gpt-4.1-nano",
    user_role: str = "public",
    mock_response: LLMResponse | None = None,
):
    """Create and compile the defended agent graph with all blue team layers.

    Defense layers:
    1. Input guard: InputFilter + SemanticGuard
    2. Agent: LLM with hardened prompt (SandwichDefense + InstructionHierarchy)
    3. Permission check: RBAC + anomaly detection before tool execution
    4. Output guard: Scan responses for leaked sensitive data
    """
    # Create tools WITH RBAC enforcement
    tools = create_tools(db, sandbox, user_role=user_role, enforce_rbac=True)
    tool_map = {t.name: t for t in tools}

    # Initialize defense components
    input_filter = InputFilter()
    semantic_guard = SemanticGuard()
    sandwich_defense = SandwichDefense()
    output_filter = OutputFilter()
    permission_validator = PermissionValidator()

    # Tool schemas for LLM
    tool_schemas = [
        {
            "type": "function",
            "function": {
                "name": t.name,
                "description": t.description,
                "parameters": t.args_schema.model_json_schema() if hasattr(t.args_schema, 'model_json_schema') else {"type": "object", "properties": {}},
            },
        }
        for t in tools
    ]

    def input_guard_node(state: dict) -> dict:
        """Filter malicious inputs before they reach the LLM."""
        messages = state.get("messages", [])
        if not messages:
            return {"blocked": False, "block_reason": ""}

        # Get the last user message
        user_msgs = [m for m in messages if isinstance(m, HumanMessage)]
        if not user_msgs:
            return {"blocked": False, "block_reason": ""}

        last_user = user_msgs[-1].content

        # Run input filter
        filter_result = input_filter.scan(last_user)
        if filter_result.is_suspicious and filter_result.risk_score >= 0.8:
            return {
                "messages": [AIMessage(
                    content=f"I detected a potential prompt injection attempt in your message. "
                    f"Matched patterns: {', '.join(filter_result.matched_patterns)}. "
                    f"For security reasons, I cannot process this request."
                )],
                "blocked": True,
                "block_reason": f"Input filter: {filter_result.matched_patterns}",
            }

        # Run semantic guard
        guard_result = semantic_guard.classify(last_user)
        if guard_result.is_malicious and guard_result.confidence >= 0.8:
            return {
                "messages": [AIMessage(
                    content=f"Your request appears to be attempting {guard_result.intent}. "
                    f"This violates our security policy. Please rephrase your request."
                )],
                "blocked": True,
                "block_reason": f"Semantic guard: {guard_result.intent} ({guard_result.confidence:.1f})",
            }

        return {"blocked": False, "block_reason": ""}

    def agent_node(state: dict) -> dict:
        """Call LLM with hardened prompt."""
        if state.get("blocked"):
            return {}  # Skip if already blocked

        messages = state.get("messages", [])

        # Build messages with sandwich defense
        msg_dicts = [_msg_to_dict(m) for m in messages if not isinstance(m, SystemMessage)]
        defended_msgs = sandwich_defense.build_messages(msg_dicts)

        # Apply instruction hierarchy
        defended_msgs = enforce_hierarchy(defended_msgs)

        # Count tool rounds to prevent infinite loops
        tool_rounds = sum(1 for m in messages if isinstance(m, ToolMessage))
        force_text = tool_rounds >= 2

        # When using mock: detect if we've already executed tools
        effective_mock = mock_response
        if mock_response and messages:
            has_tool_results = any(isinstance(m, ToolMessage) for m in messages)
            if has_tool_results and mock_response.tool_calls:
                effective_mock = LLMResponse(
                    content="Here are the results.",
                    model=mock_response.model,
                )

        active_tools = tool_schemas if not effective_mock and not force_text else None

        response = completion(
            messages=defended_msgs,
            model=model,
            tools=active_tools,
            mock_response=effective_mock,
        )

        if response.tool_calls:
            ai_msg = AIMessage(
                content=response.content,
                tool_calls=[
                    {
                        "id": tc["id"],
                        "name": tc["function"]["name"],
                        "args": json.loads(tc["function"]["arguments"])
                        if isinstance(tc["function"]["arguments"], str)
                        else tc["function"]["arguments"],
                    }
                    for tc in response.tool_calls
                ],
            )
        else:
            ai_msg = AIMessage(content=response.content)

        return {"messages": [ai_msg]}

    def permission_check_node(state: dict) -> dict:
        """Validate permissions before tool execution."""
        messages = state.get("messages", [])
        if not messages:
            return {}

        last_msg = messages[-1]
        if not hasattr(last_msg, "tool_calls") or not last_msg.tool_calls:
            return {}

        user_role_str = state.get("user_role", "public")
        blocked_tools = []

        for tc in last_msg.tool_calls:
            result = permission_validator.validate(
                user_role=user_role_str,
                tool_name=tc["name"],
                tool_args=tc["args"],
            )
            if not result.allowed:
                blocked_tools.append((tc, result.reason))

        if blocked_tools:
            # Replace the AI message's tool calls with denial
            denial_msgs = []
            for tc, reason in blocked_tools:
                denial_msgs.append(
                    ToolMessage(
                        content=f"ACCESS DENIED: {reason}",
                        tool_call_id=tc["id"],
                    )
                )
            return {"messages": denial_msgs, "blocked": True, "block_reason": "Permission denied"}

        return {}

    def tool_node(state: dict) -> dict:
        """Execute permitted tool calls."""
        if state.get("blocked"):
            return {}

        messages = state.get("messages", [])
        # Find the last AI message with tool calls
        ai_msgs = [m for m in messages if isinstance(m, AIMessage) and hasattr(m, "tool_calls") and m.tool_calls]
        if not ai_msgs:
            return {}

        last_ai = ai_msgs[-1]
        # Check if tools already have results (permission_check may have added ToolMessages)
        existing_tool_ids = {m.tool_call_id for m in messages if isinstance(m, ToolMessage)}

        tool_messages = []
        for tc in last_ai.tool_calls:
            if tc["id"] in existing_tool_ids:
                continue  # Already handled by permission check

            tool_func = tool_map.get(tc["name"])
            if tool_func:
                try:
                    result = tool_func.invoke(tc["args"])
                except Exception as e:
                    result = f"Error: {e}"
            else:
                result = f"Unknown tool: {tc['name']}"

            tool_messages.append(
                ToolMessage(content=str(result), tool_call_id=tc["id"])
            )

        return {"messages": tool_messages}

    def output_guard_node(state: dict) -> dict:
        """Scan output for leaked sensitive data."""
        messages = state.get("messages", [])
        if not messages:
            return {}

        last_msg = messages[-1]
        if not isinstance(last_msg, AIMessage):
            return {}

        result = output_filter.scan(last_msg.content)
        if result.has_leak:
            # Replace the message with sanitized version
            sanitized_msg = AIMessage(content=result.sanitized_text)
            # We can't directly replace, so we add a note
            return {
                "messages": [AIMessage(
                    content=f"{result.sanitized_text}\n\n[Note: Some sensitive data was redacted from this response.]"
                )],
            }

        return {}

    def route_after_input_guard(state: dict) -> str:
        if state.get("blocked"):
            return "__end__"
        return "agent"

    def route_after_agent(state: dict) -> str:
        messages = state.get("messages", [])
        if not messages:
            return "__end__"
        last_msg = messages[-1]
        if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
            return "permission_check"
        return "output_guard"

    def route_after_permission(state: dict) -> str:
        if state.get("blocked"):
            return "agent"  # Let agent see the denial and respond
        return "tools"

    def route_after_tools(state: dict) -> str:
        return "agent"

    def route_after_output_guard(state: dict) -> str:
        return "__end__"

    # Build the graph
    graph = StateGraph(DefendedStateSchema)
    graph.add_node("input_guard", input_guard_node)
    graph.add_node("agent", agent_node)
    graph.add_node("permission_check", permission_check_node)
    graph.add_node("tools", tool_node)
    graph.add_node("output_guard", output_guard_node)

    graph.set_entry_point("input_guard")
    graph.add_conditional_edges("input_guard", route_after_input_guard, {"agent": "agent", "__end__": END})
    graph.add_conditional_edges("agent", route_after_agent, {"permission_check": "permission_check", "output_guard": "output_guard"})
    graph.add_conditional_edges("permission_check", route_after_permission, {"tools": "tools", "agent": "agent"})
    graph.add_edge("tools", "agent")
    graph.add_edge("output_guard", END)

    return graph.compile()
