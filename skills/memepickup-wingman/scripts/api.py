#!/usr/bin/env python3
"""MemePickup API helper — stdlib-only Python equivalent of api.sh.

Security Manifest:
- Accesses: MEMEPICKUP_API_KEY
- Endpoints: https://rork-memepickup-app-3.vercel.app/api/v1/*
- File Operations: None
"""
import json
import os
import sys
import urllib.request
import urllib.error

API_BASE = "https://rork-memepickup-app-3.vercel.app/api/v1"

ACTIONS = {
    "lines":      ("POST",  f"{API_BASE}/lines/generate"),
    "replies":    ("POST",  f"{API_BASE}/replies/generate"),
    "screenshot": ("POST",  f"{API_BASE}/replies/from-screenshot"),
    "analyze":    ("POST",  f"{API_BASE}/profiles/analyze"),
    "credits":    ("GET",   f"{API_BASE}/credits"),
    "get-prefs":  ("GET",   f"{API_BASE}/preferences"),
    "set-prefs":  ("PUT",   f"{API_BASE}/preferences"),
}


def main():
    api_key = os.environ.get("MEMEPICKUP_API_KEY", "")
    if not api_key:
        print(
            '{"error":"MEMEPICKUP_API_KEY not set. Get your key from MemePickup app: Profile > Wingman API > Generate Key"}',
            file=sys.stderr,
        )
        sys.exit(1)

    action = sys.argv[1] if len(sys.argv) > 1 else ""
    if action not in ACTIONS:
        print(
            '{"error":"Unknown action. Use: lines|replies|screenshot|analyze|credits|get-prefs|set-prefs"}',
            file=sys.stderr,
        )
        sys.exit(1)

    method, endpoint = ACTIONS[action]

    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json",
    }

    data = None
    if method in ("POST", "PUT"):
        payload = sys.stdin.buffer.read()
        data = payload if payload else None

    req = urllib.request.Request(endpoint, data=data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req) as resp:
            sys.stdout.buffer.write(resp.read())
            sys.stdout.buffer.flush()
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(body, file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(
            json.dumps({"error": f"Network error: {e.reason}"}),
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
