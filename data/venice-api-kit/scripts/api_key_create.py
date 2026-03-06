# /// script
# requires-python = ">=3.10"
# dependencies = ["httpx"]
# ///
"""
Venice AI Create API Key

Create a new API key.
Requires an Admin API key.
API docs: https://docs.venice.ai
"""

import argparse
import json
import os
import sys

import httpx

VENICE_BASE_URL = "https://api.venice.ai/api/v1"

VALID_KEY_TYPES = ["INFERENCE", "ADMIN"]


def get_api_key() -> str:
    """Get Venice API key from environment."""
    api_key = os.environ.get("VENICE_API_KEY")
    if not api_key:
        print("Error: VENICE_API_KEY environment variable is not set", file=sys.stderr)
        print("Get your ADMIN API key at https://venice.ai → Settings → API Keys", file=sys.stderr)
        sys.exit(1)
    return api_key


def create_api_key(
    name: str,
    key_type: str = "INFERENCE",
) -> dict:
    """Create a new API key."""
    api_key = get_api_key()

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "name": name,
        "apiKeyType": key_type,
    }

    print(f"Creating {key_type} API key: {name}...", file=sys.stderr)

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                f"{VENICE_BASE_URL}/api_keys",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            
            data = response.json()
            
            print("\n" + "=" * 60, file=sys.stderr)
            print("NEW API KEY CREATED", file=sys.stderr)
            print("=" * 60, file=sys.stderr)
            
            print(f"\nID: {data.get('id', 'unknown')}", file=sys.stderr)
            print(f"Name: {data.get('name', 'Unnamed')}", file=sys.stderr)
            print(f"Type: {data.get('apiKeyType', 'unknown')}", file=sys.stderr)
            
            # The full key is only shown once on creation
            full_key = data.get("key")
            if full_key:
                print(f"\n⚠️  SAVE THIS KEY - IT WILL NOT BE SHOWN AGAIN:", file=sys.stderr)
                print(f"\n    {full_key}\n", file=sys.stderr)
            
            print("=" * 60 + "\n", file=sys.stderr)
            
            print(json.dumps(data, indent=2, default=str))
            
            return data

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            print("Error: Authentication failed. Make sure you're using an ADMIN API key.", file=sys.stderr)
        elif e.response.status_code == 400:
            print("Error: Invalid request. Check key name and type.", file=sys.stderr)
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
        description="Create a new Venice AI API key"
    )
    parser.add_argument(
        "--name", "-n",
        required=True,
        help="Name for the new API key"
    )
    parser.add_argument(
        "--type", "-t",
        dest="key_type",
        choices=VALID_KEY_TYPES,
        default="INFERENCE",
        help="Key type: INFERENCE (default) or ADMIN"
    )

    args = parser.parse_args()
    
    create_api_key(
        name=args.name,
        key_type=args.key_type,
    )


if __name__ == "__main__":
    main()
