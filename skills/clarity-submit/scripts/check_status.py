#!/usr/bin/env python3
"""
Check the status of a submitted hypothesis.

Usage:
  python check_status.py --id 42           # JSON format
  python check_status.py --id 42 --format summary  # Human-readable
"""

import argparse
import json
from api_client import api_get


STATUS_DESCRIPTIONS = {
    "submitted": "Submitted, awaiting validation",
    "validating": "Feasibility check running",
    "validated": "Passed validation, awaiting queue",
    "queued": "Queued for ColabFold prediction",
    "folding": "ColabFold is running",
    "complete": "Fold complete, research agents active",
    "rejected": "Did not pass feasibility check",
}


def main():
    parser = argparse.ArgumentParser(
        description="Check hypothesis status on Clarity Protocol"
    )
    parser.add_argument(
        "--id",
        type=int,
        required=True,
        help="Hypothesis ID to check"
    )
    parser.add_argument(
        "--format",
        choices=["json", "summary"],
        default="summary",
        help="Output format (default: summary)"
    )

    args = parser.parse_args()

    # Fetch status via lab API (separate from v1 API base)
    import os
    import sys
    import requests
    from api_client import get_headers

    url = f"https://clarityprotocol.io/lab/api/hypothesis/{args.id}"
    try:
        response = requests.get(url, headers=get_headers(), timeout=30)
        if response.status_code == 404:
            print(f"Error: Hypothesis {args.id} not found.", file=sys.stderr)
            sys.exit(1)
        response.raise_for_status()
        result = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Output results
    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        status = result.get("status", "unknown")
        desc = STATUS_DESCRIPTIONS.get(status, status)

        print(f"Hypothesis #{result['id']}: {result['protein_name']} {result['variant_notation']}")
        print("=" * 60)
        print(f"Status: {status} — {desc}")
        print(f"Votes:  {result.get('vote_count', 0)}")

        if result.get("created_at"):
            print(f"Submitted: {result['created_at']}")

        if result.get("fold_id"):
            print(f"\nFold available: https://clarityprotocol.io/folds-page/{result['fold_id']}")

        if result.get("rejection_reason"):
            print(f"\nRejection reason: {result['rejection_reason']}")

        if result.get("reward_tx_hash"):
            print(f"\n$FOLD reward: https://solscan.io/tx/{result['reward_tx_hash']}")

        # Show validation results if available
        vr = result.get("validation_results")
        if vr:
            print("\nValidation Results:")
            print("-" * 40)
            for db_name in ["uniprot", "clinvar", "gnomad", "pubmed"]:
                data = vr.get(db_name)
                if data:
                    if db_name == "pubmed":
                        status_str = f"{data.get('count', 0)} papers found"
                    else:
                        status_str = "Found" if data.get("found") else "Not found"
                    print(f"  {db_name:>8}: {status_str}")


if __name__ == "__main__":
    main()
