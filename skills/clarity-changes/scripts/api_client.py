#!/usr/bin/env python3
"""
Shared API client for Clarity Protocol skills.

Provides:
- API_BASE: Base URL for Clarity Protocol API
- get_headers(): Get HTTP headers including optional API key from env var
- api_get(): Perform GET request with error handling and rate limit management
"""

import os
import sys
import requests
from typing import Optional, Dict, Any


API_BASE = "https://clarityprotocol.io/api/v1"


def get_headers() -> Dict[str, str]:
    """
    Get HTTP headers for API requests.

    Reads CLARITY_API_KEY from environment variable if present.

    Returns:
        Dict with Accept header and optional X-API-Key header
    """
    headers = {
        "Accept": "application/json"
    }

    api_key = os.environ.get("CLARITY_API_KEY")
    if api_key:
        headers["X-API-Key"] = api_key

    return headers


def api_get(endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
    """
    Perform GET request to Clarity Protocol API with error handling.

    Args:
        endpoint: API endpoint (e.g., "/variants" or "/variants/123")
        params: Optional query parameters

    Returns:
        Parsed JSON response

    Raises:
        SystemExit: On error (prints user-friendly message and exits)
    """
    url = API_BASE + endpoint

    try:
        response = requests.get(
            url,
            params=params,
            headers=get_headers(),
            timeout=30
        )

        # Handle rate limiting
        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After", "unknown")
            print(f"Error: Rate limit exceeded.", file=sys.stderr)
            print(f"Retry after: {retry_after} seconds", file=sys.stderr)
            print(f"\nTip: Set CLARITY_API_KEY environment variable for higher rate limits.", file=sys.stderr)
            print(f"  Anonymous: 10 requests/minute", file=sys.stderr)
            print(f"  With API key: 100 requests/minute", file=sys.stderr)
            print(f"\nGet your API key at: https://clarityprotocol.io", file=sys.stderr)
            sys.exit(1)

        # Handle not found
        if response.status_code == 404:
            print(f"Error: Resource not found: {endpoint}", file=sys.stderr)
            print(f"The requested resource does not exist.", file=sys.stderr)
            sys.exit(1)

        # Handle other errors
        response.raise_for_status()

        return response.json()

    except requests.exceptions.Timeout:
        print(f"Error: Request timed out after 30 seconds.", file=sys.stderr)
        print(f"The API server may be unavailable or under heavy load.", file=sys.stderr)
        sys.exit(1)

    except requests.exceptions.RequestException as e:
        print(f"Error: API request failed: {e}", file=sys.stderr)
        sys.exit(1)

    except ValueError as e:
        print(f"Error: Failed to parse API response as JSON: {e}", file=sys.stderr)
        sys.exit(1)
