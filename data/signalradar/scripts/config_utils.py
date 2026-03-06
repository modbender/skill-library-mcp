#!/usr/bin/env python3
"""Configuration helpers for SignalRadar runtime."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


DEFAULT_CONFIG: dict[str, Any] = {
    "profile": {
        "timezone": "Asia/Shanghai",
        "language": "zh",
    },
    "threshold": {
        "abs_pp": 5.0,
        "rel_pct": 5.0,
        "rel_pct_enabled": False,
        "per_category_abs_pp": {},
        "per_entry_abs_pp": {},
    },
    "dedup": {
        "enabled": False,
        "window_minutes": 0,
    },
    "delivery": {
        "primary": {"channel": "openclaw", "target": "direct"},
        "fallback": [],
    },
    "source": {
        "retries": 2,
    },
    "digest": {
        "frequency": "off",
    },
    "baseline": {
        "cleanup_expired": False,
        "cleanup_ttl_days": 45,
    },
    "notion": {
        "sync_readonly_pages": False,
    },
}


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged: dict[str, Any] = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_json_config(path: Path | None) -> dict[str, Any]:
    if path is None or not path.exists():
        return {}
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    if not isinstance(obj, dict):
        return {}
    return obj

