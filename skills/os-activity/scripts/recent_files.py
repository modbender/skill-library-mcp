#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
recent-files - openclaw-os-activity
Find recently edited files of the operating system
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

def recent_files():
    query = "SELECT filename, path, type, mtime FROM recent_files ORDER BY mtime DESC LIMIT 100;"
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
        files = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON from osquery: {e}", file=sys.stderr)
        sys.exit(1)
    
    if not isinstance(files, list):
        print(f"Expected list from osquery, got {type(files)}", file=sys.stderr)
        sys.exit(1)
    
    print("Filename|Path|Type|Last Edited Time")
    for file in files:
        try:
            filename = file.get("filename", "")
            path = file.get("path", "")
            file_type = file.get("type", "")
            mtime_ts = file.get("mtime", 0)
            
            if not mtime_ts:
                mtime_str = ""
            else:
                mtime_str = datetime.fromtimestamp(int(mtime_ts)).strftime("%Y-%m-%d %H:%M:%S")
            
            print(f"{filename}|{path}|{file_type}|{mtime_str}")
        except (TypeError, ValueError) as e:
            print(f"Warning: Could not process file entry: {e}", file=sys.stderr)

def main():
    recent_files()
    
if __name__ == "__main__":
    main()