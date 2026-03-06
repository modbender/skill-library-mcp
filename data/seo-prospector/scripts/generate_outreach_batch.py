#!/usr/bin/env python3
"""
Generate outreach packages for all prospects researched on a given date.

Scans leads/prospects/YYYY-MM-DD-*/ directories for reports and runs
create_outreach.py on each.

Usage:
    generate_outreach_batch.py --date 2026-02-09
    generate_outreach_batch.py --date today
    generate_outreach_batch.py --date 2026-02-09 --template professional
"""

import argparse
import subprocess
import sys
from datetime import date
from pathlib import Path

WORKSPACE = Path.home() / ".openclaw" / "workspace"
PROSPECTS_DIR = WORKSPACE / "leads" / "prospects"
SKILL_SCRIPTS = Path(__file__).parent


def find_reports_for_date(target_date: str) -> list[Path]:
    """Find all prospect reports for a given date."""
    reports = []
    for d in PROSPECTS_DIR.iterdir():
        if d.is_dir() and d.name.startswith(target_date):
            for f in d.glob("*.md"):
                reports.append(f)
    return sorted(reports)


def main():
    parser = argparse.ArgumentParser(description="Batch outreach generation")
    parser.add_argument("--date", required=True, help="Date to process (YYYY-MM-DD or 'today')")
    parser.add_argument("--template", choices=["casual", "professional"], default="casual")
    args = parser.parse_args()

    target_date = date.today().isoformat() if args.date == "today" else args.date
    reports = find_reports_for_date(target_date)

    if not reports:
        print(f"No reports found for {target_date}", file=sys.stderr)
        sys.exit(0)

    print(f"📧 Generating outreach for {len(reports)} prospects from {target_date}\n", file=sys.stderr)

    success = 0
    errors = 0
    for i, report_path in enumerate(reports, 1):
        print(f"[{i}/{len(reports)}] {report_path.stem}...", file=sys.stderr)
        cmd = [
            "python3", str(SKILL_SCRIPTS / "create_outreach.py"),
            "--report", str(report_path),
            "--template", args.template
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"  ✅ {result.stdout.strip().split(chr(10))[-1] if result.stdout else 'done'}", file=sys.stderr)
            success += 1
        else:
            print(f"  ❌ {result.stderr[:200]}", file=sys.stderr)
            errors += 1

    print(f"\n✅ Batch outreach complete: {success} created, {errors} errors", file=sys.stderr)


if __name__ == "__main__":
    main()
