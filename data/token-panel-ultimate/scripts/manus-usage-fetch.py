#!/usr/bin/env python3
"""Manus credit usage fetcher.

Fetches task history from Manus API, calculates credit usage,
and updates memory/manus-usage.json for the token panel widget.

Usage:
    python3 manus-usage-fetch.py              # Pretty print
    python3 manus-usage-fetch.py --update     # Update JSON file
    python3 manus-usage-fetch.py --json       # Raw JSON output

Env:
    MANUS_API_KEY  - Required. Manus API key.

Credit structure (Pro plan):
    - Monthly: 4,000 credits (resets on renewal date)
    - Daily refresh: 300 credits (resets at 01:00 local)
    - Addon: Purchased credits (never expire)
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError

API_BASE = "https://api.manus.ai/v1"
DEFAULT_OUTPUT = Path.home() / ".openclaw/workspace/memory/manus-usage.json"

# Plan defaults (Pro)
MONTHLY_LIMIT = 4000
DAILY_REFRESH_LIMIT = 300
DAILY_RESET_HOUR = 1  # 01:00 local


def fetch_tasks(api_key: str) -> list:
    """Fetch all tasks from Manus API."""
    url = f"{API_BASE}/tasks"
    req = Request(url, headers={"API_KEY": api_key})
    try:
        with urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
            return data.get("data", [])
    except HTTPError as e:
        print(f"Error fetching tasks: {e.code} {e.reason}", file=sys.stderr)
        sys.exit(1)


def compute_usage(tasks: list, existing_data: dict) -> dict:
    """Compute credit usage from task list."""
    now = datetime.now()
    today_start = now.replace(hour=DAILY_RESET_HOUR, minute=0, second=0, microsecond=0)
    if now < today_start:
        today_start -= timedelta(days=1)

    # Get renewal date from existing data or default
    renewal_date = existing_data.get("renewal_date", "2026-09-29")

    # Addon credits from existing (can't be derived from API)
    addon = existing_data.get("credits", {}).get("breakdown", {}).get("addon", 0)

    # Calculate totals
    total_credits = 0
    monthly_used = 0
    daily_used = 0
    today_tasks = []

    for t in tasks:
        credits = t.get("credit_usage", 0)
        if not isinstance(credits, (int, float)):
            continue
        total_credits += credits

        ts = datetime.fromtimestamp(int(t["created_at"]))

        # Daily (since last reset at 01:00)
        if ts >= today_start:
            daily_used += credits
            today_tasks.append({
                "task": t.get("metadata", {}).get("task_title", "untitled")[:80],
                "credits": credits,
                "time": ts.strftime("%H:%M"),
            })

    # Monthly used = total credits this billing period
    # Since we can't know exact renewal cycle from API, use all-time for now
    # and let the user correct via existing data
    monthly_used = existing_data.get("credits", {}).get("breakdown", {}).get("monthly", {}).get("used", 0)

    # Recalculate from tasks in current month (rough approximation)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    monthly_credits_this_month = sum(
        t.get("credit_usage", 0)
        for t in tasks
        if isinstance(t.get("credit_usage"), (int, float))
        and datetime.fromtimestamp(int(t["created_at"])) >= month_start
    )

    daily_remaining = max(0, DAILY_REFRESH_LIMIT - daily_used)

    return {
        "plan": "pro",
        "renewal_date": renewal_date,
        "last_updated": now.strftime("%Y-%m-%dT%H:%M:%S"),
        # Flat fields for gateway budget-panel plugin compatibility
        "credits_used": monthly_credits_this_month,
        "credits_budget": MONTHLY_LIMIT,
        "credits": {
            "total_all_time": total_credits,
            "breakdown": {
                "monthly": {
                    "used": monthly_credits_this_month,
                    "limit": MONTHLY_LIMIT,
                    "remaining": max(0, MONTHLY_LIMIT - monthly_credits_this_month),
                },
                "addon": addon,
            },
            "daily_refresh": {
                "used": daily_used,
                "remaining": daily_remaining,
                "limit": DAILY_REFRESH_LIMIT,
                "reset_time": f"{DAILY_RESET_HOUR:02d}:00 local",
                "period_start": today_start.strftime("%Y-%m-%dT%H:%M:%S"),
            },
        },
        "today": {
            "tasks": len(today_tasks),
            "credits_used": daily_used,
            "breakdown": today_tasks,
        },
        "notes": {
            "cost_per_credit": "~$0.01",
            "monthly_reset": f"On renewal date ({renewal_date})",
            "daily_refresh": f"{DAILY_REFRESH_LIMIT} credits refresh at {DAILY_RESET_HOUR:02d}:00 each day",
            "total_tasks_fetched": len(tasks),
        },
    }


def main():
    parser = argparse.ArgumentParser(description="Fetch Manus credit usage")
    parser.add_argument("--update", action="store_true", help="Update JSON file")
    parser.add_argument("--json", action="store_true", help="Raw JSON output")
    parser.add_argument("--output", type=str, default=str(DEFAULT_OUTPUT), help="Output file path")
    args = parser.parse_args()

    api_key = os.environ.get("MANUS_API_KEY")
    if not api_key:
        # Fallback: Try to read from ~/.openclaw/openclaw.json
        try:
            config_path = Path.home() / ".openclaw/openclaw.json"
            if config_path.exists():
                data = json.loads(config_path.read_text())
                api_key = data.get("env", {}).get("MANUS_API_KEY")
        except Exception:
            pass

    if not api_key:
        print("Error: MANUS_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    # Load existing data for addon credits & renewal date
    output_path = Path(args.output)
    existing = {}
    if output_path.exists():
        try:
            existing = json.loads(output_path.read_text())
        except json.JSONDecodeError:
            pass

    tasks = fetch_tasks(api_key)
    usage = compute_usage(tasks, existing)

    if args.json:
        print(json.dumps(usage, indent=2))
    elif args.update:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(usage, indent=2) + "\n")
        print(f"✔ Updated {output_path}")
        # Print summary
        c = usage["credits"]
        d = c["daily_refresh"]
        m = c["breakdown"]["monthly"]
        print(f"  Daily:   {d['used']}/{d['limit']} ({d['remaining']} remaining)")
        print(f"  Monthly: {m['used']}/{m['limit']} ({m['remaining']} remaining)")
        print(f"  Today:   {usage['today']['tasks']} tasks, {usage['today']['credits_used']} credits")
    else:
        # Pretty print
        c = usage["credits"]
        d = c["daily_refresh"]
        m = c["breakdown"]["monthly"]
        print("═══ Manus Credit Usage ═══")
        print(f"  Daily:   {d['used']:>4}/{d['limit']} ({d['remaining']} remaining) [resets {d['reset_time']}]")
        print(f"  Monthly: {m['used']:>4}/{m['limit']} ({m['remaining']} remaining)")
        print(f"  Addon:   {c['breakdown']['addon']}")
        print(f"  All-time: {c['total_all_time']} credits across {usage['notes']['total_tasks_fetched']} tasks")
        print(f"\n  Today: {usage['today']['tasks']} tasks, {usage['today']['credits_used']} credits")
        for t in usage["today"]["breakdown"]:
            print(f"    {t['time']} | {t['credits']:>4} cr | {t['task']}")
        print(f"\n  Last updated: {usage['last_updated']}")


if __name__ == "__main__":
    main()
