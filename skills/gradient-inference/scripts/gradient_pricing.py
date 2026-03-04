#!/usr/bin/env python3
"""
🦞 Gradient AI — Pricing Lookup

Fetches current model pricing from DigitalOcean's Gradient AI pricing docs.
No API key needed — the pricing page is public.

Usage:
    python3 gradient_pricing.py                    # Pretty table
    python3 gradient_pricing.py --json             # Machine-readable
    python3 gradient_pricing.py --model "llama"    # Filter by model name
    python3 gradient_pricing.py --no-cache         # Skip cache, fetch live

Source: https://docs.digitalocean.com/products/gradient-ai-platform/details/pricing/
"""

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Optional

import requests

PRICING_URL = "https://docs.digitalocean.com/products/gradient-ai-platform/details/pricing/"
CACHE_PATH = Path("/tmp/gradient_pricing_cache.json")
CACHE_TTL_SECONDS = 86400  # 24 hours
FALLBACK_PATH = Path(__file__).parent / "pricing_snapshot.json"


def _parse_price(text: str) -> dict:
    """Extract input/output prices from a pricing cell's text.

    Handles formats like:
      - "$0.25 per 1M input tokens\n$0.55 per 1M output tokens"
      - "$3.00 per 1M input tokens\n$15.00 per 1M output tokens..."
      - Per-unit pricing (images, audio, TTS)

    Returns:
        dict with 'input', 'output' (floats or None), and 'unit'.
    """
    result = {"input": None, "output": None, "unit": "per 1M tokens"}

    # Try input/output pattern
    input_match = re.search(r"\$(\d+(?:\.\d+)?)\s*per\s*1M\s*input\s*tokens", text)
    output_match = re.search(r"\$(\d+(?:\.\d+)?)\s*per\s*1M\s*output\s*tokens", text)

    if input_match:
        result["input"] = float(input_match.group(1))
    if output_match:
        result["output"] = float(output_match.group(1))

    if result["input"] is not None or result["output"] is not None:
        return result

    # Try same-price pattern (e.g., "$0.65 per 1M tokens")
    same_match = re.search(r"\$(\d+(?:\.\d+)?)\s*per\s*1M\s*tokens", text)
    if same_match:
        price = float(same_match.group(1))
        result["input"] = price
        result["output"] = price
        return result

    # Try per-unit patterns (images, audio, etc.)
    unit_match = re.search(r"\$(\d+(?:\.\d+)?)\s*per\s*(.+)", text)
    if unit_match:
        result["input"] = float(unit_match.group(1))
        result["unit"] = f"per {unit_match.group(2).strip()}"

    return result


def fetch_pricing_live() -> dict:
    """Scrape pricing data from the DigitalOcean docs page.

    Returns:
        dict with 'success', 'models' list, 'fetched_at', and 'message'.
    """
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        return {
            "success": False,
            "models": [],
            "fetched_at": None,
            "message": "beautifulsoup4 not installed. Run: pip install beautifulsoup4",
        }

    try:
        resp = requests.get(PRICING_URL, timeout=15, headers={
            "User-Agent": "gradient-inference-skill/0.1 (pricing lookup)"
        })
        resp.raise_for_status()
    except requests.RequestException as e:
        return {
            "success": False,
            "models": [],
            "fetched_at": None,
            "message": f"Failed to fetch pricing page: {e}",
        }

    soup = BeautifulSoup(resp.text, "html.parser")

    # Find Foundation Model Usage section
    h2 = soup.find("h2", id="foundation-model-usage")
    if not h2:
        return {
            "success": False,
            "models": [],
            "fetched_at": None,
            "message": "Could not find Foundation Model Usage section on pricing page.",
        }

    section = h2.parent

    # Find all provider tabs: input[name="foundation-model-pricing"]
    inputs = section.find_all("input", {"name": "foundation-model-pricing"})

    models = []
    for input_tag in inputs:
        provider_id = input_tag.get("id", "")
        label_tag = section.find("label", {"for": provider_id})
        provider = label_tag.get_text(strip=True) if label_tag else "Unknown"

        # Find the next tab-content div with a table
        content_div = input_tag.find_next_sibling("div", class_="tab-content")
        if not content_div:
            continue

        table = content_div.find("table")
        if not table:
            continue

        tbody = table.find("tbody")
        if not tbody:
            continue

        for row in tbody.find_all("tr"):
            cols = row.find_all("td")
            if len(cols) < 2:
                continue

            model_name = cols[0].get_text(strip=True)
            pricing_text = cols[1].get_text("\n", strip=True)
            prices = _parse_price(pricing_text)

            models.append({
                "provider": provider,
                "model": model_name,
                "input_price": prices["input"],
                "output_price": prices["output"],
                "unit": prices["unit"],
            })

    return {
        "success": True,
        "models": models,
        "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "message": f"Fetched pricing for {len(models)} models.",
    }


