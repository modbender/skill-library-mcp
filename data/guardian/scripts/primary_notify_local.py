#!/usr/bin/env python3
"""Local primary-channel notifier stub for Guardian.

Usage from config:
  "alerts": { "primary_notify_command": "python3 /path/to/primary_notify_local.py" }

Receives one JSON argument and appends to memory/guardian-primary-notify.log.
Replace this script with channel-specific bridge as needed.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) < 2:
        return 1
    payload = json.loads(sys.argv[1])
    out = Path.home() / ".openclaw" / "workspace" / "memory" / "guardian-primary-notify.log"
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
