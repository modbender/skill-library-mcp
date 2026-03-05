#!/usr/bin/env python3
"""
approve_pairing.py - Approve a pending DM pairing request without the openclaw CLI.

Usage:
    python3 approve_pairing.py <channel> <code>
    python3 approve_pairing.py telegram PWVW264M

Supported channels: telegram, whatsapp, signal, imessage, discord, slack, feishu
"""

import json
import os
import sys
from pathlib import Path


def resolve_credentials_dir() -> Path:
    return Path(os.environ.get("OPENCLAW_CREDENTIALS_DIR", Path.home() / ".openclaw" / "credentials"))


def load_json(path: Path, fallback: dict) -> dict:
    if not path.exists():
        return fallback
    with open(path) as f:
        return json.load(f)


def write_json(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def approve(channel: str, code: str):
    creds = resolve_credentials_dir()
    pairing_path = creds / f"{channel}-pairing.json"

    if not pairing_path.exists():
        print(f"ERROR: No pending pairing requests found at {pairing_path}")
        sys.exit(1)

    pairing_data = load_json(pairing_path, {"version": 1, "requests": []})
    requests = pairing_data.get("requests", [])

    # Find the matching request
    match = next((r for r in requests if r.get("code") == code.upper()), None)

    if not match:
        print(f"ERROR: No request found with code '{code}' in {pairing_path}")
        print(f"Pending codes: {[r.get('code') for r in requests]}")
        sys.exit(1)

    sender_id = match["id"]
    account_id = match.get("meta", {}).get("accountId", "")
    first_name = match.get("meta", {}).get("firstName", "unknown")

    # Determine allowFrom file path
    # If accountId is absent or empty → legacy path: <channel>-allowFrom.json
    # If accountId is present → <channel>-<accountId>-allowFrom.json
    if account_id:
        allow_path = creds / f"{channel}-{account_id}-allowFrom.json"
    else:
        allow_path = creds / f"{channel}-allowFrom.json"

    # Load existing allowlist and add sender
    allow_data = load_json(allow_path, {"version": 1, "allowFrom": []})
    existing = allow_data.get("allowFrom", [])

    if sender_id not in existing:
        existing.append(sender_id)
        allow_data["allowFrom"] = existing
        write_json(allow_path, allow_data)
        print(f"[OK] Added {sender_id} ({first_name}) to {allow_path}")
    else:
        print(f"[INFO] {sender_id} ({first_name}) already in allowlist at {allow_path}")

    # Remove the approved request from pending
    remaining = [r for r in requests if r.get("code") != code.upper()]
    pairing_data["requests"] = remaining
    write_json(pairing_path, pairing_data)
    print(f"[OK] Cleared pairing code {code} from {pairing_path}")
    print(f"\nDone! {first_name} ({sender_id}) approved on {channel}.")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)

    channel_arg = sys.argv[1].lower().strip()
    code_arg = sys.argv[2].upper().strip()
    approve(channel_arg, code_arg)
