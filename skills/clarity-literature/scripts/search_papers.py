#!/usr/bin/env python3
"""
Search research papers in Clarity Protocol's literature database.

Usage:
  python search_papers.py                  # List all papers
  python search_papers.py --format summary  # Human-readable list
"""

import argparse
import json
from api_client import api_get


def main():
    parser = argparse.ArgumentParser(
        description="Search research papers from Clarity Protocol"
    )
    parser.add_argument(
        "--format",
        choices=["json", "summary"],
        default="json",
        help="Output format (default: json)"
    )

    args = parser.parse_args()

    # Make API request
    result = api_get("/literature")

    # Output results
    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        # Summary format
        items = result.get("items", [])
        print(f"Found {len(items)} papers\n")

        for item in items:
            print(f"PMID: {item['pmid']}")
            print(f"  Title: {item['title']}")
            print(f"  Author: {item['first_author']}")
            print(f"  Journal: {item['journal']} ({item['publication_year']})")
            print(f"  Citations: {item.get('citation_count', 0)} ({item.get('influential_citations', 0)} influential)")

            if item.get('doi'):
                print(f"  DOI: {item['doi']}")

            print()

        next_cursor = result.get("next_cursor")
        if next_cursor:
            print(f"More results available (next_cursor: {next_cursor})")


if __name__ == "__main__":
    main()
