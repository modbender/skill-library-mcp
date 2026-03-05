#!/usr/bin/env python3
"""
config.py — Configure embedding model and settings for zettel-link.

Creates/updates config/config.json with provider, model, and tuning parameters.
Supports local (ollama) and remote (openai, gemini) embedding providers.

Usage:
  uv run scripts/config.py                          # Create default config
  uv run scripts/config.py --provider openai         # Switch to OpenAI
  uv run scripts/config.py --model text-embedding-3-small --provider openai
  uv run scripts/config.py --top-k 10 --threshold 0.7
"""

import os
import sys
import json
import argparse
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = SKILL_ROOT / "config" / "config.json"

# ── Provider presets ─────────────────────────────────────────────────────────

PROVIDER_PRESETS = {
    "ollama": {
        "name": "ollama",
        "url": "http://localhost:11434",
        "default_model": "mxbai-embed-large",
    },
    "openai": {
        "name": "openai",
        "url": "https://api.openai.com/v1",
        "api_key_env": "OPENAI_API_KEY",
        "default_model": "text-embedding-3-small",
    },
    "gemini": {
        "name": "gemini",
        "url": "https://generativelanguage.googleapis.com/v1beta",
        "api_key_env": "GEMINI_API_KEY",
        "default_model": "text-embedding-004",
    },
}

DEFAULT_CONFIG = {
    "model": "mxbai-embed-large",
    "provider": {
        "name": "ollama",
        "url": "http://localhost:11434",
    },
    "max_input_length": 8192,
    "cache_dir": ".embeddings",
    "default_threshold": 0.65,
    "top_k": 5,
    "env": {
        "OPENAI_API_KEY": {
            "description": "API key for OpenAI embedding models",
            "optional": true
        },
        "GEMINI_API_KEY": {
            "description": "API key for Google Gemini embedding models",
            "optional": true
        }
    },
    "skip_dirs": [
        ".obsidian", ".trash", ".smart-env", ".makemd", ".space",
        ".claude", ".embeddings", "Spaces", "templates",
    ],
    "skip_files": [
        "CLAUDE.md", "Vault.md", "Dashboard.md", "templates.md",
    ],
}


def load_config() -> dict:
    """Load existing config or return defaults."""
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    return dict(DEFAULT_CONFIG)


def save_config(config: dict) -> None:
    """Write config to disk."""
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=4)
    print(f"✅ Config saved to {CONFIG_PATH}")


def print_config(config: dict) -> None:
    """Pretty-print the current config."""
    print("\n📋 Current configuration:")
    print(json.dumps(config, indent=4))
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Configure zettel-link embedding settings"
    )
    parser.add_argument(
        "--provider",
        choices=list(PROVIDER_PRESETS.keys()),
        help="Embedding provider (ollama, openai, gemini)",
    )
    parser.add_argument("--provider-url", help="Custom provider URL")
    parser.add_argument("--model", help="Embedding model name")
    parser.add_argument(
        "--max-input-length",
        type=int,
        help="Max input length in characters (default: 8192)",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        help="Default similarity threshold (default: 0.65)",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        help="Number of top results to return (default: 5)",
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="Just print the current config and exit",
    )
    args = parser.parse_args()

    config = load_config()

    if args.show:
        print_config(config)
        return

    changed = False

    # ── Apply provider preset ────────────────────────────────────────────
    if args.provider:
        preset = PROVIDER_PRESETS[args.provider]
        config["provider"] = {
            "name": preset["name"],
            "url": preset["url"],
        }
        if "api_key_env" in preset:
            config["provider"]["api_key_env"] = preset["api_key_env"]
        # Update model to provider default unless explicitly overridden
        if not args.model:
            config["model"] = preset["default_model"]
        changed = True

    if args.provider_url:
        config["provider"]["url"] = args.provider_url
        changed = True

    if args.model:
        config["model"] = args.model
        changed = True

    if args.max_input_length is not None:
        config["max_input_length"] = args.max_input_length
        changed = True

    if args.threshold is not None:
        config["default_threshold"] = args.threshold
        changed = True

    if args.top_k is not None:
        config["top_k"] = args.top_k
        changed = True

    # If no flags were passed and config doesn't exist yet, create defaults
    if not changed and not CONFIG_PATH.exists():
        print("🆕 Creating default config...")
        changed = True

    if changed:
        save_config(config)

    print_config(config)

    # Validate API key availability for remote providers
    provider_name = config["provider"]["name"]
    if provider_name in ("openai", "gemini"):
        key_env = config["provider"].get(
            "api_key_env", PROVIDER_PRESETS[provider_name]["api_key_env"]
        )
        if not os.environ.get(key_env):
            print(f"⚠️  Warning: Environment variable {key_env} is not set.")
            print(f"   Set it before running embed/search/link commands.")


if __name__ == "__main__":
    main()