def _read_cache() -> Optional[dict]:
    """Read cached pricing data if it exists and is fresh."""
    if not CACHE_PATH.exists():
        return None
    try:
        data = json.loads(CACHE_PATH.read_text())
        if time.time() - data.get("cached_at", 0) < CACHE_TTL_SECONDS:
            return data
    except (json.JSONDecodeError, KeyError):
        pass
    return None


def _write_cache(data: dict) -> None:
    """Write pricing data to the cache file."""
    data["cached_at"] = time.time()
    try:
        CACHE_PATH.write_text(json.dumps(data, indent=2))
    except OSError:
        pass  # Best-effort caching


def _read_fallback() -> dict:
    """Read the bundled pricing snapshot as a last resort."""
    if FALLBACK_PATH.exists():
        try:
            data = json.loads(FALLBACK_PATH.read_text())
            data["message"] = f"Using bundled snapshot ({data.get('fetched_at', 'unknown date')}). Live fetch failed."
            data["source"] = "fallback"
            return data
        except (json.JSONDecodeError, KeyError):
            pass
    return {
        "success": False,
        "models": [],
        "fetched_at": None,
        "message": "No pricing data available (live fetch failed, no fallback snapshot).",
    }


def get_pricing(use_cache: bool = True) -> dict:
    """Get model pricing with cache → live → fallback strategy.

    Args:
        use_cache: Whether to check the cache first (default True).

    Returns:
        dict with 'success', 'models', 'fetched_at', 'message', and 'source'.
    """
    # 1. Try cache
    if use_cache:
        cached = _read_cache()
        if cached:
            cached["source"] = "cache"
            return cached

    # 2. Try live scrape
    result = fetch_pricing_live()
    if result["success"]:
        result["source"] = "live"
        _write_cache(result)
        return result

    # 3. Fall back to bundled snapshot
    return _read_fallback()


def filter_pricing(models: list, query: str) -> list:
    """Filter pricing data by model name (case-insensitive substring).

    Args:
        models: List of pricing dicts.
        query: Search string.

    Returns:
        Filtered list.
    """
    q = query.lower()
    return [m for m in models if q in m.get("model", "").lower() or q in m.get("provider", "").lower()]


def format_pricing_table(models: list) -> str:
    """Format pricing data as a human-readable table.

    Args:
        models: List of pricing dicts.

    Returns:
        Formatted table string.
    """
    if not models:
        return "No pricing data found. 🦞"

    lines = []
    lines.append(f"{'Provider':<12} {'Model':<35} {'Input/1M':<12} {'Output/1M':<12}")
    lines.append("─" * 71)

    for m in sorted(models, key=lambda x: (x.get("provider", ""), x.get("model", ""))):
        provider = m.get("provider", "—")
        model = m.get("model", "—")
        inp = f"${m['input_price']:.4f}" if m.get("input_price") is not None else "—"
        out = f"${m['output_price']:.4f}" if m.get("output_price") is not None else "—"

        if m.get("unit") != "per 1M tokens":
            inp = f"{inp} ({m['unit']})"
            out = "—"

        lines.append(f"{provider:<12} {model:<35} {inp:<12} {out:<12}")

    lines.append("")
    lines.append(f"🦞 {len(models)} models priced. Choose wisely — your wallet is watching.")
    return "\n".join(lines)


# ─── CLI Interface ────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="🦞 Look up Gradient AI model pricing"
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--model", dest="query", help="Filter by model/provider name")
    parser.add_argument("--no-cache", action="store_true", help="Skip cache, fetch live")

    args = parser.parse_args()

    result = get_pricing(use_cache=not args.no_cache)

    if not result.get("success", False) and not result.get("models"):
        print(f"Error: {result.get('message', 'Unknown error')}", file=sys.stderr)
        sys.exit(1)

    models = result.get("models", [])
    if args.query:
        models = filter_pricing(models, args.query)

    if args.json:
        print(json.dumps({
            "models": models,
            "count": len(models),
            "source": result.get("source", "unknown"),
            "fetched_at": result.get("fetched_at"),
        }, indent=2))
    else:
        source_note = f"(source: {result.get('source', 'unknown')}, as of {result.get('fetched_at', 'unknown')})"
        print(format_pricing_table(models))
        print(source_note)


if __name__ == "__main__":
    main()
