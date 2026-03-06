#!/usr/bin/env python3
"""
Optional normalization helper for surf_report JSON.

This utility is intentionally stdlib-only and can be used by other agents/jobs to
enforce stable null/field behavior before downstream rendering.

Usage:
  cat raw.json | python scripts/normalize_surf_data.py > normalized.json
"""

from __future__ import annotations

import json
import sys
from typing import Any, Dict


NOW_KEYS = [
    "waveHeightM",
    "swellHeightM",
    "swellPeriodS",
    "swellDirectionDeg",
    "windSpeedMps",
    "windDirectionDeg",
    "windGustMps",
    "waterTemperatureC",
]


def normalize(payload: Dict[str, Any]) -> Dict[str, Any]:
    payload.setdefault("meta", {})
    payload.setdefault("location", {})
    payload.setdefault("now", {})
    payload.setdefault("forecast", {})
    payload.setdefault("tides", {})

    for key in NOW_KEYS:
        payload["now"].setdefault(key, None)

    payload["meta"].setdefault("warnings", [])
    payload["forecast"].setdefault("windows", {})
    payload["tides"].setdefault("extremes", [])
    payload["tides"].setdefault("byDay", {})
    payload["tides"].setdefault("trendNow", "unknown")
    return payload


def main() -> int:
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw)
        if not isinstance(payload, dict):
            print("Expected top-level JSON object", file=sys.stderr)
            return 2
        print(json.dumps(normalize(payload), ensure_ascii=True, sort_keys=True))
        return 0
    except json.JSONDecodeError as exc:
        print(f"Invalid JSON: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"Unexpected error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
