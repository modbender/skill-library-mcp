#!/usr/bin/env python3
"""Run an arbitrary command and return a standardized JSON result envelope.

Usage:
  python scripts/run_envelope.py -- <command> [args...]

Exit codes:
  0 when the wrapped command exits 0
  otherwise returns the wrapped command exit code
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def main() -> int:
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--timeout", type=int, default=0, help="Seconds; 0=none")
    ap.add_argument("cmd", nargs=argparse.REMAINDER)
    args = ap.parse_args()

    if not args.cmd or args.cmd == ["--"]:
        raise SystemExit("Provide a command after '--'")
    cmd = args.cmd
    if cmd[0] == "--":
        cmd = cmd[1:]

    started = time.time()
    started_iso = now_iso()

    try:
        cp = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=(args.timeout if args.timeout > 0 else None),
            shell=False,
        )
        exit_code = cp.returncode
        out = {
            "ok": exit_code == 0,
            "exit_code": exit_code,
            "cmd": cmd,
            "stdout": cp.stdout,
            "stderr": cp.stderr,
            "startedAt": started_iso,
            "endedAt": now_iso(),
            "durationMs": int((time.time() - started) * 1000),
        }
    except subprocess.TimeoutExpired as e:
        out = {
            "ok": False,
            "exit_code": 124,
            "cmd": cmd,
            "stdout": (e.stdout or ""),
            "stderr": (e.stderr or "") + "\nTIMEOUT",
            "startedAt": started_iso,
            "endedAt": now_iso(),
            "durationMs": int((time.time() - started) * 1000),
        }
        exit_code = 124

    print(json.dumps(out, ensure_ascii=False, indent=2))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
