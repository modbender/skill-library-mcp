#!/usr/bin/env python3
"""
Get recent changes (findings and annotations) from Clarity Protocol.

Usage:
  python get_changes.py --since "2026-02-24T00:00:00Z"
  python get_changes.py --since "2026-02-24T00:00:00Z" --type annotation
"""

import argparse
import json
from api_client import api_get


def main():
    parser = argparse.ArgumentParser(
        description="Get recent changes from Clarity Protocol"
    )
    parser.add_argument("--since", required=True, help="ISO 8601 timestamp (e.g., 2026-02-24T00:00:00Z)")
    parser.add_argument("--type", help="Filter by type: annotation, finding (comma-separated)")
    parser.add_argument("--format", choices=["json", "summary"], default="json", help="Output format")

    args = parser.parse_args()

    params = {"since": args.since}
    if args.type:
        params["type"] = args.type

    result = api_get("/changes", params=params)

    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        changes = result.get("changes", [])
        print(f"Changes since {result.get('since', args.since)}")
        print(f"Server time: {result.get('until', 'N/A')}")
        print("=" * 60)

        if not changes:
            print("No new changes.")
            return

        print(f"{len(changes)} change(s) found:\n")
        for c in changes:
            print(f"  [{c['type'].upper()}] ID:{c['id']} variant:{c['variant_id']}")
            if c.get("description"):
                print(f"    {c['description'][:100]}")
            print(f"    {c['timestamp']}")
            print()

        print(f"\nUse --since \"{result.get('until', '')}\" for next poll")


if __name__ == "__main__":
    main()
