#!/usr/bin/env python3
"""
PackageTracker — Standalone update checker for cron/scheduled tasks.
Checks all active packages and sends Telegram notifications for changes.

Usage:
    python check_updates.py          # Check all active packages
    python check_updates.py --quiet  # Suppress "no updates" output

Exit codes: 0 = success, 1 = error
"""

import argparse
import sys
import os

# Ensure we can import tracker module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tracker import check_updates, list_packages


def main():
    parser = argparse.ArgumentParser(description="Check package tracking updates")
    parser.add_argument("-q", "--quiet", action="store_true", help="Suppress output when no updates")
    args = parser.parse_args()

    try:
        active = list_packages(active_only=True)
        if not active:
            if not args.quiet:
                print("📭 No active packages to check")
            return 0

        if not args.quiet:
            print(f"🔍 Checking {len(active)} active package(s)...")

        updates = check_updates()

        if not args.quiet or updates:
            print(f"✅ Check complete. {len(updates)} update(s) found.")

        return 0
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
