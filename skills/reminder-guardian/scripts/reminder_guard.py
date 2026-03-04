#!/usr/bin/env python3
"""Reminder Guardian CLI: log, prepare, and audit reminder jobs."""
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime
from pathlib import Path
REPO_ROOT = Path(__file__).resolve().parents[3]
SKILL_ROOT = Path(__file__).resolve().parents[2]
LOG_PATH = REPO_ROOT / "memory" / "reminder-log.json"
TIME_HELPER = SKILL_ROOT / "scripts" / "time_helper.py"

STATUS_PENDING = "pending"
STATUS_SCHEDULED = "scheduled"
STATUS_SENT = "sent"


def call_time_helper(offset: str | None = None) -> str:
    cmd = ["python3", str(TIME_HELPER)]
    if offset:
        cmd.append(offset)
    result = subprocess.run(cmd, capture_output=True, text=True)
    output = result.stdout.strip()
    if not output:
        raise RuntimeError("Time helper did not return anything")
    if output.startswith("Error"):
        raise RuntimeError(output)
    return output


def ensure_log() -> list[dict]:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not LOG_PATH.exists():
        LOG_PATH.write_text("[]", encoding="utf-8")
    try:
        return json.loads(LOG_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Corrupted reminder log: {exc}")


def save_log(entries: list[dict]) -> None:
    LOG_PATH.write_text(json.dumps(entries, indent=2, ensure_ascii=False), encoding="utf-8")


def next_id(entries: list[dict]) -> int:
    if not entries:
        return 1
    return max(entry["id"] for entry in entries) + 1


def parse_iso(value: str) -> datetime:
    try:
        return datetime.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"Invalid ISO timestamp '{value}': {exc}")


def describe(entry: dict) -> str:
    return (
        f"[{entry['id']}] {entry['status']} → {entry['time']} → {entry['message']}"
        + (f" ({entry.get('label')})" if entry.get("label") else "")
    )


def format_blueprint(entry: dict) -> str:
    schedule = {"kind": "at", "at": entry["time"]}
    payload = {
        "kind": "systemEvent",
        "text": f"Reminder: {entry['message']}" + (f" — {entry.get('note')}" if entry.get('note') else ""),
    }
    return json.dumps({"schedule": schedule, "payload": payload, "label": entry.get("label", "Reminder")}, indent=2, ensure_ascii=False)


def add_command(args: argparse.Namespace) -> None:
    entries = ensure_log()
    if args.when and args.offset:
        raise RuntimeError("Please pass either --when or --offset, not both.")

    time_value = None
    if args.when:
        time_value = args.when
    elif args.offset:
        time_value = call_time_helper(args.offset)
    else:
        time_value = call_time_helper()

    parse_iso(time_value)
    now = call_time_helper()

    entry = {
        "id": next_id(entries),
        "label": args.label or "Reminder",
        "message": args.message,
        "time": time_value,
        "status": STATUS_PENDING,
        "note": args.note,
        "created_at": now,
        "updated_at": now,
    }
    entries.append(entry)
    save_log(entries)

    print("Reminder logged:")
    print(describe(entry))
    print("Cron blueprint to schedule this reminder:")
    print(format_blueprint(entry))
    print("→ Run `openclaw cron add` with the blueprint (set delivery channel) and then mark the reminder as scheduled." )


def list_command(args: argparse.Namespace) -> None:
    entries = ensure_log()
    filtered = [e for e in entries if e["status"] in args.status]
    if not filtered:
        print("No reminders matching the requested statuses.")
        return
    for entry in sorted(filtered, key=lambda e: e["time"]):
        print(describe(entry))


def mark_status(entry: dict, status: str, note: str | None) -> dict:
    entry["status"] = status
    entry["updated_at"] = call_time_helper()
    if note:
        entry["note"] = note
    return entry


def update_command(args: argparse.Namespace) -> None:
    entries = ensure_log()
    for entry in entries:
        if entry["id"] == args.id:
            updated = mark_status(entry, args.status, args.note)
            save_log(entries)
            print("Updated entry:")
            print(describe(updated))
            return
    raise RuntimeError(f"Reminder with id {args.id} not found.")


def blueprint_command(args: argparse.Namespace) -> None:
    entries = ensure_log()
    for entry in entries:
        if entry["id"] == args.id:
            print(format_blueprint(entry))
            if args.mark:
                entry["status"] = STATUS_SCHEDULED
                entry["updated_at"] = call_time_helper()
                save_log(entries)
                print("Marked as scheduled.")
            return
    raise RuntimeError(f"Reminder with id {args.id} not found.")


def next_command(args: argparse.Namespace) -> None:
    entries = ensure_log()
    pending = [e for e in entries if e["status"] == STATUS_PENDING]
    if not pending:
        print("No pending reminders.")
        return
    next_entry = min(pending, key=lambda e: e["time"])
    print(describe(next_entry))
    print("Blueprint:")
    print(format_blueprint(next_entry))


def main() -> None:
    parser = argparse.ArgumentParser("Reminder Guardian")
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add", help="Log a reminder and get the Cron blueprint.")
    add_parser.add_argument("--message", "-m", required=True, help="Friendly reminder text.")
    add_parser.add_argument("--when", "-w", help="Exact ISO timestamp for the reminder (yyyy-mm-ddThh:mm:ss).")
    add_parser.add_argument("--offset", "-o", help="Offset for the reminder (e.g., +15m, +2h, +1d).")
    add_parser.add_argument("--label", "-l", default="Reminder", help="Human label that appears in the log.")
    add_parser.add_argument("--note", "-n", help="Optional note or context for the reminder.")
    add_parser.set_defaults(func=add_command)

    list_parser = subparsers.add_parser("list", help="List reminders filtered by status.")
    list_parser.add_argument(
        "--status", "-s",
        action="append",
        choices=[STATUS_PENDING, STATUS_SCHEDULED, STATUS_SENT],
        default=[STATUS_PENDING, STATUS_SCHEDULED, STATUS_SENT],
        help="Filter by status (can list multiple times).",
    )
    list_parser.set_defaults(func=list_command)

    update_parser = subparsers.add_parser("update", help="Manually update a reminder's status.")
    update_parser.add_argument("id", type=int, help="ID of the reminder to update.")
    update_parser.add_argument(
        "--status", "-s", choices=[STATUS_PENDING, STATUS_SCHEDULED, STATUS_SENT], required=True
    )
    update_parser.add_argument("--note", "-n", help="Optional note to add when updating.")
    update_parser.set_defaults(func=update_command)

    blueprint_parser = subparsers.add_parser("blueprint", help="Show the Cron blueprint for a reminder.")
    blueprint_parser.add_argument("id", type=int, help="Reminder ID.")
    blueprint_parser.add_argument("--mark", "-m", action="store_true", help="Mark reminder as scheduled when blueprint is printed.")
    blueprint_parser.set_defaults(func=blueprint_command)

    next_parser = subparsers.add_parser("next", help="Show the next pending reminder.")
    next_parser.set_defaults(func=next_command)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
