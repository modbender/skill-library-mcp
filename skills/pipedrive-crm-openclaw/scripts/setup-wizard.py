#!/usr/bin/env python3
"""Minimal setup helper for pipedrive-crm-openclaw skill."""

from __future__ import annotations

import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request


def _prompt(label: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    value = input(f"{label}{suffix}: ").strip()
    return value or default


def _test_with_token(domain: str, token: str) -> tuple[bool, str]:
    base = f"https://{domain}.pipedrive.com/api/v1"
    qs = urllib.parse.urlencode({"api_token": token})
    url = f"{base}/users/me?{qs}"
    req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "OpenClaw-Pipedrive-Skill/1.0.0"})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            if resp.status >= 200 and resp.status < 300:
                return True, "Connection OK"
            return False, f"Unexpected status: {resp.status}"
    except urllib.error.HTTPError as exc:
        return False, f"HTTP {exc.code}"
    except Exception as exc:
        return False, str(exc)


def main() -> int:
    print("Pipedrive CRM Setup Wizard\n")
    domain = _prompt("Pipedrive company domain (subdomain only, e.g. acme)", os.environ.get("PIPEDRIVE_COMPANY_DOMAIN", ""))
    if not re.match(r"^[a-zA-Z0-9-]{1,100}$", domain or ""):
        print("Invalid company domain format.")
        return 2

    mode = _prompt("Auth mode: token or oauth", "token").lower()

    if mode not in {"token", "oauth"}:
        print("Auth mode must be 'token' or 'oauth'.")
        return 2

    if mode == "token":
        token = _prompt("PIPEDRIVE_API_TOKEN", os.environ.get("PIPEDRIVE_API_TOKEN", ""))
        if not token:
            print("PIPEDRIVE_API_TOKEN is required for token mode.")
            return 2
        ok, message = _test_with_token(domain, token)
        print(f"Connection test: {message}")
        print("\nExport these variables:")
        print(f"export PIPEDRIVE_COMPANY_DOMAIN={domain}")
        print("export PIPEDRIVE_API_TOKEN=<your_token>")
        return 0 if ok else 1

    access_token = _prompt("PIPEDRIVE_ACCESS_TOKEN", os.environ.get("PIPEDRIVE_ACCESS_TOKEN", ""))
    if not access_token:
        print("PIPEDRIVE_ACCESS_TOKEN is required for oauth mode.")
        return 2

    print("\nExport these variables:")
    print(f"export PIPEDRIVE_COMPANY_DOMAIN={domain}")
    print("export PIPEDRIVE_ACCESS_TOKEN=<your_oauth_access_token>")
    print("\nOAuth mode selected. Run `test_connection` with the main script to verify scopes.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
