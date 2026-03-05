#!/usr/bin/env python3
"""
Jackal Memory client — no dependencies beyond Python stdlib.

Usage:
  python client.py save <key> <content>
  python client.py load <key>
  python client.py provision <jackal_address>

Auth: reads JACKAL_MEMORY_API_KEY from environment.
"""

import json
import os
import sys
import urllib.error
import urllib.request

BASE_URL = "https://web-production-5cce7.up.railway.app"


def _api_key() -> str:
    key = os.environ.get("JACKAL_MEMORY_API_KEY", "")
    if not key:
        print("Error: JACKAL_MEMORY_API_KEY is not set.", file=sys.stderr)
        sys.exit(1)
    return key


def _request(method: str, path: str, body: dict | None = None) -> dict:
    url = BASE_URL + path
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {_api_key()}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        error = json.loads(e.read())
        print(f"Error {e.code}: {error.get('detail', e.reason)}", file=sys.stderr)
        sys.exit(1)


def cmd_save(key: str, content: str) -> None:
    result = _request("POST", "/save", {"key": key, "content": content})
    print(f"Saved — key: {result['key']}  cid: {result['cid']}")


def cmd_load(key: str) -> None:
    result = _request("GET", f"/load/{key}")
    print(result["content"])


def cmd_provision(jackal_address: str) -> None:
    result = _request("POST", "/provision", {"jackal_address": jackal_address})
    print(f"Provisioned — address: {result['jackal_address']}  tx: {result['tx_hash']}")


def main() -> None:
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(0)

    cmd = args[0]

    if cmd == "save" and len(args) == 3:
        cmd_save(args[1], args[2])
    elif cmd == "load" and len(args) == 2:
        cmd_load(args[1])
    elif cmd == "provision" and len(args) == 2:
        cmd_provision(args[1])
    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
