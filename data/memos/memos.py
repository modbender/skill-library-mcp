# memos.py

import os
import json
import sys
import requests
from typing import Dict, Optional, Any
from requests.exceptions import RequestException, HTTPError, Timeout, ConnectionError

# Configuration
BASE_URL = os.getenv("MEMOS_URL")
TOKEN = os.getenv("MEMOS_TOKEN")

if not BASE_URL:
    raise RuntimeError("MEMOS_URL environment variable is not set.")
if not TOKEN:
    raise RuntimeError("MEMOS_TOKEN environment variable is not set.")

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
}

# Custom exception for Memos API errors
class MemosAPIError(Exception):
    """Exception raised for Memos API errors."""
    def __init__(self, message: str, status_code: Optional[int] = None, response: Optional[Dict] = None):
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(self.message)

# Helper to make requests with proper error handling
def _request(method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None) -> Any:
    """
    Make an HTTP request to the Memos API with comprehensive error handling.

    Args:
        method: HTTP method (GET, POST, DELETE, etc.)
        endpoint: API endpoint path
        data: Optional JSON payload
        params: Optional query parameters

    Returns:
        Parsed JSON response or empty dict for no-content responses

    Raises:
        MemosAPIError: For API-specific errors
        RequestException: For network/connection errors
    """
    url = f"{BASE_URL}{endpoint}"

    try:
        resp = requests.request(
            method,
            url,
            headers=HEADERS,
            json=data,
            params=params,
            timeout=30  # 30 second timeout
        )

        # Handle successful responses
        resp.raise_for_status()

        # Return empty dict for 204 No Content or empty responses
        if resp.status_code == 204 or not resp.content:
            return {}

        return resp.json()

    except HTTPError as e:
        # Try to extract error message from response
        error_msg = f"HTTP {e.response.status_code}: {e.response.reason}"
        try:
            error_data = e.response.json()
            if "message" in error_data:
                error_msg = f"{error_msg} - {error_data['message']}"
        except:
            pass
        raise MemosAPIError(error_msg, e.response.status_code, e.response.text)

    except Timeout:
        raise MemosAPIError(f"Request to {url} timed out after 30 seconds")

    except ConnectionError as e:
        raise MemosAPIError(f"Failed to connect to {BASE_URL}: {str(e)}")

    except RequestException as e:
        raise MemosAPIError(f"Request failed: {str(e)}")

# Command functions

def create(content: str, visibility: str = "PUBLIC") -> Dict[str, Any]:
    """
    Create a new memo with the #openclaw tag.

    Args:
        content: The memo content in Markdown format
        visibility: One of PRIVATE, PROTECTED, or PUBLIC (default: PUBLIC)

    Returns:
        Dictionary containing the created memo details

    Raises:
        MemosAPIError: If the API request fails
        ValueError: If visibility is invalid

    API Reference:
    https://usememos.com/docs/api/memoservice/CreateMemo
    """
    valid_visibilities = {"PRIVATE", "PROTECTED", "PUBLIC", "VISIBILITY_UNSPECIFIED"}
    if visibility.upper() not in valid_visibilities:
        raise ValueError(f"Invalid visibility '{visibility}'. Must be one of: {', '.join(valid_visibilities)}")

    # Append the tag to the content
    content_with_tag = f"{content}\n#openclaw"

    payload = {
        "content": content_with_tag,
        "visibility": visibility.upper()
    }

    return _request("POST", "/api/v1/memos", payload)


def get(memo_id: str) -> Dict[str, Any]:
    """
    Retrieve a memo by its ID.

    Args:
        memo_id: The memo ID (format: memos/{id} or just {id})

    Returns:
        Dictionary containing memo details

    Raises:
        MemosAPIError: If the memo doesn't exist or request fails

    API Reference:
    https://usememos.com/docs/api/memoservice/GetMemo
    """
    # Ensure memo_id has the correct format
    if not memo_id.startswith("memos/"):
        memo_id = f"memos/{memo_id}"

    return _request("GET", f"/api/v1/{memo_id}")


def delete(memo_id: str, force: bool = False) -> Dict[str, Any]:
    """
    Delete a memo by its ID.

    Args:
        memo_id: The memo ID (format: memos/{id} or just {id})
        force: If True, delete even if it has associated data (default: False)

    Returns:
        Empty dict on successful deletion

    Raises:
        MemosAPIError: If deletion fails

    API Reference:
    https://usememos.com/docs/api/memoservice/DeleteMemo
    """
    # Ensure memo_id has the correct format
    if not memo_id.startswith("memos/"):
        memo_id = f"memos/{memo_id}"

    params = {"force": str(force).lower()} if force else None
    return _request("DELETE", f"/api/v1/{memo_id}", params=params)


