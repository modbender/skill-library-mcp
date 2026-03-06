"""Model pricing data for various AI providers.

Prices are per 1M tokens (input/output) as of Feb 2026.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ModelPricing:
    """Pricing for a specific model."""
    provider: str
    model: str
    input_per_1m: float  # $ per 1M input tokens
    output_per_1m: float  # $ per 1M output tokens
    aliases: tuple[str, ...] = ()  # Alternative names


# Anthropic pricing (as of Feb 2026)
ANTHROPIC_PRICING = [
    ModelPricing("anthropic", "claude-opus-4", 15.00, 75.00, ("opus-4", "opus")),
    ModelPricing("anthropic", "claude-sonnet-4", 3.00, 15.00, ("sonnet-4", "sonnet")),
    ModelPricing("anthropic", "claude-3.5-sonnet", 3.00, 15.00, ("claude-3-5-sonnet", "3.5-sonnet")),
    ModelPricing("anthropic", "claude-3.5-haiku", 0.80, 4.00, ("haiku", "3.5-haiku")),
    ModelPricing("anthropic", "claude-3-opus", 15.00, 75.00, ("claude-3-opus-20240229",)),
]

# OpenAI pricing
OPENAI_PRICING = [
    ModelPricing("openai", "gpt-4o", 2.50, 10.00, ("4o",)),
    ModelPricing("openai", "gpt-4o-mini", 0.15, 0.60, ("4o-mini",)),
    ModelPricing("openai", "gpt-4-turbo", 10.00, 30.00, ("gpt-4-turbo-preview",)),
    ModelPricing("openai", "gpt-4", 30.00, 60.00, ()),
    ModelPricing("openai", "o1", 15.00, 60.00, ("o1-preview",)),
    ModelPricing("openai", "o1-mini", 3.00, 12.00, ()),
    ModelPricing("openai", "o3-mini", 1.10, 4.40, ()),
]

# Google pricing
GOOGLE_PRICING = [
    ModelPricing("google", "gemini-2.0-flash", 0.10, 0.40, ("gemini-flash", "2.0-flash")),
    ModelPricing("google", "gemini-2.0-pro", 1.25, 5.00, ("gemini-pro", "2.0-pro")),
    ModelPricing("google", "gemini-1.5-pro", 1.25, 5.00, ("1.5-pro",)),
    ModelPricing("google", "gemini-1.5-flash", 0.075, 0.30, ("1.5-flash",)),
]

# Azure OpenAI (same as OpenAI for most models)
AZURE_PRICING = [
    ModelPricing("azure", "gpt-4o", 2.50, 10.00, ("azure-gpt-4o",)),
    ModelPricing("azure", "gpt-4o-mini", 0.15, 0.60, ("azure-4o-mini",)),
    ModelPricing("azure", "gpt-4", 30.00, 60.00, ("azure-gpt-4",)),
]

# Combined pricing lookup
ALL_PRICING = ANTHROPIC_PRICING + OPENAI_PRICING + GOOGLE_PRICING + AZURE_PRICING


def get_pricing(provider: str, model: str) -> Optional[ModelPricing]:
    """Look up pricing for a provider/model combo."""
    provider = provider.lower()
    model = model.lower()
    
    for p in ALL_PRICING:
        if p.provider == provider:
            if p.model.lower() == model or model in [a.lower() for a in p.aliases]:
                return p
    
    # Fuzzy match - check if model contains the pricing model name
    for p in ALL_PRICING:
        if p.provider == provider and p.model.lower() in model:
            return p
    
    return None


def calculate_cost(provider: str, model: str, input_tokens: int, output_tokens: int) -> float:
    """Calculate the cost in USD for a given usage."""
    pricing = get_pricing(provider, model)
    if not pricing:
        return 0.0
    
    input_cost = (input_tokens / 1_000_000) * pricing.input_per_1m
    output_cost = (output_tokens / 1_000_000) * pricing.output_per_1m
    return input_cost + output_cost


def list_supported_models() -> list[tuple[str, str]]:
    """Return list of (provider, model) tuples."""
    return [(p.provider, p.model) for p in ALL_PRICING]
