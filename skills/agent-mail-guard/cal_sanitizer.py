#!/usr/bin/env python3
"""
Calendar Event Sanitization Middleware for OpenClaw AI Agent.

Applies the same security pipeline as the email sanitizer to Google Calendar
event fields — title, description, location, attendees, organizer, and any
extended properties.

Usage:
    # CLI — pipe JSON event(s) via stdin
    echo '{"summary":"Meeting","description":"Notes..."}' | python3 cal_sanitizer.py

    # As module
    from cal_sanitizer import sanitize_event
    result = sanitize_event({"summary": "Meeting", "description": "Notes..."})

Python 3.11+ stdlib only.
"""

import json
import sys
from typing import Any

from sanitize_core import (
    classify_sender,
    detect_cross_field_injection,
    normalize_unicode,
    sanitize_text,
    strip_html,
    strip_invisible_unicode,
)

# ---------------------------------------------------------------------------
# Light sanitization for short fields (title, location, attendee names)
# ---------------------------------------------------------------------------

def _sanitize_short_field(text: str) -> tuple[str, list[str]]:
    """Sanitize a short field (title, location). Returns (clean, flags).

    Uses the full sanitize_text pipeline capped at 500 chars.
    """
    if not text:
        return "", []
    clean, flags, _ = sanitize_text(text, max_len=500)
    return clean, flags


def _sanitize_email_addr(email: str) -> str:
    """Light sanitize an email address string."""
    email = strip_invisible_unicode(email)
    email = normalize_unicode(email)
    return email.strip()


# ---------------------------------------------------------------------------
# Main sanitize_event function
# ---------------------------------------------------------------------------

def sanitize_event(event: dict[str, Any]) -> dict[str, Any]:
    """
    Sanitize a single calendar event dict.

    Accepts fields from gog cal output or Google Calendar API format.
    Returns structured, safe output.
    """
    # Extract raw fields (support both gog CLI and API key names)
    title_raw = str(event.get("summary", event.get("title", "")))
    desc_raw = str(event.get("description", event.get("notes", "")))
    location_raw = str(event.get("location", ""))
    organizer_raw = event.get("organizer", "")
    attendees_raw = event.get("attendees", [])
    start = event.get("start", "")
    end = event.get("end", "")
    conference_raw = str(event.get("conferenceDescription", event.get("hangoutLink", "")))
    ext_props = event.get("extendedProperties", {})

    # Normalize organizer to string (may be dict with "email" key)
    if isinstance(organizer_raw, dict):
        organizer_email = str(organizer_raw.get("email", ""))
        organizer_name = str(organizer_raw.get("displayName", ""))
    else:
        organizer_email = str(organizer_raw)
        organizer_name = ""

    # Normalize attendees to list of email strings
    attendee_emails: list[str] = []
    if isinstance(attendees_raw, list):
        for a in attendees_raw:
            if isinstance(a, dict):
                attendee_emails.append(str(a.get("email", "")))
            elif isinstance(a, str):
                attendee_emails.append(a)

    # --- Sanitize each field ---
    all_flags: list[str] = []

    title_clean, title_flags = _sanitize_short_field(title_raw)
    all_flags.extend(title_flags)

    # Description gets full pipeline (biggest injection vector)
    desc_clean, desc_flags, desc_orig_len = sanitize_text(desc_raw)
    all_flags.extend(desc_flags)

    location_clean, loc_flags = _sanitize_short_field(location_raw)
    all_flags.extend(loc_flags)

    # Sanitize organizer name
    if organizer_name:
        organizer_name, org_name_flags = _sanitize_short_field(organizer_name)
        all_flags.extend(org_name_flags)

    organizer_email = _sanitize_email_addr(organizer_email)

    # Sanitize attendee emails
    attendee_emails = [_sanitize_email_addr(e) for e in attendee_emails if e]

    # Sanitize conference link description
    conf_clean, conf_flags = _sanitize_short_field(conference_raw)
    all_flags.extend(conf_flags)

    # Sanitize extended properties
    if ext_props:
        for section in ("private", "shared"):
            props = ext_props.get(section, {})
            if isinstance(props, dict):
                for key, val in props.items():
                    _, prop_flags = _sanitize_short_field(str(val))
                    all_flags.extend(prop_flags)

    # Cross-field injection detection (title + description + location)
    cross_flags = detect_cross_field_injection([title_clean, desc_clean, location_clean])
    all_flags.extend(cross_flags)

    # Deduplicate flags (preserving order)
    unique_flags = list(dict.fromkeys(all_flags))

    # Classify organizer
    organizer_tier = classify_sender(organizer_email) if organizer_email else "unknown"
    suspicious = len(unique_flags) > 0

    # For unknown organizers, return minimal output (title + time only)
    if organizer_tier == "unknown":
        return {
            "title_clean": title_clean,
            "start": start,
            "end": end,
            "organizer": organizer_email,
            "organizer_tier": "unknown",
            "suspicious": suspicious,
            "flags": unique_flags,
            "summary_level": "minimal",
        }

    return {
        "title_clean": title_clean,
        "description_clean": desc_clean,
        "location_clean": location_clean,
        "start": start,
        "end": end,
        "organizer": organizer_email,
        "organizer_name": organizer_name,
        "attendees": attendee_emails,
        "conference": conf_clean if conf_clean else None,
        "suspicious": suspicious,
        "flags": unique_flags,
        "organizer_tier": organizer_tier,
        "summary_level": "full",
    }


def sanitize_events(events: list[dict[str, Any]]) -> dict[str, Any]:
    """Sanitize a list of calendar event dicts. Returns wrapped output."""
    return {"events": [sanitize_event(e) for e in events]}


# ---------------------------------------------------------------------------
# CLI entrypoint
# ---------------------------------------------------------------------------

def main():
    """Read JSON from stdin, sanitize, print JSON to stdout."""
    raw = sys.stdin.read()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        print(json.dumps({"error": "Invalid JSON input"}), file=sys.stderr)
        sys.exit(1)

    if isinstance(data, list):
        result = sanitize_events(data)
    elif isinstance(data, dict):
        # Single event or already wrapped
        if "events" in data and isinstance(data["events"], list):
            result = sanitize_events(data["events"])
        else:
            result = sanitize_event(data)
    else:
        print(json.dumps({"error": "Expected JSON object or array"}), file=sys.stderr)
        sys.exit(1)

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
