#!/usr/bin/env python3
"""Calendar operations for CalDAV."""

import sys
from pathlib import Path

# Add scripts dir to path
sys.path.insert(0, str(Path(__file__).parent))

from utils import (
    get_client,
    print_result,
    load_config,
    CalendarCommand,
)


def cmd_list(args):
    """List all calendars."""
    client = get_client()
    principal = client.principal()

    calendars = principal.calendars()

    if not calendars:
        print_result(True, "No calendars found")
        return

    data = []
    for cal in calendars:
        info = {
            "name": cal.name or "Unnamed",
            "url": str(cal.url),
            "id": str(cal.url).rstrip("/").split("/")[-1] if cal.url else None,
        }

        # Try to get additional properties
        try:
            props = cal.get_properties([("{DAV:}", "displayname"), ("{DAV:}", "resourcetype")])
            info["displayname"] = props.get("{DAV:}displayname", "")
        except Exception:
            pass

        data.append(info)

    print_result(True, f"Found {len(calendars)} calendar(s)", {"calendars": data})


def cmd_create(args):
    """Create a new calendar."""
    client = get_client()
    principal = client.principal()

    cal_id = args.id or args.name.lower().replace(" ", "-").replace("/", "-")

    try:
        cal = principal.make_calendar(
            name=args.name,
            cal_id=cal_id,
        )

        # Set additional properties if provided
        if args.description or args.color:
            props = {}
            if args.description:
                # Would need additional DAV property setting
                pass
            if args.color:
                # Calendar color is often a custom property
                pass

        print_result(
            True,
            f"Calendar '{args.name}' created",
            {"id": cal_id, "url": str(cal.url)},
        )
    except Exception as e:
        if "already exists" in str(e).lower():
            print_result(False, f"Calendar '{cal_id}' already exists")
        else:
            print_result(False, f"Failed to create calendar: {e}")


def cmd_delete(args):
    """Delete a calendar."""
    client = get_client()
    principal = client.principal()

    # Find calendar by name or ID
    calendar = None
    for cal in principal.calendars():
        cal_id = str(cal.url).rstrip("/").split("/")[-1]
        if cal_id == args.id or cal.name == args.id:
            calendar = cal
            break

    if not calendar:
        print_result(False, f"Calendar '{args.id}' not found")
        return

    if not args.force:
        # Ask for confirmation
        try:
            confirm = input(f"Delete calendar '{calendar.name}'? [y/N] ")
            if confirm.lower() != "y":
                print_result(False, "Cancelled")
                return
        except EOFError:
            # Non-interactive mode
            print_result(False, "Use --force to skip confirmation")
            return

    try:
        calendar.delete()
        print_result(True, f"Calendar '{args.id}' deleted")
    except Exception as e:
        print_result(False, f"Failed to delete calendar: {e}")


def cmd_info(args):
    """Get calendar info."""
    client = get_client()
    principal = client.principal()

    # Find calendar
    calendar = None
    for cal in principal.calendars():
        cal_id = str(cal.url).rstrip("/").split("/")[-1]
        if cal_id == args.id or cal.name == args.id:
            calendar = cal
            break

    if not calendar:
        print_result(False, f"Calendar '{args.id}' not found")
        return

    info = {
        "name": calendar.name,
        "url": str(calendar.url),
        "id": str(calendar.url).rstrip("/").split("/")[-1],
    }

    # Get properties
    try:
        from caldav.lib.namespace import ns

        props = calendar.get_properties(
            [
                (ns("d"), "displayname"),
                (ns("caldav"), "calendar-description"),
                (ns("caldav"), "calendar-timezone"),
                (ns("caldav"), "supported-calendar-component-set"),
            ]
        )

        info["displayname"] = props.get(ns("d", "displayname"), "")
        info["description"] = props.get(ns("caldav", "calendar-description"), "")
        info["timezone"] = props.get(ns("caldav", "calendar-timezone"), "")

        components = props.get(ns("caldav", "supported-calendar-component-set"), "")
        info["components"] = components if components else "VEVENT, VTODO"
    except Exception:
        pass

    # Count events
    try:
        events = calendar.events()
        todos = calendar.todos()
        info["event_count"] = len(events)
        info["todo_count"] = len(todos)
    except Exception:
        pass

    print_result(True, f"Calendar info for '{args.id}'", info)


