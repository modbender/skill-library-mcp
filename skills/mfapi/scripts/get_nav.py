#!/usr/bin/env python3
"""Get latest mutual fund NAV by ISIN code using MFapi.in.

Usage:
    python3 get_nav.py <ISIN> [ISIN ...]

Examples:
    python3 get_nav.py INF200K01UT4
    python3 get_nav.py INF200K01UT4 INF846K01DP8
"""

import json
import sys
import time
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional

BASE_URL = "https://api.mfapi.in"
CACHE_PATH = Path("/tmp/mfapi-schemes.json")
CACHE_MAX_AGE = 86400  # 24 hours in seconds


def load_cache() -> List[Dict[str, Any]]:
    """Load scheme list from cache, refreshing if stale or missing."""
    if CACHE_PATH.exists() and (time.time() - CACHE_PATH.stat().st_mtime) < CACHE_MAX_AGE:
        with open(CACHE_PATH) as f:
            return json.load(f)
    return refresh_cache()


def refresh_cache() -> List[Dict[str, Any]]:
    """Download full scheme list and write to cache."""
    data = api_get("/mf")
    CACHE_PATH.write_text(json.dumps(data))
    return data


def api_get(path: str):
    """GET request to MFapi.in and return parsed JSON."""
    url = f"{BASE_URL}{path}"
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def find_scheme_code(isin: str, schemes: List[Dict[str, Any]]) -> Optional[int]:
    """Find scheme code by matching ISIN against isinGrowth or isinDivReinvestment."""
    for s in schemes:
        if s.get("isinGrowth") == isin or s.get("isinDivReinvestment") == isin:
            return s["schemeCode"]
    return None


def get_nav_by_isin(isin: str) -> Dict[str, Any]:
    """Resolve ISIN to scheme code, fetch latest NAV, return result dict."""
    schemes = load_cache()
    scheme_code = find_scheme_code(isin, schemes)

    # Cache miss — refresh and retry
    if scheme_code is None:
        schemes = refresh_cache()
        scheme_code = find_scheme_code(isin, schemes)

    if scheme_code is None:
        return {"isin": isin, "error": f"No scheme found for ISIN {isin}"}

    resp = api_get(f"/mf/{scheme_code}/latest")
    meta = resp.get("meta", {})
    nav_entry = resp.get("data", [{}])[0]

    return {
        "isin": isin,
        "scheme_code": meta.get("scheme_code", scheme_code),
        "scheme_name": meta.get("scheme_name"),
        "fund_house": meta.get("fund_house"),
        "category": meta.get("scheme_category"),
        "nav": nav_entry.get("nav"),
        "date": nav_entry.get("date"),
    }


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <ISIN> [ISIN ...]", file=sys.stderr)
        sys.exit(1)

    results = [get_nav_by_isin(isin) for isin in sys.argv[1:]]
    output = results[0] if len(results) == 1 else results
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
