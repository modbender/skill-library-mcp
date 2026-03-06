#!/usr/bin/env python3

"""RAGFlow status summary (non-secret).

Inputs:
- Required env: RAGFLOW_BASE_URL, RAGFLOW_API_KEY

Behavior:
- GET {base_url}/v1/system/status (auth)
- Prints a compact key summary (no secrets)

Exit codes:
- 0: OK
- 2: HTTP failure
- 3: invalid JSON
"""

import json
import os
import urllib.error
import urllib.request


def get_env(name: str) -> str:
    v = os.environ.get(name, "").strip()
    if not v:
        raise SystemExit(f"ERROR: missing env {name}")
    return v


def http_get(url: str, api_key: str, timeout: int = 15) -> tuple[int, bytes]:
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    req = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read() or b""


def main() -> int:
    base_url = get_env("RAGFLOW_BASE_URL").rstrip("/")
    api_key = get_env("RAGFLOW_API_KEY")

    st, body = http_get(f"{base_url}/v1/system/status", api_key)
    if st != 200:
        print(f"FAIL status_http={st}")
        return 2

    try:
        data = json.loads(body.decode("utf-8", errors="replace"))
    except Exception:
        print("FAIL invalid_json")
        return 3

    payload = data.get("data") if isinstance(data, dict) else None
    if payload is None:
        payload = data

    keys = sorted(payload.keys()) if isinstance(payload, dict) else []
    print("OK keys=" + ",".join(keys[:30]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
