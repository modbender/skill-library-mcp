"""
RLM Config Builder — Generates fast-rlm configuration from OpenClaw settings.

Takes the resolved provider config and model pairs to produce a
YAML config file that fast-rlm can consume.
"""

import os
import tempfile
from pathlib import Path
from typing import Optional

import yaml

from model_pairs import get_model_pair
from provider_bridge import ProviderConfig


# Default RLM settings for memory queries (optimized for speed + cost)
DEFAULT_MEMORY_CONFIG = {
    "max_depth": 2,                 # memory → file → section (2 levels enough for memory)
    "max_calls_per_subagent": 10,   # keep it fast
    "truncate_len": 3000,           # enough to read memory sections
    "max_money_spent": 0.25,        # 25 cents max per memory query
    "max_completion_tokens": 30000,
    "max_prompt_tokens": 200000,
    "api_max_retries": 3,
    "api_timeout_ms": 120000,       # 2 minute timeout
}


def build_rlm_config(
    provider_config: ProviderConfig,
    overrides: Optional[dict] = None,
) -> dict:
    """
    Build a complete RLM config dict from OpenClaw provider settings.
    
    Args:
        provider_config: Resolved provider configuration
        overrides: Optional dict of user overrides
    
    Returns:
        Complete RLM config dict ready for fast-rlm
    """
    # Get model pair
    pair = get_model_pair(provider_config.primary_model)
    
    config = {
        **DEFAULT_MEMORY_CONFIG,
        "primary_agent": pair["primary"],
        "sub_agent": pair["sub_agent"],
    }
    
    # Apply user overrides
    if overrides:
        config.update(overrides)
    
    return config


def write_temp_config(config: dict) -> str:
    """
    Write RLM config to a temporary YAML file.
    
    Returns:
        Path to the temporary config file
    """
    tmpfile = tempfile.mktemp(suffix=".yaml", prefix="deeprecall_")
    with open(tmpfile, "w") as f:
        yaml.dump(config, f, default_flow_style=False)
    return tmpfile


def set_env_for_rlm(provider_config: ProviderConfig):
    """
    Set environment variables that fast-rlm reads for API access.
    
    This bridges OpenClaw's auth to fast-rlm's expected env vars.
    """
    os.environ["RLM_MODEL_API_KEY"] = provider_config.api_key
    os.environ["RLM_MODEL_BASE_URL"] = provider_config.base_url


if __name__ == "__main__":
    from provider_bridge import resolve_provider
    
    try:
        provider = resolve_provider()
        config = build_rlm_config(provider)
        
        print("📝 Generated RLM Config:")
        print(yaml.dump(config, default_flow_style=False))
        print(f"Primary: {config['primary_agent']}")
        print(f"Sub-agent: {config['sub_agent']}")
    except RuntimeError as e:
        print(f"❌ {e}")
