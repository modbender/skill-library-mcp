#!/usr/bin/env python3
"""
Check status and overview of Clarity Protocol API.

Usage:
  python check_status.py                 # Human-readable status report
  python check_status.py --format json   # JSON format
"""

import argparse
import json
from api_client import api_get


def main():
    parser = argparse.ArgumentParser(
        description="Check Clarity Protocol API status and overview"
    )
    parser.add_argument(
        "--format",
        choices=["json", "summary"],
        default="summary",
        help="Output format (default: summary)"
    )

    args = parser.parse_args()

    # Get API info
    api_info = api_get("/")

    # Get variant count
    variants = api_get("/variants")
    variant_count = len(variants.get("items", []))

    # Output results
    if args.format == "json":
        combined = {
            "api_info": api_info,
            "variant_count": variant_count
        }
        print(json.dumps(combined, indent=2))
    else:
        # Summary format
        print("Clarity Protocol Status Report")
        print("=" * 60)
        print(f"API: {api_info.get('name', 'Unknown')} v{api_info.get('version', 'Unknown')}")
        print(f"Description: {api_info.get('description', 'N/A')}")
        print()

        print(f"Total Variants Tracked: {variant_count}")
        print()

        print("Available Endpoints:")
        print("-" * 60)
        endpoints = api_info.get("endpoints", [])
        for endpoint in endpoints:
            print(f"  {endpoint}")
        print()

        print("Rate Limits:")
        print("-" * 60)
        rate_limits = api_info.get("rate_limits", {})
        anonymous = rate_limits.get("anonymous", "Unknown")
        authenticated = rate_limits.get("authenticated", "Unknown")
        print(f"  Anonymous: {anonymous}")
        print(f"  With API key: {authenticated}")
        print()

        print("Get your API key at: https://clarityprotocol.io")


if __name__ == "__main__":
    main()
