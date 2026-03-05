"""
hourly_heartbeat.py — Top-500 Skill Snapshot + Project Metadata

Runs every hour via Windows Task Scheduler.
- Snapshots the top 500 ClawHub skills (5 pages, ~4 seconds)
- Tracks OpenClaw ecosystem GitHub repos (stars, PRs, releases)
- Append-only inserts — no dedup destruction of earlier hourly rows

Usage:
    python hourly_heartbeat.py              # Normal run
    python hourly_heartbeat.py --pages 10   # More skills
    python hourly_heartbeat.py --skip-meta  # Skip GitHub metadata
"""

import argparse
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Ensure project root is in path
sys.path.insert(0, str(Path(__file__).parent))

import discovery
import storage
import project_tracker


def main():
    parser = argparse.ArgumentParser(description="Hourly heartbeat snapshot")
    parser.add_argument("--pages", type=int, default=5, help="API pages to fetch (100 skills/page)")
    parser.add_argument("--skip-meta", action="store_true", help="Skip GitHub project metadata")
    args = parser.parse_args()

    now = datetime.now(timezone.utc)
    print(f"[HEARTBEAT] {now.strftime('%Y-%m-%d %H:%M')} UTC — top-{args.pages * 100} snapshot")

    # Phase 1: ClawHub skill snapshot
    storage.init_db()

    skills = discovery.discover(
        sort="downloads",
        max_pages=args.pages,
    )

    if not skills:
        print("[HEARTBEAT] No skills returned — aborting")
        return

    storage.upsert_skills(skills)
    storage.append_snapshot(skills)

    # Phase 2: OpenClaw ecosystem metadata
    if not args.skip_meta:
        print("[HEARTBEAT] Tracking OpenClaw ecosystem repos...")
        try:
            project_tracker.capture()
        except Exception as e:
            print(f"[HEARTBEAT] Project tracker failed (non-fatal): {e}")

    print(f"[HEARTBEAT] Complete — {len(skills)} skills, {now.strftime('%H:%M')} UTC")


if __name__ == "__main__":
    main()
