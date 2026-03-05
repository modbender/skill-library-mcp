#!/usr/bin/env python3
"""Credential safety helper for Salesforce skill (Keychain-first)."""

from __future__ import annotations

import subprocess
from pathlib import Path

KEYCHAIN_SERVICE = "openclaw.salesforce"
KEYS = [
    "SALESFORCE_CLIENT_ID",
    "SALESFORCE_CLIENT_SECRET",
    "SALESFORCE_INSTANCE_URL",
]
LEGACY_FILES = [
    Path.home() / ".config" / "openclaw" / "salesforce_credentials.env",
    Path.home() / ".config" / "manus" / "salesforce_credentials.env",
]


def _keychain_has(account: str) -> tuple[bool, int]:
    result = subprocess.run(
        ["security", "find-generic-password", "-a", account, "-s", KEYCHAIN_SERVICE, "-w"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return False, 0
    value = result.stdout.strip()
    return bool(value), len(value)


def main() -> int:
    print(f"Keychain service: {KEYCHAIN_SERVICE}\n")

    missing = []
    for key in KEYS:
        ok, length = _keychain_has(key)
        if ok:
            print(f"✅ {key}: present (length={length})")
        else:
            print(f"❌ {key}: missing")
            missing.append(key)

    print("\nLegacy plaintext file check:")
    found_plaintext = False
    for p in LEGACY_FILES:
        if p.exists():
            print(f"⚠️ Found legacy plaintext credentials file: {p}")
            found_plaintext = True
        else:
            print(f"✅ Absent: {p}")

    print("\nSecurity checklist:")
    print("- Use dedicated least-privilege Salesforce integration user")
    print("- Never paste secrets into chat/history")
    print("- Rotate secrets if exposed")

    if missing:
        print(f"\nResult: NOT READY (missing in Keychain: {', '.join(missing)})")
        return 1

    if found_plaintext:
        print("\nResult: WARNING (credentials exist, but remove legacy plaintext file[s]).")
        return 2

    print("\nResult: READY (Keychain-only credential posture looks good).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
