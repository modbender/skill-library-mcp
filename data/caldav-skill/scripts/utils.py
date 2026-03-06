#!/usr/bin/env python3
"""Shared utilities for CalDAV operations."""

import os
import json
import argparse
from pathlib import Path
from typing import Optional, Dict, Any

# Config file locations
CONFIG_PATHS = [
    Path.home() / ".config" / "caldav" / "config.json",
    Path("/etc/caldav/config.json"),
]


def load_config() -> Dict[str, Any]:
    """Load configuration from file or environment."""
    config = {}

    # Try config files
    for config_path in CONFIG_PATHS:
        if config_path.exists():
            with open(config_path) as f:
                config.update(json.load(f))
            break

    # Environment overrides
    if os.environ.get("CALDAV_URL"):
        config["url"] = os.environ["CALDAV_URL"]
    if os.environ.get("CALDAV_USER"):
        config["username"] = os.environ["CALDAV_USER"]
    if os.environ.get("CALDAV_PASSWORD"):
        config["password"] = os.environ["CALDAV_PASSWORD"]

    return config


def get_client():
    """Get authenticated CalDAV client."""
    try:
        from caldav import DAVClient
    except ImportError:
        print("Error: caldav library not installed.")
        print("Install with: pip install caldav")
        raise SystemExit(1)

    config = load_config()

    if not config.get("url"):
        print("Error: No CalDAV URL configured.")
        print("Set CALDAV_URL environment variable or create config.json")
        raise SystemExit(1)

    return DAVClient(
        url=config.get("url"),
        username=config.get("username"),
        password=config.get("password"),
    )


def format_datetime(dt_str: str) -> str:
    """Format datetime string for display."""
    # Handle various formats
    if "T" in dt_str:
        if dt_str.endswith("Z"):
            return dt_str.replace("Z", " UTC")
        return dt_str
    return dt_str


