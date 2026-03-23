"""Tests for core/llm.py."""

from src.core.llm import LLMResponse, completion


class TestLLMCompletion:
    def test_mock_response_bypasses_api(self):
        mock = LLMResponse(content="Hello!", model="mock")
        result = completion(
            messages=[{"role": "user", "content": "Hi"}],
            mock_response=mock,
        )
        assert result.content == "Hello!"
        assert result.model == "mock"

    def test_mock_response_with_tool_calls(self):
        mock = LLMResponse(
            content="",
            tool_calls=[
                {"id": "tc_1", "function": {"name": "query_database", "arguments": '{"sql": "SELECT 1"}'}}
            ],
        )
        result = completion(
            messages=[{"role": "user", "content": "query"}],
            mock_response=mock,
        )
        assert len(result.tool_calls) == 1
        assert result.tool_calls[0]["function"]["name"] == "query_database"

    def test_llm_response_dataclass(self):
        resp = LLMResponse(content="test", model="gpt-4o-mini")
        assert resp.content == "test"
        assert resp.tool_calls == []
        assert resp.usage == {}
