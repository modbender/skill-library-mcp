#!/usr/bin/env python3
"""Fetch Google Autocomplete suggestions for a topic with question modifiers.
Optionally enrich with search volume via DataForSEO Keywords Data API."""

from __future__ import annotations

import argparse
import base64
import json
import os
import subprocess
import sys
import time
import urllib.request
import urllib.parse

MODIFIERS = ["what", "how", "why", "should", "can", "does", "is", "when", "where", "which", "will", "are", "do"]
BASE_URL = "https://suggestqueries.google.com/complete/search"
DATAFORSEO_BATCH = 700  # max keywords per request


def fetch_suggestions(query: str) -> list[str]:
    params = urllib.parse.urlencode({"client": "firefox", "q": query})
    url = f"{BASE_URL}?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode())
    return data[1] if len(data) > 1 else []


def get_keychain(service: str) -> str:
    """Read a value from macOS Keychain."""
    try:
        return subprocess.check_output(
            ["security", "find-generic-password", "-s", service, "-w"],
            stderr=subprocess.DEVNULL
        ).decode().strip()
    except subprocess.CalledProcessError:
        return ""


def fetch_search_volumes(keywords: list[str], location_code: int = 2840, language_code: str = "en") -> dict[str, int | None]:
    """Fetch avg monthly search volumes from DataForSEO Keywords Data API.
    Returns {keyword: volume} dict. Volume is None if not found."""
    login = os.environ.get("DATAFORSEO_LOGIN") or get_keychain("dataforseo-login")
    password = os.environ.get("DATAFORSEO_PASSWORD") or get_keychain("dataforseo-password")
    if not login or not password:
        print("WARNING: DataForSEO credentials not found. Skipping volume lookup.", file=sys.stderr)
        return {}

    volumes = {}
    # Batch keywords
    for i in range(0, len(keywords), DATAFORSEO_BATCH):
        batch = keywords[i:i + DATAFORSEO_BATCH]
        payload = [{"keywords": batch, "location_code": location_code, "language_code": language_code}]
        data = json.dumps(payload).encode()
        url = "https://api.dataforseo.com/v3/keywords_data/google_ads/search_volume/live"

        auth = base64.b64encode(f"{login}:{password}".encode()).decode()
        req = urllib.request.Request(url, data=data, method="POST", headers={
            "Authorization": f"Basic {auth}",
            "Content-Type": "application/json"
        })

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode())
            if result.get("tasks"):
                for task in result["tasks"]:
                    if task.get("result"):
                        for item in task["result"]:
                            kw = item.get("keyword", "").lower()
                            vol = item.get("search_volume")
                            volumes[kw] = vol
        except Exception as e:
            print(f"WARNING: DataForSEO API error: {e}", file=sys.stderr)

    return volumes


def main():
    parser = argparse.ArgumentParser(description="Find question-based autocomplete suggestions for a topic.")
    parser.add_argument("topic", help='Topic to research, e.g. "travel itinerary"')
    parser.add_argument("--modifiers", nargs="+", default=MODIFIERS, help="Question modifiers (default: what how why)")
    parser.add_argument("--delay", type=float, default=0.0, help="Delay in seconds between requests (use 0.5-1.0 for batch runs)")
    parser.add_argument("--json", dest="as_json", action="store_true", help="Output as JSON")
    parser.add_argument("--volume", action="store_true", help="Fetch avg monthly search volume via DataForSEO")
    parser.add_argument("--location", type=int, default=2840, help="DataForSEO location code (default: 2840 = US)")
    parser.add_argument("--lang", default="en", help="Language code for volume lookup (default: en)")
    args = parser.parse_args()

    results = {}
    all_keywords = []
    for i, mod in enumerate(args.modifiers):
        if i > 0 and args.delay > 0:
            time.sleep(args.delay)
        query = f"{mod} {args.topic}"
        suggestions = fetch_suggestions(query)
        results[mod] = suggestions
        all_keywords.extend(suggestions)

    # Dedupe while preserving order
    seen = set()
    unique_keywords = []
    for kw in all_keywords:
        kw_lower = kw.lower()
        if kw_lower not in seen:
            seen.add(kw_lower)
            unique_keywords.append(kw)

    # Fetch volumes if requested
    volumes = {}
    if args.volume and unique_keywords:
        print(f"Fetching search volumes for {len(unique_keywords)} keywords...", file=sys.stderr)
        volumes = fetch_search_volumes(unique_keywords, args.location, args.lang)

    if args.as_json:
        if volumes:
            # Enrich results with volume data
            enriched = {}
            for mod, suggestions in results.items():
                enriched[mod] = [
                    {"keyword": s, "volume": volumes.get(s.lower())}
                    for s in suggestions
                ]
            print(json.dumps(enriched, indent=2))
        else:
            print(json.dumps(results, indent=2))
    else:
        for mod, suggestions in results.items():
            print(f"\n### {mod} {args.topic}")
            if suggestions:
                for s in suggestions:
                    if volumes:
                        vol = volumes.get(s.lower())
                        vol_str = f" [{vol:,}/mo]" if vol is not None else " [—]"
                        print(f"  - {s}{vol_str}")
                    else:
                        print(f"  - {s}")
            else:
                print("  (no suggestions)")


if __name__ == "__main__":
    main()
