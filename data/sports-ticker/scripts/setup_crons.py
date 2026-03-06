#!/usr/bin/env python3
"""
Generate cron job configurations for sports-ticker skill.

Outputs JSON configurations that the agent can use with the cron tool.
Does NOT create crons directly — the agent handles that via platform tools.

Usage:
    python3 setup_crons.py <telegram_id> <timezone>
    python3 setup_crons.py 123456789 "Europe/London"
    python3 setup_crons.py --list  # Show example configs
"""

import sys
import json
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
SCRIPT_DIR = SKILL_DIR / "scripts"


def get_cron_configs(telegram_id: str, timezone: str) -> list[dict]:
    """Generate cron job configurations for the agent to create."""
    
    return [
        {
            "name": "football-match-check",
            "description": "Daily morning check for team matches. Auto-updates live-ticker schedule when matches found.",
            "schedule": {
                "kind": "cron",
                "expr": "0 9 * * *",
                "tz": timezone
            },
            "sessionTarget": "isolated",
            "payload": {
                "kind": "agentTurn",
                "message": f"Check if any configured teams play today.\n\nRun: python3 {SCRIPT_DIR}/ticker.py\n\nIf a match is found today:\n1. Send match info to Telegram\n2. Update the live-ticker cron schedule to run every 2 mins during match hours\n3. Set a reminder 5 mins before kickoff\n\nIf no match today, reply NO_REPLY"
            },
            "delivery": {
                "mode": "announce",
                "channel": "telegram",
                "to": telegram_id,
                "bestEffort": True
            },
            "enabled": True
        },
        {
            "name": "sports-live-ticker",
            "description": "Live match monitoring - runs every 2 mins during matches. Auto-scheduled by match-check.",
            "schedule": {
                "kind": "cron",
                "expr": "*/2 * * * *",
                "tz": timezone
            },
            "sessionTarget": "isolated",
            "payload": {
                "kind": "agentTurn",
                "message": f"Run: python3 {SCRIPT_DIR}/live_monitor.py\n\nIf output contains alerts (goals, kick-off, full-time, red cards), format nicely and include in response.\nIf no alerts, reply NO_REPLY"
            },
            "delivery": {
                "mode": "announce",
                "channel": "telegram",
                "to": telegram_id,
                "bestEffort": False
            },
            "enabled": False
        },
        {
            "name": "sports-reminder",
            "description": "Pre-match reminder. Auto-scheduled by match-check.",
            "schedule": {
                "kind": "cron",
                "expr": "0 14 * * *",
                "tz": timezone
            },
            "sessionTarget": "main",
            "payload": {
                "kind": "systemEvent",
                "text": "⏰ Match reminder: Your team plays soon! Check the schedule."
            },
            "enabled": False
        }
    ]


def main():
    if len(sys.argv) == 2 and sys.argv[1] == "--list":
        crons = get_cron_configs("YOUR_TELEGRAM_ID", "Europe/London")
        print(json.dumps(crons, indent=2))
        return
    
    if len(sys.argv) < 3:
        print(__doc__)
        print("\nExamples:")
        print("  python3 setup_crons.py 123456789 'Europe/London'")
        print("  python3 setup_crons.py --list")
        sys.exit(1)
    
    telegram_id = sys.argv[1]
    timezone = sys.argv[2]
    
    crons = get_cron_configs(telegram_id, timezone)
    
    # Output JSON for the agent to use with cron tool
    print(json.dumps({
        "instructions": "Use the cron tool to create these jobs. Do NOT use subprocess or CLI commands.",
        "crons": crons
    }, indent=2))
    
    # Save configs for reference
    config_file = SKILL_DIR / "cron_configs.json"
    with open(config_file, "w") as f:
        json.dump(crons, f, indent=2)


if __name__ == "__main__":
    main()
