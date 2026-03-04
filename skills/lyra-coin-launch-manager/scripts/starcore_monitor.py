#!/usr/bin/env python3
"""Run normalize -> verify -> bookmark for STARCORE family, with minimal logging.

Usage:
  python starcore_monitor.py \
    --symbols STARCORE,STARCOREX,STARCORECOIN \
    --log daily_health.md
"""
from __future__ import annotations

import argparse
import datetime as dt
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]  # .../workspace
LOG_DEFAULT = ROOT / "daily_health.md"


def run(cmd: list[str]):
    subprocess.check_call(cmd, cwd=ROOT)


def append_log(path: Path, line: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write("\n" + line)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--symbols", default="STARCORE,STARCOREX,STARCORECOIN", help="Comma-separated symbols")
    ap.add_argument("--log", default=str(LOG_DEFAULT), help="Path to log file (append)")
    args = ap.parse_args()

    syms = args.symbols

    try:
        run([
            "python",
            "skills/public/lyra-coin-launch-manager/scripts/normalize_starcore_family.py",
            "--symbols",
            syms,
        ])
        run([
            "python",
            "skills/public/lyra-coin-launch-manager/scripts/verify_starcore_family.py",
            "--symbols",
            syms,
        ])
        run([
            "python",
            "skills/public/lyra-coin-launch-manager/scripts/bookmark_starcore_family.py",
            "--symbols",
            syms,
            "--receipts",
            "state/starcore_family_receipts_summary.json",
        ])
        ts = dt.datetime.now().strftime("%Y-%m-%d %H:%M %Z")
        append_log(Path(args.log), f"[{ts}] STARCORE monitor: normalize+verify+bookmark OK for {syms}")
    except subprocess.CalledProcessError as e:
        ts = dt.datetime.now().strftime("%Y-%m-%d %H:%M %Z")
        append_log(Path(args.log), f"[{ts}] STARCORE monitor: ERROR (code {e.returncode}) during {e.cmd}")
        raise


if __name__ == "__main__":
    main()
