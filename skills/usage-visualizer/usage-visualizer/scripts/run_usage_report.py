#!/usr/bin/env python3
"""
One-step usage reporting runner.
Always syncs latest usage data first (unless --no-sync), then generates text or image report.
"""

import argparse
import os
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")


def run(cmd):
    result = subprocess.run(cmd, cwd=BASE_DIR, text=True, capture_output=True)
    if result.stdout:
        print(result.stdout.strip())
    if result.stderr:
        print(result.stderr.strip())
    if result.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}")


def main():
    parser = argparse.ArgumentParser(description="Sync usage data, then generate usage report")
    parser.add_argument("--mode", choices=["image", "text"], default="image", help="Report output mode")
    parser.add_argument("--period", choices=["today", "yesterday", "week", "month"], default="today")
    parser.add_argument("--no-sync", action="store_true", help="Skip fetch/sync step")
    args = parser.parse_args()

    py = sys.executable

    if not args.no_sync:
        run([py, os.path.join(SCRIPTS_DIR, "fetch_usage.py")])

    if args.mode == "text":
        run([py, os.path.join(SCRIPTS_DIR, "report.py"), "--period", args.period, "--text"])
        return

    # image mode
    img_cmd = [py, os.path.join(SCRIPTS_DIR, "generate_report_image.py")]
    if args.period == "today":
        img_cmd.append("--today")
    elif args.period == "yesterday":
        img_cmd.append("--yesterday")
    else:
        img_cmd.extend(["--period", args.period])

    run(img_cmd)


if __name__ == "__main__":
    main()
