#!/usr/bin/env python3

"""RAGFlow ping (liveness + optional readiness).

Inputs:
- Required env: RAGFLOW_BASE_URL
- Optional env: RAGFLOW_API_KEY

Behavior:
- Liveness: GET {base_url}/openapi.json (no auth) must return 200
- If RAGFLOW_API_KEY is set:
  - Readiness: GET {base_url}/v1/system/status (Bearer) must return 200

Exit codes:
- 0: OK
- 2: liveness failed
- 3: readiness failed
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


def http_get(url: str, api_key: str | None = None, timeout: int = 10) -> tuple[int, bytes]:
    headers = {"Accept": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    req = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read() or b""


def main() -> int:
    base_url = get_env("RAGFLOW_BASE_URL").rstrip("/")
    api_key = os.environ.get("RAGFLOW_API_KEY", "").strip() or None

    st, _ = http_get(f"{base_url}/openapi.json", api_key=None)
    if st != 200:
        print(f"LIVENESS_FAIL openapi.json status={st}")
        return 2

    if not api_key:
        print("OK_LIVE (no api key set)")
        return 0

    st2, body2 = http_get(f"{base_url}/v1/system/status", api_key=api_key)
    if st2 != 200:
        print(f"READINESS_FAIL system/status status={st2}")
        return 3

    try:
        data = json.loads(body2.decode("utf-8", errors="replace"))
        keys = sorted(list(data.keys())) if isinstance(data, dict) else []
        print("OK_READY keys=" + ",".join(keys[:20]))
    except Exception:
        print("OK_READY")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
