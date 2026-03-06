"""
DeepRead Device Flow Authentication

OAuth 2.0 Device Authorization Flow (RFC 8628) for AI agents.
Requests a device code, waits for user approval, and stores the
resulting API key as the DEEPREAD_API_KEY environment variable.

Only contacts: api.deepread.tech
"""

import json
import os
import sys
import time
from urllib.error import HTTPError
from urllib.request import Request, urlopen

API_BASE = "https://api.deepread.tech"


def request_device_code(agent_name: str = "clawdhub-agent") -> dict:
    """Request a device code and user code from the DeepRead API.

    POST /v1/agent/device/code
    Body: {"agent_name": "..."}  (optional, shown on approval screen)
    Returns: device_code, user_code, verification_uri,
             verification_uri_complete, expires_in, interval
    """
    req = Request(
        f"{API_BASE}/v1/agent/device/code",
        data=json.dumps({"agent_name": agent_name}).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(req) as resp:
        return json.loads(resp.read())


def poll_for_token(device_code: str, interval: int) -> str:
    """Poll until the user approves and we receive an API key.

    POST /v1/agent/device/token
    Body: {"device_code": "..."}
    Returns: api_key (on success) or error string
    """
    payload = json.dumps({"device_code": device_code}).encode()

    while True:
        req = Request(
            f"{API_BASE}/v1/agent/device/token",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(req) as resp:
                data = json.loads(resp.read())
        except HTTPError as exc:
            data = json.loads(exc.read())

        error = data.get("error")
        if not error:
            # api_key is returned exactly once — save it immediately
            return data["api_key"]
        if error == "authorization_pending":
            time.sleep(interval)
        elif error == "slow_down":
            interval += 5
            time.sleep(interval)
        else:
            print(f"Error: {error}", file=sys.stderr)
            sys.exit(1)


def store_api_key(api_key: str) -> None:
    """Store the API key as an environment variable for the current session only.

    Does NOT write to disk. The user can persist it manually using a
    secrets manager (recommended) or their shell profile.
    """
    os.environ["DEEPREAD_API_KEY"] = api_key
    print("DEEPREAD_API_KEY has been set for this session.")
    print()
    print("To persist across sessions (user action):")
    print("  Option 1 (recommended): Store in a secrets manager (OS keychain, 1Password CLI, pass)")
    print("  Option 2: Manually add 'export DEEPREAD_API_KEY=\"...\"' to ~/.zshrc")


def main() -> None:
    """Run the complete device flow."""
    print("Requesting device code...")
    device = request_device_code()

    print()
    print(f"Open: {device['verification_uri']}")
    print(f"Enter code: {device['user_code']}")
    if device.get("verification_uri_complete"):
        print(f"Or open directly: {device['verification_uri_complete']}")
    print()
    print("Waiting for approval...")

    api_key = poll_for_token(device["device_code"], device.get("interval", 5))

    print()
    print("Approved!")
    store_api_key(api_key)


if __name__ == "__main__":
    main()
