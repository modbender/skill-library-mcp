#!/usr/bin/env python3
"""
Set up or refresh TickTick OAuth credentials.
"""

from datetime import datetime, timezone
import json
import os
from pathlib import Path

import requests
from urllib.parse import urlencode

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG_FILE = BASE_DIR / "config.json"
DEFAULT_CREDENTIALS_FILE = BASE_DIR / "config" / "ticktick_creds.json"
DEFAULT_TOKEN_FILE = BASE_DIR / "data" / "ticktick_token.json"


def to_abs_path(path_value):
    path = Path(path_value).expanduser()
    if path.is_absolute():
        return path
    return (BASE_DIR / path).resolve()


def load_repo_config():
    if not DEFAULT_CONFIG_FILE.exists():
        return {}
    try:
        with open(DEFAULT_CONFIG_FILE) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def resolve_paths():
    config = load_repo_config()
    credentials_raw = os.environ.get(
        "TICKTICK_CREDENTIALS_FILE", str(DEFAULT_CREDENTIALS_FILE)
    )
    token_raw = os.environ.get("TICKTICK_TOKEN_FILE", config.get("ticktick_token", ""))
    if not token_raw:
        token_raw = str(DEFAULT_TOKEN_FILE)
    return to_abs_path(credentials_raw), to_abs_path(token_raw)


def load_credentials(credentials_file):
    with open(credentials_file) as f:
        return json.load(f)


def save_token(token_data, token_file):
    token_file.parent.mkdir(parents=True, exist_ok=True)
    with open(token_file, "w") as f:
        json.dump(token_data, f, indent=2)
    print(f"Token saved to: {token_file}")


def get_authorization_code(creds):
    auth_url = "https://ticktick.com/oauth/authorize"
    params = {
        "client_id": creds["client_id"],
        "response_type": "code",
        "scope": "tasks:read tasks:write",
        "redirect_uri": creds["redirect_uri"],
    }

    full_url = f"{auth_url}?{urlencode(params)}"

    print("\n" + "=" * 80)
    print("Open this URL in your browser and approve access:")
    print("=" * 80)
    print(full_url)
    print("=" * 80)
    print("\nAfter authorization, copy the value of `code` from the redirect URL.")
    print(f"Example: {creds['redirect_uri']}?code=YOUR_CODE\n")

    auth_code = input("Paste authorization code: ").strip()
    return auth_code


def exchange_code_for_token(creds, auth_code):
    token_url = "https://ticktick.com/oauth/token"

    data = {
        "client_id": creds["client_id"],
        "client_secret": creds["client_secret"],
        "code": auth_code,
        "grant_type": "authorization_code",
        "redirect_uri": creds["redirect_uri"],
        "scope": "tasks:read tasks:write",
    }

    print("\nRequesting access token...")
    response = requests.post(token_url, data=data, timeout=30)

    if response.status_code == 200:
        token_data = response.json()
        print("Access token received.")
        return token_data

    print(f"Failed to get token ({response.status_code}): {response.text}")
    return None


def main():
    credentials_file, token_file = resolve_paths()

    print("\nTickTick OAuth setup\n")
    print(f"Credentials file: {credentials_file}")
    print(f"Token output:     {token_file}\n")

    if not credentials_file.exists():
        print("Credentials file was not found.")
        print(
            "Create config/ticktick_creds.json from the example file, "
            "or set TICKTICK_CREDENTIALS_FILE."
        )
        return

    creds = load_credentials(credentials_file)
    required = {"client_id", "client_secret", "redirect_uri"}
    missing = sorted(required - set(creds))
    if missing:
        print(f"Credentials file is missing fields: {', '.join(missing)}")
        return

    if token_file.exists():
        choice = input("Existing token found. Re-authorize? (y/N): ").strip().lower()
        if choice != "y":
            print("Keeping existing token file.")
            return

    auth_code = get_authorization_code(creds)
    if not auth_code:
        print("No authorization code provided.")
        return

    token_data = exchange_code_for_token(creds, auth_code)
    if token_data:
        token_data["created_at"] = datetime.now(timezone.utc).isoformat()
        save_token(token_data, token_file)
        print("\nSetup completed. You can run `python sync.py` now.")
        return
    print("\nSetup failed. Check credentials and network access.")


if __name__ == "__main__":
    main()
