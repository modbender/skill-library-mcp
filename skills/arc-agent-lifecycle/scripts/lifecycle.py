#!/usr/bin/env python3
"""Agent Lifecycle Manager — Version, snapshot, diff, and retire agent configurations."""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

LIFECYCLE_DIR = Path.home() / ".openclaw" / "lifecycle"
LIFECYCLE_DIR.mkdir(parents=True, exist_ok=True)

SNAPSHOTS_DIR = LIFECYCLE_DIR / "snapshots"
SNAPSHOTS_DIR.mkdir(exist_ok=True)

HISTORY_FILE = LIFECYCLE_DIR / "history.json"
RETIREMENTS_FILE = LIFECYCLE_DIR / "retirements.json"


def _load_json(path, default=None):
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return default if default is not None else []


def _save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)


def _log_event(event_type, details):
    """Append an event to the history log."""
    history = _load_json(HISTORY_FILE, [])
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "type": event_type,
        **details,
    }
    history.append(event)
    # Keep last 500 events
    if len(history) > 500:
        history = history[-500:]
    _save_json(HISTORY_FILE, history)
    return event


def _scan_skills():
    """Scan installed skills and return their metadata."""
    skills = {}
    skill_dirs = [
        Path.home() / ".openclaw" / "skills",
        Path.home() / ".openclaw" / "workspace" / "skills",
    ]

    for base_dir in skill_dirs:
        if not base_dir.exists():
            continue
        for skill_path in sorted(base_dir.iterdir()):
            if not skill_path.is_dir():
                continue
            name = skill_path.name
            skill_md = skill_path / "SKILL.md"
            meta = {"name": name, "path": str(skill_path)}

            if skill_md.exists():
                with open(skill_md) as f:
                    content = f.read()
                # Extract version from frontmatter if present
                for line in content.split('\n')[:20]:
                    if line.strip().startswith('version:'):
                        meta["version"] = line.split(':', 1)[1].strip()
                    if line.strip().startswith('description:'):
                        meta["description"] = line.split(':', 1)[1].strip()[:100]

                meta["size_bytes"] = sum(
                    f.stat().st_size for f in skill_path.rglob("*") if f.is_file()
                    and '__pycache__' not in str(f)
                )
                meta["file_count"] = sum(
                    1 for f in skill_path.rglob("*") if f.is_file()
                    and '__pycache__' not in str(f)
                )
                meta["last_modified"] = datetime.fromtimestamp(
                    skill_md.stat().st_mtime, tz=timezone.utc
                ).isoformat()

            skills[name] = meta

    return skills


def snapshot(name):
    """Take a snapshot of current agent state."""
    skills = _scan_skills()

    snap = {
        "name": name,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "skill_count": len(skills),
        "skills": skills,
    }

    snap_path = SNAPSHOTS_DIR / f"{name}.json"
    _save_json(snap_path, snap)
    _log_event("snapshot", {"name": name, "skill_count": len(skills)})

    print(f"Snapshot '{name}' saved — {len(skills)} skills captured")
    return snap


def list_snapshots():
    """List all saved snapshots."""
    snaps = []
    for f in sorted(SNAPSHOTS_DIR.glob("*.json")):
        data = _load_json(f, {})
        snaps.append({
            "name": data.get("name", f.stem),
            "created_at": data.get("created_at", "unknown"),
            "skill_count": data.get("skill_count", 0),
        })
    return snaps


def diff_snapshots(from_name, to_name):
    """Compare two snapshots and show differences."""
    from_path = SNAPSHOTS_DIR / f"{from_name}.json"
    to_path = SNAPSHOTS_DIR / f"{to_name}.json"

    if not from_path.exists():
        print(f"Snapshot '{from_name}' not found")
        return None
    if not to_path.exists():
        print(f"Snapshot '{to_name}' not found")
        return None

    from_snap = _load_json(from_path, {})
    to_snap = _load_json(to_path, {})

    from_skills = set(from_snap.get("skills", {}).keys())
    to_skills = set(to_snap.get("skills", {}).keys())

    added = to_skills - from_skills
    removed = from_skills - to_skills
    common = from_skills & to_skills

    changed = []
    for name in common:
        f = from_snap["skills"][name]
        t = to_snap["skills"][name]
        if f.get("size_bytes") != t.get("size_bytes") or f.get("file_count") != t.get("file_count"):
            changed.append(name)

    result = {
        "from": from_name,
        "to": to_name,
        "added": sorted(added),
        "removed": sorted(removed),
        "changed": sorted(changed),
        "unchanged": len(common) - len(changed),
    }

    return result


