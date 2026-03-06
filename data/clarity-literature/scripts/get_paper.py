#!/usr/bin/env python3
"""
Get details for a specific research paper by PMID.

Usage:
  python get_paper.py --pmid 12345678              # JSON format
  python get_paper.py --pmid 12345678 --format summary  # Human-readable
"""

import argparse
import json
from api_client import api_get


def main():
    parser = argparse.ArgumentParser(
        description="Get paper details from Clarity Protocol by PMID"
    )
    parser.add_argument(
        "--pmid",
        type=int,
        required=True,
        help="PubMed ID of the paper to retrieve"
    )
    parser.add_argument(
        "--format",
        choices=["json", "summary"],
        default="json",
        help="Output format (default: json)"
    )

    args = parser.parse_args()

    # Make API request
    result = api_get(f"/literature/{args.pmid}")

    # Output results
    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        # Summary format
        print(f"Paper Details (PMID: {result['pmid']})")
        print("=" * 60)
        print(f"Title: {result['title']}")
        print(f"Author: {result['first_author']}")
        print(f"Journal: {result['journal']}")
        print(f"Year: {result['publication_year']}")

        if result.get('doi'):
            print(f"DOI: {result['doi']}")

        print(f"Citations: {result.get('citation_count', 0)}")
        print(f"Influential citations: {result.get('influential_citations', 0)}")
        print(f"Full text available: {'Yes' if result.get('has_fulltext') else 'No'}")
        print()

        if result.get('abstract'):
            print("Abstract:")
            print("-" * 60)
            print(result['abstract'])
            print()


if __name__ == "__main__":
    main()
