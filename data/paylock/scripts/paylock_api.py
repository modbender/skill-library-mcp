#!/usr/bin/env python3
"""Lightweight PayLock API client for OpenClaw skills."""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, Optional

DEFAULT_API = "http://localhost:8767"


class PayLockError(Exception):
    """API request failed."""


class PayLockClient:
    def __init__(self, base_url: Optional[str] = None) -> None:
        self.base_url = (base_url or os.getenv("PAYLOCK_API_BASE") or DEFAULT_API).rstrip("/")

    def request(
        self,
        method: str,
        path: str,
        payload: Optional[Dict[str, Any]] = None,
        timeout: int = 30,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/{path.lstrip('/')}"
        data = None
        headers = {"Accept": "application/json"}

        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"

        req = urllib.request.Request(url=url, method=method.upper(), data=data, headers=headers)

        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                body = resp.read().decode("utf-8")
                if not body.strip():
                    return {"ok": True, "status": resp.status}
                try:
                    return json.loads(body)
                except json.JSONDecodeError:
                    return {"ok": True, "status": resp.status, "raw": body}
        except urllib.error.HTTPError as err:
            raw = err.read().decode("utf-8", errors="replace") if err.fp else ""
            try:
                parsed = json.loads(raw) if raw else {}
            except json.JSONDecodeError:
                parsed = {"error": raw or str(err)}
            raise PayLockError(
                f"HTTP {err.code} {err.reason} | {json.dumps(parsed, ensure_ascii=False)}"
            ) from err
        except urllib.error.URLError as err:
            raise PayLockError(f"Connection error: {err}") from err


def print_json(data: Dict[str, Any]) -> None:
    print(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True))


def run_with_error_handling(fn) -> None:
    try:
        fn()
    except PayLockError as err:
        print(f"PayLock API error: {err}", file=sys.stderr)
        sys.exit(1)
    except Exception as err:  # noqa: BLE001
        print(f"Unexpected error: {err}", file=sys.stderr)
        sys.exit(1)
