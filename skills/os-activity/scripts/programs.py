#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
programs - openclaw-os-activity
Find what programs have installed on the operating system
"""
import sys
import json
from pathlib import Path
import subprocess

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

def programs():
    query = "SELECT name, version, install_location, publisher FROM programs ORDER BY name;"
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
        programs = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON from osquery: {e}", file=sys.stderr)
        sys.exit(1)
    
    if not isinstance(programs, list):
        print(f"Expected list from osquery, got {type(programs)}", file=sys.stderr)
        sys.exit(1)
    
    print("Name|Publisher|Version|Install Location")
    for program in programs:
        try:
            name = program.get("name", "")
            publisher = program.get("publisher", "")
            version = program.get("version", "")
            install_location = program.get("install_location", "")
            
            print(f"{name}|{publisher}|{version}|{install_location}")
        except (TypeError, ValueError) as e:
            print(f"Warning: Could not process program entry: {e}", file=sys.stderr)

def main():
    programs()
    
if __name__ == "__main__":
    main()