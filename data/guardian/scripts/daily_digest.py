#!/usr/bin/env python3
"""
Guardian Daily Digest Script
-----------------------------
Generates and outputs the daily security digest for delivery
to the agent's primary channel via OpenClaw message infrastructure.

When run via OpenClaw cron with message delivery enabled, the stdout
will be automatically sent to the configured channel.

Usage (in crontab):
  0 9 * * * openclaw run "python3 skills/guardian/scripts/daily_digest.py" --deliver-to=agent
  
Or as a standalone script for testing:
  python3 scripts/daily_digest.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def skill_root() -> Path:
    """Return the Guardian skill root."""
    return Path(__file__).resolve().parents[1]


# Shared config loader (prefers OpenClaw config → guardian config.json)
sys.path.insert(0, str(skill_root() / "core"))
from settings import load_config  # type: ignore  # noqa: E402


def main() -> int:
    """Generate and output the daily digest."""
    cfg = load_config()
    
    # Check if daily digest is enabled
    if not cfg.get("alerts", {}).get("daily_digest", True):
        # Digest disabled in config — exit silently
        return 0
    
    # Check if Guardian is enabled
    if not cfg.get("enabled", True):
        # Guardian disabled — skip digest
        return 0
    
    # Generate the report using admin.py
    admin_script = skill_root() / "scripts" / "admin.py"
    try:
        result = subprocess.run(
            [sys.executable, str(admin_script), "report", "--deliver"],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        
        if result.returncode != 0:
            sys.stderr.write(f"Report generation failed: {result.stderr}\n")
            return 1
        
        report_text = result.stdout.strip()
        if not report_text:
            sys.stderr.write("Report generated but was empty\n")
            return 1
        
        # Output the report to stdout (will be delivered by OpenClaw infrastructure)
        print(report_text)
        return 0
    
    except subprocess.TimeoutExpired:
        sys.stderr.write("Report generation timed out\n")
        return 1
    except Exception as e:
        sys.stderr.write(f"Unexpected error: {e}\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
