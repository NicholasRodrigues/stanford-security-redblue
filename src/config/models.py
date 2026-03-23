"""LiteLLM model registry mapping logical names to provider model strings."""

MODEL_REGISTRY: dict[str, str] = {
    "fast": "openai/gpt-4o-mini",
    "smart": "anthropic/claude-sonnet-4-20250514",
    "local": "ollama/llama3.2",
}


def resolve_model(name: str) -> str:
    """Resolve a logical model name to a LiteLLM model string.

    Accepts both logical names ('fast', 'smart', 'local') and
    direct provider strings ('openai/gpt-4o-mini').
    """
    return MODEL_REGISTRY.get(name, name)
