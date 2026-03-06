# /// script
# requires-python = ">=3.10"
# dependencies = ["httpx"]
# ///
"""
Venice AI API Keys List

List all your API keys.
Requires an Admin API key.
API docs: https://docs.venice.ai
"""

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
        return dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return date_str


def list_api_keys() -> list:
    """List all API keys."""
    api_key = get_api_key()

    headers = {
        "Authorization": f"Bearer {api_key}",
    }

    print("Fetching API keys...", file=sys.stderr)

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.get(
                f"{VENICE_BASE_URL}/api_keys",
                headers=headers
            )
            response.raise_for_status()
            
            data = response.json()
            keys = data.get("data", [])
            
            # Pretty print the keys
            print("\n" + "=" * 70, file=sys.stderr)
            print("VENICE AI API KEYS", file=sys.stderr)
            print("=" * 70, file=sys.stderr)
            
            if not keys:
                print("\nNo API keys found.", file=sys.stderr)
            else:
                print(f"\nFound {len(keys)} API key(s):\n", file=sys.stderr)
                
                for i, key in enumerate(keys, 1):
                    key_id = key.get("id", "unknown")
                    name = key.get("name", "Unnamed")
                    key_type = key.get("apiKeyType", "unknown")
                    created = format_date(key.get("createdAt"))
                    last_used = format_date(key.get("lastUsedAt"))
                    
                    # Mask the key prefix if available
                    key_prefix = key.get("keyPrefix", "")
                    if key_prefix:
                        masked_key = f"{key_prefix}..."
                    else:
                        masked_key = "***"
                    
                    print(f"[{i}] {name}", file=sys.stderr)
                    print(f"    ID: {key_id}", file=sys.stderr)
                    print(f"    Type: {key_type}", file=sys.stderr)
                    print(f"    Key: {masked_key}", file=sys.stderr)
                    print(f"    Created: {created}", file=sys.stderr)
                    print(f"    Last Used: {last_used}", file=sys.stderr)
                    
                    # Show rate limits if available
                    rate_limits = key.get("rateLimits")
                    if rate_limits:
                        print(f"    Rate Limits: {rate_limits}", file=sys.stderr)
                    
                    print("", file=sys.stderr)
            
            print("=" * 70 + "\n", file=sys.stderr)
            
            # Also output as JSON for programmatic use
            print(json.dumps(data, indent=2, default=str))
            
            return keys

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            print("Error: Authentication failed. Make sure you're using an ADMIN API key.", file=sys.stderr)
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
    list_api_keys()


if __name__ == "__main__":
    main()

