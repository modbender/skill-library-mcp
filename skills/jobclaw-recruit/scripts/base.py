#!/usr/bin/env python3
"""
Base module for recruiter CLI scripts.
Handles token management, authentication, and HTTP requests.
"""
import os
import json
import urllib.request
import urllib.error

# Token storage location
TOKEN_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".token")

# Default API endpoint
DEFAULT_API = "https://api.jobclaw.ai"


class TokenManager:
    """Manages user authentication tokens."""

    def __init__(self, api_url=DEFAULT_API, user_type="RECRUITER"):
        self.api_url = api_url
        self.user_type = user_type
        self._token = None

    def get_token(self):
        """Get valid token (from cache, file, or create new)."""
        # 1. Return cached token if available
        if self._token:
            return self._token

        # 2. Try to load from file
        if os.path.exists(TOKEN_FILE):
            try:
                with open(TOKEN_FILE, 'r') as f:
                    saved_token = f.read().strip()

                # Verify token is still valid
                if self._verify_token(saved_token):
                    self._token = saved_token
                    return self._token
            except Exception:
                pass

        # 3. Create new token
        self._token = self._create_token()
        return self._token

    def _verify_token(self, token):
        """Verify if token is valid."""
        try:
            result = http_request(
                f"{self.api_url}/auth/verify",
                method="GET",
                token=token
            )
            return result.get("result", {}).get("valid", False)
        except Exception:
            return False

    def _create_token(self):
        """Create a new authentication token."""
        result = http_request(
            f"{self.api_url}/auth/token",
            method="POST",
            data={"userType": self.user_type}
        )

        if "result" not in result:
            raise Exception(f"Failed to create token: {result.get('error', 'Unknown error')}")

        new_token = result["result"]["token"]

        # Save token to file
        try:
            with open(TOKEN_FILE, 'w') as f:
                f.write(new_token)
        except Exception:
            pass  # Non-critical if we can't save

        return new_token

    def clear_token(self):
        """Clear cached token and file."""
        self._token = None
        if os.path.exists(TOKEN_FILE):
            try:
                os.remove(TOKEN_FILE)
            except Exception:
                pass


def http_request(url, method="GET", data=None, token=None):
    """
    Send HTTP request and return parsed JSON response.

    Args:
        url: Full URL to request
        method: HTTP method (GET, POST, PUT, DELETE)
        data: Request body data (will be JSON encoded)
        token: Optional authentication token

    Returns:
        dict: Parsed JSON response

    Raises:
        Exception: If request fails
    """
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "JobClaw-Skill-Script/2.0"
    }

    if token:
        headers["Authorization"] = f"Bearer {token}"

    body = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req) as resp:
            response_data = json.loads(resp.read().decode("utf-8"))

            # Check if response indicates success
            if not response_data.get("success", True):
                raise Exception(response_data.get("error", "Request failed"))

            return response_data

    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        try:
            error_data = json.loads(error_body)
            error_msg = error_data.get("message", error_body)
        except Exception:
            error_msg = error_body

        raise Exception(f"HTTP {e.code}: {error_msg}")

    except urllib.error.URLError as e:
        raise Exception(f"Connection error: {e.reason}")


class AuthenticatedClient:
    """HTTP client with automatic token management."""

    def __init__(self, api_url=DEFAULT_API, user_type="RECRUITER"):
        self.api_url = api_url
        self.token_manager = TokenManager(api_url, user_type)

    def request(self, endpoint, method="GET", data=None, retry_auth=True):
        """
        Send authenticated request with automatic token refresh.

        Args:
            endpoint: API endpoint (e.g., "/jobs")
            method: HTTP method
            data: Request body data
            retry_auth: Whether to retry with new token if auth fails

        Returns:
            dict: Response data
        """
        url = f"{self.api_url}{endpoint}"
        token = self.token_manager.get_token()

        try:
            return http_request(url, method, data, token)

        except Exception as e:
            error_msg = str(e)

            # If authentication failed and retry is enabled, get new token and retry
            if retry_auth and ("401" in error_msg or "Unauthorized" in error_msg):
                self.token_manager.clear_token()
                token = self.token_manager.get_token()
                return http_request(url, method, data, token)

            raise

    def get(self, endpoint):
        """Send GET request."""
        return self.request(endpoint, "GET")

    def post(self, endpoint, data):
        """Send POST request."""
        return self.request(endpoint, "POST", data)

    def put(self, endpoint, data):
        """Send PUT request."""
        return self.request(endpoint, "PUT", data)

    def delete(self, endpoint):
        """Send DELETE request."""
        return self.request(endpoint, "DELETE")


def format_response(data, include_token=False):
    """
    Format response data for output.

    Args:
        data: Response data from API
        include_token: Whether to include token in output

    Returns:
        dict: Formatted response
    """
    response = {
        "success": data.get("success", True),
        "result": data.get("result")
    }

    if include_token:
        # This will be set by the calling script
        pass

    if "error" in data:
        response["error"] = data["error"]

    return response
