#!/usr/bin/env python3
"""
Shared API utilities for FileWave skill.

Consolidates common patterns:
- URL normalization
- Session creation with auth headers
- Safe API requests with error handling
- Exponential backoff retry logic
"""

import time
import requests
import sys
from typing import Callable, Tuple, Optional, Any


def normalize_server_url(server: str) -> str:
    """
    Ensure server URL has https:// prefix and no trailing slash.
    
    Args:
        server: Server hostname or URL (e.g., "filewave.company.com" or "https://filewave.company.com/")
    
    Returns:
        Normalized URL (e.g., "https://filewave.company.com")
    """
    if not server.startswith(("http://", "https://")):
        server = f"https://{server}"
    return server.rstrip("/")


def create_filewave_session(token: str) -> requests.Session:
    """
    Create requests session with FileWave API headers.
    
    Args:
        token: FileWave API token (Bearer token)
    
    Returns:
        Configured requests.Session with auth headers
    """
    session = requests.Session()
    session.headers.update({
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    })
    return session


def safe_api_request(
    session: requests.Session,
    method: str,
    url: str,
    on_error_callback: Optional[Callable] = None,
    **kwargs
) -> Tuple[bool, Optional[Any]]:
    """
    Execute API request with consistent error handling.
    
    Args:
        session: requests.Session configured with auth headers
        method: HTTP method ("get", "post", "patch", etc.)
        url: Full URL to request
        on_error_callback: Optional function to call on error (e.g., cache clearing)
        **kwargs: Additional args to pass to requests (json, params, etc.)
    
    Returns:
        Tuple of (success: bool, response_data: dict or None)
        - success=True, response_data=parsed JSON
        - success=False, response_data=None
    """
    try:
        # Route to correct HTTP method
        if method.lower() == "get":
            resp = session.get(url, timeout=10, **kwargs)
        elif method.lower() == "post":
            resp = session.post(url, timeout=10, **kwargs)
        elif method.lower() == "patch":
            resp = session.patch(url, timeout=10, **kwargs)
        elif method.lower() == "delete":
            resp = session.delete(url, timeout=10, **kwargs)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        # Raise for HTTP errors
        resp.raise_for_status()
        
        # Return JSON response
        try:
            return True, resp.json()
        except ValueError:
            # Some responses may be empty
            return True, None
    
    except requests.exceptions.Timeout:
        print(f"API timeout ({method} {url})", file=sys.stderr)
        if on_error_callback:
            on_error_callback()
        return False, None
    
    except requests.exceptions.HTTPError as e:
        print(f"API HTTP error ({method} {url}): {e.response.status_code}", file=sys.stderr)
        if on_error_callback:
            on_error_callback()
        return False, None
    
    except requests.exceptions.RequestException as e:
        print(f"API request error ({method} {url}): {e}", file=sys.stderr)
        if on_error_callback:
            on_error_callback()
        return False, None


def api_call_with_backoff(
    func: Callable[[], Tuple[Optional[bool], Optional[str]]],
    initial_backoff_ms: int = 100,
    max_backoff_ms: int = 2000,
    timeout_seconds: int = 120,
    verbose: bool = True
) -> Tuple[bool, str]:
    """
    Execute callable with exponential backoff retry logic.
    
    Designed for API calls that may be throttled (HTTP 429, 503, 504).
    Retries with exponential backoff until timeout or success.
    
    Args:
        func: Callable that returns (success: bool|None, message: str)
              - Returns (True, msg) → success, return immediately
              - Returns (False, msg) → permanent failure, return immediately
              - Returns (None, None) → retry signal, continue backoff
        initial_backoff_ms: Starting backoff delay (100ms default)
        max_backoff_ms: Maximum backoff delay (2000ms default)
        timeout_seconds: Overall timeout (120s default = 2 minutes)
        verbose: Print backoff messages to stderr
    
    Returns:
        Tuple of (success: bool, message: str)
    
    Example:
        def patch_device():
            resp = session.patch(url, json={"name": "New Name"})
            if resp.status_code == 200:
                return True, "Updated"
            elif resp.status_code in [429, 503, 504]:
                return None, None  # Retry signal
            else:
                return False, f"HTTP {resp.status_code}"
        
        success, msg = api_call_with_backoff(patch_device)
    """
    start_time = time.time()
    attempt = 0
    
    while True:
        elapsed = time.time() - start_time
        if elapsed > timeout_seconds:
            return False, f"Timeout after {timeout_seconds}s"
        
        # Call the function
        result = func()
        
        if result is None:
            return False, "Function returned None (expected tuple)"
        
        success, message = result
        
        # Success: return immediately
        if success is True:
            return True, message
        
        # Permanent failure: return immediately
        if success is False:
            return False, message
        
        # Retry signal (success is None): backoff and try again
        if success is None:
            delay_ms = min(initial_backoff_ms * (2 ** attempt), max_backoff_ms)
            delay_s = delay_ms / 1000.0
            
            if verbose:
                print(f"    Retrying with backoff {delay_s:.2f}s...", file=sys.stderr)
            
            time.sleep(delay_s)
            attempt += 1
            continue


# Example usage patterns (for development docs):

"""
Pattern 1: URL normalization
    server = normalize_server_url("filewave.company.com")
    # Result: "https://filewave.company.com"

Pattern 2: Session creation
    session = create_filewave_session(token)
    # Session now has Authorization header set

Pattern 3: Safe API request
    success, data = safe_api_request(
        session,
        "get",
        "https://filewave.company.com/api/devices/v1/devices/123"
    )
    if success:
        print(data["name"])

Pattern 4: Backoff retry
    def update_device():
        resp = session.patch(url, json={"name": "New"})
        if resp.status_code == 200:
            return True, "Success"
        elif resp.status_code in [429, 503, 504]:
            return None, None  # Retry
        else:
            return False, f"HTTP {resp.status_code}"
    
    success, msg = api_call_with_backoff(update_device)
"""
