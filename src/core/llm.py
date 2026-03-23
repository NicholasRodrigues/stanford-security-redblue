"""LiteLLM wrapper with retry logic and mock support for testing."""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from typing import Any, Optional

from tenacity import retry, stop_after_attempt, wait_exponential

# Suppress noisy LiteLLM logging
logging.getLogger("LiteLLM").setLevel(logging.WARNING)
logging.getLogger("litellm").setLevel(logging.WARNING)
os.environ.setdefault("LITELLM_LOG", "WARNING")


@dataclass
class LLMResponse:
    """Standardized response from LLM call."""

    content: str
    tool_calls: list[dict] = field(default_factory=list)
    model: str = ""
    usage: dict = field(default_factory=dict)


def _parse_response(raw: Any) -> LLMResponse:
    """Parse a litellm response into our standardized format."""
    choice = raw.choices[0]
    msg = choice.message

    tool_calls = []
    if hasattr(msg, "tool_calls") and msg.tool_calls:
        for tc in msg.tool_calls:
            tool_calls.append(
                {
                    "id": tc.id,
                    "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                }
            )

    return LLMResponse(
        content=msg.content or "",
        tool_calls=tool_calls,
        model=getattr(raw, "model", ""),
        usage=dict(getattr(raw, "usage", {})) if hasattr(raw, "usage") else {},
    )


@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10), reraise=True)
def _call_litellm(model: str, messages: list[dict], tools: Optional[list] = None, **kwargs) -> Any:
    """Call litellm with retry logic."""
    import litellm

    litellm.suppress_debug_info = True

    params = {"model": model, "messages": messages, **kwargs}
    if tools:
        params["tools"] = tools
    return litellm.completion(**params)


def completion(
    messages: list[dict],
    model: str = "openai/gpt-4.1-nano",
    tools: Optional[list] = None,
    mock_response: Optional[LLMResponse] = None,
    **kwargs,
) -> LLMResponse:
    """Call LLM and return standardized response.

    Args:
        messages: Chat messages in OpenAI format.
        model: LiteLLM model string.
        tools: Optional tool definitions.
        mock_response: If provided, skip the API call and return this directly.
    """
    if mock_response is not None:
        return mock_response

    try:
        raw = _call_litellm(model, messages, tools, **kwargs)
        return _parse_response(raw)
    except Exception as e:
        # Return a graceful error response instead of crashing
        return LLMResponse(
            content=f"I'm sorry, I encountered an error processing your request.",
            model=model,
        )
