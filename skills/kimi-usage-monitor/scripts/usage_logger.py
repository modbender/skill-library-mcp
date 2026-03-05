#!/usr/bin/env python3
"""
Kimi Usage Logger - For autonomous operation and cron integration.
Logs usage to activity feed and memory for decision-making.
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent

def check_usage():
    """Run usage check and return data."""
    script = SKILL_DIR / "scripts" / "fetch_usage.py"
    
    try:
        result = subprocess.run(
            ["python3", str(script), "--json"],
            capture_output=True,
            text=True,
            timeout=60
        )
        return json.loads(result.stdout)
    except Exception as e:
        return {"error": str(e)}

def make_decision(data):
    """Return decision recommendation based on usage."""
    if "error" in data:
        return "⚠️ Could not check usage — proceed with caution"
    
    usage = data.get('weekly_usage_percent', 50)
    remaining = 100 - usage
    
    if remaining > 50:
        return "🟢 High capacity — full operations approved"
    elif remaining > 25:
        return "🟡 Moderate capacity — prioritize essential tasks"
    else:
        return "🔴 Low capacity — essential tasks only, defer proactive work"

if __name__ == "__main__":
    data = check_usage()
    
    # Print decision for autonomous systems
    decision = make_decision(data)
    print(decision)
    
    # Output JSON for parsing
    if "--json" in sys.argv:
        print(json.dumps({
            "decision": decision,
            "usage": data
        }, indent=2))
