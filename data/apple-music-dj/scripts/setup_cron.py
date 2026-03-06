#!/usr/bin/env python3
"""
setup_cron.py — Automation scheduler for Apple Music DJ.

Generates and installs crontab entries for recurring jobs:
  weekly-mix        Generate a fresh playlist every Monday morning
  new-releases      Check for new releases from favourite artists weekly
  daily-drop        Surface a daily pick recommendation
  health-check      Scan playlists for removed/stale tracks monthly

Usage:
  python3 setup_cron.py list                    Show planned cron jobs
  python3 setup_cron.py install [--jobs J,...]  Install selected (or all) jobs
  python3 setup_cron.py remove  [--jobs J,...]  Remove selected (or all) jobs
  python3 setup_cron.py status                  Show currently installed jobs

Options:
  --profile PATH    Path to taste profile JSON (required for install)
  --storefront SF   Storefront code (default: from config)
  --log-dir DIR     Directory for log files (default: ~/.apple-music-dj/logs)

Requires: crontab available on the system.
"""

import sys
if sys.version_info < (3, 9):
    sys.exit(
        f"ERROR: Python 3.9+ is required (you have "
        f"{sys.version_info.major}.{sys.version_info.minor}). Please upgrade."
    )

import argparse
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from _common import load_config

SCRIPT_DIR = Path(__file__).resolve().parent
MARKER = "# apple-music-dj"


# ── Job Definitions ──────────────────────────────────────────────

def build_job_defs(python: str, profile: str, sf: str,
                   log_dir: str) -> dict[str, dict]:
    """Return cron job definitions keyed by job name."""
    strategy = SCRIPT_DIR / "strategy_engine.py"
    daily_pick = SCRIPT_DIR / "daily_pick.py"
    new_releases = SCRIPT_DIR / "new_releases.sh"
    health = SCRIPT_DIR / "playlist_health.py"

    return {
        "weekly-mix": {
            "description": "Generate a fresh playlist every Monday at 7 AM",
            "schedule": "0 7 * * 1",
            "command": (
                f"{python} {strategy} --strategy trend "
                f"--profile {profile} --storefront {sf} --create"
            ),
            "log": f"{log_dir}/weekly-mix.log",
        },
        "new-releases": {
            "description": "Check for new releases every Wednesday at 8 AM",
            "schedule": "0 8 * * 3",
            "command": f"bash {new_releases} {sf}",
            "log": f"{log_dir}/new-releases.log",
        },
        "daily-drop": {
            "description": "Surface a daily pick every day at 8:30 AM",
            "schedule": "30 8 * * *",
            "command": (
                f"{python} {daily_pick} daily --profile {profile}"
            ),
            "log": f"{log_dir}/daily-drop.log",
        },
        "health-check": {
            "description": "Scan playlists for issues on the 1st of each month",
            "schedule": "0 9 1 * *",
            "command": (
                f"{python} {health} check all --profile {profile}"
            ),
            "log": f"{log_dir}/health-check.log",
        },
    }


def format_cron_line(job: dict, name: str) -> str:
    """Format a single crontab line with logging and marker."""
    return (
        f"{job['schedule']} {job['command']} >> {job['log']} 2>&1 "
        f"{MARKER}:{name}"
    )


# ── Crontab Interaction ─────────────────────────────────────────

def get_current_crontab() -> str:
    """Read current crontab, returning empty string if none."""
    try:
        result = subprocess.run(
            ["crontab", "-l"], capture_output=True, text=True
        )
        if result.returncode == 0:
            return result.stdout
    except FileNotFoundError:
        print("ERROR: crontab not found on this system.", file=sys.stderr)
        sys.exit(1)
    return ""


def set_crontab(content: str) -> bool:
    """Write content as the new crontab."""
    try:
        result = subprocess.run(
            ["crontab", "-"], input=content, capture_output=True, text=True
        )
        return result.returncode == 0
    except FileNotFoundError:
        print("ERROR: crontab not found on this system.", file=sys.stderr)
        return False


def get_installed_jobs() -> list[str]:
    """Return list of installed apple-music-dj job names."""
    crontab = get_current_crontab()
    jobs = []
    for line in crontab.splitlines():
        if MARKER in line:
            # Extract job name from marker
            parts = line.split(f"{MARKER}:")
            if len(parts) > 1:
                jobs.append(parts[-1].strip())
    return jobs


# ── Commands ─────────────────────────────────────────────────────