def parse_datetime(dt_str: str):
    """Parse datetime string to datetime object."""
    from datetime import datetime

    # Try various formats
    formats = [
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(dt_str, fmt)
        except ValueError:
            continue

    raise ValueError(f"Unable to parse datetime: {dt_str}")


def print_result(success: bool, message: str, data: Optional[Dict] = None):
    """Print result in consistent format."""
    import json

    result = {"success": success, "message": message}
    if data:
        result["data"] = data

    print(json.dumps(result, indent=2, default=str))


class CalendarCommand:
    """Base class for calendar commands."""

    def __init__(self):
        self.parser = argparse.ArgumentParser(description="Calendar operations")
        subparsers = self.parser.add_subparsers(dest="command", required=True)

        # List
        subparsers.add_parser("list", help="List all calendars")

        # Create
        create = subparsers.add_parser("create", help="Create a new calendar")
        create.add_argument("--name", required=True, help="Calendar display name")
        create.add_argument("--id", help="Calendar ID (URL-safe)")
        create.add_argument("--description", help="Calendar description")
        create.add_argument(
            "--color", help="Calendar color (hex, e.g., #FF0000)"
        )

        # Delete
        delete = subparsers.add_parser("delete", help="Delete a calendar")
        delete.add_argument("--id", required=True, help="Calendar ID or name")
        delete.add_argument("--force", action="store_true", help="Skip confirmation")

        # Info
        info = subparsers.add_parser("info", help="Get calendar info")
        info.add_argument("--id", required=True, help="Calendar ID or name")

        # Export
        export = subparsers.add_parser("export", help="Export calendar to ICS")
        export.add_argument("--id", required=True, help="Calendar ID or name")
        export.add_argument("--output", "-o", help="Output file path")

        # Import
        imp = subparsers.add_parser("import", help="Import ICS file")
        imp.add_argument("--calendar", required=True, help="Target calendar ID or name")
        imp.add_argument("--file", "-f", required=True, help="ICS file to import")

    def run(self):
        args = self.parser.parse_args()
        getattr(self, f"cmd_{args.command}")(args)


class EventCommand:
    """Base class for event commands."""

    def __init__(self):
        self.parser = argparse.ArgumentParser(description="Event operations")
        subparsers = self.parser.add_subparsers(dest="command", required=True)

        # List
        list_cmd = subparsers.add_parser("list", help="List events")
        list_cmd.add_argument("--calendar", "-c", help="Filter by calendar")
        list_cmd.add_argument("--start", help="Start date (YYYY-MM-DD)")
        list_cmd.add_argument("--end", help="End date (YYYY-MM-DD)")
        list_cmd.add_argument("--limit", type=int, default=50, help="Max results")

        # Create
        create = subparsers.add_parser("create", help="Create an event")
        create.add_argument("--calendar", "-c", required=True, help="Target calendar")
        create.add_argument("--summary", "-s", required=True, help="Event title")
        create.add_argument("--start", required=True, help="Start datetime")
        create.add_argument("--end", help="End datetime")
        create.add_argument("--allday", action="store_true", help="All-day event")
        create.add_argument("--description", "-d", help="Event description")
        create.add_argument("--location", "-l", help="Event location")
        create.add_argument("--rrule", help="Recurrence rule (e.g., FREQ=WEEKLY)")
        create.add_argument("--uid", help="Custom UID")
        create.add_argument("--timezone", help="Timezone (e.g., America/New_York)")

        # Update
        update = subparsers.add_parser("update", help="Update an event")
        update.add_argument("--uid", required=True, help="Event UID")
        update.add_argument("--calendar", "-c", help="Calendar (if known)")
        update.add_argument("--summary", "-s", help="New title")
        update.add_argument("--start", help="New start datetime")
        update.add_argument("--end", help="New end datetime")
        update.add_argument("--description", "-d", help="New description")
        update.add_argument("--location", "-l", help="New location")
        update.add_argument("--status", choices=["CONFIRMED", "TENTATIVE", "CANCELLED"])

        # Delete
        delete = subparsers.add_parser("delete", help="Delete an event")
        delete.add_argument("--uid", required=True, help="Event UID")
        delete.add_argument("--calendar", "-c", help="Calendar (if known)")
        delete.add_argument("--force", action="store_true", help="Skip confirmation")

        # Search
        search = subparsers.add_parser("search", help="Search events")
        search.add_argument("--query", "-q", required=True, help="Search query")
        search.add_argument("--calendar", "-c", help="Filter by calendar")

        # Get
        get = subparsers.add_parser("get", help="Get event by UID")
        get.add_argument("--uid", required=True, help="Event UID")
        get.add_argument("--calendar", "-c", help="Calendar (if known)")

    def run(self):
        args = self.parser.parse_args()
        getattr(self, f"cmd_{args.command}")(args)


class TodoCommand:
    """Base class for todo commands."""

    def __init__(self):
        self.parser = argparse.ArgumentParser(description="Todo operations")
        subparsers = self.parser.add_subparsers(dest="command", required=True)

        # List
        list_cmd = subparsers.add_parser("list", help="List todos")
        list_cmd.add_argument("--calendar", "-c", help="Filter by calendar")
        list_cmd.add_argument("--completed", action="store_true", help="Show completed")
        list_cmd.add_argument("--overdue", action="store_true", help="Show overdue only")

        # Create
        create = subparsers.add_parser("create", help="Create a todo")
        create.add_argument("--calendar", "-c", required=True, help="Target calendar")
        create.add_argument("--summary", "-s", required=True, help="Todo title")
        create.add_argument("--due", help="Due date")
        create.add_argument("--description", "-d", help="Description")
        create.add_argument("--priority", type=int, help="Priority (1-9)")
        create.add_argument("--categories", help="Comma-separated categories")

        # Complete
        complete = subparsers.add_parser("complete", help="Mark todo complete")
        complete.add_argument("--uid", required=True, help="Todo UID")
        complete.add_argument("--calendar", "-c", help="Calendar")

        # Delete
        delete = subparsers.add_parser("delete", help="Delete a todo")
        delete.add_argument("--uid", required=True, help="Todo UID")
        delete.add_argument("--calendar", "-c", help="Calendar")
        delete.add_argument("--force", action="store_true", help="Skip confirmation")

    def run(self):
        args = self.parser.parse_args()
        getattr(self, f"cmd_{args.command}")(args)
