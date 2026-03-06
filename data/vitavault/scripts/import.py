#!/usr/bin/env python3
"""Import VitaVault health exports (JSON or CSV) into ~/vitavault/data/."""

import argparse
import csv
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path.home() / "vitavault" / "data"
LATEST_LINK = DATA_DIR / "latest.json"


def ensure_dirs():
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def parse_csv(path: Path) -> list[dict]:
    """Convert CSV export to list of HealthRecord dicts."""
    records = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rec = dict(row)
            # Convert numeric fields
            if rec.get("value") and rec["value"] != "":
                try:
                    rec["value"] = float(rec["value"])
                except ValueError:
                    pass
            else:
                rec["value"] = None
            if rec.get("timezoneOffsetMinutes"):
                try:
                    rec["timezoneOffsetMinutes"] = int(rec["timezoneOffsetMinutes"])
                except ValueError:
                    rec["timezoneOffsetMinutes"] = 0
            rec["categoryValue"] = rec.get("categoryValue") or None
            rec["metadata"] = None
            records.append(rec)
    return records


def load_export(path: Path) -> dict:
    """Load a VitaVault export file (JSON or CSV) and return normalized payload."""
    suffix = path.suffix.lower()

    if suffix == ".json":
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        # Handle both wrapped (with metadata) and raw array formats
        if isinstance(data, list):
            return {
                "exportDate": datetime.now(timezone.utc).isoformat(),
                "schemaVersion": "2.0",
                "recordCount": len(data),
                "records": data,
            }
        return data

    elif suffix == ".csv":
        records = parse_csv(path)
        return {
            "exportDate": datetime.now(timezone.utc).isoformat(),
            "schemaVersion": "2.0",
            "recordCount": len(records),
            "records": records,
        }

    else:
        print(f"Error: unsupported file type '{suffix}'. Use .json or .csv", file=sys.stderr)
        sys.exit(1)


def merge_records(existing: list[dict], new: list[dict]) -> list[dict]:
    """Merge records, newer wins on ID collision."""
    by_id = {}
    for rec in existing:
        rid = rec.get("id")
        if rid:
            by_id[rid] = rec
    for rec in new:
        rid = rec.get("id")
        if rid:
            by_id[rid] = rec
        else:
            by_id[id(rec)] = rec
    merged = sorted(by_id.values(), key=lambda r: r.get("startDate", ""))
    return merged


def import_file(source: Path, tag: str | None = None):
    """Import a VitaVault export into ~/vitavault/data/."""
    ensure_dirs()
    data = load_export(source)
    records = data.get("records", [])

    if not records:
        print("Warning: no records found in export file.", file=sys.stderr)

    # Merge with existing latest if present
    if LATEST_LINK.exists():
        with open(LATEST_LINK, encoding="utf-8") as f:
            existing = json.load(f)
        existing_records = existing.get("records", [])
        merged = merge_records(existing_records, records)
        data["records"] = merged
        data["recordCount"] = len(merged)
        print(f"Merged: {len(existing_records)} existing + {len(records)} new = {len(merged)} total")
    else:
        print(f"First import: {len(records)} records")

    # Save timestamped file
    ts = datetime.now().strftime("%Y-%m-%dT%H-%M")
    if tag:
        ts = f"{ts}-{tag}"
    dest = DATA_DIR / f"{ts}.json"
    with open(dest, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    # Update latest symlink
    if LATEST_LINK.is_symlink() or LATEST_LINK.exists():
        LATEST_LINK.unlink()
    LATEST_LINK.symlink_to(dest.name)

    print(f"Imported {data['recordCount']} records to {dest}")
    print(f"Latest: {LATEST_LINK} -> {dest.name}")

    # Print type summary
    type_counts: dict[str, int] = {}
    for rec in data["records"]:
        t = rec.get("type", "unknown")
        type_counts[t] = type_counts.get(t, 0) + 1
    print(f"\nData types ({len(type_counts)}):")
    for t, count in sorted(type_counts.items(), key=lambda x: -x[1])[:15]:
        print(f"  {t}: {count:,}")
    if len(type_counts) > 15:
        print(f"  ... and {len(type_counts) - 15} more types")


def main():
    parser = argparse.ArgumentParser(description="Import VitaVault health export")
    parser.add_argument("file", help="Path to VitaVault export (.json or .csv)")
    parser.add_argument("--tag", help="Optional tag for this import (e.g. 'feb-2026')")
    args = parser.parse_args()

    source = Path(args.file).expanduser().resolve()
    if not source.exists():
        print(f"Error: file not found: {source}", file=sys.stderr)
        sys.exit(1)

    import_file(source, args.tag)


if __name__ == "__main__":
    main()
