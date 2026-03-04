from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def decode_fields(fields: Dict[Any, Any]) -> Dict[str, Any]:
    return {
        (k.decode() if isinstance(k, bytes) else k): (v.decode() if isinstance(v, bytes) else v)
        for k, v in fields.items()
    }


def normalize_event(stream: str, event_id: str, fields: Dict[str, Any], payload_field: str | None, payload_encoding: str) -> dict:
    decoded = decode_fields(fields)
    payload = decoded

    if payload_field:
        payload = decoded.get(payload_field)
        if payload_encoding == "json" and isinstance(payload, str):
            try:
                payload = json.loads(payload)
            except Exception:
                payload = None
        elif payload_encoding == "string" and payload is not None:
            payload = str(payload)
        elif payload_encoding == "hash":
            payload = decoded

    return {
        "event_id": event_id,
        "source": "redis_stream",
        "topic": stream,
        "timestamp": utc_now(),
        "payload": payload,
    }


def get_field(data: dict, path: str):
    cur = data
    for part in path.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            return None
    return cur


def match_filter(event: dict, rule: dict | None) -> bool:
    if not rule:
        return True
    field = rule.get("field")
    op = rule.get("op")
    value = rule.get("value")
    actual = get_field(event, field) if field else None
    if op == "==":
        return actual == value
    if op == "!=":
        return actual != value
    if op == ">":
        return actual is not None and actual > value
    if op == "<":
        return actual is not None and actual < value
    if op == "in":
        return actual in value if isinstance(value, (list, tuple, set)) else False
    if op == "contains":
        return value in actual if isinstance(actual, (list, str)) else False
    return False


def render_template(template: str, event: dict) -> str:
    if not template:
        return f"New event: {event['event_id']}"
    out = template

    # Support nested paths like {{payload.city}}
    def lookup(path: str):
        cur = event
        for part in path.split("."):
            if isinstance(cur, dict) and part in cur:
                cur = cur[part]
            else:
                return None
        return cur

    # Replace {{path}} patterns
    import re
    pattern = re.compile(r"\{\{\s*([^\}]+?)\s*\}\}")

    def repl(match):
        key = match.group(1).strip()
        val = lookup(key)
        return "" if val is None else str(val)

    return pattern.sub(repl, out)
