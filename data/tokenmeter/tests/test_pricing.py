"""Tests for pricing module."""

import pytest
from tokenmeter.pricing import get_pricing, calculate_cost, list_supported_models


def test_get_pricing_exact_match():
    """Test exact model name match."""
    pricing = get_pricing("anthropic", "claude-sonnet-4")
    assert pricing is not None
    assert pricing.model == "claude-sonnet-4"
    assert pricing.input_per_1m == 3.00
    assert pricing.output_per_1m == 15.00


def test_get_pricing_alias():
    """Test alias matching."""
    pricing = get_pricing("anthropic", "sonnet")
    assert pricing is not None
    assert pricing.model == "claude-sonnet-4"


def test_get_pricing_unknown():
    """Test unknown model returns None."""
    pricing = get_pricing("anthropic", "gpt-4")  # Wrong provider
    assert pricing is None


def test_calculate_cost():
    """Test cost calculation."""
    # 1000 input + 500 output tokens with claude-sonnet-4
    # Input: (1000 / 1M) * $3 = $0.003
    # Output: (500 / 1M) * $15 = $0.0075
    # Total: $0.0105
    cost = calculate_cost("anthropic", "claude-sonnet-4", 1000, 500)
    assert abs(cost - 0.0105) < 0.0001


def test_calculate_cost_unknown_model():
    """Unknown model should return 0 cost."""
    cost = calculate_cost("unknown", "unknown-model", 1000, 500)
    assert cost == 0.0


def test_list_supported_models():
    """Test listing all models."""
    models = list_supported_models()
    assert len(models) > 10
    assert ("anthropic", "claude-sonnet-4") in models
    assert ("openai", "gpt-4o") in models