def retire_skill(skill_name, reason=""):
    """Record a skill retirement."""
    retirements = _load_json(RETIREMENTS_FILE, [])
    entry = {
        "skill": skill_name,
        "retired_at": datetime.now(timezone.utc).isoformat(),
        "reason": reason,
    }
    retirements.append(entry)
    _save_json(RETIREMENTS_FILE, retirements)
    _log_event("retirement", {"skill": skill_name, "reason": reason})
    print(f"Recorded retirement of '{skill_name}': {reason}")
    return entry


def show_history(limit=20):
    """Show recent change history."""
    history = _load_json(HISTORY_FILE, [])
    return history[-limit:]


def main():
    parser = argparse.ArgumentParser(description="Agent Lifecycle Manager")
    sub = parser.add_subparsers(dest="command")

    p_snap = sub.add_parser("snapshot", help="Take a snapshot")
    p_snap.add_argument("--name", required=True, help="Snapshot name")

    p_list = sub.add_parser("list", help="List snapshots")

    p_diff = sub.add_parser("diff", help="Compare snapshots")
    p_diff.add_argument("--from", dest="from_name", required=True)
    p_diff.add_argument("--to", required=True)

    p_retire = sub.add_parser("retire", help="Record skill retirement")
    p_retire.add_argument("--skill", required=True)
    p_retire.add_argument("--reason", default="", help="Reason for retirement")

    p_hist = sub.add_parser("history", help="View change history")
    p_hist.add_argument("--limit", type=int, default=20)
    p_hist.add_argument("--json", action="store_true")

    p_roll = sub.add_parser("rollback", help="Rollback to snapshot")
    p_roll.add_argument("--to", required=True)
    p_roll.add_argument("--dry-run", action="store_true")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "snapshot":
        snapshot(args.name)

    elif args.command == "list":
        snaps = list_snapshots()
        if snaps:
            print(f"{'Name':<30} {'Created':<28} {'Skills':<8}")
            print("-" * 66)
            for s in snaps:
                print(f"{s['name']:<30} {s['created_at']:<28} {s['skill_count']}")
        else:
            print("No snapshots found. Use 'snapshot --name <name>' to create one.")

    elif args.command == "diff":
        result = diff_snapshots(args.from_name, args.to)
        if result:
            print(f"\nDiff: {result['from']} -> {result['to']}")
            if result["added"]:
                print(f"\n  Added ({len(result['added'])}):")
                for s in result["added"]:
                    print(f"    + {s}")
            if result["removed"]:
                print(f"\n  Removed ({len(result['removed'])}):")
                for s in result["removed"]:
                    print(f"    - {s}")
            if result["changed"]:
                print(f"\n  Changed ({len(result['changed'])}):")
                for s in result["changed"]:
                    print(f"    ~ {s}")
            print(f"\n  Unchanged: {result['unchanged']}")

    elif args.command == "retire":
        retire_skill(args.skill, args.reason)

    elif args.command == "history":
        events = show_history(args.limit)
        if args.json:
            print(json.dumps(events, indent=2))
        else:
            if events:
                for e in events:
                    ts = e.get("timestamp", "?")[:19]
                    etype = e.get("type", "?")
                    detail = {k: v for k, v in e.items() if k not in ("timestamp", "type")}
                    print(f"  [{ts}] {etype}: {json.dumps(detail)}")
            else:
                print("No history yet.")

    elif args.command == "rollback":
        snap_path = SNAPSHOTS_DIR / f"{args.to}.json"
        if not snap_path.exists():
            print(f"Snapshot '{args.to}' not found")
            sys.exit(1)
        snap = _load_json(snap_path, {})
        current = _scan_skills()
        snap_skills = set(snap.get("skills", {}).keys())
        current_skills = set(current.keys())
        to_install = snap_skills - current_skills
        to_remove = current_skills - snap_skills
        if args.dry_run:
            print(f"DRY RUN — Rollback to '{args.to}':")
            if to_install:
                print(f"  Would need to install: {', '.join(sorted(to_install))}")
            if to_remove:
                print(f"  Would need to remove: {', '.join(sorted(to_remove))}")
            if not to_install and not to_remove:
                print("  No changes needed — current state matches snapshot")
        else:
            print("Full rollback not implemented — use dry-run to see what changed, then manually adjust.")


if __name__ == "__main__":
    main()
