# /// script
# requires-python = ">=3.10"
# dependencies = ["httpx"]
# ///
"""
Venice AI Get API Key Details

Get details for a specific API key.
Requires an Admin API key.
API docs: https://docs.venice.ai
"""

import argparse
import json
import os
import sys
from datetime import datetime

import httpx

VENICE_BASE_URL = "https://api.venice.ai/api/v1"


def get_api_key() -> str:
    """Get Venice API key from environment."""
    api_key = os.environ.get("VENICE_API_KEY")
    if not api_key:
        print("Error: VENICE_API_KEY environment variable is not set", file=sys.stderr)
        print("Get your ADMIN API key at https://venice.ai → Settings → API Keys", file=sys.stderr)
        sys.exit(1)
    return api_key


def format_date(date_str: str | None) -> str:
    """Format ISO date string for display."""
    if not date_str:
        return "Never"
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return date_str


def get_key_details(key_id: str) -> dict:
    """Get details for a specific API key."""
    api_key = get_api_key()

    headers = {
        "Authorization": f"Bearer {api_key}",
    }

    print(f"Fetching details for key: {key_id}...", file=sys.stderr)

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.get(
                f"{VENICE_BASE_URL}/api_keys/{key_id}",
                headers=headers
            )
            response.raise_for_status()
            
            data = response.json()
            
            print("\n" + "=" * 60, file=sys.stderr)
            print("API KEY DETAILS", file=sys.stderr)
            print("=" * 60, file=sys.stderr)
            
            print(f"\nID: {data.get('id', 'unknown')}", file=sys.stderr)
            print(f"Name: {data.get('name', 'Unnamed')}", file=sys.stderr)
            print(f"Type: {data.get('apiKeyType', 'unknown')}", file=sys.stderr)
            
            key_prefix = data.get("keyPrefix", "")
            if key_prefix:
                print(f"Key Prefix: {key_prefix}...", file=sys.stderr)
            
            print(f"Created: {format_date(data.get('createdAt'))}", file=sys.stderr)
            print(f"Last Used: {format_date(data.get('lastUsedAt'))}", file=sys.stderr)
            
            rate_limits = data.get("rateLimits")
            if rate_limits:
                print(f"\nRate Limits:", file=sys.stderr)
                for key, value in rate_limits.items():
                    print(f"  • {key}: {value}", file=sys.stderr)
            
            print("\n" + "=" * 60 + "\n", file=sys.stderr)
            
            print(json.dumps(data, indent=2, default=str))
            
            return data

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            print("Error: Authentication failed. Make sure you're using an ADMIN API key.", file=sys.stderr)
        elif e.response.status_code == 404:
            print(f"Error: API key not found: {key_id}", file=sys.stderr)
        else:
            print(f"HTTP Error: {e.response.status_code}", file=sys.stderr)
        try:
            error_data = e.response.json()
            print(f"Details: {error_data}", file=sys.stderr)
        except Exception:
            print(f"Response: {e.response.text[:500]}", file=sys.stderr)
        sys.exit(1)
    except httpx.RequestError as e:
        print(f"Request Error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Get details for a specific Venice AI API key"
    )
    parser.add_argument(
        "--id", "-i",
        required=True,
        help="API key ID to get details for"
    )

    args = parser.parse_args()
    get_key_details(args.id)


if __name__ == "__main__":
    main()
