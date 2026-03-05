#!/usr/bin/env python3
"""QR Password payload format v1 — encode/decode library."""

import json
import sys

FORMAT_VERSION = 1

def encode(username: str, password: str, domain: str) -> str:
    """Encode credentials to QR payload string (JSON)."""
    payload = {"v": FORMAT_VERSION, "u": username, "p": password, "d": domain}
    return json.dumps(payload, separators=(",", ":"))

def decode(data: str) -> dict:
    """Decode QR payload string to credential dict. Returns {username, password, domain}."""
    obj = json.loads(data)
    if obj.get("v") != FORMAT_VERSION:
        raise ValueError(f"Unsupported format version: {obj.get('v')}")
    return {"username": obj["u"], "password": obj["p"], "domain": obj["d"]}

if __name__ == "__main__":
    # CLI: encode or decode
    if len(sys.argv) < 2 or sys.argv[1] not in ("encode", "decode"):
        print("Usage: qr-format.py encode|decode", file=sys.stderr)
        sys.exit(1)
    if sys.argv[1] == "encode":
        data = json.load(sys.stdin)
        print(encode(data["username"], data["password"], data["domain"]))
    else:
        print(json.dumps(decode(sys.stdin.read().strip())))
