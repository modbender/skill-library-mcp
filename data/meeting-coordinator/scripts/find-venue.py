#!/usr/bin/env python3
"""
Search for meeting venues using goplaces CLI.

Usage:
  python3 find-venue.py --location "Union Square, NYC" --type coffee
  python3 find-venue.py --location "Penn Station, NYC" --type lunch --min-rating 4.5
"""

import argparse
import subprocess
import json
import re
import sys

QUERY_MAP = {
    "coffee": "coffee shop",
    "cafe": "cafe",
    "lunch": "restaurant for lunch",
    "dinner": "restaurant for dinner",
    "restaurant": "restaurant",
}


def search_venues(location: str, venue_type: str, min_rating: float = 0.0):
    """Search for venues and return structured results."""
    query = QUERY_MAP.get(venue_type, venue_type)
    search_term = f"{query} near {location}"

    try:
        result = subprocess.run(
            ["goplaces", "search", search_term],
            capture_output=True, text=True, check=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"Error: goplaces search failed: {e.stderr}", file=sys.stderr)
        return []

    venues = []
    current = {}

    for line in result.stdout.strip().split("\n"):
        line = line.strip()
        if not line:
            continue

        # New venue entry: "1. Name — Address"
        m = re.match(r"^\d+\.\s+(.+?)\s+—\s+(.+)$", line)
        if m:
            if current:
                venues.append(current)
            current = {"name": m.group(1), "address": m.group(2)}
            continue

        if line.startswith("ID:"):
            current["place_id"] = line.split(": ", 1)[1]
        elif line.startswith("Rating:"):
            current["rating"] = line.split(": ", 1)[1]
        elif line.startswith("Types:"):
            current["types"] = line.split(": ", 1)[1]
        elif line.startswith("Open now:"):
            current["open_now"] = line.split(": ", 1)[1] == "yes"

    if current:
        venues.append(current)

    # Filter by min rating
    if min_rating > 0:
        filtered = []
        for v in venues:
            try:
                r = float(v.get("rating", "0").split("·")[0].strip())
                if r >= min_rating:
                    filtered.append(v)
            except ValueError:
                pass
        venues = filtered

    # Sort by rating descending
    def rating_key(v):
        try:
            return float(v.get("rating", "0").split("·")[0].strip())
        except ValueError:
            return 0.0
    venues.sort(key=rating_key, reverse=True)

    return venues


def main():
    p = argparse.ArgumentParser(description="Search for meeting venues")
    p.add_argument("--location", required=True, help='Area (e.g., "SoHo, NYC")')
    p.add_argument("--type", required=True,
                   choices=["coffee", "cafe", "lunch", "dinner", "restaurant"],
                   help="Venue type")
    p.add_argument("--min-rating", type=float, default=0.0,
                   help="Minimum Google rating (e.g., 4.5)")
    args = p.parse_args()

    venues = search_venues(args.location, args.type, args.min_rating)
    print(json.dumps(venues, indent=2))


if __name__ == "__main__":
    main()
