# /// script
# requires-python = ">=3.10"
# dependencies = ["httpx"]
# ///
"""
Venice AI Update API Key

Update an existing API key's settings.
Requires an Admin API key.
API docs: https://docs.venice.ai
"""

import argparse
import json
import os
import sys

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


def update_api_key(
    key_id: str,
    name: str | None = None,
) -> dict:
    """Update an API key."""
    api_key = get_api_key()

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {}
    if name:
        payload["name"] = name

    if not payload:
        print("Error: No updates specified. Use --name to update the key name.", file=sys.stderr)
        sys.exit(1)

    print(f"Updating API key: {key_id}...", file=sys.stderr)

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.patch(
                f"{VENICE_BASE_URL}/api_keys/{key_id}",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            
            data = response.json()
            
            print("\n" + "=" * 60, file=sys.stderr)
            print("API KEY UPDATED", file=sys.stderr)
            print("=" * 60, file=sys.stderr)
            
            print(f"\nID: {data.get('id', 'unknown')}", file=sys.stderr)
            print(f"Name: {data.get('name', 'Unnamed')}", file=sys.stderr)
            print(f"Type: {data.get('apiKeyType', 'unknown')}", file=sys.stderr)
            
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
        description="Update a Venice AI API key"
    )
    parser.add_argument(
        "--id", "-i",
        required=True,
        help="API key ID to update"
    )
    parser.add_argument(
        "--name", "-n",
        help="New name for the API key"
    )

    args = parser.parse_args()
    
    update_api_key(
        key_id=args.id,
        name=args.name,
    )


if __name__ == "__main__":
    main()
