#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
processes - openclaw-os-activity
Find what processes are running on the operating system
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

def processes():
    query = "SELECT pid, name, parent, path, start_time, cmdline, cwd, user_time, system_time, percent_processor_time FROM processes ORDER BY pid;"
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
        processes = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON from osquery: {e}", file=sys.stderr)
        sys.exit(1)
    
    if not isinstance(processes, list):
        print(f"Expected list from osquery, got {type(processes)}", file=sys.stderr)
        sys.exit(1)
    
    print("PID|Name|Parent|Path|Start Time|Command Line|Current Working Directory|User Time|System Time|Percent Processor Time")
    for process in processes:
        try:
            pid = process.get("pid", "")
            name = process.get("name", "")
            parent = process.get("parent", "")
            path = process.get("path", "")
            start_time = process.get("start_time", "")
            cmdline = process.get("cmdline", "")
            cwd = process.get("cwd", "")
            user_time = process.get("user_time", "")
            system_time = process.get("system_time", "")
            percent_processor_time = process.get("percent_processor_time", "")
            
            if start_time != "":
                try:
                    start_time = datetime.fromtimestamp(int(start_time)).strftime("%Y-%m-%d %H:%M:%S")
                except (TypeError, ValueError, OSError):
                    start_time = ""

            print(f"{pid}|{name}|{parent}|{path}|{start_time}|{cmdline}|{cwd}|{user_time}|{system_time}|{percent_processor_time}")
        except (TypeError, ValueError, OSError) as e:
            print(f"Warning: Could not process process entry: {e}", file=sys.stderr)

def main():
    processes()
    
if __name__ == "__main__":
    main()