#!/usr/bin/env python3
"""
Pre-flight check for intensive operations.
Call this before spawning subagents or starting multi-step research.
"""

import json
import subprocess
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent

def check_usage():
    """Get current usage data."""
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

def preflight_check(operation_type="standard"):
    """
    Check if we should proceed with operation.
    
    operation_type: 'light', 'standard', 'intensive'
    Returns: (should_proceed, message, usage_data)
    """
    data = check_usage()
    
    if "error" in data:
        return False, f"⚠️ Could not check usage: {data['error']}", data
    
    usage = data.get('weekly_usage_percent', 50)
    remaining = 100 - usage
    
    # Thresholds by operation type
    thresholds = {
        "light": 10,      # Need only 10% remaining
        "standard": 25,   # Need 25% remaining
        "intensive": 50   # Need 50% remaining
    }
    
    min_remaining = thresholds.get(operation_type, 25)
    
    if remaining >= min_remaining:
        return True, f"🟢 {operation_type.title()} operation approved ({remaining}% remaining)", data
    elif remaining >= min_remaining // 2:
        return True, f"🟡 Proceeding with caution ({remaining}% remaining, wanted {min_remaining}%)", data
    else:
        return False, f"🔴 {operation_type.title()} operation blocked — only {remaining}% remaining (need {min_remaining}%)", data

if __name__ == "__main__":
    op_type = sys.argv[1] if len(sys.argv) > 1 else "standard"
    proceed, message, data = preflight_check(op_type)
    
    print(message)
    
    if "--json" in sys.argv:
        print(json.dumps({
            "proceed": proceed,
            "message": message,
            "usage": data,
            "operation_type": op_type
        }, indent=2))
    
    sys.exit(0 if proceed else 1)
