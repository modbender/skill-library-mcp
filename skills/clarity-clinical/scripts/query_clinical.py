#!/usr/bin/env python3
"""
Query clinical variant data from ClinVar and gnomAD.

Usage:
  python query_clinical.py                             # List all variants
  python query_clinical.py --gene-symbol MAPT          # Filter by gene
  python query_clinical.py --gene MAPT --variant NM_005910.6:c.926C>T  # Specific variant
"""

import argparse
import json
from api_client import api_get


def main():
    parser = argparse.ArgumentParser(
        description="Query clinical variant data from Clarity Protocol"
    )
    parser.add_argument(
        "--gene-symbol",
        help="Filter by gene symbol (e.g., 'MAPT', 'APP')"
    )
    parser.add_argument(
        "--gene",
        help="Gene symbol for specific variant lookup (requires --variant)"
    )
    parser.add_argument(
        "--variant",
        help="HGVS variant notation for specific lookup (requires --gene)"
    )
    parser.add_argument(
        "--format",
        choices=["json", "summary"],
        default="json",
        help="Output format (default: json)"
    )

    args = parser.parse_args()

    # Validate gene/variant pairing
    if (args.gene and not args.variant) or (args.variant and not args.gene):
        parser.error("--gene and --variant must be used together")

    # Determine endpoint and parameters
    if args.gene and args.variant:
        # Specific variant lookup
        result = api_get(f"/clinical/{args.gene}/{args.variant}")
        results = [result]  # Wrap in list for uniform processing
        is_single = True
    elif args.gene_symbol:
        # Filter by gene symbol
        result = api_get("/clinical", params={"gene_symbol": args.gene_symbol})
        results = result.get("items", [])
        is_single = False
    else:
        # List all
        result = api_get("/clinical")
        results = result.get("items", [])
        is_single = False

    # Output results
    if args.format == "json":
        if is_single:
            print(json.dumps(results[0], indent=2))
        else:
            print(json.dumps(result, indent=2))
    else:
        # Summary format
        if not is_single:
            print(f"Found {len(results)} clinical variants\n")

        for item in results:
            print(f"Gene: {item['gene_symbol']}")
            print(f"Variant: {item['variant_notation']}")
            print(f"ClinVar Significance: {item.get('clinvar_significance', 'N/A')}")
            print(f"Review Status: {item.get('clinvar_review_status', 'N/A')}")

            if item.get('clinvar_last_evaluated'):
                print(f"Last Evaluated: {item['clinvar_last_evaluated']}")

            if item.get('gnomad_af') is not None:
                af = item['gnomad_af']
                af_percent = af * 100
                print(f"gnomAD Frequency: {af:.6f} ({af_percent:.4f}%)")
                print(f"gnomAD Counts: {item.get('gnomad_ac', 0)}/{item.get('gnomad_an', 0)}")

            print(f"Fetched: {item.get('fetched_at', 'N/A')}")
            print()

        if not is_single:
            next_cursor = result.get("next_cursor")
            if next_cursor:
                print(f"More results available (next_cursor: {next_cursor})")


if __name__ == "__main__":
    main()
