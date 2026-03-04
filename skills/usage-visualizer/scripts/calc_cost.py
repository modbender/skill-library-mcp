"""
Model pricing data for LLM cost calculation
Based on LiteLLM's model_prices_and_context_window.json
Updated: 2026-02-16
"""
import json
import os
from typing import Dict, Optional, Tuple, Set

# Track models without pricing
UNKNOWN_MODELS: Set[str] = set()


def get_unknown_models() -> Set[str]:
    """Get set of models without pricing"""
    return UNKNOWN_MODELS.copy()


def clear_unknown_models():
    """Clear unknown models tracking"""
    UNKNOWN_MODELS.clear()

# Model pricing (per 1M tokens)
# Format: "model_name": {"input": price, "output": price, "cache_read": price, "cache_creation": price}
MODEL_PRICING = {
    # OpenAI Models
    "gpt-5": {"input": 1.25, "output": 10.0, "cache_read": 0, "cache_creation": 0},
    "gpt-5-mini": {"input": 0.25, "output": 1.0, "cache_read": 0, "cache_creation": 0},
    "gpt-4.1": {"input": 2.0, "output": 8.0, "cache_read": 0, "cache_creation": 0},
    "gpt-4.1-mini": {"input": 0.15, "output": 0.6, "cache_read": 0, "cache_creation": 0},
    "gpt-4.1-nano": {"input": 0.1, "output": 0.4, "cache_read": 0, "cache_creation": 0},
    "gpt-4o": {"input": 2.5, "output": 10.0, "cache_read": 0, "cache_creation": 0},
    "gpt-4o-mini": {"input": 0.15, "output": 0.6, "cache_read": 0, "cache_creation": 0},
    "gpt-4o-audio-preview": {"input": 2.5, "output": 10.0, "cache_read": 0, "cache_creation": 0},
    "gpt-4o-realtime-preview": {"input": 2.5, "output": 10.0, "cache_read": 0, "cache_creation": 0},
    "o1": {"input": 15.0, "output": 60.0, "cache_read": 0, "cache_creation": 0},
    "o1-mini": {"input": 1.1, "output": 4.4, "cache_read": 0, "cache_creation": 0},
    "o1-pro": {"input": 15.0, "output": 60.0, "cache_read": 0, "cache_creation": 0},
    "gpt-4-turbo": {"input": 10.0, "output": 30.0, "cache_read": 0, "cache_creation": 0},
    "gpt-4-turbo-2024-04-09": {"input": 10.0, "output": 30.0, "cache_read": 0, "cache_creation": 0},
    "gpt-4": {"input": 30.0, "output": 60.0, "cache_read": 0, "cache_creation": 0},
    "gpt-4-32k": {"input": 60.0, "output": 120.0, "cache_read": 0, "cache_creation": 0},
    "gpt-3.5-turbo": {"input": 0.5, "output": 1.5, "cache_read": 0, "cache_creation": 0},
    "gpt-3.5-turbo-0125": {"input": 0.5, "output": 1.5, "cache_read": 0, "cache_creation": 0},
    "gpt-3.5-turbo-1106": {"input": 1.0, "output": 2.0, "cache_read": 0, "cache_creation": 0},

    # Anthropic Models
    "claude-opus-4.1": {"input": 15.0, "output": 75.0, "cache_read": 1.5, "cache_creation": 18.75},
    "claude-opus-4": {"input": 15.0, "output": 75.0, "cache_read": 1.5, "cache_creation": 18.75},
    "claude-opus-3-5": {"input": 15.0, "output": 75.0, "cache_read": 1.5, "cache_creation": 18.75},
    "claude-sonnet-4.5": {"input": 3.0, "output": 15.0, "cache_read": 0.3, "cache_creation": 3.75},
    "claude-sonnet-4": {"input": 3.0, "output": 15.0, "cache_read": 0.3, "cache_creation": 3.75},
    "claude-sonnet-3.5": {"input": 3.0, "output": 15.0, "cache_read": 0.3, "cache_creation": 3.75},
    "claude-3.5-sonnet-20241022": {"input": 3.0, "output": 15.0, "cache_read": 0.3, "cache_creation": 3.75},
    "claude-3.5-sonnet-20240620": {"input": 3.0, "output": 15.0, "cache_read": 0.3, "cache_creation": 3.75},
    "claude-3.5-haiku": {"input": 0.25, "output": 1.25, "cache_read": 0.03, "cache_creation": 0.3},
    "claude-3.5-haiku-20240620": {"input": 0.25, "output": 1.25, "cache_read": 0.03, "cache_creation": 0.3},
    "claude-3-opus": {"input": 15.0, "output": 75.0, "cache_read": 0, "cache_creation": 0},
    "claude-3-sonnet": {"input": 3.0, "output": 15.0, "cache_read": 0, "cache_creation": 0},
    "claude-3-haiku": {"input": 0.25, "output": 1.25, "cache_read": 0, "cache_creation": 0},

    # MiniMax Models
    "minimax": {"input": 0.0, "output": 0.0, "cache_read": 0, "cache_creation": 0},
    "minimax-m2.5": {"input": 0.0, "output": 0.0, "cache_read": 0, "cache_creation": 0},
    "MiniMax-M2.5": {"input": 0.0, "output": 0.0, "cache_read": 0, "cache_creation": 0},

    # Gemini Models
    "gemini-2.0-flash-exp": {"input": 0.0, "output": 0.0, "cache_read": 0, "cache_creation": 0},
    "gemini-2.0-flash-thinking-exp": {"input": 0.0, "output": 0.0, "cache_read": 0, "cache_creation": 0},
    "gemini-3-flash": {"input": 0.075, "output": 0.3, "cache_read": 0, "cache_creation": 0},
    "gemini-1.5-pro": {"input": 1.25, "output": 5.0, "cache_read": 0, "cache_creation": 0},
    "gemini-1.5-flash": {"input": 0.075, "output": 0.3, "cache_read": 0, "cache_creation": 0},
    "gemini-1.5-flash-8b": {"input": 0.0375, "output": 0.15, "cache_read": 0, "cache_creation": 0},
    "gemini-1.0-pro": {"input": 0.5, "output": 1.5, "cache_read": 0, "cache_creation": 0},
    "gemini-1.0-pro-vision": {"input": 0.25, "output": 0.5, "cache_read": 0, "cache_creation": 0},
    "gemini-ultra": {"input": 2.0, "output": 6.0, "cache_read": 0, "cache_creation": 0},
}