def cmd_list(job_defs: dict[str, dict]):
    """Show all available jobs and their schedules."""
    installed = set(get_installed_jobs())
    print("Available apple-music-dj cron jobs:\n")
    for name, job in job_defs.items():
        status = "✅ installed" if name in installed else "⬚ not installed"
        print(f"  {name:20s} {status}")
        print(f"    {job['description']}")
        print(f"    Schedule: {job['schedule']}")
        print(f"    Command:  {job['command']}")
        print(f"    Log:      {job['log']}")
        print()


def cmd_install(job_defs: dict[str, dict], selected: list[str],
                log_dir: str):
    """Install selected cron jobs."""
    # Ensure log directory exists
    Path(log_dir).mkdir(parents=True, exist_ok=True)

    crontab = get_current_crontab()
    lines = crontab.splitlines()

    # Remove existing apple-music-dj lines for selected jobs
    filtered = []
    for line in lines:
        is_ours = False
        for name in selected:
            if f"{MARKER}:{name}" in line:
                is_ours = True
                break
        if not is_ours:
            filtered.append(line)

    # Add new lines
    for name in selected:
        if name not in job_defs:
            print(f"WARNING: Unknown job '{name}', skipping.", file=sys.stderr)
            continue
        new_line = format_cron_line(job_defs[name], name)
        filtered.append(new_line)
        print(f"  ✅ {name}: {job_defs[name]['schedule']}")

    new_crontab = "\n".join(filtered)
    if not new_crontab.endswith("\n"):
        new_crontab += "\n"

    if set_crontab(new_crontab):
        print(f"\n{len(selected)} job(s) installed successfully.")
    else:
        print("ERROR: Failed to update crontab.", file=sys.stderr)
        sys.exit(1)


def cmd_remove(job_defs: dict[str, dict], selected: list[str]):
    """Remove selected cron jobs."""
    crontab = get_current_crontab()
    lines = crontab.splitlines()

    removed = 0
    filtered = []
    for line in lines:
        is_ours = False
        for name in selected:
            if f"{MARKER}:{name}" in line:
                is_ours = True
                removed += 1
                print(f"  🗑  Removed: {name}")
                break
        if not is_ours:
            filtered.append(line)

    if removed == 0:
        print("No matching jobs found to remove.")
        return

    new_crontab = "\n".join(filtered)
    if not new_crontab.endswith("\n"):
        new_crontab += "\n"

    if set_crontab(new_crontab):
        print(f"\n{removed} job(s) removed.")
    else:
        print("ERROR: Failed to update crontab.", file=sys.stderr)
        sys.exit(1)


def cmd_status():
    """Show currently installed apple-music-dj cron jobs."""
    installed = get_installed_jobs()
    if not installed:
        print("No apple-music-dj cron jobs currently installed.")
        return

    print(f"{len(installed)} apple-music-dj job(s) installed:\n")
    crontab = get_current_crontab()
    for line in crontab.splitlines():
        if MARKER in line:
            print(f"  {line}")
    print()


# ── Main ─────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Apple Music DJ — Automation Scheduler"
    )
    parser.add_argument("command", choices=["list", "install", "remove", "status"],
                        help="Action to perform")
    parser.add_argument("--jobs", default=None,
                        help="Comma-separated job names (default: all)")
    parser.add_argument("--profile", default=None,
                        help="Path to taste profile JSON")
    parser.add_argument("--storefront", default=None,
                        help="Storefront code")
    parser.add_argument("--log-dir", default=None,
                        help="Directory for log files")
    parser.add_argument("--python", default=None,
                        help="Path to python3 executable")

    args = parser.parse_args()
    config = load_config()

    # Resolve defaults
    sf = args.storefront or config.get("default_storefront", "us")
    log_dir = args.log_dir or str(Path.home() / ".apple-music-dj" / "logs")
    python_path = args.python or sys.executable
    profile = args.profile or str(Path.home() / ".apple-music-dj" / "profile.json")

    job_defs = build_job_defs(python_path, profile, sf, log_dir)
    all_names = list(job_defs.keys())

    selected = all_names
    if args.jobs:
        selected = [j.strip() for j in args.jobs.split(",")]

    if args.command == "list":
        cmd_list(job_defs)
    elif args.command == "install":
        if not args.profile:
            print("WARNING: Using default profile path. "
                  "Specify --profile for a custom location.", file=sys.stderr)
        cmd_install(job_defs, selected, log_dir)
    elif args.command == "remove":
        cmd_remove(job_defs, selected)
    elif args.command == "status":
        cmd_status()


if __name__ == "__main__":
    main()
