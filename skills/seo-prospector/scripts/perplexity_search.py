#!/usr/bin/env python3
"""
Perplexity API wrapper for web search in cron jobs and scripts.

Uses the Perplexity chat completions API with the sonar model for
grounded web search with citations.

Config: API key read from ~/.openclaw/mcp-config/perplexity.json

Usage:
    python3 perplexity_search.py "your search query"
    python3 perplexity_search.py "plumber Louisville KY" --max-tokens 500
    python3 perplexity_search.py "web design Louisville" --json

Output: Search results with citations (plain text or JSON).
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


CONFIG_PATH = Path.home() / ".openclaw" / "mcp-config" / "perplexity.json"
API_URL = "https://api.perplexity.ai/chat/completions"


def load_api_key() -> str:
    if not CONFIG_PATH.exists():
        print(f"Error: Perplexity config not found at {CONFIG_PATH}", file=sys.stderr)
        sys.exit(1)
    config = json.loads(CONFIG_PATH.read_text())
    key = config.get("env", {}).get("PERPLEXITY_API_KEY")
    if not key:
        print("Error: PERPLEXITY_API_KEY not found in config", file=sys.stderr)
        sys.exit(1)
    return key


def search(query: str, api_key: str, max_tokens: int = 1000,
           system_prompt: str | None = None) -> dict:
    """Call Perplexity API and return full response."""
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": query})

    payload = {
        "model": "sonar",
        "messages": messages,
        "max_tokens": max_tokens,
    }

    cmd = [
        "curl", "-sS",
        "-X", "POST", API_URL,
        "-H", f"Authorization: Bearer {api_key}",
        "-H", "Content-Type: application/json",
        "-d", json.dumps(payload),
    ]

    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if proc.returncode != 0:
        raise RuntimeError(f"curl failed: {proc.stderr or proc.stdout}")

    return json.loads(proc.stdout)


def main():
    parser = argparse.ArgumentParser(description="Perplexity web search")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--max-tokens", type=int, default=1000, help="Max response tokens")
    parser.add_argument("--system", type=str, default=None, help="System prompt")
    parser.add_argument("--json", action="store_true", help="Output full JSON response")
    args = parser.parse_args()

    api_key = load_api_key()

    result = search(
        query=args.query,
        api_key=api_key,
        max_tokens=args.max_tokens,
        system_prompt=args.system,
    )

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        # Extract just the text content
        choices = result.get("choices", [])
        if choices:
            content = choices[0].get("message", {}).get("content", "")
            print(content)
            # Print citations if available
            citations = result.get("citations", [])
            if citations:
                print("\n--- Sources ---")
                for i, url in enumerate(citations, 1):
                    print(f"[{i}] {url}")
        else:
            print("No results")
            if "error" in result:
                print(f"Error: {result['error']}", file=sys.stderr)


if __name__ == "__main__":
    main()
