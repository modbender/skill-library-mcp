#!/usr/bin/env python3
"""
Kimi Usage Monitor - Fetches usage via OpenClaw browser tool.

Requires Chrome with OpenClaw extension attached to a tab
at https://www.kimi.com/code/console
"""

import json
import subprocess
import sys
import re

def get_usage():
    """Get usage data from Kimi console via browser."""
    
    # First, find the Kimi console tab
    result = subprocess.run(
        ["openclaw", "browser", "tabs"],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    if result.returncode != 0:
        return {"error": "Browser not available", "message": "Ensure Chrome extension is attached"}
    
    # Parse to find Kimi tab ID
    tabs_output = result.stdout
    kimi_tab_id = None
    
    # Try to find targetId for kimi.com URL
    for line in tabs_output.split('\n'):
        if '"url":' in line and 'kimi.com' in line:
            # Look for targetId in nearby lines
            pass
    
    # Alternative: look for targetId pattern
    import re
    matches = re.findall(r'targetId["\']?\s*:\s*["\']?([A-F0-9]+)', tabs_output)
    
    # Try each targetId until we find the Kimi tab
    for target_id in matches:
        snap_result = subprocess.run(
            ["openclaw", "browser", "snapshot", "--target-id", target_id],
            capture_output=True,
            text=True,
            timeout=30
        )
        if snap_result.returncode == 0 and "kimi.com" in snap_result.stdout.lower():
            kimi_tab_id = target_id
            snapshot = snap_result.stdout
            break
    
    if not kimi_tab_id:
        return {"error": "Kimi console tab not found", "message": "Open https://www.kimi.com/code/console and attach the extension"}
    
    # Parse usage data from snapshot
    data = {
        "timestamp": subprocess.check_output(["date", "+%Y-%m-%d %H:%M:%S"]).decode().strip()
    }
    
    # Find Weekly usage section
    weekly_match = re.search(r'Weekly usage.*?([0-9]+)%', snapshot, re.DOTALL | re.IGNORECASE)
    if weekly_match:
        data["weekly_usage_percent"] = int(weekly_match.group(1))
    
    weekly_reset = re.search(r'Resets in ([0-9]+) hours?', snapshot, re.IGNORECASE)
    if weekly_reset:
        data["weekly_resets_hours"] = int(weekly_reset.group(1))
    
    # Find Rate limit section
    rate_match = re.search(r'Rate limit details.*?([0-9]+)%', snapshot, re.DOTALL | re.IGNORECASE)
    if rate_match:
        data["rate_limit_percent"] = int(rate_match.group(1))
    
    # Find second "Resets in" for rate limit
    resets = re.findall(r'Resets in ([0-9]+) hours?', snapshot, re.IGNORECASE)
    if len(resets) >= 2:
        data["rate_limit_resets_hours"] = int(resets[1])
    elif len(resets) == 1:
        data["rate_limit_resets_hours"] = int(resets[0])
    
    return data

def format_output(data, as_json=False):
    if as_json:
        print(json.dumps(data, indent=2))
        return
    
    if "error" in data:
        print(f"❌ {data['error']}")
        if "message" in data:
            print(f"   {data['message']}")
        return
    
    print("📊 Kimi Usage Monitor")
    print("=" * 40)
    
    if "weekly_usage_percent" in data:
        used = data["weekly_usage_percent"]
        remaining = 100 - used
        hours = data.get("weekly_resets_hours", "?")
        print(f"\n🗓️  Weekly Usage")
        print(f"   Used: {used}%")
        print(f"   Remaining: {remaining}%")
        print(f"   Resets in: {hours} hours")
        
        if remaining > 50:
            print(f"   Status: 🟢 Healthy — full ops approved")
        elif remaining > 25:
            print(f"   Status: 🟡 Moderate — plan accordingly")
        else:
            print(f"   Status: 🔴 Low — prioritize essential tasks")
    
    if "rate_limit_percent" in data:
        used = data["rate_limit_percent"]
        hours = data.get("rate_limit_resets_hours", "?")
        print(f"\n⚡ Rate Limit")
        print(f"   Used: {used}%")
        print(f"   Resets in: {hours} hours")

if __name__ == "__main__":
    as_json = "--json" in sys.argv
    data = get_usage()
    format_output(data, as_json)