# Model aliases (map common names to pricing keys)
MODEL_ALIASES = {
    # OpenAI
    "gpt-4o-2024-05-13": "gpt-4o",
    "gpt-4o-mini-2024-07-18": "gpt-4o-mini",
    "chatgpt-4o-latest": "gpt-4o",
    "chatgpt-4o-mini-latest": "gpt-4o-mini",
    "gpt-4-turbo-preview": "gpt-4-turbo",
    "gpt-4-0125-preview": "gpt-4-turbo",
    "gpt-4-1106-preview": "gpt-4-turbo",
    "o1-2024-12-17": "o1",
    "o1-mini-2024-09-16": "o1-mini",

    # Anthropic
    "claude-opus-4-5-20250501": "claude-opus-4.1",
    "claude-sonnet-4-5-20250501": "claude-sonnet-4.5",
    "claude-sonnet-3.5-20240620": "claude-sonnet-3.5",
    "claude-3-5-sonnet-20240620": "claude-sonnet-3.5",
    "claude-3-5-haiku-20240620": "claude-3.5-haiku",
    "claude-3-opus-20240229": "claude-3-opus",
    "claude-3-sonnet-20240229": "claude-3-sonnet",
    "claude-3-haiku-20240307": "claude-3-haiku",

    # Gemini
    "gemini-1.5-pro-001": "gemini-1.5-pro",
    "gemini-1.5-flash-001": "gemini-1.5-flash",
    "gemini-1.5-flash-8b-exp-0924": "gemini-1.5-flash-8b",
    "gemini-1.5-flash-exp-0820": "gemini-1.5-flash",
    "gemini-1.0-pro-001": "gemini-1.0-pro",
    "gemini-1.0-pro-vision-001": "gemini-1.0-pro-vision",
}


def get_pricing(model: str) -> Optional[Dict]:
    """Get pricing for a model"""
    # Check aliases first
    pricing_key = MODEL_ALIASES.get(model, model)

    # Try exact match
    if pricing_key in MODEL_PRICING:
        return MODEL_PRICING[pricing_key]

    # Try partial match (e.g., gpt-4o-mini matches gpt-4o-mini)
    for key in MODEL_PRICING:
        if key in model or model in key:
            return MODEL_PRICING[key]

    return None


def calculate_cost(
    model: str,
    input_tokens: int = 0,
    output_tokens: int = 0,
    cache_read_tokens: int = 0,
    cache_creation_tokens: int = 0
) -> Tuple[float, float]:
    """
    Calculate cost for a request

    Args:
        model: Model name
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        cache_read_tokens: Number of cache read tokens (Anthropic)
        cache_creation_tokens: Number of cache creation tokens (Anthropic)

    Returns:
        (Cost, Savings) in USD
    """
    pricing = get_pricing(model)

    if pricing is None:
        # No pricing available - track and return 0
        UNKNOWN_MODELS.add(model)
        return 0.0, 0.0

    # Base cost calculation
    input_price = pricing.get("input", 0) / 1_000_000
    output_price = pricing.get("output", 0) / 1_000_000
    cache_read_price = pricing.get("cache_read", 0) / 1_000_000
    cache_creation_price = pricing.get("cache_creation", 0) / 1_000_000

    # Calculate costs
    # For regular input tokens (not from cache)
    billable_input = input_tokens - cache_read_tokens
    if billable_input < 0:
        billable_input = 0

    input_cost = billable_input * input_price

    # Cache read tokens (90% discount for Anthropic)
    cache_read_cost = cache_read_tokens * cache_read_price

    # Cache creation tokens
    cache_creation_cost = cache_creation_tokens * cache_creation_price

    # Output tokens
    output_cost = output_tokens * output_price

    total_cost = input_cost + cache_read_cost + cache_creation_cost + output_cost

    # Calculate Savings (What it would have cost without cache)
    # Savings = (cache_read_tokens * input_price) - cache_read_cost
    savings = cache_read_tokens * (input_price - cache_read_price)
    if savings < 0: savings = 0

    return float(round(total_cost, 6)), float(round(savings, 6))


def load_pricing_from_file(filepath: str) -> Dict:
    """Load pricing from a JSON file"""
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return json.load(f)
    return {}


def save_pricing_to_file(pricing: Dict, filepath: str):
    """Save pricing to a JSON file"""
    with open(filepath, 'w') as f:
        json.dump(pricing, f, indent=2)


if __name__ == "__main__":
    # Test
    test_cases = [
        ("gpt-4o", 1000, 500, 0, 0),
        ("claude-sonnet-4.5", 1000, 500, 2000, 500),
        ("gemini-1.5-pro", 5000, 1000, 0, 0),
    ]

    print("Cost Calculation Test:")
    print("-" * 50)
    for model, inp, out, cache_r, cache_c in test_cases:
        cost, savings = calculate_cost(model, inp, out, cache_r, cache_c)
        print(f"{model}: {inp} in, {out} out, {cache_r} cache_r, {cache_c} cache_c = ${cost:.4f} (Saved: ${savings:.4f})")
