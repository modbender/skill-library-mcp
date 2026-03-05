#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
recent-dirs - openclaw-os-activity
Find recently opened directories via Windows File Explorer
"""
import sys
import json
from pathlib import Path
import subprocess
from datetime import datetime

# Configure console encoding for Windows
if sys.platform.startswith("win"):
    # Use UTF-8 for console output
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

OSQUERY = Path.home() / ".openclaw" / "tools" / "os-activity" / "osquery" / "osqueryi"
OSQUERY = OSQUERY.with_suffix(".exe") if sys.platform.startswith("win") else OSQUERY
if not OSQUERY.exists():
    print(f"Error: osquery not found. {OSQUERY} not found.", file=sys.stderr)
    sys.exit(1)
    
def safe_parse_timestamp(timestamp):
    try:
        return datetime.fromtimestamp(int(timestamp)).strftime("%Y-%m-%d %H:%M:%S")
    except (TypeError, ValueError, OSError):
        return ""

def recent_dirs():
    query = "SELECT source, path, accessed_time, created_time, modified_time FROM shellbags ORDER BY accessed_time DESC LIMIT 1000;"
    try:
        result = subprocess.run(
            [str(OSQUERY), "--json", query],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'  # Replace unencodable characters instead of failing
        )
    except Exception as e:
        print(f"Error running osquery: {e}", file=sys.stderr)
        sys.exit(1)
    
    if result.returncode != 0:
        print(f"Error running osquery: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    
    if not result.stdout or not result.stdout.strip():
        print("No data returned from osquery", file=sys.stderr)
        sys.exit(1)
    
    try:
        dirs = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON from osquery: {e}", file=sys.stderr)
        sys.exit(1)
    
    if not isinstance(dirs, list):
        print(f"Expected list from osquery, got {type(dirs)}", file=sys.stderr)
        sys.exit(1)
    
    print("Path|Source|Last Accessed Time|Last Modified Time|Created Time")
    for dir in dirs:
        try:
            source = dir.get("source", "")
            path = dir.get("path", "")
            accessed_time = dir.get("accessed_time", "")
            modified_time = dir.get("modified_time", "")
            created_time = dir.get("created_time", "")
            accessed_time = safe_parse_timestamp(accessed_time)
            modified_time = safe_parse_timestamp(modified_time)
            created_time = safe_parse_timestamp(created_time)
  
            print(f"{source}|{path}|{accessed_time}|{modified_time}|{created_time}")
        except (TypeError, ValueError) as e:
            print(f"Warning: Could not process directory entry: {e}", file=sys.stderr)

def main():
    recent_dirs()
    
if __name__ == "__main__":
    main()