# /// script
# requires-python = ">=3.10"
# dependencies = ["httpx"]
# ///
"""
Venice AI Delete API Key

Delete an API key. This action is irreversible.
Requires an Admin API key.
API docs: https://docs.venice.ai
"""

import argparse
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


def delete_api_key(key_id: str, force: bool = False) -> bool:
    """Delete an API key."""
    api_key = get_api_key()

    if not force:
        print(f"\n⚠️  WARNING: You are about to delete API key: {key_id}", file=sys.stderr)
        print("This action is IRREVERSIBLE.", file=sys.stderr)
        print("\nUse --force to confirm deletion.\n", file=sys.stderr)
        sys.exit(1)

    headers = {
        "Authorization": f"Bearer {api_key}",
    }

    print(f"Deleting API key: {key_id}...", file=sys.stderr)

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.delete(
                f"{VENICE_BASE_URL}/api_keys/{key_id}",
                headers=headers
            )
            response.raise_for_status()
            
            print("\n" + "=" * 60, file=sys.stderr)
            print("API KEY DELETED", file=sys.stderr)
            print("=" * 60, file=sys.stderr)
            print(f"\n✓ Successfully deleted key: {key_id}", file=sys.stderr)
            print("\n" + "=" * 60 + "\n", file=sys.stderr)
            
            return True

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            print("Error: Authentication failed. Make sure you're using an ADMIN API key.", file=sys.stderr)
        elif e.response.status_code == 404:
            print(f"Error: API key not found: {key_id}", file=sys.stderr)
        elif e.response.status_code == 400:
            print("Error: Cannot delete this key. It may be protected or in use.", file=sys.stderr)
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
        description="Delete a Venice AI API key (irreversible)"
    )
    parser.add_argument(
        "--id", "-i",
        required=True,
        help="API key ID to delete"
    )
    parser.add_argument(
        "--force", "-f",
        action="store_true",
        help="Confirm deletion (required)"
    )

    args = parser.parse_args()
    delete_api_key(args.id, args.force)


if __name__ == "__main__":
    main()
