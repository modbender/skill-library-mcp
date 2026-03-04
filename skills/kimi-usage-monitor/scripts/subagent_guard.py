#!/usr/bin/env python3
"""
Smart subagent spawner with quota awareness.
Checks usage before spawning intensive subagents.
"""

import json
import subprocess
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent

def get_usage():
    """Get current usage."""
    try:
        result = subprocess.run(
            ["python3", str(SKILL_DIR / "scripts/fetch_usage.py"), "--json"],
            capture_output=True,
            text=True,
            timeout=60
        )
        return json.loads(result.stdout)
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    data = get_usage()
    
    if "error" in data:
        print(json.dumps({
            "can_spawn": True,
            "error": data["error"],
            "note": "Defaulting to allow due to check failure"
        }, indent=2))
        sys.exit(0)
    
    usage = data.get('weekly_usage_percent', 50)
    remaining = 100 - usage
    
    can_spawn = remaining >= 25
    
    result = {
        "can_spawn": can_spawn,
        "usage_percent": usage,
        "remaining_percent": remaining,
        "resets_hours": data.get('weekly_resets_hours')
    }
    
    print(json.dumps(result, indent=2))
    sys.exit(0 if can_spawn else 1)
