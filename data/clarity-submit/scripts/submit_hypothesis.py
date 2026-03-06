#!/usr/bin/env python3
"""
Submit a protein variant hypothesis to Clarity Protocol.

Usage:
  python submit_hypothesis.py --protein SOD1 --variant A4V --rationale "ALS-linked mutation"
  python submit_hypothesis.py --protein MAPT --variant P301L --rationale "Tau pathology" --wallet YOUR_WALLET
"""

import argparse
import json
from api_client import api_post


def main():
    parser = argparse.ArgumentParser(
        description="Submit a protein variant hypothesis to Clarity Protocol"
    )
    parser.add_argument(
        "--protein",
        required=True,
        help="Protein name (e.g., SOD1, MAPT, APP, SNCA)"
    )
    parser.add_argument(
        "--variant",
        required=True,
        help="Variant notation (e.g., A4V, P301L, G2019S)"
    )
    parser.add_argument(
        "--rationale",
        required=True,
        help="Why this variant is worth investigating (min 10 characters)"
    )
    parser.add_argument(
        "--disease",
        default=None,
        help="Disease area (optional, auto-detected from protein)"
    )
    parser.add_argument(
        "--wallet",
        default=None,
        help="Solana wallet address for $FOLD reward eligibility (optional)"
    )
    parser.add_argument(
        "--format",
        choices=["json", "summary"],
        default="summary",
        help="Output format (default: summary)"
    )

    args = parser.parse_args()

    # Build request body
    body = {
        "protein_name": args.protein,
        "variant_notation": args.variant,
        "rationale": args.rationale,
    }
    if args.disease:
        body["disease_area"] = args.disease
    if args.wallet:
        body["wallet_address"] = args.wallet

    # Submit hypothesis
    result = api_post("/hypotheses", body)

    # Output results
    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        print(f"Hypothesis Submitted (ID: {result['id']})")
        print("=" * 60)
        print(f"Protein: {result['protein_name']}")
        print(f"Variant: {result['variant_notation']}")
        print(f"Status:  {result['status']}")
        print()
        print(f"Track progress: https://clarityprotocol.io{result['tracking_url']}")
        print()
        print("Feasibility validation is running. The pipeline will:")
        print("  1. Check UniProt, ClinVar, gnomAD, PubMed")
        print("  2. Auto-queue for ColabFold if validated")
        print("  3. Assign AI research agents to monitor")


if __name__ == "__main__":
    main()
