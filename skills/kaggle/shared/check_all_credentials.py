#!/usr/bin/env python3
"""Unified Kaggle credential checker.

Combines the best of all credential checking implementations:
- Checks all 3 credentials (USERNAME, KEY, API_TOKEN) like check_registration.py
- Auto-maps KAGGLE_TOKEN → KAGGLE_KEY like check_credentials.py
- Loads .env via dotenv if available
- Reads ~/.kaggle/kaggle.json as fallback
- Returns structured JSON output for easy parsing
- Never prints actual credential values — only masked status

Usage:
    python3 skills/kaggle/shared/check_all_credentials.py
    python3 skills/kaggle/shared/check_all_credentials.py --json

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
    pass


def _read_kaggle_json() -> dict:
    """Read ~/.kaggle/kaggle.json if it exists and is valid."""
    kaggle_json = Path.home() / ".kaggle" / "kaggle.json"
    if not kaggle_json.exists():
        return {}
    try:
        creds = json.loads(kaggle_json.read_text())
        mode = oct(kaggle_json.stat().st_mode)[-3:]
        if mode != "600":
            print(f"[WARN] {kaggle_json} permissions are {mode}, should be 600")
            print(f"       Run: chmod 600 {kaggle_json}")
        return creds
    except (json.JSONDecodeError, KeyError):
        print(f"[WARN] {kaggle_json} exists but is malformed")
        return {}


def _mask(value: str, prefix_len: int = 0) -> str:
    """Mask a credential value, showing only first prefix_len and last 4 chars."""
    if not value:
        return "****"
    if len(value) <= prefix_len + 4:
        return "****"
    return value[:prefix_len] + "*" * max(0, len(value) - prefix_len - 4) + value[-4:]


def _ensure_kaggle_json(username: str, key: str) -> None:
    """Create ~/.kaggle/kaggle.json if it doesn't exist."""
    kaggle_json = Path.home() / ".kaggle" / "kaggle.json"
    if kaggle_json.exists():
        return
    kaggle_json.parent.mkdir(parents=True, exist_ok=True)
    kaggle_json.write_text(json.dumps({"username": username, "key": key}))
    kaggle_json.chmod(0o600)
    print(f"[INFO] Created {kaggle_json} (chmod 600)")


def check_all_credentials(output_json: bool = False) -> bool:
    """Check for all 3 Kaggle credentials. Returns True if all found."""
    kaggle_json_data = _read_kaggle_json()
    results = {}
    all_ok = True

    # --- Auto-map KAGGLE_TOKEN → KAGGLE_KEY ---
    if os.getenv("KAGGLE_TOKEN") and not os.getenv("KAGGLE_KEY"):
        print("[WARN] Found KAGGLE_TOKEN but tools expect KAGGLE_KEY")
        print("       Auto-mapping: KAGGLE_KEY = KAGGLE_TOKEN")
        os.environ["KAGGLE_KEY"] = os.environ["KAGGLE_TOKEN"]

    # --- KAGGLE_USERNAME ---
    username = os.getenv("KAGGLE_USERNAME") or kaggle_json_data.get("username")
    if username:
        source = "env" if os.getenv("KAGGLE_USERNAME") else "kaggle.json"
        results["KAGGLE_USERNAME"] = {"status": "OK", "value": username, "source": source}
        print(f"[OK] KAGGLE_USERNAME: {username} (from {source})")
    else:
        results["KAGGLE_USERNAME"] = {"status": "MISSING", "value": None, "source": None}
        print("[MISSING] KAGGLE_USERNAME")
        print("          Your Kaggle handle. Set it in .env or create an account at:")
        print("          https://www.kaggle.com/account/login")
        all_ok = False

    # --- KAGGLE_KEY ---
    key = os.getenv("KAGGLE_KEY") or kaggle_json_data.get("key")
    if key:
        source = "env" if os.getenv("KAGGLE_KEY") else "kaggle.json"
        results["KAGGLE_KEY"] = {"status": "OK", "value": _mask(key), "source": source}
        print(f"[OK] KAGGLE_KEY: {_mask(key)} (from {source})")
        # Ensure kaggle.json exists for CLI compatibility
        if username:
            _ensure_kaggle_json(username, key)
    else:
        results["KAGGLE_KEY"] = {"status": "MISSING", "value": None, "source": None}
        print("[MISSING] KAGGLE_KEY")
        print("          Legacy 32-char hex API key. Generate at:")
        print("          https://www.kaggle.com/settings -> API -> Create New Token")
        all_ok = False

    # --- KAGGLE_API_TOKEN ---
    api_token = os.getenv("KAGGLE_API_TOKEN")
    if api_token:
        results["KAGGLE_API_TOKEN"] = {"status": "OK", "value": _mask(api_token, 5), "source": "env"}
        print(f"[OK] KAGGLE_API_TOKEN: {_mask(api_token, 5)} (from env)")
    else:
        results["KAGGLE_API_TOKEN"] = {"status": "MISSING", "value": None, "source": None}
        print("[MISSING] KAGGLE_API_TOKEN")
        print("          KGAT-prefixed scoped token. Generate at:")
        print("          https://www.kaggle.com/settings -> API -> Create API Token")
        print("          (This is a different button from 'Create New Token')")
        all_ok = False

    # --- Summary ---
    print()
    if all_ok:
        print("All 3 Kaggle credentials found. You're ready to go!")
    else:
        found = sum(1 for r in results.values() if r["status"] == "OK")
        print(f"{found}/3 credentials found. Missing credentials need to be configured.")
        print()
        print("Save all three to your .env file:")
        print()
        print("  KAGGLE_USERNAME=your_username")
        print("  KAGGLE_KEY=your_32_char_hex_key")
        print("  KAGGLE_API_TOKEN=KGAT_your_scoped_token")
        print()
        print("Full setup guide: skills/kaggle/modules/registration/references/kaggle-setup.md")

    if output_json:
        print()
        print("--- JSON ---")
        print(json.dumps(results, indent=2))

    return all_ok


if __name__ == "__main__":
    json_mode = "--json" in sys.argv
    ok = check_all_credentials(output_json=json_mode)
    sys.exit(0 if ok else 1)
