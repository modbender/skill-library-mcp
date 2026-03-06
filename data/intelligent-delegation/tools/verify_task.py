#!/usr/bin/env python3
"""
Task output verification tool.
Run checks against delegated task output to confirm success.

Usage:
    python3 verify_task.py --check file_exists --path /path/to/file
    python3 verify_task.py --check valid_json --path /path/to/file.json
    python3 verify_task.py --check min_size --path /path/to/file --min 100
    python3 verify_task.py --check json_min_items --path /path/to/file.json --min 10
    python3 verify_task.py --check markdown_sections --path /path/to/file.md --sections "Overview,Summary"
    python3 verify_task.py --check sqlite_rows --path /path/to/db --table items --min 100
    python3 verify_task.py --check port_alive --port 8080
    python3 verify_task.py --check all --manifest /path/to/manifest.json

Manifest format (for --check all):
[
    {"check": "file_exists", "path": "/path/to/file"},
    {"check": "valid_json", "path": "/path/to/file.json"},
    {"check": "sqlite_rows", "path": "/path/to/db", "table": "items", "min": 100}
]

Exit codes:
    0 = all checks passed
    1 = one or more checks failed
    2 = usage error
"""

import argparse
import json
import os
import sqlite3
import sys
import urllib.request


def check_file_exists(path, **_):
    if os.path.exists(path):
        size = os.path.getsize(path)
        return True, f"✅ File exists: {path} ({size} bytes)"
    return False, f"❌ File not found: {path}"


def check_valid_json(path, **_):
    if not os.path.exists(path):
        return False, f"❌ File not found: {path}"
    try:
        with open(path) as f:
            data = json.load(f)
        if isinstance(data, list):
            return True, f"✅ Valid JSON array with {len(data)} items"
        elif isinstance(data, dict):
            return True, f"✅ Valid JSON object with {len(data)} keys"
        return True, f"✅ Valid JSON ({type(data).__name__})"
    except json.JSONDecodeError as e:
        return False, f"❌ Invalid JSON: {e}"


def check_min_size(path, min_bytes=100, **_):
    if not os.path.exists(path):
        return False, f"❌ File not found: {path}"
    size = os.path.getsize(path)
    if size >= int(min_bytes):
        return True, f"✅ File size {size} bytes >= {min_bytes}"
    return False, f"❌ File too small: {size} bytes < {min_bytes}"


def check_json_min_items(path, min_items=1, **_):
    if not os.path.exists(path):
        return False, f"❌ File not found: {path}"
    try:
        with open(path) as f:
            data = json.load(f)
        if isinstance(data, list) and len(data) >= int(min_items):
            return True, f"✅ JSON has {len(data)} items >= {min_items}"
        elif isinstance(data, list):
            return False, f"❌ JSON has {len(data)} items < {min_items}"
        return False, f"❌ JSON root is not an array"
    except json.JSONDecodeError as e:
        return False, f"❌ Invalid JSON: {e}"


def check_markdown_sections(path, sections="", **_):
    if not os.path.exists(path):
        return False, f"❌ File not found: {path}"
    with open(path) as f:
        content = f.read()
    required = [s.strip() for s in sections.split(",") if s.strip()]
    missing = []
    for section in required:
        if f"## {section}" not in content and f"# {section}" not in content:
            missing.append(section)
    if not missing:
        return True, f"✅ All {len(required)} required sections found"
    return False, f"❌ Missing sections: {', '.join(missing)}"


def check_sqlite_rows(path, table="", min_rows=1, **_):
    if not os.path.exists(path):
        return False, f"❌ Database not found: {path}"
    try:
        conn = sqlite3.connect(path)
        count = conn.execute(f"SELECT COUNT(*) FROM [{table}]").fetchone()[0]
        conn.close()
        if count >= int(min_rows):
            return True, f"✅ Table '{table}' has {count} rows >= {min_rows}"
        return False, f"❌ Table '{table}' has {count} rows < {min_rows}"
    except Exception as e:
        return False, f"❌ SQLite error: {e}"


def check_port_alive(port=0, **_):
    try:
        req = urllib.request.Request(f"http://127.0.0.1:{int(port)}/", method="HEAD")
        with urllib.request.urlopen(req, timeout=3) as resp:
            return True, f"✅ Port {port} responding (status {resp.status})"
    except urllib.error.HTTPError as e:
        return True, f"✅ Port {port} responding (status {e.code})"
    except Exception as e:
        return False, f"❌ Port {port} not responding: {e}"


CHECKS = {
    "file_exists": check_file_exists,
    "valid_json": check_valid_json,
    "min_size": check_min_size,
    "json_min_items": check_json_min_items,
    "markdown_sections": check_markdown_sections,
    "sqlite_rows": check_sqlite_rows,
    "port_alive": check_port_alive,
}


def run_manifest(manifest_path):
    with open(manifest_path) as f:
        checks = json.load(f)
    
    results = []
    all_passed = True
    for spec in checks:
        check_name = spec.pop("check")
        if check_name not in CHECKS:
            results.append((False, f"❌ Unknown check: {check_name}"))
            all_passed = False
            continue
        fn = CHECKS[check_name]
        passed, msg = fn(**spec)
        results.append((passed, msg))
        if not passed:
            all_passed = False
    
    return all_passed, results


def main():
    parser = argparse.ArgumentParser(description="Verify task output")
    parser.add_argument("--check", required=True, help="Check type or 'all' for manifest")
    parser.add_argument("--path", help="File/DB path")
    parser.add_argument("--manifest", help="Manifest JSON path (for --check all)")
    parser.add_argument("--min", help="Minimum value (size, items, rows)", default="1")
    parser.add_argument("--table", help="SQLite table name")
    parser.add_argument("--sections", help="Comma-separated required markdown sections")
    parser.add_argument("--port", help="Port number", default="0")
    args = parser.parse_args()
    
    if args.check == "all":
        if not args.manifest:
            print("❌ --manifest required for --check all")
            sys.exit(2)
        passed, results = run_manifest(args.manifest)
        for ok, msg in results:
            print(msg)
        print(f"\n{'✅ ALL CHECKS PASSED' if passed else '❌ SOME CHECKS FAILED'}")
        sys.exit(0 if passed else 1)
    
    if args.check not in CHECKS:
        print(f"❌ Unknown check: {args.check}")
        print(f"Available: {', '.join(CHECKS.keys())}")
        sys.exit(2)
    
    fn = CHECKS[args.check]
    passed, msg = fn(
        path=args.path or "",
        min_bytes=args.min,
        min_items=args.min,
        min_rows=args.min,
        table=args.table or "",
        sections=args.sections or "",
        port=args.port,
    )
    print(msg)
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
