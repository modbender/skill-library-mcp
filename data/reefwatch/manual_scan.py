#!/usr/bin/env python3
"""
ReefWatch Manual Scanner 🪸
On-demand YARA scan of a specific file or directory.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="ReefWatch Manual Scanner")
    parser.add_argument("--target", required=True, help="File or directory to scan")
    parser.add_argument("--max-size-mb", type=int, default=50, help="Max file size in MB")
    parser.add_argument("--timeout", type=int, default=30, help="Per-file timeout in seconds")
    parser.add_argument("--json", action="store_true", help="Output results as JSON to stdout")
    args = parser.parse_args()

    target = Path(args.target).expanduser()
    if not target.exists():
        print(f"❌ Target not found: {target}")
        sys.exit(1)

    try:
        import yara
    except ImportError:
        print("❌ yara-python not installed. Run: pip3 install yara-python")
        sys.exit(1)

    # Load rules
    rules_dir = Path(__file__).parent / "rules" / "yara"
    if not rules_dir.exists():
        print("❌ No YARA rules found. Run setup_rules.py first.")
        sys.exit(1)

    rule_files = list(rules_dir.rglob("*.yar")) + list(rules_dir.rglob("*.yara"))
    if not rule_files:
        print("❌ No .yar files found in rules directory.")
        sys.exit(1)

    print(f"🪸 ReefWatch Manual Scan")
    print(f"   Target: {target}")
    print(f"   Rules:  {len(rule_files)} YARA files")
    print("─" * 40)

    # Compile rules
    filepaths = {f"rule_{i}": str(r) for i, r in enumerate(rule_files)}
    try:
        rules = yara.compile(filepaths=filepaths)
    except Exception as e:
        print(f"❌ Failed to compile rules: {e}")
        sys.exit(1)

    # Collect files to scan
    max_size = args.max_size_mb * 1024 * 1024
    if target.is_file() and not target.is_symlink():
        files = [target]
    elif target.is_file():
        files = []  # Skip symlink targets
    else:
        files = [f for f in target.rglob("*") if f.is_file() and not f.is_symlink()]

    scanned = 0
    findings = []

    for f in files:
        try:
            if f.stat().st_size > max_size:
                continue
            matches = rules.match(str(f), timeout=args.timeout)
            scanned += 1

            if matches:
                for m in matches:
                    finding = {
                        "file": str(f),
                        "rule": m.rule,
                        "tags": list(m.tags),
                        "meta": dict(m.meta) if m.meta else {},
                        "time": datetime.now(timezone.utc).isoformat(),
                    }
                    findings.append(finding)
                    if not args.json:
                        severity = finding["meta"].get("severity", "HIGH")
                        print(f"  🔴 MATCH: {m.rule}")
                        print(f"     File: {f}")
                        print(f"     Tags: {', '.join(m.tags) if m.tags else 'none'}")
                        print(f"     Severity: {severity}")
                        print()

            if not args.json and scanned % 100 == 0:
                print(f"  ... scanned {scanned} files", end="\r")

        except Exception as e:
            print(f"  ⚠ Cannot scan {f}: {e}", file=sys.stderr)

    if args.json:
        result = {
            "target": str(target),
            "files_scanned": scanned,
            "findings": findings,
            "time": datetime.now(timezone.utc).isoformat(),
        }
        print(json.dumps(result, indent=2))
        sys.exit(1 if findings else 0)

    print("─" * 40)
    print(f"Scan complete")
    print(f"   Files scanned: {scanned}")
    print(f"   Findings:      {len(findings)}")

    if findings:
        print(f"\n{len(findings)} threats detected!")
        report_path = Path(__file__).parent / "manual_scan_report.json"
        report_flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
        if hasattr(os, "O_NOFOLLOW"):
            report_flags |= os.O_NOFOLLOW
        fd = os.open(str(report_path), report_flags, 0o600)
        with os.fdopen(fd, "w") as fh:
            json.dump(findings, fh, indent=2)
        print(f"   Report saved to: {report_path}")
        sys.exit(1)
    else:
        print(f"\nNo threats detected.")


if __name__ == "__main__":
    main()
