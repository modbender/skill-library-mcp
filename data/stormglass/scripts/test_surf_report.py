#!/usr/bin/env python3
"""
Test runner for scripts/surf_report.py.

This script executes the CLI with multiple argument combinations and verifies:
- Success/failure exit codes
- JSON output shape and key fields
- Handling of location mode and coordinate mode
- Argument validation failures

Uses --mock to avoid external API calls and credentials.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import List


ROOT = Path(__file__).resolve().parent.parent
CLI = ROOT / "scripts" / "surf_report.py"
PYTHON_BIN = "/usr/bin/python3"


def run_case(args: List[str]) -> subprocess.CompletedProcess[str]:
    cmd = [PYTHON_BIN, str(CLI)] + args
    return subprocess.run(cmd, capture_output=True, text=True, check=False, cwd=str(ROOT))


def assert_json_shape(stdout: str) -> None:
    payload = json.loads(stdout)
    for key in ("meta", "location", "now", "forecast", "tides"):
        if key not in payload:
            raise AssertionError(f"Missing top-level key: {key}")
    now = payload["now"]
    for key in (
        "waveHeightM",
        "swellHeightM",
        "swellPeriodS",
        "swellDirectionDeg",
        "windSpeedMps",
        "windDirectionDeg",
        "windGustMps",
        "waterTemperatureC",
    ):
        if key not in now:
            raise AssertionError(f"Missing now.{key}")


def main() -> int:
    failures = []

    cases = [
        {
            "name": "location now json mock",
            "args": ["--location", "Highcliffe Beach", "--horizon", "now", "--mock", "--output", "json"],
            "expect_code": 0,
            "expect_json": True,
        },
        {
            "name": "coords 24h json mock",
            "args": ["--lat", "50.735", "--lon", "-1.705", "--horizon", "24h", "--mock", "--output", "json"],
            "expect_code": 0,
            "expect_json": True,
        },
        {
            "name": "coords 72h pretty mock",
            "args": ["--lat", "50.735", "--lon", "-1.705", "--horizon", "72h", "--mock", "--output", "pretty"],
            "expect_code": 0,
            "expect_json": False,
        },
        {
            "name": "missing location and coords",
            "args": ["--horizon", "24h", "--mock"],
            "expect_code": 2,
            "expect_json": False,
        },
        {
            "name": "partial coords missing lon",
            "args": ["--lat", "50.735", "--mock"],
            "expect_code": 2,
            "expect_json": False,
        },
        {
            "name": "location and coords together invalid",
            "args": ["--location", "Highcliffe Beach", "--lat", "50.735", "--lon", "-1.705", "--mock"],
            "expect_code": 2,
            "expect_json": False,
        },
    ]

    for case in cases:
        proc = run_case(case["args"])
        ok = proc.returncode == case["expect_code"]
        if ok and case["expect_json"]:
            try:
                assert_json_shape(proc.stdout)
            except Exception as exc:
                ok = False
                failures.append(f"{case['name']}: json validation failed ({exc})")
        if not ok:
            failures.append(
                f"{case['name']}: expected code {case['expect_code']}, got {proc.returncode}. "
                f"stderr={proc.stderr.strip()!r}"
            )

    if failures:
        print("TEST FAILURES:", file=sys.stderr)
        for item in failures:
            print(f"- {item}", file=sys.stderr)
        return 1

    print(f"All {len(cases)} test cases passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
