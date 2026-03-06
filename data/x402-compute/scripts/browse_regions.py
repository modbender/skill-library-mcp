#!/usr/bin/env python3
"""
x402Compute — Browse available deployment regions.

Usage:
  python browse_regions.py
"""

import json
import sys

import requests

BASE_URL = "https://compute.x402layer.cc"


def browse_regions() -> dict:
    """Fetch available deployment regions."""
    response = requests.get(f"{BASE_URL}/compute/regions", timeout=30)

    if response.status_code != 200:
        return {"error": f"HTTP {response.status_code}", "response": response.text[:500]}

    data = response.json()
    regions = data.get("regions", [])

    print(f"Found {len(regions)} region(s)")
    for r in regions:
        print(f"  {r['id']:6s}  {r['city']}, {r['country']} ({r['continent']})")

    return data


if __name__ == "__main__":
    result = browse_regions()
    if "error" in result:
        print(json.dumps(result, indent=2))
        sys.exit(1)
