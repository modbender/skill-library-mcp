#!/usr/bin/env python3
import argparse
import json
import os
import shlex
import subprocess
import sys
import time
from pathlib import Path

import requests


def load_cursor(path: Path) -> str:
    if not path.exists():
        return "0"
    try:
        value = path.read_text(encoding="utf-8").strip()
        return value or "0"
    except Exception:
        return "0"


def save_cursor(path: Path, cursor: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(cursor, encoding="utf-8")


def parse_on_events_command(raw: str | None) -> list[str] | None:
    if not raw:
        return None
    try:
        parts = shlex.split(raw, posix=True)
    except ValueError:
        return None
    if not parts:
        return None
    return parts


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fallback long-poll daemon for runtimes that cannot receive wake webhooks."
    )
    parser.add_argument("--base-url", default="https://api.thrd.email")
    parser.add_argument("--cursor-file", default=".thrd_cursor")
    parser.add_argument("--timeout-ms", type=int, default=25000)
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument(
        "--on-events",
        help=(
            "Optional command to run whenever one or more events are received. "
            "Executed safely without a shell (example: --on-events \"echo inbound-ready\")."
        ),
    )
    args = parser.parse_args()
    on_events_cmd = parse_on_events_command(args.on_events)

    if args.on_events and not on_events_cmd:
        print(
            json.dumps(
                {
                    "ok": False,
                    "error": "Invalid --on-events value. Provide a command string such as \"echo inbound-ready\".",
                }
            )
        )
        return 1

    api_key = os.environ.get("THRD_API_KEY")
    if not api_key:
        print(json.dumps({"ok": False, "error": "THRD_API_KEY environment variable not set."}))
        return 1

    base_url = args.base_url.rstrip("/")
    cursor_path = Path(args.cursor_file)
    cursor = load_cursor(cursor_path)
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    print(f"Thrd poll daemon started (cursor={cursor}, file={cursor_path}).", file=sys.stderr)

    while True:
        try:
            resp = requests.get(
                f"{base_url}/v1/events",
                headers=headers,
                params={"cursor": cursor, "timeout": args.timeout_ms, "limit": args.limit},
                timeout=(args.timeout_ms / 1000.0) + 10,
            )
            resp.raise_for_status()
            data = resp.json()
            events = data.get("events", [])
            next_cursor = data.get("next_cursor", cursor)

            if events:
                summary = {
                    "ok": True,
                    "received": len(events),
                    "cursor": next_cursor,
                    "types": [ev.get("type") for ev in events],
                }
                print(json.dumps(summary))

                if on_events_cmd:
                    subprocess.run(on_events_cmd, shell=False, check=False)

                ack = requests.post(
                    f"{base_url}/v1/events/ack",
                    headers=headers,
                    json={"cursor": str(next_cursor)},
                    timeout=30,
                )
                ack.raise_for_status()

                cursor = str(next_cursor)
                save_cursor(cursor_path, cursor)

        except KeyboardInterrupt:
            print("Stopped by user.", file=sys.stderr)
            return 0
        except Exception as exc:
            print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
            time.sleep(3)


if __name__ == "__main__":
    raise SystemExit(main())
