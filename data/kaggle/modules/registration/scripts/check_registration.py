#!/usr/bin/env python3
"""Check that all three Kaggle credentials are configured.

Checks for:
  1. KAGGLE_USERNAME — Kaggle handle
  2. KAGGLE_KEY — Legacy 32-char hex API key
  3. KAGGLE_API_TOKEN — KGAT-prefixed scoped token

Sources checked (in order):
  - Environment variables (including from .env via python-dotenv)
  - ~/.kaggle/kaggle.json (for username + legacy key)

Usage:
    python3 scripts/check_registration.py

Exit codes:
    0 — All 3 credentials found
    1 — One or more credentials missing
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


def _read_kaggle_json() -> dict:
    """Read ~/.kaggle/kaggle.json if it exists and is valid."""
    kaggle_json = Path.home() / ".kaggle" / "kaggle.json"
    if not kaggle_json.exists():
        return {}
    try:
        creds = json.loads(kaggle_json.read_text())
        # Check permissions
        mode = oct(kaggle_json.stat().st_mode)[-3:]
        if mode != "600":
            print(f"[WARN] {kaggle_json} permissions are {mode}, should be 600")
            print(f"       Run: chmod 600 {kaggle_json}")
        return creds
    except (json.JSONDecodeError, KeyError):
        print(f"[WARN] {kaggle_json} exists but is malformed")
        return {}


def check_registration() -> bool:
    """Check for all 3 Kaggle credentials. Returns True if all found."""
    kaggle_json = _read_kaggle_json()
    all_ok = True

    # --- KAGGLE_USERNAME ---
    username = os.getenv("KAGGLE_USERNAME") or kaggle_json.get("username")
    if username:
        source = "env" if os.getenv("KAGGLE_USERNAME") else "kaggle.json"
        print(f"[OK] KAGGLE_USERNAME: {username} (from {source})")
    else:
        print("[MISSING] KAGGLE_USERNAME")
        print("          Your Kaggle handle. Set it in .env or create an account at:")
        print("          https://www.kaggle.com/account/login")
        all_ok = False

    # --- KAGGLE_KEY ---
    key = os.getenv("KAGGLE_KEY") or os.getenv("KAGGLE_TOKEN") or kaggle_json.get("key")
    if key:
        if os.getenv("KAGGLE_TOKEN") and not os.getenv("KAGGLE_KEY"):
            print("[WARN] Found KAGGLE_TOKEN but tools expect KAGGLE_KEY")
            print("       Auto-mapping: KAGGLE_KEY = KAGGLE_TOKEN")
        source = "env" if (os.getenv("KAGGLE_KEY") or os.getenv("KAGGLE_TOKEN")) else "kaggle.json"
        # Mask all but last 4 chars
        masked = "*" * max(0, len(key) - 4) + key[-4:] if len(key) > 4 else "****"
        print(f"[OK] KAGGLE_KEY: {masked} (from {source})")
    else:
        print("[MISSING] KAGGLE_KEY")
        print("          Legacy 32-char hex API key. Generate at:")
        print("          https://www.kaggle.com/settings → API → Create New Token")
        all_ok = False

    # --- KAGGLE_API_TOKEN ---
    api_token = os.getenv("KAGGLE_API_TOKEN")
    if api_token:
        masked = api_token[:5] + "*" * max(0, len(api_token) - 9) + api_token[-4:] if len(api_token) > 9 else "****"
        print(f"[OK] KAGGLE_API_TOKEN: {masked} (from env)")
    else:
        print("[MISSING] KAGGLE_API_TOKEN")
        print("          KGAT-prefixed scoped token. Generate at:")
        print("          https://www.kaggle.com/settings → API → Create API Token")
        print("          (This is a different button from 'Create New Token')")
        all_ok = False

    # --- Summary ---
    print()
    if all_ok:
        print("All 3 Kaggle credentials found. You're ready to go!")
    else:
        print("One or more credentials are missing. Follow the instructions above,")
        print("then save all three to your .env file:")
        print()
        print("  KAGGLE_USERNAME=your_username")
        print("  KAGGLE_KEY=your_32_char_hex_key")
        print("  KAGGLE_API_TOKEN=KGAT_your_scoped_token")
        print()
        print("Full setup guide: skills/kaggle/modules/registration/references/kaggle-setup.md")

    return all_ok


if __name__ == "__main__":
    ok = check_registration()
    sys.exit(0 if ok else 1)
