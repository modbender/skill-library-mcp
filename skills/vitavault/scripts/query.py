#!/usr/bin/env python3
"""VitaVault Health Data Query - Pull health data from VitaVault cloud API.

Usage:
    python3 query.py latest              # Get most recent health snapshot
    python3 query.py range 2026-02-01 2026-02-28  # Get date range
    python3 query.py summary             # Get latest + formatted summary

Environment:
    VITAVAULT_API_URL   - API base URL (required - set to your private API endpoint)
    VITAVAULT_SYNC_TOKEN - Bearer token for authentication
"""

import os
import sys
import json
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from datetime import datetime, timedelta

API_URL = os.environ.get("VITAVAULT_API_URL", "")
if not API_URL:
    print("Error: VITAVAULT_API_URL environment variable is required.", file=sys.stderr)
    print("Set it to your private VitaVault API endpoint.", file=sys.stderr)
    sys.exit(1)
TOKEN = os.environ.get("VITAVAULT_SYNC_TOKEN", "")


def api_get(path: str) -> dict:
    url = f"{API_URL}{path}"
    req = Request(url)
    req.add_header("User-Agent", "VitaVault-OpenClaw/1.0")
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    try:
        with urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except HTTPError as e:
        body = e.read().decode()
        print(f"API error {e.code}: {body}", file=sys.stderr)
        sys.exit(1)


def format_metric(name: str, value, unit: str = "") -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        value = round(value, 1)
    return f"  {name}: {value}{' ' + unit if unit else ''}"


def format_snapshot(snap: dict) -> str:
    m = snap.get("metrics", {})
    date = snap.get("date", "unknown")
    synced = snap.get("syncedAt", "")

    lines = [f"Health Data for {date} (synced: {synced[:19]})", ""]

    metric_map = [
        ("Steps", m.get("steps"), "steps"),
        ("Active Energy", m.get("activeEnergy"), "kcal"),
        ("Heart Rate", m.get("heartRate"), "bpm avg"),
        ("Resting HR", m.get("restingHeartRate"), "bpm"),
        ("HRV", m.get("hrv"), "ms"),
        ("Blood Oxygen", m.get("bloodOxygen"), "%"),
        ("Respiratory Rate", m.get("respiratoryRate"), "brpm"),
        ("Sleep", m.get("sleepHours"), "hours"),
        ("Distance", m.get("distance"), "km"),
        ("Exercise", m.get("exerciseMinutes"), "min"),
        ("Flights Climbed", m.get("flightsClimbed"), "floors"),
        ("Weight", m.get("bodyMass"), "lbs"),
    ]

    for name, val, unit in metric_map:
        line = format_metric(name, val, unit)
        if line:
            lines.append(line)

    return "\n".join(lines)


def cmd_latest():
    data = api_get("/v1/health/latest")
    print(json.dumps(data, indent=2))


def cmd_range(start: str, end: str):
    data = api_get(f"/v1/health/range?start={start}&end={end}")
    print(json.dumps(data, indent=2))


def cmd_summary():
    data = api_get("/v1/health/latest")
    print(format_snapshot(data))


def cmd_week():
    end = datetime.now().strftime("%Y-%m-%d")
    start = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    data = api_get(f"/v1/health/range?start={start}&end={end}")
    snapshots = data.get("data", [])
    if not snapshots:
        print("No health data found for the past week.")
        return
    print(f"Health Data: {start} to {end} ({len(snapshots)} days)\n")
    for snap in snapshots:
        print(format_snapshot(snap))
        print()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "latest":
        cmd_latest()
    elif cmd == "range" and len(sys.argv) >= 4:
        cmd_range(sys.argv[2], sys.argv[3])
    elif cmd == "summary":
        cmd_summary()
    elif cmd == "week":
        cmd_week()
    else:
        print(__doc__)
        sys.exit(1)
