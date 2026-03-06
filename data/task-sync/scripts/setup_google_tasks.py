#!/usr/bin/env python3
"""
Set up or refresh Google Tasks OAuth credentials.
"""

import json
import os
from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/tasks"]
BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG_FILE = BASE_DIR / "config.json"
DEFAULT_CREDENTIALS_FILE = BASE_DIR / "config" / "google_credentials.json"
DEFAULT_TOKEN_FILE = BASE_DIR / "data" / "google_token.json"


def to_abs_path(path_value):
    path = Path(path_value).expanduser()
    if path.is_absolute():
        return path
    return (BASE_DIR / path).resolve()


def load_config():
    if not DEFAULT_CONFIG_FILE.exists():
        return {}
    try:
        with open(DEFAULT_CONFIG_FILE) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def resolve_paths():
    config = load_config()

    credentials_raw = os.environ.get(
        "GOOGLE_CREDENTIALS_FILE", str(DEFAULT_CREDENTIALS_FILE)
    )
    token_raw = os.environ.get("GOOGLE_TOKEN_FILE", config.get("google_token", ""))
    if not token_raw:
        token_raw = str(DEFAULT_TOKEN_FILE)

    return to_abs_path(credentials_raw), to_abs_path(token_raw)


def main():
    credentials_file, token_file = resolve_paths()

    print("\nGoogle Tasks OAuth setup\n")
    print(f"Credentials file: {credentials_file}")
    print(f"Token output:     {token_file}\n")

    if not credentials_file.exists():
        print("Credentials file was not found.")
        print(
            "Create a Google OAuth desktop client JSON at "
            f"{credentials_file}, or set GOOGLE_CREDENTIALS_FILE."
        )
        return

    if token_file.exists():
        print("Removing existing token file...")
        token_file.unlink()

    flow = InstalledAppFlow.from_client_secrets_file(str(credentials_file), SCOPES)

    auth_url, _ = flow.authorization_url(prompt="consent")

    print("=" * 80)
    print("Open this URL in your browser and approve access:")
    print("=" * 80)
    print(auth_url)
    print("=" * 80)
    print("\nAfter authorization, copy the code from the redirect page.\n")

    code = input("Paste authorization code: ").strip()
    if not code:
        print("No authorization code provided.")
        return

    flow.fetch_token(code=code)
    creds = flow.credentials

    token_file.parent.mkdir(parents=True, exist_ok=True)
    token_data = {
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "scopes": creds.scopes,
        "expiry": creds.expiry.isoformat() if creds.expiry else None,
    }

    with open(token_file, "w") as f:
        json.dump(token_data, f, indent=2)

    print(f"\nOAuth setup completed. Token saved to: {token_file}")


if __name__ == "__main__":
    main()
