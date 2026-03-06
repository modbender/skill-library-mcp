#!/usr/bin/env python3
"""
Query protein variants from Clarity Protocol.

Usage:
  python query_variants.py                    # List all variants
  python query_variants.py --disease Alzheimer  # Filter by disease
  python query_variants.py --protein-name MAPT  # Filter by protein
"""

import argparse
import json
from api_client import api_get


def main():
    parser = argparse.ArgumentParser(
        description="Query protein variants from Clarity Protocol"
    )
    parser.add_argument(
        "--disease",
        help="Filter by disease name (e.g., 'Alzheimer', 'Parkinson')"
    )
    parser.add_argument(
        "--protein-name",
        help="Filter by protein name (e.g., 'MAPT', 'APP', 'SOD1')"
    )
    parser.add_argument(
        "--format",
        choices=["json", "summary"],
        default="json",
        help="Output format (default: json)"
    )

    args = parser.parse_args()

    # Build query parameters
    params = {}
    if args.disease:
        params["disease"] = args.disease
    if args.protein_name:
        params["protein_name"] = args.protein_name

    # Make API request
    result = api_get("/variants", params=params if params else None)

    # Output results
    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        # Summary format
        items = result.get("items", [])
        print(f"Found {len(items)} variants\n")

        for item in items:
            print(f"ID: {item['id']}")
            print(f"  Protein: {item['protein_name']}")
            print(f"  Variant: {item['variant']}")
            print(f"  Disease: {item['disease']}")
            print(f"  Confidence: {item['average_confidence']:.1f}%")
            print(f"  Created: {item['created_at']}")
            print()

        next_cursor = result.get("next_cursor")
        if next_cursor:
            print(f"More results available (next_cursor: {next_cursor})")


if __name__ == "__main__":
    main()