def cmd_export(args):
    """Export calendar to ICS."""
    client = get_client()
    principal = client.principal()

    # Find calendar
    calendar = None
    for cal in principal.calendars():
        cal_id = str(cal.url).rstrip("/").split("/")[-1]
        if cal_id == args.id or cal.name == args.id:
            calendar = cal
            break

    if not calendar:
        print_result(False, f"Calendar '{args.id}' not found")
        return

    try:
        # Get all events as ICS
        events = calendar.events()
        ics_content = "BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//OpenClaw CalDAV Export//EN\n"

        for event in events:
            # Get raw ICS data
            data = event.data
            # Extract VEVENT from the full VCALENDAR
            if "BEGIN:VEVENT" in data:
                start = data.find("BEGIN:VEVENT")
                end = data.find("END:VEVENT") + len("END:VEVENT")
                ics_content += data[start:end] + "\n"

        ics_content += "END:VCALENDAR\n"

        if args.output:
            output_path = Path(args.output)
            output_path.write_text(ics_content)
            print_result(True, f"Exported to {args.output}", {"events": len(events)})
        else:
            print(ics_content)

    except Exception as e:
        print_result(False, f"Failed to export: {e}")


def cmd_import(args):
    """Import ICS file to calendar."""
    client = get_client()
    principal = client.principal()

    # Find target calendar
    calendar = None
    for cal in principal.calendars():
        cal_id = str(cal.url).rstrip("/").split("/")[-1]
        if cal_id == args.calendar or cal.name == args.calendar:
            calendar = cal
            break

    if not calendar:
        print_result(False, f"Calendar '{args.calendar}' not found")
        return

    # Read ICS file
    ics_path = Path(args.file)
    if not ics_path.exists():
        print_result(False, f"File not found: {args.file}")
        return

    ics_content = ics_path.read_text()

    try:
        # Parse and import events
        from icalendar import Calendar

        cal = Calendar.from_ical(ics_content)

        imported = 0
        for component in cal.walk():
            if component.name == "VEVENT":
                # Create event from component
                ics_data = f"BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//OpenClaw Import//EN\nBEGIN:VEVENT\n"
                # Add properties
                for line in component.to_ical().decode().split("\n"):
                    if line and not line.startswith("BEGIN:VCALENDAR") and not line.startswith("END:VCALENDAR"):
                        ics_data += line + "\n"
                ics_data += "END:VEVENT\nEND:VCALENDAR"

                calendar.save_event(ics_data)
                imported += 1

        print_result(True, f"Imported {imported} event(s)", {"imported": imported})

    except ImportError:
        print_result(False, "icalendar library required for import. pip install icalendar")
    except Exception as e:
        print_result(False, f"Failed to import: {e}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Calendar operations")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # List
    subparsers.add_parser("list", help="List all calendars")

    # Create
    create = subparsers.add_parser("create", help="Create a new calendar")
    create.add_argument("--name", required=True, help="Calendar display name")
    create.add_argument("--id", help="Calendar ID (URL-safe)")
    create.add_argument("--description", help="Calendar description")
    create.add_argument("--color", help="Calendar color (hex)")

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
    imp.add_argument("--calendar", "-c", required=True, help="Target calendar")
    imp.add_argument("--file", "-f", required=True, help="ICS file to import")

    args = parser.parse_args()

    # Dispatch
    globals()[f"cmd_{args.command}"](args)


if __name__ == "__main__":
    main()