def list_memos(
    pageSize: int = 20,
    pageToken: Optional[str] = None,
    state: Optional[str] = None,
    orderBy: Optional[str] = None,
    filter: Optional[str] = None,
    showDeleted: Optional[bool] = None
) -> Dict[str, Any]:
    """
    List memos with pagination and optional filtering.

    Args:
        pageSize: Maximum number of memos to return (1-1000, default: 20)
        pageToken: Token from previous call for pagination
        state: Filter by state - NORMAL or ARCHIVED
        orderBy: Sort order (e.g., "pinned desc, display_time desc")
        filter: CEL expression filter
        showDeleted: Include deleted memos if True

    Returns:
        Dictionary with 'memos' array and 'nextPageToken' for pagination

    Raises:
        MemosAPIError: If the request fails
        ValueError: If pageSize is out of range

    API Reference:
    https://usememos.com/docs/api/memoservice/ListMemos
    """
    if not (1 <= pageSize <= 1000):
        raise ValueError(f"pageSize must be between 1 and 1000, got {pageSize}")

    valid_states = {"NORMAL", "ARCHIVED", "STATE_UNSPECIFIED"}
    if state and state.upper() not in valid_states:
        raise ValueError(f"Invalid state '{state}'. Must be one of: {', '.join(valid_states)}")

    params: Dict[str, str] = {"pageSize": str(pageSize)}

    if pageToken:
        params["pageToken"] = pageToken
    if state:
        params["state"] = state.upper()
    if orderBy:
        params["orderBy"] = orderBy
    if filter:
        params["filter"] = filter
    if showDeleted is not None:
        params["showDeleted"] = str(showDeleted).lower()

    return _request("GET", "/api/v1/memos", params=params)


# Entry point for OpenClaw skill dispatcher

def main(command: str, args: list[str]) -> Dict[str, Any]:
    """
    Main entry point for the memos skill commands.

    Args:
        command: The command to execute (create, get, delete, list)
        args: List of command arguments

    Returns:
        Result dictionary from the API

    Raises:
        ValueError: If command is unknown or args are invalid
        MemosAPIError: If API request fails
    """
    try:
        if command == "create":
            if len(args) < 1:
                raise ValueError("create requires at least 1 argument: <content> [visibility]")
            content = args[0]
            visibility = args[1] if len(args) > 1 else "PUBLIC"
            return create(content, visibility)

        elif command == "get":
            if len(args) != 1:
                raise ValueError("get requires exactly 1 argument: <memo_id>")
            return get(args[0])

        elif command == "delete":
            if len(args) < 1:
                raise ValueError("delete requires at least 1 argument: <memo_id> [force]")
            memo_id = args[0]
            force = args[1].lower() == "true" if len(args) > 1 else False
            return delete(memo_id, force)

        elif command == "list":
            page_size = int(args[0]) if args else 20
            return list_memos(pageSize=page_size)

        else:
            raise ValueError(f"Unknown command: {command}")

    except (ValueError, MemosAPIError) as e:
        # Re-raise our custom errors
        raise
    except Exception as e:
        # Wrap unexpected errors
        raise MemosAPIError(f"Unexpected error in {command}: {str(e)}")


if __name__ == "__main__":
    try:
        if len(sys.argv) < 2:
            print(json.dumps({
                "error": "No command provided",
                "usage": "python memos.py <command> [args...]",
                "commands": ["create", "get", "delete", "list"]
            }, indent=2))
            sys.exit(1)

        cmd = sys.argv[1]
        params = sys.argv[2:]
        result = main(cmd, params)
        print(json.dumps(result, indent=2))
        sys.exit(0)

    except MemosAPIError as e:
        error_output = {
            "error": "Memos API Error",
            "message": e.message,
        }
        if e.status_code:
            error_output["status_code"] = e.status_code
        if e.response:
            error_output["response"] = e.response
        print(json.dumps(error_output, indent=2), file=sys.stderr)
        sys.exit(1)

    except ValueError as e:
        print(json.dumps({
            "error": "Invalid arguments",
            "message": str(e)
        }, indent=2), file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        print(json.dumps({
            "error": "Unexpected error",
            "message": str(e)
        }, indent=2), file=sys.stderr)
        sys.exit(1)

