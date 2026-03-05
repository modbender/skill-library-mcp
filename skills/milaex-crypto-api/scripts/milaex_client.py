#!/usr/bin/env python3
"""Small Milaex API client helper used by this skill's scripts.

Design goals:
- minimal deps (requests only)
- prints JSON to stdout
- consistent error handling
- optionally emits rate-limit headers to stderr
"""

from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from typing import Any, Dict, Optional

import requests

RATE_HEADERS = [
    "X-Rate-Limit-Limit",
    "X-Rate-Limit-Remaining",
    "X-Rate-Limit-Reset",
    "X-Rate-Limit-Monthly",
]


@dataclass
class MilaexConfig:
    base_url: str
    api_key: str


def load_config() -> MilaexConfig:
    base_url = os.getenv("MILAEX_BASE_URL", "https://api.milaex.com").rstrip("/")
    api_key = os.getenv("MILAEX_API_KEY", "").strip()
    if not api_key:
        raise SystemExit(
            "Missing MILAEX_API_KEY env var. "
            "Set it to your Milaex API key (x-api-key header)."
        )
    return MilaexConfig(base_url=base_url, api_key=api_key)


def _print_rate_headers(resp: requests.Response) -> None:
    present = {k: resp.headers.get(k) for k in RATE_HEADERS if resp.headers.get(k) is not None}
    if present:
        sys.stderr.write("Rate-limit headers:\n")
        for k in RATE_HEADERS:
            if k in present:
                sys.stderr.write(f"  {k}: {present[k]}\n")


def _parse_first_json_object(text: str) -> Any:
    """Parse the first JSON object/array from a string.

    Some Milaex deployments return JSON with an incorrect content-type, and in
    some cases return two concatenated JSON payloads. We parse the first complete
    JSON object/array to keep output consistent.
    """

    s = (text or "").strip()
    if not s:
        return {"raw": text}

    # Fast path
    try:
        return json.loads(s)
    except Exception:
        pass

    # Attempt to extract the first balanced {...} or [...]
    opener = None
    for ch in s:
        if ch in "{[":
            opener = ch
            break
        if not ch.isspace():
            break

    if opener is None:
        return {"raw": text}

    closer = "}" if opener == "{" else "]"
    level = 0
    end = None

    for i, ch in enumerate(s):
        if ch == opener:
            level += 1
        elif ch == closer:
            level -= 1
            if level == 0:
                end = i + 1
                break

    if end is None:
        return {"raw": text}

    try:
        return json.loads(s[:end])
    except Exception:
        return {"raw": text}


def request_json(
    path: str,
    params: Optional[Dict[str, Any]] = None,
    *,
    print_rate_headers: bool = True,
    timeout_s: int = 30,
) -> Any:
    cfg = load_config()
    url = f"{cfg.base_url}{path}"

    headers = {
        "x-api-key": cfg.api_key,
        "accept": "application/json",
    }

    try:
        resp = requests.get(url, headers=headers, params=params or {}, timeout=timeout_s)
    except requests.RequestException as e:
        raise SystemExit(f"Request failed: {e}")

    if print_rate_headers:
        _print_rate_headers(resp)

    # Try to parse JSON even on errors (API often returns structured errors)
    body_text = resp.text
    data: Any
    content_type = (resp.headers.get("content-type") or "").lower()
    if "application/json" in content_type:
        try:
            data = resp.json()
        except Exception:
            data = _parse_first_json_object(body_text)
    else:
        # Content-type may be wrong; try parsing anyway.
        data = _parse_first_json_object(body_text)

    if resp.status_code >= 400:
        # Print a helpful error to stderr and exit non-zero.
        sys.stderr.write(f"HTTP {resp.status_code} calling {url}\n")
        try:
            sys.stderr.write(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
        except Exception:
            sys.stderr.write(str(data) + "\n")
        raise SystemExit(1)

    # Milaex can also return a structured *application-level* error with HTTP 200.
    # The common envelope looks like: {"Code": 104, "Message": "...", "Description": "...", "Errors": [...]}
    # where Code==0 means success.
    if isinstance(data, dict) and "Code" in data:
        code = data.get("Code")
        try:
            code_int = int(code)
        except Exception:
            code_int = None

        if code_int not in (None, 0):
            msg = data.get("Message") or "Milaex operation failed"
            desc = data.get("Description")
            sys.stderr.write(f"Milaex error Code={code_int}: {msg}\n")
            if desc:
                sys.stderr.write(f"Description: {desc}\n")
            # Special-case: 104 = operation not supported (capabilities mismatch)
            if code_int == 104:
                sys.stderr.write(
                    "Hint: This exchange may not support the requested operation. "
                    "Check the exchange capabilities payload from /api/v1/exchange.\n"
                )
            # Print full payload for debugging.
            try:
                sys.stderr.write(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
            except Exception:
                sys.stderr.write(str(data) + "\n")
            raise SystemExit(1)

    return data


def print_json(data: Any) -> None:
    json.dump(data, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
