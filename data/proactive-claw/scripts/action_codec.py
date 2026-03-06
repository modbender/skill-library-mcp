#!/usr/bin/env python3
"""
action_codec.py — Encode/decode action metadata in calendar event descriptions.

Stores a single-line JSON marker in event descriptions for cross-backend compatibility:
  PC_ACTION: {"action_event_uid":"...","action_type":"reminder",...}

This allows the planner to re-read action calendar events and correlate them
with the DB even if the DB is partially desynced.

Usage (library — imported by action_planner.py and action_executor.py):
  from action_codec import encode_action_description, decode_action_description
"""
from __future__ import annotations

import json
import sys

if sys.version_info < (3, 8):
    print(json.dumps({"error": "python_version_too_old", "detail": "Python 3.8+ required."}))
    sys.exit(1)

PREFIX = "PC_ACTION:"


def encode_action_description(existing_desc: str, payload: dict) -> str:
    """Append or replace PC_ACTION marker in an event description.

    Args:
        existing_desc: Existing description text (may already have a marker).
        payload: Dict with action metadata (action_event_uid, action_type, etc.)

    Returns:
        Updated description with PC_ACTION line at the end.
    """
    # Remove any existing PC_ACTION line
    lines = []
    for line in (existing_desc or "").splitlines():
        if not line.strip().startswith(PREFIX):
            lines.append(line)

    # Append new marker
    marker = f"{PREFIX} {json.dumps(payload, separators=(',', ':'))}"
    lines.append(marker)

    return "\n".join(lines)


def decode_action_description(desc: str) -> dict:
    """Parse PC_ACTION marker from an event description.

    Args:
        desc: Full event description text.

    Returns:
        Parsed payload dict, or None if no marker found.
    """
    if not desc:
        return None

    for line in desc.splitlines():
        stripped = line.strip()
        if stripped.startswith(PREFIX):
            json_str = stripped[len(PREFIX):].strip()
            try:
                return json.loads(json_str)
            except (json.JSONDecodeError, ValueError):
                return None

    return None


def build_action_payload(action_event_uid: str, action_type: str,
                         user_event_uid: str, relationship: str,
                         due_ts: int, status: str = "planned") -> dict:
    """Build a standard payload dict for encoding into a description."""
    return {
        "action_event_uid": action_event_uid,
        "action_type": action_type,
        "user_event_uid": user_event_uid,
        "relationship": relationship,
        "due_ts": due_ts,
        "status": status,
    }


def update_status_in_description(desc: str, new_status: str) -> str:
    """Update the status field in a PC_ACTION marker without changing other fields."""
    payload = decode_action_description(desc)
    if payload is None:
        return desc
    payload["status"] = new_status
    return encode_action_description(desc, payload)
