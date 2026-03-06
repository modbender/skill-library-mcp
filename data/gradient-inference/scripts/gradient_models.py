#!/usr/bin/env python3
"""
🦞 Gradient AI — Model Discovery

Lists available models on DigitalOcean's Gradient Serverless Inference API.
Think of it as window-shopping for LLMs — before you swipe the card.

Usage:
    python3 gradient_models.py                    # Pretty table
    python3 gradient_models.py --json             # Machine-readable
    python3 gradient_models.py --filter "llama"   # Search by name

Docs: https://docs.digitalocean.com/products/gradient-ai-platform/how-to/use-serverless-inference/
"""

import argparse
import json
import os
import sys
from typing import Optional

import requests

INFERENCE_BASE_URL = "https://inference.do-ai.run/v1"


def list_models(api_key: Optional[str] = None) -> dict:
    """List all available models from the Gradient Inference API.

    Calls GET /v1/models to discover what's currently available.

    Args:
        api_key: Gradient Model Access Key. Falls back to GRADIENT_API_KEY env var.

    Returns:
        dict with 'success', 'models' (list), and 'message'.
    """
    api_key = api_key or os.environ.get("GRADIENT_API_KEY", "")

    if not api_key:
        return {"success": False, "models": [], "message": "No GRADIENT_API_KEY configured."}

    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        resp = requests.get(f"{INFERENCE_BASE_URL}/models", headers=headers, timeout=15)
        resp.raise_for_status()

        data = resp.json()
        models = data.get("data", data.get("models", []))

        return {
            "success": True,
            "models": models,
            "message": f"Found {len(models)} available models.",
        }
    except requests.RequestException as e:
        return {"success": False, "models": [], "message": f"API request failed: {str(e)}"}


def filter_models(models: list, query: str) -> list:
    """Filter models by name or ID (case-insensitive substring match).

    Args:
        models: List of model dicts from list_models().
        query: Search string to match against model id/name.

    Returns:
        Filtered list of matching models.
    """
    query_lower = query.lower()
    return [
        m for m in models
        if query_lower in m.get("id", "").lower()
        or query_lower in m.get("name", m.get("id", "")).lower()
    ]


def format_model_table(models: list) -> str:
    """Format models as a human-readable table.

    Args:
        models: List of model dicts.

    Returns:
        Formatted table string.
    """
    if not models:
        return "No models found. 🦞 The ocean is empty."

    lines = []
    lines.append(f"{'Model ID':<45} {'Owned By':<20}")
    lines.append("─" * 65)

    for m in sorted(models, key=lambda x: x.get("id", "")):
        model_id = m.get("id", "unknown")
        owned_by = m.get("owned_by", m.get("owner", "—"))
        lines.append(f"{model_id:<45} {owned_by:<20}")

    lines.append("")
    lines.append(f"🦞 {len(models)} models available. Choose wisely.")
    return "\n".join(lines)


# ─── CLI Interface ────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="🦞 List available Gradient AI models"
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--filter", dest="query", help="Filter models by name/id")

    args = parser.parse_args()

    result = list_models()

    if not result["success"]:
        print(f"Error: {result['message']}", file=sys.stderr)
        sys.exit(1)

    models = result["models"]
    if args.query:
        models = filter_models(models, args.query)

    if args.json:
        print(json.dumps({"models": models, "count": len(models)}, indent=2))
    else:
        print(format_model_table(models))


if __name__ == "__main__":
    main()
