"""
Model Pairs — Auto-selects a cheaper sub-agent model based on the user's primary model.

The primary model handles the REPL reasoning (depth 0).
The sub-agent model handles recursive memory queries (depth 1+).
"""

# Maps primary model patterns to their cheaper counterparts
# Keys are substrings matched against the full model ID
MODEL_PAIRS = {
    # Anthropic
    "claude-opus-4": "claude-sonnet-4-20250514",
    "claude-sonnet-4": "claude-haiku-3.5",
    "claude-sonnet-3.5": "claude-haiku-3.5",
    "claude-3-opus": "claude-3-sonnet",
    "claude-3.5-sonnet": "claude-3.5-haiku",
    
    # OpenAI
    "gpt-4o": "gpt-4o-mini",
    "gpt-4.1": "gpt-4.1-mini",
    "gpt-4-turbo": "gpt-4o-mini",
    "gpt-4.5": "gpt-4o-mini",
    "o3": "gpt-4o-mini",
    "o4-mini": "gpt-4o-mini",
    
    # Google
    "gemini-2.5-pro": "gemini-2.5-flash",
    "gemini-2.0-pro": "gemini-2.0-flash",
    "gemini-1.5-pro": "gemini-1.5-flash",
    
    # Meta (via OpenRouter / local)
    "llama-3.3-70b": "llama-3.3-8b",
    "llama-3.1-405b": "llama-3.1-70b",
    "llama-3.1-70b": "llama-3.1-8b",
    
    # Mistral
    "mistral-large": "mistral-small",
    "mixtral-8x22b": "mixtral-8x7b",
    
    # DeepSeek
    "deepseek-v3": "deepseek-v3",
    "deepseek-r1": "deepseek-v3",
    
    # Qwen
    "qwen-max": "qwen-plus",
    "qwen-plus": "qwen-turbo",
}


def get_sub_agent_model(primary_model: str) -> str:
    """
    Given a primary model ID (e.g., "claude-opus-4-20250514" or "anthropic/claude-opus-4"),
    return a cheaper sub-agent model for RLM worker tasks.
    
    Args:
        primary_model: Full model ID string (may include provider prefix like "anthropic/")
    
    Returns:
        Sub-agent model ID string (without provider prefix)
    """
    # Remove provider prefix if present (e.g., "anthropic/claude-opus-4" → "claude-opus-4")
    model_name = primary_model.split("/")[-1] if "/" in primary_model else primary_model
    
    # Try to match against known pairs (substring match)
    for pattern, sub_model in MODEL_PAIRS.items():
        if pattern in model_name.lower():
            return sub_model
    
    # Fallback: use the same model (user can always override)
    return model_name


def get_model_pair(primary_model: str) -> dict:
    """
    Returns both primary and sub-agent model names.
    
    Args:
        primary_model: Full model ID string
    
    Returns:
        Dict with 'primary' and 'sub_agent' keys
    """
    # Strip provider prefix for RLM config (it uses OpenAI-compatible format)
    primary_clean = primary_model.split("/")[-1] if "/" in primary_model else primary_model
    sub_agent = get_sub_agent_model(primary_model)
    
    return {
        "primary": primary_clean,
        "sub_agent": sub_agent,
    }


if __name__ == "__main__":
    # Test model pairing
    test_models = [
        "anthropic/claude-opus-4-20250514",
        "github-copilot/claude-opus-4.6",
        "openai/gpt-4o",
        "gpt-4.1",
        "gemini-2.5-pro",
        "llama-3.3-70b",
        "deepseek-r1",
        "some-unknown-model",
    ]
    
    for model in test_models:
        pair = get_model_pair(model)
        print(f"  {model:45s} → primary: {pair['primary']:30s} sub: {pair['sub_agent']}")
