"""Test platform adapter for Codeflow.

This adapter is intended for local tests only. It writes relay posts/edits as
JSON lines to stdout so unit tests can assert on the rendered output without
making network requests.
"""

from __future__ import annotations

import json
import os
import sys
from typing import Optional


MAX_TEXT = 1_000_000
SUPPORTS_EDIT = True

DELIVERY_STATS = {
    "http_requests": 0,
    "http_ok": 0,
    "http_fail": 0,
    "http_retries": 0,
    "last_error": "",
    "rate_limit_count": 0,
    "fail_by_code": {},
    "drops": 0,
    "anchor_recreates": 0,
    "last_retry_after": None,
}

_OVERRIDE_STATS = os.environ.get("CODEFLOW_TEST_DELIVERY_STATS")
if _OVERRIDE_STATS:
    try:
        parsed = json.loads(_OVERRIDE_STATS)
        if isinstance(parsed, dict):
            DELIVERY_STATS.update(parsed)
    except Exception:
        pass

_NEXT_ID = 1


def _emit(op: str, text: str, *, name: Optional[str] = None, message_id: Optional[int] = None) -> None:
    payload = {"op": op, "text": text}
    if name is not None:
        payload["name"] = name
    if message_id is not None:
        payload["message_id"] = message_id
    sys.stdout.write(json.dumps(payload, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def post(text: str, name: Optional[str] = None) -> None:
    _emit("post", text or "", name=name)


def post_single(text: str, name: Optional[str] = None) -> int:
    global _NEXT_ID
    mid = int(_NEXT_ID)
    _NEXT_ID += 1
    _emit("post_single", text or "", name=name, message_id=mid)
    return mid


def edit(message_id: int, text: str) -> bool:
    _emit("edit", text or "", message_id=int(message_id))
    return True


def edit_single(message_id: int, text: str) -> bool:
    _emit("edit_single", text or "", message_id=int(message_id))
    return True
