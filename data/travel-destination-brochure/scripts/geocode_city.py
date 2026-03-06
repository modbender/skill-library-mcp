#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["requests"]
# ///
"""
Geocode a city name to lat/lng using Nominatim (OpenStreetMap).
Usage: uv run scripts/geocode_city.py "Paris, France"
       uv run scripts/geocode_city.py "Tokyo" --json
"""
import argparse
import json
import sys
from urllib.parse import quote

import requests

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
HEADERS = {"User-Agent": "TravelDestinationBrochure/1.0 (skill)"}


def geocode(query: str, limit: int = 1) -> list[dict]:
    params = {"q": query, "format": "json", "limit": limit}
    r = requests.get(NOMINATIM_URL, params=params, headers=HEADERS, timeout=10)
    r.raise_for_status()
    return r.json()


def main() -> None:
    ap = argparse.ArgumentParser(description="Geocode a city name to latitude/longitude.")
    ap.add_argument("city", help='City name, e.g. "Paris, France" or "Tokyo"')
    ap.add_argument("--limit", type=int, default=1, help="Max results (default 1)")
    ap.add_argument("--json", action="store_true", help="Output raw JSON only")
    args = ap.parse_args()

    try:
        results = geocode(args.city, limit=args.limit)
    except requests.RequestException as e:
        print(f"Geocoding failed: {e}", file=sys.stderr)
        sys.exit(1)

    if not results:
        print(f"No results for: {args.city}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(results, indent=2))
        return

    first = results[0]
    lat = float(first["lat"])
    lon = float(first["lon"])
    display = first.get("display_name", "")
    out = {"lat": lat, "lng": lon, "display_name": display}
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
