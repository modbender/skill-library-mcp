#!/usr/bin/env python3
"""Guardian trust grant cache backed by a local JSON state file."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from .settings import resolve_workspace
except ImportError:
    from settings import resolve_workspace

SCOPE_TYPES = ("session", "action_type", "specific", "channel", "blanket")

TTL_DEFAULTS = {
    "session": 3600,
    "action_type": 86400,
    "specific": 0,
    "channel": 604800,
    "blanket": 3600,
}


def default_cache_path() -> Path:
    """Return the default cache file path inside Guardian workspace."""
    return resolve_workspace() / "dashboard" / "guardian-cache-state.json"


def _resolve_path(path: Optional[str] = None) -> Path:
    if path:
        return Path(path).expanduser().resolve()
    return default_cache_path()


def _load(path: Optional[str] = None) -> Dict[str, Any]:
    """Load cache state from disk with safe fallback on malformed files."""
    target = _resolve_path(path)
    if target.exists():
        try:
            return json.loads(target.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {"grants": [], "audit_trail": [], "updated": None}


def _save(data: Dict[str, Any], path: Optional[str] = None) -> None:
    """Persist cache state to disk."""
    target = _resolve_path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    data["updated"] = datetime.now(timezone.utc).isoformat()
    target.write_text(json.dumps(data, indent=2), encoding="utf-8")


def grant(
    action: str,
    channel: str,
    scope: str = "action_type",
    ttl_seconds: Optional[int] = None,
    details: Optional[Dict[str, Any]] = None,
    path: Optional[str] = None,
) -> Dict[str, Any]:
    """Create and persist a new trust grant."""
    if scope not in SCOPE_TYPES:
        raise ValueError(f"Invalid scope: {scope}. Must be one of {SCOPE_TYPES}")

    effective_ttl = TTL_DEFAULTS.get(scope, 86400) if ttl_seconds is None else ttl_seconds
    now = datetime.now(timezone.utc)
    expires = (now + timedelta(seconds=effective_ttl)).isoformat() if effective_ttl > 0 else None

    grant_obj = {
        "id": "g" + uuid.uuid4().hex[:8],
        "action": action,
        "channel": channel,
        "scope": scope,
        "created": now.isoformat(),
        "expires": expires,
        "details": details,
    }

    data = _load(path)
    data["grants"].append(grant_obj)
    data["audit_trail"].append(
        {
            "event": "grant",
            "grant_id": grant_obj["id"],
            "action": action,
            "channel": channel,
            "scope": scope,
            "timestamp": now.isoformat(),
        }
    )
    _save(data, path)
    return grant_obj


def check(action: str, channel: str, path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Return the first active grant matching action/channel semantics."""
    data = _load(path)
    now = datetime.now(timezone.utc)

    for grant_obj in data["grants"]:
        expires = grant_obj.get("expires")
        if expires:
            exp = datetime.fromisoformat(expires)
            if exp.tzinfo is None:
                exp = exp.replace(tzinfo=timezone.utc)
            if exp < now:
                continue

        scope = grant_obj.get("scope", "specific")
        if scope == "blanket":
            return grant_obj
        if scope == "channel" and grant_obj["channel"] == channel:
            return grant_obj
        if scope == "action_type" and grant_obj["action"] == action:
            return grant_obj
        if scope in {"specific", "session"} and grant_obj["action"] == action and grant_obj["channel"] == channel:
            return grant_obj

    return None


def revoke(grant_id: str, path: Optional[str] = None) -> None:
    """Revoke a specific grant by removing it from cache."""
    data = _load(path)
    data["grants"] = [grant_obj for grant_obj in data["grants"] if grant_obj["id"] != grant_id]
    data["audit_trail"].append(
        {
            "event": "revoke",
            "grant_id": grant_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    )
    _save(data, path)


def revoke_all(path: Optional[str] = None) -> int:
    """Revoke all grants and return number of removed grants."""
    data = _load(path)
    count = len(data["grants"])
    data["grants"] = []
    data["audit_trail"].append(
        {
            "event": "revoke_all",
            "count": count,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    )
    _save(data, path)
    return count


def list_active(path: Optional[str] = None) -> List[Dict[str, Any]]:
    """List active (non-expired) grants."""
    data = _load(path)
    now = datetime.now(timezone.utc)
    active: List[Dict[str, Any]] = []
    for grant_obj in data["grants"]:
        expires = grant_obj.get("expires")
        if expires:
            exp = datetime.fromisoformat(expires)
            if exp.tzinfo is None:
                exp = exp.replace(tzinfo=timezone.utc)
            if exp < now:
                continue
        active.append(grant_obj)
    return active
