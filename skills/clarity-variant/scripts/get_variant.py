#!/usr/bin/env python3
"""
Get detailed information about a specific protein variant.

Usage:
  python get_variant.py --fold-id 1              # JSON format
  python get_variant.py --fold-id 1 --format summary  # Human-readable
"""

import argparse
import json
from api_client import api_get


def main():
    parser = argparse.ArgumentParser(
        description="Get detailed variant information from Clarity Protocol"
    )
    parser.add_argument(
        "--fold-id",
        type=int,
        required=True,
        help="Fold ID of the variant to retrieve"
    )
    parser.add_argument(
        "--format",
        choices=["json", "summary"],
        default="json",
        help="Output format (default: json)"
    )

    args = parser.parse_args()

    # Make API request
    result = api_get(f"/variants/{args.fold_id}")

    # Output results
    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        # Summary format
        print(f"Variant Details (ID: {result['id']})")
        print("=" * 60)
        print(f"Protein: {result['protein_name']}")
        print(f"Variant: {result['variant']}")
        print(f"Disease: {result['disease']}")
        print(f"UniProt ID: {result.get('uniprot_id', 'N/A')}")
        print(f"Confidence: {result['average_confidence']:.1f}%")
        print(f"Created: {result['created_at']}")
        print()

        if result.get('ai_summary'):
            print("AI Summary:")
            print("-" * 60)
            print(result['ai_summary'])
            print()

        if result.get('notes'):
            print("Notes:")
            print("-" * 60)
            print(result['notes'])
            print()


if __name__ == "__main__":
    main()
