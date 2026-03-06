#!/usr/bin/env python3
"""Event operations for CalDAV."""

import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

# Add scripts dir to path
sys.path.insert(0, str(Path(__file__).parent))

from utils import get_client, print_result, parse_datetime


def find_calendar(client, calendar_name: str):
    """Find calendar by name or ID."""
    principal = client.principal()
    for cal in principal.calendars():
        cal_id = str(cal.url).rstrip("/").split("/")[-1]
        if cal_id == calendar_name or cal.name == calendar_name:
            return cal
    return None


def format_event(event) -> dict:
    """Format event for display."""
    data = {
        "uid": event.icalendar_component.get("uid", "unknown"),
        "url": str(event.url) if event.url else None,
    }

    vevent = event.icalendar_component

    # Summary
    if vevent.get("summary"):
        data["summary"] = str(vevent["summary"])

    # Description
    if vevent.get("description"):
        data["description"] = str(vevent["description"])

    # Location
    if vevent.get("location"):
        data["location"] = str(vevent["location"])

    # Dates
    if vevent.get("dtstart"):
        dt = vevent["dtstart"].dt
        if hasattr(dt, "strftime"):
            data["start"] = dt.isoformat()
        else:
            # Date object (all-day)
            data["start"] = str(dt)
            data["all_day"] = True

    if vevent.get("dtend"):
        dt = vevent["dtend"].dt
        if hasattr(dt, "strftime"):
            data["end"] = dt.isoformat()
        else:
            data["end"] = str(dt)

    # Status
    if vevent.get("status"):
        data["status"] = str(vevent["status"])

    # Recurrence
    if vevent.get("rrule"):
        data["recurrence"] = str(vevent["rrule"])

    # Attendees
    if vevent.get("attendee"):
        attendees = vevent["attendee"]
        if not isinstance(attendees, list):
            attendees = [attendees]
        data["attendees"] = [str(a) for a in attendees]

    return data


def cmd_list(args):
    """List events."""
    client = get_client()
    principal = client.principal()

    # Determine date range
    if args.start:
        start = parse_datetime(args.start)
    else:
        start = datetime.now() - timedelta(days=7)

    if args.end:
        end = parse_datetime(args.end)
    else:
        end = datetime.now() + timedelta(days=30)

    all_events = []

    if args.calendar:
        calendars = [find_calendar(client, args.calendar)]
        calendars = [c for c in calendars if c]
    else:
        calendars = principal.calendars()

    for cal in calendars:
        if not cal:
            continue

        try:
            events = cal.date_search(start=start, end=end)
            for event in events:
                event_data = format_event(event)
                event_data["calendar"] = cal.name
                all_events.append(event_data)
        except Exception as e:
            # Some calendars might not support date_search
            pass

    # Sort by start date
    all_events.sort(key=lambda e: e.get("start", ""))

    # Limit results
    all_events = all_events[: args.limit]

    print_result(
        True,
        f"Found {len(all_events)} event(s)",
        {"events": all_events, "range": {"start": str(start), "end": str(end)}},
    )


def cmd_create(args):
    """Create a new event."""
    client = get_client()

    calendar = find_calendar(client, args.calendar)
    if not calendar:
        print_result(False, f"Calendar '{args.calendar}' not found")
        return

    # Parse dates
    start = parse_datetime(args.start)

    if args.allday:
        # All-day event
        start_date = start.date() if hasattr(start, "date") else start
        end_date = None
        if args.end:
            end_dt = parse_datetime(args.end)
            end_date = end_dt.date() if hasattr(end_dt, "date") else end_dt
    else:
        # Timed event
        if args.end:
            end = parse_datetime(args.end)
        else:
            # Default 1 hour duration
            end = start + timedelta(hours=1)

    try:
        # Build event
        if args.allday:
            event = calendar.save_event(
                dtstart=start_date,
                dtend=end_date,
                summary=args.summary,
                description=args.description,
                location=args.location,
            )
        else:
            extra_kwargs = {}
            if args.rrule:
                extra_kwargs["rrule"] = args.rrule
            if args.uid:
                extra_kwargs["uid"] = args.uid

            event = calendar.save_event(
                dtstart=start,
                dtend=end,
                summary=args.summary,
                description=args.description,
                location=args.location,
                **extra_kwargs,
            )

        event_data = format_event(event)
        print_result(True, "Event created", event_data)

    except Exception as e:
        print_result(False, f"Failed to create event: {e}")


