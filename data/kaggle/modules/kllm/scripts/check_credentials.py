#!/usr/bin/env python3
"""Check that Kaggle credentials are configured and valid.

Checks (in order):
  1. KAGGLE_API_TOKEN env var (new style, preferred by kagglehub)
  2. KAGGLE_USERNAME + KAGGLE_KEY env vars (legacy)
  3. KAGGLE_TOKEN env var (common misconfiguration — auto-maps to KAGGLE_KEY)
  4. .env file in current directory
  5. ~/.kaggle/kaggle.json

If credentials are found via env vars but ~/.kaggle/kaggle.json is missing,
this script will create it so that both kagglehub and kaggle-cli work.

Usage:
    python scripts/check_credentials.py
"""

import json
import os
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass  # dotenv not installed; skip .env loading


def _ensure_kaggle_json(username: str, key: str) -> None:
    """Create ~/.kaggle/kaggle.json if it doesn't exist."""
    kaggle_json = Path.home() / ".kaggle" / "kaggle.json"
    if kaggle_json.exists():
        return
    kaggle_json.parent.mkdir(parents=True, exist_ok=True)
    kaggle_json.write_text(json.dumps({"username": username, "key": key}))
    kaggle_json.chmod(0o600)
    print(f"[INFO] Created {kaggle_json} (chmod 600)")


def check_credentials() -> bool:
    """Check for valid Kaggle credentials. Returns True if found."""
    # 1. Check new-style KAGGLE_API_TOKEN env var (preferred by kagglehub)
    api_token = os.getenv("KAGGLE_API_TOKEN")
    if api_token:
        print("[OK] Credentials found via KAGGLE_API_TOKEN environment variable")
        return True

    # 2. Check legacy KAGGLE_USERNAME + KAGGLE_KEY env vars
    username = os.getenv("KAGGLE_USERNAME")
    key = os.getenv("KAGGLE_KEY")
    if username and key:
        print(f"[OK] Credentials found via KAGGLE_USERNAME + KAGGLE_KEY (user: {username})")
        _ensure_kaggle_json(username, key)
        return True

    # 3. Check for common misconfiguration: KAGGLE_TOKEN instead of KAGGLE_KEY
    #    Some environments set KAGGLE_TOKEN, but kagglehub expects KAGGLE_API_TOKEN
    #    and kaggle-cli expects KAGGLE_KEY. Auto-map if found.
    token = os.getenv("KAGGLE_TOKEN")
    if token and username:
        print(f"[WARN] Found KAGGLE_TOKEN but tools expect KAGGLE_KEY or KAGGLE_API_TOKEN")
        print(f"       Auto-mapping: KAGGLE_KEY=KAGGLE_TOKEN, KAGGLE_API_TOKEN=KAGGLE_TOKEN")
        os.environ["KAGGLE_KEY"] = token
        os.environ["KAGGLE_API_TOKEN"] = token
        _ensure_kaggle_json(username, token)
        print(f"[OK] Credentials configured (user: {username})")
        return True
    elif token and not username:
        print(f"[WARN] Found KAGGLE_TOKEN but KAGGLE_USERNAME is not set")
        print(f"       Set KAGGLE_USERNAME to use token-based auth")

    # 4. Check ~/.kaggle/kaggle.json
    kaggle_json = Path.home() / ".kaggle" / "kaggle.json"
    if kaggle_json.exists():
        try:
            creds = json.loads(kaggle_json.read_text())
            if "username" in creds and "key" in creds:
                print(f"[OK] Credentials found in {kaggle_json} (user: {creds['username']})")

                # Check permissions
                mode = oct(kaggle_json.stat().st_mode)[-3:]
                if mode != "600":
                    print(f"[WARN] File permissions are {mode}, should be 600")
                    print(f"       Run: chmod 600 {kaggle_json}")

                return True
        except (json.JSONDecodeError, KeyError):
            print(f"[ERROR] {kaggle_json} exists but is malformed")
            return False

    print("[ERROR] No Kaggle credentials found.")
    print()
    print("To fix, do ONE of the following:")
    print()
    print("  Option 1: Set KAGGLE_API_TOKEN (recommended for kagglehub)")
    print('    export KAGGLE_API_TOKEN="your_api_token"')
    print()
    print("  Option 2: Set legacy environment variables")
    print('    export KAGGLE_USERNAME="your_username"')
    print('    export KAGGLE_KEY="your_api_key"')
    print()
    print("  Option 3: Create kaggle.json")
    print("    mkdir -p ~/.kaggle")
    print('    echo \'{"username":"your_username","key":"your_api_key"}\' > ~/.kaggle/kaggle.json')
    print("    chmod 600 ~/.kaggle/kaggle.json")
    print()
    print("  Get your API key at: https://www.kaggle.com/settings (API section)")
    return False


if __name__ == "__main__":
    ok = check_credentials()
    sys.exit(0 if ok else 1)
