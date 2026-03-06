#!/usr/bin/env python3
"""
Shared API client for Clarity Protocol skills.

Provides:
- API_BASE: Base URL for Clarity Protocol API
- get_headers(): Get HTTP headers including optional API key from env var
- api_get(): Perform GET request with error handling and rate limit management
- api_post(): Perform POST request with write API key authentication
"""

import os
import sys
import requests
from typing import Optional, Dict, Any


API_BASE = "https://clarityprotocol.io/api/v1"


def get_headers(write: bool = False) -> Dict[str, str]:
    """
    Get HTTP headers for API requests.

    Args:
        write: If True, use CLARITY_WRITE_KEY for write operations.
               If False, use CLARITY_API_KEY for read operations.

    Returns:
        Dict with Accept/Content-Type headers and optional X-API-Key header
    """
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    if write:
        api_key = os.environ.get("CLARITY_WRITE_KEY")
        if not api_key:
            print("Error: CLARITY_WRITE_KEY environment variable not set.", file=sys.stderr)
            print("Set it with: export CLARITY_WRITE_KEY=your_write_key_here", file=sys.stderr)
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

        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After", "unknown")
            print(f"Error: Rate limit exceeded.", file=sys.stderr)
            print(f"Retry after: {retry_after} seconds", file=sys.stderr)
            sys.exit(1)

        if response.status_code == 404:
            print(f"Error: Resource not found: {endpoint}", file=sys.stderr)
            sys.exit(1)

        response.raise_for_status()
        return response.json()

    except requests.exceptions.Timeout:
        print(f"Error: Request timed out after 30 seconds.", file=sys.stderr)
        sys.exit(1)

    except requests.exceptions.RequestException as e:
        print(f"Error: API request failed: {e}", file=sys.stderr)
        sys.exit(1)


def api_post(endpoint: str, data: Dict[str, Any]) -> Any:
    """
    Perform POST request to Clarity Protocol API with write authentication.

    Requires CLARITY_WRITE_KEY environment variable.

    Args:
        endpoint: API endpoint (e.g., "/hypotheses")
        data: Request body as dict

    Returns:
        Parsed JSON response

    Raises:
        SystemExit: On error (prints user-friendly message and exits)
    """
    url = API_BASE + endpoint

    try:
        response = requests.post(
            url,
            json=data,
            headers=get_headers(write=True),
            timeout=30
        )

        if response.status_code == 403:
            print("Error: Invalid or missing write API key.", file=sys.stderr)
            print("Set CLARITY_WRITE_KEY environment variable with a valid write key.", file=sys.stderr)
            sys.exit(1)

        if response.status_code == 422:
            detail = response.json().get("detail", "Validation error")
            print(f"Error: {detail}", file=sys.stderr)
            sys.exit(1)

        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After", "unknown")
            print(f"Error: Rate limit exceeded (max 10 submissions/day).", file=sys.stderr)
            print(f"Retry after: {retry_after} seconds", file=sys.stderr)
            sys.exit(1)

        response.raise_for_status()
        return response.json()

    except requests.exceptions.Timeout:
        print(f"Error: Request timed out after 30 seconds.", file=sys.stderr)
        sys.exit(1)

    except requests.exceptions.RequestException as e:
        print(f"Error: API request failed: {e}", file=sys.stderr)
        sys.exit(1)
