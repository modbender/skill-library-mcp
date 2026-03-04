#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone

DEFAULT_PATH = os.environ.get("EVENT_WATCHER_WEBHOOK_LOG", "webhook_events.jsonl")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--path", default=DEFAULT_PATH)
    ap.add_argument("--topic", default="webhook")
    ap.add_argument("--event-id", default=None)
    ap.add_argument("--payload", default=None, help="JSON string payload (if not using stdin)")
    args = ap.parse_args()

    raw = None
    if not sys.stdin.isatty():
        raw = sys.stdin.read().strip()
    if not raw and args.payload:
        raw = args.payload
    if not raw:
        raise SystemExit("No payload provided (stdin or --payload)")

    try:
        payload = json.loads(raw)
    except Exception:
        payload = raw

    event = {
        "event_id": args.event_id or f"webhook-{int(datetime.now().timestamp()*1000)}",
        "source": "webhook",
        "topic": args.topic,
        "timestamp": utc_now(),
        "payload": payload,
    }

    with open(args.path, "a") as f:
        f.write(json.dumps(event) + "\n")


if __name__ == "__main__":
    main()
