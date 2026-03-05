#!/usr/bin/env python3
"""
One-step usage reporting runner.
Always syncs latest usage data first (unless --no-sync), then generates text or image report.
"""

import argparse
import os
import json
import subprocess
import sys
from pathlib import Path

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")


def run(cmd):
    result = subprocess.run(cmd, cwd=BASE_DIR, text=True, capture_output=True)
    if result.returncode != 0:
        return False, result.stdout.strip(), result.stderr.strip()
    return True, result.stdout.strip(), result.stderr.strip()


def main():
    parser = argparse.ArgumentParser(description="Sync usage data, then generate usage report")
    parser.add_argument("--mode", choices=["image", "text"], default="image", help="Report output mode")
    parser.add_argument("--period", choices=["today", "yesterday", "week", "month"], default="today")
    parser.add_argument("--no-sync", action="store_true", help="Skip fetch/sync step")
    parser.add_argument("--json", action="store_true", help="Output result as JSON")
    args = parser.parse_args()

    py = sys.executable
    results = {"steps": []}

    # Step 1: Sync
    if not args.no_sync:
        success, out, err = run([py, os.path.join(SCRIPTS_DIR, "fetch_usage.py")])
        results["steps"].append({"name": "sync", "success": success, "output": out, "error": err})
        if not success and not args.json:
            print(f"Sync failed: {err}")
            sys.exit(1)

    # Step 2: Generate Report
    if args.mode == "text":
        success, out, err = run([py, os.path.join(SCRIPTS_DIR, "report.py"), "--period", args.period, "--text"])
        results["steps"].append({"name": "text_report", "success": success, "output": out, "error": err})
        
        if args.json:
            results["status"] = "success" if success else "error"
            results["text_summary"] = out
            print(json.dumps(results, indent=2, ensure_ascii=False))
        else:
            if out: print(out)
            if err: print(err, file=sys.stderr)
            if not success: sys.exit(1)
        return

    # Image mode
    img_cmd = [py, os.path.join(SCRIPTS_DIR, "generate_report_image.py")]
    if args.period == "today":
        img_cmd.append("--today")
    elif args.period == "yesterday":
        img_cmd.append("--yesterday")
    else:
        img_cmd.extend(["--period", args.period])

    success, out, err = run(img_cmd)
    results["steps"].append({"name": "image_report", "success": success, "output": out, "error": err})

    # Try to find image path from output
    image_path = None
    if success and "->" in out:
        image_path = out.split("->")[-1].strip()

    if args.json:
        results["status"] = "success" if success else "error"
        results["image_path"] = image_path
        results["output"] = out
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        if out: print(out)
        if err: print(err, file=sys.stderr)
        if not success: sys.exit(1)


if __name__ == "__main__":
    main()
