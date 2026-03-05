#!/usr/bin/env python3

"""RAGFlow ops-level smoke test (system endpoints only).

Inputs:
- Required env: RAGFLOW_BASE_URL, RAGFLOW_API_KEY

Checks:
1) GET {base_url}/v1/system/status (auth)
2) GET {base_url}/v1/system/ping (auth/no-auth depends on deployment; we send Bearer)

Exit codes:
- 0: OK
- 2: system/status failed
- 3: system/ping failed

Note:
- This script is intentionally decoupled from any application-layer usage.
- It does not call non-system endpoints.
"""

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

    st, _ = http_get(f"{base_url}/v1/system/status", api_key)
    if st != 200:
        print(f"FAIL system/status status={st}")
        return 2

    st2, _ = http_get(f"{base_url}/v1/system/ping", api_key)
    if st2 != 200:
        print(f"FAIL system/ping status={st2}")
        return 3

    print("OK smoke")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