def cmd_update(args):
    """Update an existing event."""
    client = get_client()

    event = None
    calendar = None

    # Find event
    if args.calendar:
        calendar = find_calendar(client, args.calendar)
        if calendar:
            try:
                event = calendar.event_by_uid(args.uid)
            except Exception:
                pass

    if not event:
        # Search all calendars
        principal = client.principal()
        for cal in principal.calendars():
            try:
                event = cal.event_by_uid(args.uid)
                calendar = cal
                break
            except Exception:
                pass

    if not event:
        print_result(False, f"Event '{args.uid}' not found")
        return

    try:
        # Get existing component
        vevent = event.icalendar_component

        # Update properties
        if args.summary:
            vevent["summary"] = args.summary
        if args.description is not None:
            if args.description:
                vevent["description"] = args.description
            elif "description" in vevent:
                del vevent["description"]
        if args.location is not None:
            if args.location:
                vevent["location"] = args.location
            elif "location" in vevent:
                del vevent["location"]
        if args.status:
            vevent["status"] = args.status
        if args.start:
            start = parse_datetime(args.start)
            vevent["dtstart"] = vevent.pop("dtstart")
            vevent["dtstart"].dt = start
        if args.end:
            end = parse_datetime(args.end)
            vevent["dtend"] = vevent.pop("dtend")
            vevent["dtend"].dt = end

        # Save changes
        event.save()

        event_data = format_event(event)
        print_result(True, "Event updated", event_data)

    except Exception as e:
        print_result(False, f"Failed to update event: {e}")


def cmd_delete(args):
    """Delete an event."""
    client = get_client()

    event = None

    # Find event
    if args.calendar:
        calendar = find_calendar(client, args.calendar)
        if calendar:
            try:
                event = calendar.event_by_uid(args.uid)
            except Exception:
                pass

    if not event:
        principal = client.principal()
        for cal in principal.calendars():
            try:
                event = cal.event_by_uid(args.uid)
                break
            except Exception:
                pass

    if not event:
        print_result(False, f"Event '{args.uid}' not found")
        return

    if not args.force:
        try:
            confirm = input(f"Delete event '{args.uid}'? [y/N] ")
            if confirm.lower() != "y":
                print_result(False, "Cancelled")
                return
        except EOFError:
            print_result(False, "Use --force to skip confirmation")
            return

    try:
        event.delete()
        print_result(True, f"Event '{args.uid}' deleted")
    except Exception as e:
        print_result(False, f"Failed to delete event: {e}")


def cmd_search(args):
    """Search events by text."""
    client = get_client()
    principal = client.principal()

    results = []
    query_lower = args.query.lower()

    calendars = principal.calendars()
    if args.calendar:
        cal = find_calendar(client, args.calendar)
        if cal:
            calendars = [cal]
        else:
            calendars = []

    for cal in calendars:
        try:
            events = cal.events()
            for event in events:
                vevent = event.icalendar_component

                # Search in summary, description, location
                searchable = []
                if vevent.get("summary"):
                    searchable.append(str(vevent["summary"]))
                if vevent.get("description"):
                    searchable.append(str(vevent["description"]))
                if vevent.get("location"):
                    searchable.append(str(vevent["location"]))

                text = " ".join(searchable).lower()
                if query_lower in text:
                    event_data = format_event(event)
                    event_data["calendar"] = cal.name
                    results.append(event_data)

        except Exception:
            pass

    print_result(True, f"Found {len(results)} matching event(s)", {"events": results})


def cmd_get(args):
    """Get event by UID."""
    client = get_client()

    event = None
    calendar = None

    if args.calendar:
        calendar = find_calendar(client, args.calendar)
        if calendar:
            try:
                event = calendar.event_by_uid(args.uid)
            except Exception:
                pass

    if not event:
        principal = client.principal()
        for cal in principal.calendars():
            try:
                event = cal.event_by_uid(args.uid)
                calendar = cal
                break
            except Exception:
                pass

    if not event:
        print_result(False, f"Event '{args.uid}' not found")
        return

    event_data = format_event(event)
    event_data["calendar"] = calendar.name if calendar else None
    event_data["raw"] = event.data

    print_result(True, "Event found", event_data)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Event operations")
    subparsers = parser.add_subparsers(dest="command", required=True)

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
    create.add_argument("--description", "-d", help="Description")
    create.add_argument("--location", "-l", help="Location")
    create.add_argument("--rrule", help="Recurrence rule")
    create.add_argument("--uid", help="Custom UID")

    # Update
    update = subparsers.add_parser("update", help="Update an event")
    update.add_argument("--uid", required=True, help="Event UID")
    update.add_argument("--calendar", "-c", help="Calendar")
    update.add_argument("--summary", "-s", help="New title")
    update.add_argument("--start", help="New start")
    update.add_argument("--end", help="New end")
    update.add_argument("--description", "-d", help="New description")
    update.add_argument("--location", "-l", help="New location")
    update.add_argument("--status", choices=["CONFIRMED", "TENTATIVE", "CANCELLED"])

    # Delete
    delete = subparsers.add_parser("delete", help="Delete an event")
    delete.add_argument("--uid", required=True, help="Event UID")
    delete.add_argument("--calendar", "-c", help="Calendar")
    delete.add_argument("--force", action="store_true", help="Skip confirmation")

    # Search
    search = subparsers.add_parser("search", help="Search events")
    search.add_argument("--query", "-q", required=True, help="Search query")
    search.add_argument("--calendar", "-c", help="Filter by calendar")

    # Get
    get = subparsers.add_parser("get", help="Get event by UID")
    get.add_argument("--uid", required=True, help="Event UID")
    get.add_argument("--calendar", "-c", help="Calendar")

    args = parser.parse_args()
    globals()[f"cmd_{args.command}"](args)


if __name__ == "__main__":
    main()
