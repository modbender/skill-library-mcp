#!/usr/bin/env python3
"""Fetch Table Mountain Aerial Cableway status from official API."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path
from typing import Any, Dict
from urllib import request

API_URL = "https://cms.tablemountain.net/admin/actions/submissions/default/weather-api"
FIELDS = [
    "statusType",
    "status",
    "temperature",
    "visibility",
    "wind",
    "firstUp",
    "lastUp",
    "lastDown",
    "waitingTimeBottom",
    "waitingTimeTop",
    "lastUpdated",
]


def fetch_status(url: str, timeout: int) -> Dict[str, Any]:
    with request.urlopen(url, timeout=timeout) as resp:  # noqa: S310 (trusted URL)
        return json.load(resp)


def format_summary(data: Dict[str, Any]) -> str:
    last_updated = data.get("lastUpdated")
    try:
        if last_updated:
            dt_obj = dt.datetime.fromisoformat(last_updated.replace("Z", "+00:00"))
            last_updated_local = dt_obj.astimezone(dt.timezone(dt.timedelta(hours=2)))
            last_updated_str = last_updated_local.strftime("%d.%m.%Y %H:%M (%Z)")
        else:
            last_updated_str = "unbekannt"
    except ValueError:
        last_updated_str = last_updated or "unbekannt"

    parts = [
        f"Status: {data.get('statusType', 'unbekannt')} – {data.get('status', '')}".strip(),
        f"Letztes Update: {last_updated_str}",
        f"Wetter: {data.get('temperature', 'n/a')} · Sicht: {data.get('visibility', 'n/a')} · Wind: {data.get('wind', 'n/a')}",
        f"Fahrplan: first up {data.get('firstUp', 'n/a')}, last up {data.get('lastUp', 'n/a')}, last down {data.get('lastDown', 'n/a')}",
        f"Queues: bottom {data.get('waitingTimeBottom', 'n/a')}, top {data.get('waitingTimeTop', 'n/a')}",
    ]
    return "\n".join(parts)


def write_output(data: Dict[str, Any], path: Path, output_format: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if output_format == "json":
        payload = {key: data.get(key) for key in FIELDS}
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    else:
        path.write_text(format_summary(data) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch Table Mountain cableway status")
    parser.add_argument("--url", default=API_URL, help="API URL (default: %(default)s)")
    parser.add_argument("--timeout", type=int, default=15, help="HTTP timeout in seconds")
    parser.add_argument(
        "--output",
        default="data/table-mountain/status.txt",
        help="Output path for summary or JSON",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        data = fetch_status(args.url, args.timeout)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)

    write_output(data, Path(args.output), args.format)
    if args.format == "json":
        print(json.dumps({key: data.get(key) for key in FIELDS}, ensure_ascii=False, indent=2))
    else:
        print(format_summary(data))


if __name__ == "__main__":
    main()
