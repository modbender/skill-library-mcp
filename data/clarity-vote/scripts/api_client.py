#!/usr/bin/env python3
"""
Shared API client for Clarity Protocol skills (read + write).

Provides:
- API_BASE: Base URL for Clarity Protocol API
- get_headers(): Get HTTP headers including optional API key from env var
- api_get(): Perform GET request with error handling
- api_post(): Perform POST request with write API key authentication
"""

import os
import sys
import requests
from typing import Optional, Dict, Any


API_BASE = "https://clarityprotocol.io/api/v1"


def get_headers(write=False) -> Dict[str, str]:
    """
    Get HTTP headers for API requests.

    Args:
        write: If True, requires CLARITY_WRITE_API_KEY for write operations

    Returns:
        Dict with Accept header and API key header
    """
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    if write:
        api_key = os.environ.get("CLARITY_WRITE_API_KEY")
        if not api_key:
            print("Error: CLARITY_WRITE_API_KEY environment variable is required for write operations.", file=sys.stderr)
            print("\nSet it with:", file=sys.stderr)
            print("  export CLARITY_WRITE_API_KEY=your_write_key_here", file=sys.stderr)
            sys.exit(1)
        headers["X-API-Key"] = api_key
    else:
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
    """
    url = API_BASE + endpoint

    try:
        response = requests.get(
            url,
            params=params,
            headers=get_headers(),
            timeout=30
        )

        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After", "unknown")
            print(f"Error: Rate limit exceeded. Retry after {retry_after} seconds.", file=sys.stderr)
            sys.exit(1)

        if response.status_code == 404:
            print(f"Error: Resource not found: {endpoint}", file=sys.stderr)
            sys.exit(1)

        response.raise_for_status()
        return response.json()

    except requests.exceptions.Timeout:
        print("Error: Request timed out after 30 seconds.", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"Error: API request failed: {e}", file=sys.stderr)
        sys.exit(1)


def api_post(endpoint: str, data: Dict[str, Any]) -> Any:
    """
    Perform POST request to Clarity Protocol API with write API key.

    Args:
        endpoint: API endpoint (e.g., "/variants/1/annotations")
        data: JSON body to send

    Returns:
        Parsed JSON response
    """
    import json
    url = API_BASE + endpoint

    try:
        response = requests.post(
            url,
            json=data,
            headers=get_headers(write=True),
            timeout=30
        )

        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After", "unknown")
            print(f"Error: Rate limit exceeded. Retry after {retry_after} seconds.", file=sys.stderr)
            sys.exit(1)

        if response.status_code == 403:
            print("Error: Invalid write API key. Check CLARITY_WRITE_API_KEY.", file=sys.stderr)
            sys.exit(1)

        if response.status_code == 404:
            print(f"Error: Resource not found: {endpoint}", file=sys.stderr)
            sys.exit(1)

        if response.status_code == 409:
            detail = response.json().get("detail", {})
            print(f"Error: Conflict — {detail.get('message', 'Resource already exists')}", file=sys.stderr)
            if isinstance(detail, dict) and "existing_vote" in detail:
                print(f"Existing vote: {json.dumps(detail['existing_vote'], indent=2)}", file=sys.stderr)
            sys.exit(1)

        if response.status_code == 422:
            detail = response.json().get("detail", "Validation error")
            print(f"Error: {detail}", file=sys.stderr)
            sys.exit(1)

        response.raise_for_status()
        return response.json()

    except requests.exceptions.Timeout:
        print("Error: Request timed out after 30 seconds.", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"Error: API request failed: {e}", file=sys.stderr)
        sys.exit(1)
