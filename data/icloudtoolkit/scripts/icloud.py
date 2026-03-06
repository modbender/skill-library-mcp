#!/usr/bin/env python3
"""icloud.py — Unified iCloud Calendar + Email CLI for OpenClaw."""

import argparse
import json
import os
import subprocess
import sys
import uuid
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from pathlib import Path


# --- Config ---

def load_config():
    """Load config.json relative to this script's location."""
    script_dir = Path(__file__).resolve().parent
    config_path = script_dir.parent / "config" / "config.json"
    if not config_path.exists():
        print(f"Error: config not found at {config_path}", file=sys.stderr)
        sys.exit(1)
    with open(config_path) as f:
        cfg = json.load(f)
    cfg["calendar_base"] = os.path.expanduser(cfg["calendar_base"])
    if "contacts_base" in cfg:
        cfg["contacts_base"] = os.path.expanduser(cfg["contacts_base"])
    if "subscribed_calendar_base" in cfg:
        cfg["subscribed_calendar_base"] = os.path.expanduser(cfg["subscribed_calendar_base"])
    return cfg


def save_config_field(field, value):
    """Update a single field in config.json without expanding paths.

    Reads the raw JSON, sets config[field] = value, writes back.
    This avoids load_config()'s path expansion (expanduser) which would
    bake absolute paths into the file, breaking portability.
    """
    script_dir = Path(__file__).resolve().parent
    config_path = script_dir.parent / "config" / "config.json"
    with open(config_path) as f:
        raw = json.load(f)
    raw[field] = value
    with open(config_path, "w") as f:
        json.dump(raw, f, indent=2)
        f.write("\n")


def load_raw_config():
    """Load config.json without path expansion. For reading fields like disabled_calendars."""
    script_dir = Path(__file__).resolve().parent
    config_path = script_dir.parent / "config" / "config.json"
    with open(config_path) as f:
        return json.load(f)


# --- Calendar Helpers ---

def local_to_utc(date_str, time_str, tz_name):
    """Convert local time to UTC iCalendar format (e.g. "20260315T200000Z").

    Uses zoneinfo for DST-aware conversion.
    """
    naive = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    local_dt = naive.replace(tzinfo=ZoneInfo(tz_name))
    utc_dt = local_dt.astimezone(ZoneInfo("UTC"))
    return utc_dt.strftime("%Y%m%dT%H%M%SZ")


def fold_line(line):
    """RFC 5545 line folding: break lines longer than 75 bytes."""
    if len(line.encode("utf-8")) <= 75:
        return line
    result = []
    current = ""
    for char in line:
        test = current + char
        if len(test.encode("utf-8")) > 75:
            result.append(current)
            current = " " + char
        else:
            current = test
    if current:
        result.append(current)
    return "\r\n".join(result)


def escape_ics_text(text):
    r"""Escape special characters per RFC 5545 §3.3.11."""
    text = text.replace("\\", "\\\\")
    text = text.replace(";", "\\;")
    text = text.replace(",", "\\,")
    text = text.replace("\n", "\\n")
    return text


def generate_ics(summary, dtstart_utc, dtend_utc, uid, location=None, description=None):
    """Generate a .ics file with pure UTC timestamps (no VTIMEZONE)."""
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//OpenClaw//iCloudToolkit//EN",
        "BEGIN:VEVENT",
        f"DTSTART:{dtstart_utc}",
        f"DTEND:{dtend_utc}",
        f"DTSTAMP:{dtstart_utc}",
        f"UID:{uid}",
        fold_line(f"SUMMARY:{escape_ics_text(summary)}"),
        "STATUS:CONFIRMED",
    ]
    if location:
        lines.append(fold_line(f"LOCATION:{escape_ics_text(location)}"))
    if description:
        lines.append(fold_line(f"DESCRIPTION:{escape_ics_text(description)}"))
    lines.extend([
        "END:VEVENT",
        "END:VCALENDAR",
    ])
    return "\r\n".join(lines) + "\r\n"


def generate_allday_ics(summary, date_str, uid, description=None):
    """Generate an all-day event .ics using VALUE=DATE format."""
    date_val = date_str.replace("-", "")
    end_date = datetime.strptime(date_str, "%Y-%m-%d") + timedelta(days=1)
    end_val = end_date.strftime("%Y%m%d")
    now_utc = datetime.now(tz=timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//OpenClaw//iCloudToolkit//EN",
        "BEGIN:VEVENT",
        f"DTSTART;VALUE=DATE:{date_val}",
        f"DTEND;VALUE=DATE:{end_val}",
        f"DTSTAMP:{now_utc}",
        f"UID:{uid}",
        fold_line(f"SUMMARY:{escape_ics_text(summary)}"),
        "STATUS:CONFIRMED",
    ]
    if description:
        lines.append(fold_line(f"DESCRIPTION:{escape_ics_text(description)}"))
    lines.extend([
        "END:VEVENT",
        "END:VCALENDAR",
    ])
    return "\r\n".join(lines) + "\r\n"


def _validate_dir_id(dir_id, label="directory ID"):
    """Reject dir_ids that could cause path traversal."""
    if not dir_id or ".." in dir_id or "/" in dir_id or "\\" in dir_id:
        print(f"Error: Invalid {label}: {dir_id!r} — must be a plain directory "
              f"name, not a path.", file=sys.stderr)
        sys.exit(1)
    return dir_id


def resolve_calendar_dir(calendar_name, config):
    """Map a calendar name to its filesystem directory."""
    calendars = config.get("calendars", {})
    if calendar_name not in calendars:
        valid = ", ".join(sorted(calendars.keys()))
        print(f"Error: Unknown calendar '{calendar_name}'. Valid: {valid}", file=sys.stderr)
        sys.exit(1)
    dir_id = _validate_dir_id(calendars[calendar_name], f"calendar '{calendar_name}'")
    cal_dir = os.path.join(config["calendar_base"], dir_id)
    if not os.path.isdir(cal_dir):
        print(f"Error: Calendar directory not found: {cal_dir}", file=sys.stderr)
        sys.exit(1)
    return cal_dir


def sanitize_feed_ics(raw_ics):
    """Strip VCALENDAR-level UID lines from an ICS feed.

    Some providers (e.g. MetricAid) put a UID: line on the VCALENDAR wrapper
    itself.  vdirsyncer's Item.ident does a flat scan for the first UID: line,
    so when it splits the feed into individual VEVENTs every item gets the
    same ident — dict collision — only one survives.

    This function removes any UID: or UID;...: line (including RFC 5545
    folded continuation lines) that appears between BEGIN:VCALENDAR and
    the first component (BEGIN:VEVENT / BEGIN:VTODO / BEGIN:VJOURNAL).
    VEVENT-level UIDs are left untouched.
    """
    lines = raw_ics.splitlines(keepends=True)
    out = []
    in_header = False  # between BEGIN:VCALENDAR and first component
    skip_folded = False  # consuming folded continuation of a UID line

    for line in lines:
        stripped = line.strip()

        if stripped == "BEGIN:VCALENDAR":
            in_header = True
            skip_folded = False
            out.append(line)
            continue

        # End of header region — first component found
        if in_header and stripped.startswith("BEGIN:"):
            in_header = False
            skip_folded = False

        if in_header:
            # RFC 5545 folded continuation: line starts with space or tab
            if skip_folded and line[:1] in (" ", "\t"):
                continue  # drop continuation of the UID line
            skip_folded = False

            # Match UID: or UID;param: (case-insensitive)
            upper = stripped.upper()
            if upper.startswith("UID:") or upper.startswith("UID;"):
                skip_folded = True  # next lines might be folded continuations
                continue  # drop this line

        out.append(line)

    return "".join(out)


MAX_FEED_SIZE = 10 * 1024 * 1024  # 10 MB — reject oversized feeds


def _validate_ics_feed(content, dir_id):
    """Validate that content is structurally valid ICS before caching.

    Rejects content that isn't a well-formed iCalendar feed to prevent
    malformed data from reaching downstream parsers (vdirsyncer, khal).
    Returns True if valid, raises ValueError if not.
    """
    if not content or not content.strip():
        raise ValueError(f"Feed {dir_id}: empty content")

    if len(content) > MAX_FEED_SIZE:
        raise ValueError(
            f"Feed {dir_id}: exceeds {MAX_FEED_SIZE // 1024 // 1024}MB limit "
            f"({len(content)} bytes)")

    # Must be text-based iCalendar — reject binary content
    # Check for null bytes which indicate binary data
    if "\x00" in content:
        raise ValueError(f"Feed {dir_id}: contains binary data (null bytes)")

    # Structural check: must have VCALENDAR wrapper and at least one component
    upper = content.upper()
    if "BEGIN:VCALENDAR" not in upper:
        raise ValueError(f"Feed {dir_id}: missing BEGIN:VCALENDAR")
    if "END:VCALENDAR" not in upper:
        raise ValueError(f"Feed {dir_id}: missing END:VCALENDAR")
    if "BEGIN:VEVENT" not in upper and "BEGIN:VTODO" not in upper:
        raise ValueError(f"Feed {dir_id}: no VEVENT or VTODO components")

    # BEGIN/END count parity — catches truncated or concatenated feeds.
    # Prefix with newline so the first line is also matchable, then count
    # "\nBEGIN:" and "\nEND:" to avoid substring hits like DTEND:.
    normed = "\n" + upper.replace("\r\n", "\n").replace("\r", "\n")
    begin_count = normed.count("\nBEGIN:")
    end_count = normed.count("\nEND:")
    if begin_count != end_count:
        raise ValueError(
            f"Feed {dir_id}: mismatched BEGIN/END count "
            f"({begin_count} vs {end_count})")

    return True


def _validate_feed_url(url):
    """Reject feed URLs with dangerous schemes.

    Only allow http/https — block file://, ftp://, data://, etc. that
    could be used to read local files or access unexpected protocols.
    """
    from urllib.parse import urlparse
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError(
            f"Blocked feed URL with scheme {parsed.scheme!r}: {url} "
            f"— only http/https allowed")
    return url


def fetch_and_sanitize_feeds(config):
    """Pre-fetch and sanitize all subscribed calendar HTTP feeds.

    For each URL in config["subscribed_sources"], fetches the ICS content,
    validates it is structurally sound iCalendar data, strips any
    VCALENDAR-level UID (which causes vdirsyncer ident collisions),
    and writes the sanitized content to a local cache file.  vdirsyncer then
    reads from these cache files via singlefile storage instead of fetching
    the raw (broken) feeds directly.

    On fetch failure the existing cache file is preserved — no data is lost.
    """
    from urllib.request import Request, urlopen
    from urllib.error import HTTPError, URLError

    sources = config.get("subscribed_sources", {})
    if not sources:
        return

    sub_base = config.get("subscribed_calendar_base",
                          os.path.expanduser("~/.local/share/vdirsyncer/subscriptions"))
    cache_dir = os.path.join(sub_base, "_feed_cache")
    os.makedirs(cache_dir, exist_ok=True)

    for dir_id, url in sources.items():
        _validate_dir_id(dir_id, f"subscribed source '{dir_id}'")
        cache_path = os.path.join(cache_dir, f"{dir_id}.ics")
        try:
            _validate_feed_url(url)

            req = Request(url)
            req.add_header("User-Agent", "icloud-toolkit/1.0")
            resp = urlopen(req, timeout=60)
            raw = resp.read().decode("utf-8", errors="replace")

            _validate_ics_feed(raw, dir_id)
            sanitized = sanitize_feed_ics(raw)

            # Atomic write: write to temp then rename so a crash mid-write
            # doesn't corrupt the cache
            tmp_path = cache_path + ".tmp"
            with open(tmp_path, "w") as f:
                f.write(sanitized)
            os.replace(tmp_path, cache_path)

        except ValueError as e:
            print(f"  Warning: Rejected feed for {dir_id}: {e}",
                  file=sys.stderr)
        except (HTTPError, URLError, OSError) as e:
            print(f"  Warning: Failed to fetch feed for {dir_id}: {e}",
                  file=sys.stderr)
            # Preserve existing cache — don't overwrite with nothing


def run_sync(config):
    """Run vdirsyncer sync, pre-fetching subscribed feeds first."""
    fetch_and_sanitize_feeds(config)
    vdirsyncer = config["bins"]["vdirsyncer"]
    result = subprocess.run(
        [vdirsyncer, "sync"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"Sync warning: {result.stderr.strip()}", file=sys.stderr)
    return result.returncode == 0


# --- Calendar Commands ---

def cmd_calendar_create(args, config):
    """Create a timed calendar event."""
    print("Syncing calendars...")
    run_sync(config)

    cal_dir = resolve_calendar_dir(args.calendar, config)
    tz_name = config["timezone"]

    dtstart_utc = local_to_utc(args.date, args.start, tz_name)
    dtend_utc = local_to_utc(args.date, args.end, tz_name)
    event_uid = str(uuid.uuid4())

    ics_content = generate_ics(
        summary=args.title,
        dtstart_utc=dtstart_utc,
        dtend_utc=dtend_utc,
        uid=event_uid,
        location=args.location,
        description=args.description,
    )

    ics_path = os.path.join(cal_dir, f"{event_uid}.ics")
    with open(ics_path, "w") as f:
        f.write(ics_content)

    print("Syncing to iCloud...")
    run_sync(config)

    print(f"Created: {args.title}")
    print(f"  Calendar: {args.calendar}")
    print(f"  Date: {args.date}")
    print(f"  Time: {args.start} - {args.end} (local)")
    print(f"  UID: {event_uid}")


def cmd_calendar_create_allday(args, config):
    """Create an all-day calendar event."""
    print("Syncing calendars...")
    run_sync(config)

    cal_dir = resolve_calendar_dir(args.calendar, config)
    event_uid = str(uuid.uuid4())

    ics_content = generate_allday_ics(
        summary=args.title,
        date_str=args.date,
        uid=event_uid,
        description=args.description,
    )

    ics_path = os.path.join(cal_dir, f"{event_uid}.ics")
    with open(ics_path, "w") as f:
        f.write(ics_content)

    print("Syncing to iCloud...")
    run_sync(config)

    print(f"Created all-day event: {args.title}")
    print(f"  Calendar: {args.calendar}")
    print(f"  Date: {args.date}")
    print(f"  UID: {event_uid}")


def cmd_calendar_list(args, config):
    """List upcoming events using khal."""
    run_sync(config)
    khal = config["bins"]["khal"]
    cmd = [khal, "list"]
    if args.calendar:
        cmd.extend(["-a", args.calendar])
    days = args.days or 1
    cmd.extend(["today", f"{days}d"])
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.stdout.strip():
        print(result.stdout.strip())
    else:
        print("No events found.")
    if result.returncode != 0 and result.stderr.strip():
        print(result.stderr.strip(), file=sys.stderr)


def cmd_calendar_search(args, config):
    """Search events using khal."""
    run_sync(config)
    khal = config["bins"]["khal"]
    result = subprocess.run(
        [khal, "search", args.query],
        capture_output=True, text=True
    )
    if result.stdout.strip():
        print(result.stdout.strip())
    else:
        print(f"No events matching '{args.query}'.")
    if result.returncode != 0 and result.stderr.strip():
        print(result.stderr.strip(), file=sys.stderr)


def cmd_calendar_delete(args, config):
    """Delete an event by UID."""
    print("Syncing calendars...")
    run_sync(config)

    uid = args.uid
    found = None
    for cal_name, dir_id in config["calendars"].items():
        _validate_dir_id(dir_id, f"calendar '{cal_name}'")
        cal_dir = os.path.join(config["calendar_base"], dir_id)
        ics_path = os.path.join(cal_dir, f"{uid}.ics")
        if os.path.exists(ics_path):
            found = (cal_name, ics_path)
            break

    if not found:
        # Try searching by UID inside .ics file contents
        for cal_name, dir_id in config["calendars"].items():
            cal_dir = os.path.join(config["calendar_base"], dir_id)
            if not os.path.isdir(cal_dir):
                continue
            for fname in os.listdir(cal_dir):
                if not fname.endswith(".ics"):
                    continue
                fpath = os.path.join(cal_dir, fname)
                with open(fpath) as f:
                    if f"UID:{uid}" in f.read():
                        found = (cal_name, fpath)
                        break
            if found:
                break

    if not found:
        print(f"Error: No event found with UID '{uid}'", file=sys.stderr)
        sys.exit(1)

    cal_name, ics_path = found
    os.remove(ics_path)
    print(f"Deleted event {uid} from {cal_name}")

    print("Syncing to iCloud...")
    run_sync(config)
    print("Done.")


def cmd_calendar_sync(args, config):
    """Manually trigger a calendar sync."""
    print("Syncing...")
    if run_sync(config):
        print("Sync complete.")
    else:
        print("Sync completed with warnings.", file=sys.stderr)


def cmd_calendar_disable(args, config):
    """Disable a calendar so it's excluded from listings and searches."""
    name = args.name
    raw = load_raw_config()

    # Validate: the calendar must exist in owned or subscribed calendars
    all_cals = dict(raw.get("calendars", {}))
    all_cals.update(raw.get("subscribed_calendars", {}))
    if name not in all_cals:
        print(f"Error: Unknown calendar '{name}'.", file=sys.stderr)
        print(f"Valid calendars: {', '.join(sorted(all_cals.keys()))}", file=sys.stderr)
        sys.exit(1)

    disabled = raw.get("disabled_calendars", [])
    if name in disabled:
        print(f"Calendar '{name}' is already disabled.")
        return

    disabled.append(name)
    save_config_field("disabled_calendars", disabled)

    # Regenerate khal config so the disabled calendar is excluded
    from setup import generate_khal_config
    cal_base = os.path.expanduser(raw.get("calendar_base", "~/.local/share/vdirsyncer/calendars"))
    sub_cal_base = raw.get("subscribed_calendar_base")
    if sub_cal_base:
        sub_cal_base = os.path.expanduser(sub_cal_base)
    generate_khal_config(
        raw.get("calendars", {}), cal_base, raw.get("default_calendar", ""),
        tz=raw.get("timezone"),
        subscribed_calendars=raw.get("subscribed_calendars"),
        disabled_calendars=disabled,
        subscribed_cal_base=sub_cal_base,
    )
    print(f"Disabled calendar '{name}'. It will no longer appear in listings.")


def cmd_calendar_enable(args, config):
    """Re-enable a disabled calendar."""
    name = args.name
    raw = load_raw_config()

    disabled = raw.get("disabled_calendars", [])
    if name not in disabled:
        print(f"Calendar '{name}' is not disabled.")
        return

    disabled.remove(name)
    save_config_field("disabled_calendars", disabled)

    # Regenerate khal config so the calendar is included again
    from setup import generate_khal_config
    cal_base = os.path.expanduser(raw.get("calendar_base", "~/.local/share/vdirsyncer/calendars"))
    sub_cal_base = raw.get("subscribed_calendar_base")
    if sub_cal_base:
        sub_cal_base = os.path.expanduser(sub_cal_base)
    generate_khal_config(
        raw.get("calendars", {}), cal_base, raw.get("default_calendar", ""),
        tz=raw.get("timezone"),
        subscribed_calendars=raw.get("subscribed_calendars"),
        disabled_calendars=disabled,
        subscribed_cal_base=sub_cal_base,
    )
    print(f"Enabled calendar '{name}'. It will appear in listings again.")


# --- Email Commands ---

def run_himalaya(config, args, timeout=30):
    """Run himalaya with --config pointing to our isolated himalaya.toml."""
    himalaya_bin = config["bins"]["himalaya"]
    himalaya_config = config["himalaya_config"]
    cmd = [himalaya_bin, "--config", himalaya_config] + list(args)
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        return "", f"Command timed out after {timeout}s", 1


def cmd_email_list(args, config):
    """List emails via himalaya."""
    cmd = ["envelope", "list"]
    count = args.count or 10
    cmd.extend(["--page-size", str(count)])
    if args.folder:
        cmd.extend(["-f", args.folder])
    if args.unread:
        cmd.extend(["flag", "unseen"])
    elif args.query:
        cmd.extend(args.query.split())
    stdout, stderr, rc = run_himalaya(config, cmd)
    print(stdout.strip() if stdout.strip() else "No emails found.")
    if rc != 0 and stderr.strip():
        print(stderr.strip(), file=sys.stderr)


def cmd_email_read(args, config):
    """Read an email by ID."""
    cmd = ["message", "read"]
    if args.folder:
        cmd.extend(["-f", args.folder])
    cmd.append(args.id)
    stdout, stderr, rc = run_himalaya(config, cmd)
    print(stdout.strip() if stdout.strip() else "Could not read message.")
    if rc != 0 and stderr.strip():
        print(stderr.strip(), file=sys.stderr)


def cmd_email_send(args, config):
    """Send an email by piping MML to himalaya."""
    himalaya_bin = config["bins"]["himalaya"]
    himalaya_config = config["himalaya_config"]
    display_name = config.get("display_name", "")
    email = config["account_email"]

    mml = f"From: {display_name} <{email}>\n"
    mml += f"To: {args.to}\n"
    mml += f"Subject: {args.subject}\n"
    mml += f"\n{args.body}\n"

    result = subprocess.run(
        [himalaya_bin, "--config", himalaya_config, "message", "send"],
        input=mml, capture_output=True, text=True
    )
    if result.returncode == 0:
        print(f"Email sent to {args.to}")
    elif "cannot add IMAP message" in result.stderr:
        print(f"Email sent to {args.to}")
        print(f"Warning: could not save copy to Sent folder: {result.stderr.strip()}",
              file=sys.stderr)
    else:
        print(f"Error sending email: {result.stderr.strip()}", file=sys.stderr)
        sys.exit(1)


def cmd_email_reply(args, config):
    """Reply to an email. Reads original headers for threading and From matching."""
    display_name = config.get("display_name", "")
    default_email = config["account_email"]
    known_addresses = config.get("email_addresses", [default_email])

    # Read original message headers
    cmd = ["message", "read", "--preview", "--no-headers",
           "-H", "From", "-H", "To", "-H", "Cc", "-H", "Subject",
           "-H", "Message-ID", "-H", "References"]
    if args.folder:
        cmd.extend(["-f", args.folder])
    cmd.append(args.id)

    stdout, stderr, rc = run_himalaya(config, cmd)
    if rc != 0:
        print(f"Error reading message {args.id}: {stderr.strip()}", file=sys.stderr)
        sys.exit(1)

    headers = {}
    for line in stdout.splitlines():
        if not line.strip():
            break
        if ": " in line:
            key, val = line.split(": ", 1)
            headers[key] = val

    orig_from = headers.get("From", "")
    orig_to = headers.get("To", "")
    orig_cc = headers.get("Cc", "")
    orig_subject = headers.get("Subject", "")
    orig_msg_id = headers.get("Message-ID", "")
    orig_references = headers.get("References", "")

    # Reply from whichever of our addresses received the original
    reply_from = default_email
    all_recipients = (orig_to + " " + orig_cc).lower()
    for addr in known_addresses:
        if addr.lower() in all_recipients:
            reply_from = addr
            break

    reply_to = orig_from

    # Reply-all: include original To/Cc minus ourselves
    if args.all:
        all_addrs = orig_to
        if orig_cc:
            all_addrs += ", " + orig_cc
        cc_parts = [a.strip() for a in all_addrs.split(",")
                    if reply_from.lower() not in a.lower()
                    and orig_from.lower() not in a.lower()]
        reply_cc = ", ".join(cc_parts)
    else:
        reply_cc = ""

    if orig_subject.lower().startswith("re:"):
        reply_subject = orig_subject
    else:
        reply_subject = f"Re: {orig_subject}"

    # Threading headers
    references = orig_references
    if orig_msg_id:
        references = f"{references} {orig_msg_id}".strip()

    mml = f"From: {display_name} <{reply_from}>\n"
    mml += f"To: {reply_to}\n"
    if reply_cc:
        mml += f"Cc: {reply_cc}\n"
    mml += f"Subject: {reply_subject}\n"
    if orig_msg_id:
        mml += f"In-Reply-To: {orig_msg_id}\n"
    if references:
        mml += f"References: {references}\n"
    mml += f"\n{args.body}\n"

    himalaya_bin = config["bins"]["himalaya"]
    himalaya_config = config["himalaya_config"]
    result = subprocess.run(
        [himalaya_bin, "--config", himalaya_config, "message", "send"],
        input=mml, capture_output=True, text=True
    )
    if result.returncode == 0:
        print(f"Reply sent to {reply_to} (from {reply_from})")
    elif "cannot add IMAP message" in result.stderr:
        print(f"Reply sent to {reply_to} (from {reply_from})")
        print(f"Warning: could not save copy to Sent folder: {result.stderr.strip()}",
              file=sys.stderr)
    else:
        print(f"Error sending reply: {result.stderr.strip()}", file=sys.stderr)
        sys.exit(1)


def cmd_email_search(args, config):
    """Search emails by query."""
    cmd = ["envelope", "list"]
    if args.folder:
        cmd.extend(["-f", args.folder])
    cmd.extend(args.query.split())
    stdout, stderr, rc = run_himalaya(config, cmd)
    print(stdout.strip() if stdout.strip() else f"No emails matching '{args.query}'.")
    if rc != 0 and stderr.strip():
        print(stderr.strip(), file=sys.stderr)


def cmd_email_move(args, config):
    """Move an email to a different folder."""
    cmd = ["message", "move"]
    if args.source:
        cmd.extend(["-f", args.source])
    cmd.extend([args.folder, args.id])
    stdout, stderr, rc = run_himalaya(config, cmd)
    if rc == 0:
        print(f"Moved message {args.id} to {args.folder}")
    else:
        print(f"Error: {stderr.strip()}", file=sys.stderr)
        sys.exit(1)


def cmd_email_delete(args, config):
    """Delete an email (moves to Trash/Deleted Messages)."""
    cmd = ["message", "delete"]
    if args.folder:
        cmd.extend(["-f", args.folder])
    cmd.append(args.id)
    stdout, stderr, rc = run_himalaya(config, cmd)
    if rc == 0:
        print(f"Deleted message {args.id}")
    else:
        print(f"Error deleting message: {stderr.strip()}", file=sys.stderr)
        sys.exit(1)


def cmd_folder_purge(args, config):
    """Purge all emails from a folder (folder remains, contents deleted)."""
    cmd = ["folder", "purge", "-y", args.folder]
    stdout, stderr, rc = run_himalaya(config, cmd, timeout=120)
    if rc == 0:
        print(f"Purged folder {args.folder}")
    else:
        print(f"Error purging folder: {stderr.strip()}", file=sys.stderr)
        sys.exit(1)


# --- Contact Helpers ---

def escape_vcard_text(text):
    r"""Escape special characters per RFC 6350 / vCard 3.0."""
    text = text.replace("\\", "\\\\")
    text = text.replace(";", "\\;")
    text = text.replace(",", "\\,")
    text = text.replace("\n", "\\n")
    return text


_KNOWN_VCF_PROPS = {
    "BEGIN", "END", "VERSION", "PRODID",
    "N", "FN", "UID",
    "EMAIL", "TEL", "ORG", "TITLE", "NOTE", "NICKNAME",
    "ADR", "URL", "BDAY", "CATEGORIES",
}


def parse_vcf(vcf_text):
    """Parse a vCard 3.0 string into a dict, preserving unknown properties."""
    # Unfold continuation lines
    unfolded = vcf_text.replace("\r\n ", "").replace("\r\n\t", "").replace("\n ", "").replace("\n\t", "")
    lines = [l for l in unfolded.splitlines() if l.strip()]

    result = {
        "n": "", "fn": "", "uid": "",
        "email": [], "tel": [], "adr": [], "url": [],
        "org": "", "title": "", "note": "", "nickname": "", "bday": "",
        "categories": [],
        "_extra_lines": [],
    }

    for line in lines:
        # Split property name from value (handle params like TEL;type=CELL:+1234)
        if ":" not in line:
            continue
        prop_with_params, value = line.split(":", 1)
        parts = prop_with_params.split(";", 1)
        prop_name = parts[0].upper()
        params = parts[1] if len(parts) > 1 else ""

        if prop_name in ("BEGIN", "END", "VERSION", "PRODID"):
            continue
        elif prop_name == "N":
            result["n"] = value
        elif prop_name == "FN":
            result["fn"] = value
        elif prop_name == "UID":
            result["uid"] = value
        elif prop_name == "EMAIL":
            result["email"].append({"value": value, "params": params})
        elif prop_name == "TEL":
            result["tel"].append({"value": value, "params": params})
        elif prop_name == "ADR":
            result["adr"].append({"value": value, "params": params})
        elif prop_name == "URL":
            result["url"].append({"value": value, "params": params})
        elif prop_name == "ORG":
            result["org"] = value
        elif prop_name == "TITLE":
            result["title"] = value
        elif prop_name == "NOTE":
            result["note"] = value
        elif prop_name == "NICKNAME":
            result["nickname"] = value
        elif prop_name == "BDAY":
            result["bday"] = value
        elif prop_name == "CATEGORIES":
            result["categories"] = [c.strip() for c in value.split(",")]
        else:
            # Unknown/X- property — preserve for lossless round-trip
            result["_extra_lines"].append(line)

    return result


def generate_vcf(n=";;;; ", fn="", uid=None, email=None, tel=None, org="",
                 title="", note="", nickname="", adr=None, url=None,
                 bday="", categories=None, _extra_lines=None, **kwargs):
    """Generate a vCard 3.0 string.

    For org-only contacts, pass fn="Company Name" with n=";;;;".
    _extra_lines preserves unknown/X- properties for lossless edits.
    """
    if uid is None:
        uid = str(uuid.uuid4())

    lines = [
        "BEGIN:VCARD",
        "VERSION:3.0",
        "PRODID:-//OpenClaw//iCloudToolkit//EN",
        fold_line(f"N:{n}"),
        fold_line(f"FN:{fn}"),
        f"UID:{uid}",
    ]

    if email:
        for e in email:
            if isinstance(e, dict):
                params = f";{e['params']}" if e.get("params") else ""
                lines.append(fold_line(f"EMAIL{params}:{e['value']}"))
            else:
                lines.append(fold_line(f"EMAIL;type=INTERNET:{e}"))

    if tel:
        for t in tel:
            if isinstance(t, dict):
                params = f";{t['params']}" if t.get("params") else ""
                lines.append(fold_line(f"TEL{params}:{t['value']}"))
            else:
                lines.append(fold_line(f"TEL;type=VOICE:{t}"))

    if org:
        lines.append(fold_line(f"ORG:{escape_vcard_text(org)}"))
    if title:
        lines.append(fold_line(f"TITLE:{escape_vcard_text(title)}"))
    if note:
        lines.append(fold_line(f"NOTE:{escape_vcard_text(note)}"))
    if nickname:
        lines.append(fold_line(f"NICKNAME:{escape_vcard_text(nickname)}"))
    if bday:
        lines.append(f"BDAY:{bday}")

    if adr:
        for a in adr:
            if isinstance(a, dict):
                params = f";{a['params']}" if a.get("params") else ""
                lines.append(fold_line(f"ADR{params}:{a['value']}"))
            else:
                lines.append(fold_line(f"ADR;type=HOME:{a}"))

    if url:
        for u in url:
            if isinstance(u, dict):
                params = f";{u['params']}" if u.get("params") else ""
                lines.append(fold_line(f"URL{params}:{u['value']}"))
            else:
                lines.append(fold_line(f"URL:{u}"))

    if categories:
        lines.append(fold_line(f"CATEGORIES:{','.join(categories)}"))

    # Replay preserved X- and unknown properties for lossless round-trip
    if _extra_lines:
        for extra in _extra_lines:
            lines.append(fold_line(extra))

    lines.append("END:VCARD")
    return "\r\n".join(lines) + "\r\n"


def find_vcf_by_uid(uid, config):
    """Find a .vcf file by scanning contents for UID line. Returns (path, addressbook_name) or None."""
    contacts_base = config.get("contacts_base", "")
    addressbooks = config.get("addressbooks", {})

    for ab_name, dir_id in addressbooks.items():
        _validate_dir_id(dir_id, f"addressbook '{ab_name}'")
        ab_dir = os.path.join(contacts_base, dir_id)
        if not os.path.isdir(ab_dir):
            continue
        for fname in os.listdir(ab_dir):
            if not fname.endswith(".vcf"):
                continue
            fpath = os.path.join(ab_dir, fname)
            try:
                with open(fpath) as f:
                    content = f.read()
                if f"UID:{uid}" in content:
                    return (fpath, ab_name)
            except (IOError, OSError):
                continue
    return None


# --- Contact Commands ---

def resolve_addressbook_dir(addressbook_name, config):
    """Map an address book name to its filesystem directory."""
    addressbooks = config.get("addressbooks", {})
    if addressbook_name not in addressbooks:
        valid = ", ".join(sorted(addressbooks.keys()))
        print(f"Error: Unknown address book '{addressbook_name}'. Valid: {valid}", file=sys.stderr)
        sys.exit(1)
    dir_id = _validate_dir_id(addressbooks[addressbook_name], f"addressbook '{addressbook_name}'")
    ab_dir = os.path.join(config["contacts_base"], dir_id)
    if not os.path.isdir(ab_dir):
        print(f"Error: Address book directory not found: {ab_dir}", file=sys.stderr)
        sys.exit(1)
    return ab_dir


def run_khard(config, args):
    """Run khard and return (stdout, stderr, returncode)."""
    khard_bin = config["bins"]["khard"]
    cmd = [khard_bin] + list(args)
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        return "", "Command timed out after 30s", 1


def require_sync(config):
    """Run vdirsyncer sync, abort on failure. Use for write operations."""
    if not run_sync(config):
        print("Error: Sync failed. Aborting to prevent data conflicts.", file=sys.stderr)
        sys.exit(1)


def _print_contact(contact):
    """Pretty-print a parsed contact dict."""
    print(f"  Name: {contact.get('fn', 'N/A')}")
    if contact.get("uid"):
        print(f"  UID: {contact['uid']}")
    if contact.get("org"):
        print(f"  Organization: {contact['org']}")
    if contact.get("title"):
        print(f"  Title: {contact['title']}")
    for e in contact.get("email", []):
        label = e.get("params", "").replace("type=", "").replace("INTERNET;", "") or "email"
        print(f"  Email ({label}): {e['value']}")
    for t in contact.get("tel", []):
        label = t.get("params", "").replace("type=", "") or "phone"
        print(f"  Phone ({label}): {t['value']}")
    for a in contact.get("adr", []):
        label = a.get("params", "").replace("type=", "") or "address"
        # vCard address fields: PO;ext;street;city;state;zip;country
        parts = a["value"].split(";")
        addr_str = ", ".join(p for p in parts if p)
        if addr_str:
            print(f"  Address ({label}): {addr_str}")
    for u in contact.get("url", []):
        print(f"  URL: {u['value']}")
    if contact.get("nickname"):
        print(f"  Nickname: {contact['nickname']}")
    if contact.get("bday"):
        print(f"  Birthday: {contact['bday']}")
    if contact.get("note"):
        print(f"  Note: {contact['note']}")
    if contact.get("categories"):
        print(f"  Categories: {', '.join(contact['categories'])}")


def cmd_contact_list(args, config):
    """List contacts via khard."""
    run_sync(config)
    cmd = ["list"]
    if args.addressbook:
        cmd.extend(["-a", args.addressbook])
    stdout, stderr, rc = run_khard(config, cmd)
    if stdout.strip():
        lines = stdout.strip().splitlines()
        if args.count:
            # khard list includes a header line
            lines = lines[:1] + lines[1:args.count + 1]
        print("\n".join(lines))
    else:
        print("No contacts found.")
    if rc != 0 and stderr.strip():
        print(stderr.strip(), file=sys.stderr)


def cmd_contact_show(args, config):
    """Show a contact by UID or search term."""
    run_sync(config)
    # Try UID lookup first
    result = find_vcf_by_uid(args.query, config)
    if result:
        fpath, ab_name = result
        with open(fpath) as f:
            content = f.read()
        contact = parse_vcf(content)
        print(f"Contact from {ab_name}:")
        _print_contact(contact)
        return

    # Fall back to khard show
    stdout, stderr, rc = run_khard(config, ["show", args.query])
    if rc == 0 and stdout.strip():
        print(stdout.strip())
    else:
        print(f"No contact found for '{args.query}'")
        if stderr.strip():
            print(stderr.strip(), file=sys.stderr)


def cmd_contact_search(args, config):
    """Search contacts via khard."""
    run_sync(config)
    stdout, stderr, rc = run_khard(config, ["list", args.query])
    if stdout.strip():
        print(stdout.strip())
    else:
        print(f"No contacts matching '{args.query}'.")
    if rc != 0 and stderr.strip():
        print(stderr.strip(), file=sys.stderr)


def cmd_contact_sync(args, config):
    """Manually trigger a contacts sync."""
    print("Syncing contacts...")
    if run_sync(config):
        print("Sync complete.")
    else:
        print("Sync completed with warnings.", file=sys.stderr)


def cmd_contact_create(args, config):
    """Create a new contact."""
    print("Syncing contacts...")
    require_sync(config)

    first = args.first or ""
    last = args.last or ""

    if args.fn:
        fn = args.fn
    elif first or last:
        fn = f"{first} {last}".strip()
    else:
        print("Error: Provide first/last name or --fn for the contact name.", file=sys.stderr)
        sys.exit(1)

    # N field: Last;First;Middle;Prefix;Suffix
    n = f"{last};{first};;;"

    contact_uid = str(uuid.uuid4())
    emails = [{"value": e, "params": "type=INTERNET"} for e in (args.email or [])]
    phones = [{"value": p, "params": "type=CELL"} for p in (args.phone or [])]

    vcf_content = generate_vcf(
        n=n, fn=fn, uid=contact_uid,
        email=emails or None,
        tel=phones or None,
        org=args.org or "",
        title=args.title or "",
        note=args.note or "",
        nickname=args.nickname or "",
        bday=args.birthday or "",
        categories=args.category or None,
    )

    # Write to default or specified address book
    ab_name = args.addressbook or config.get("default_addressbook", "")
    if not ab_name:
        ab_name = next(iter(config.get("addressbooks", {})), "")
    if not ab_name:
        print("Error: No address book configured.", file=sys.stderr)
        sys.exit(1)

    ab_dir = resolve_addressbook_dir(ab_name, config)
    vcf_path = os.path.join(ab_dir, f"{contact_uid}.vcf")
    with open(vcf_path, "w") as f:
        f.write(vcf_content)

    print("Syncing to iCloud...")
    run_sync(config)

    print(f"Created contact: {fn}")
    print(f"  Address book: {ab_name}")
    print(f"  UID: {contact_uid}")


def cmd_contact_delete(args, config):
    """Delete a contact by UID."""
    print("Syncing contacts...")
    require_sync(config)

    result = find_vcf_by_uid(args.uid, config)
    if not result:
        print(f"Error: No contact found with UID '{args.uid}'", file=sys.stderr)
        sys.exit(1)

    fpath, ab_name = result
    # Read name before deleting for confirmation output
    with open(fpath) as f:
        contact = parse_vcf(f.read())
    contact_name = contact.get("fn", "Unknown")

    os.remove(fpath)
    print(f"Deleted contact '{contact_name}' ({args.uid}) from {ab_name}")

    print("Syncing to iCloud...")
    run_sync(config)
    print("Done.")


def cmd_contact_edit(args, config):
    """Edit an existing contact, preserving unknown/X- properties."""
    print("Syncing contacts...")
    require_sync(config)

    result = find_vcf_by_uid(args.uid, config)
    if not result:
        print(f"Error: No contact found with UID '{args.uid}'", file=sys.stderr)
        sys.exit(1)

    fpath, ab_name = result
    with open(fpath) as f:
        original = f.read()
    contact = parse_vcf(original)

    # Track whether any changes were made
    changed = False

    # Name fields
    if args.first is not None or args.last is not None:
        # Parse existing N field: Last;First;Middle;Prefix;Suffix
        n_parts = contact["n"].split(";") if contact["n"] else ["", "", "", "", ""]
        while len(n_parts) < 5:
            n_parts.append("")
        if args.last is not None:
            n_parts[0] = args.last
        if args.first is not None:
            n_parts[1] = args.first
        contact["n"] = ";".join(n_parts)
        # Update FN unless --fn is explicitly given
        if not args.fn:
            contact["fn"] = f"{n_parts[1]} {n_parts[0]}".strip()
        changed = True

    if args.fn is not None:
        contact["fn"] = args.fn
        changed = True

    # Replace-all fields
    if args.email is not None:
        contact["email"] = [{"value": e, "params": "type=INTERNET"} for e in args.email]
        changed = True
    if args.phone is not None:
        contact["tel"] = [{"value": p, "params": "type=CELL"} for p in args.phone]
        changed = True

    # Add/remove email
    if args.add_email:
        for e in args.add_email:
            contact["email"].append({"value": e, "params": "type=INTERNET"})
        changed = True
    if args.remove_email:
        for e in args.remove_email:
            contact["email"] = [x for x in contact["email"] if x["value"].lower() != e.lower()]
        changed = True

    # Add/remove phone
    if args.add_phone:
        for p in args.add_phone:
            contact["tel"].append({"value": p, "params": "type=CELL"})
        changed = True
    if args.remove_phone:
        for p in args.remove_phone:
            contact["tel"] = [x for x in contact["tel"] if x["value"] != p]
        changed = True

    # Simple string fields — only update if explicitly provided
    if args.org is not None:
        contact["org"] = args.org
        changed = True
    if args.title is not None:
        contact["title"] = args.title
        changed = True
    if args.note is not None:
        contact["note"] = args.note
        changed = True
    if args.nickname is not None:
        contact["nickname"] = args.nickname
        changed = True
    if args.birthday is not None:
        contact["bday"] = args.birthday
        changed = True

    if not changed:
        print("No changes specified.")
        return

    # Generate new vCard, write back to SAME file path (preserves vdirsyncer filename)
    vcf_content = generate_vcf(**contact)
    with open(fpath, "w") as f:
        f.write(vcf_content)

    print("Syncing to iCloud...")
    run_sync(config)

    print(f"Updated contact: {contact['fn']}")
    _print_contact(contact)


# --- Calendar Refresh ---

def cmd_calendar_refresh(args, config):
    """Re-discover calendars via CalDAV PROPFIND and update config mappings.

    Steps:
    1. vdirsyncer discover + sync (pulls new collections from iCloud)
    2. PROPFIND to get calendar metadata (display names, owned/subscribed, source URLs)
    3. For subscribed calendars with source_url not yet on disk:
       a. Add to subscribed_sources
       b. Regenerate vdirsyncer config with HTTP pairs
       c. Re-run vdirsyncer discover + sync (creates local dirs for HTTP feeds)
    4. Cross-reference all PROPFIND results against local dirs
    5. Save config + regenerate khal config
    """
    from setup import (run_vdirsyncer_discover, propfind_calendars,
                        generate_khal_config, generate_vdirsyncer_config)

    raw = load_raw_config()
    cal_base = os.path.expanduser(raw.get("calendar_base", "~/.local/share/vdirsyncer/calendars"))
    sub_cal_base = os.path.expanduser(
        raw.get("subscribed_calendar_base", "~/.local/share/vdirsyncer/subscriptions"))

    # Step 1: Pre-fetch subscribed feeds + vdirsyncer discover + sync
    vdirsyncer_bin = config["bins"]["vdirsyncer"]
    print("Syncing calendar collections from iCloud...")
    fetch_and_sanitize_feeds(config)
    run_vdirsyncer_discover(vdirsyncer_bin)

    # Step 2: Resolve apple_id for PROPFIND auth
    apple_id = raw.get("apple_id")
    if not apple_id:
        addresses = raw.get("email_addresses", [])
        apple_id = addresses[-1] if addresses else None
        if not apple_id:
            print("Error: No apple_id in config and no email_addresses to fall back to.",
                  file=sys.stderr)
            print("Re-run 'setup finalize' to populate apple_id.", file=sys.stderr)
            sys.exit(1)
        save_config_field("apple_id", apple_id)
        print(f"  Backfilled apple_id from email_addresses: {apple_id}")

    script_dir = Path(__file__).resolve().parent
    auth_path = script_dir.parent / "config" / "auth"

    # Step 3: PROPFIND discovery
    propfind_results = None
    try:
        propfind_results = propfind_calendars(apple_id, auth_path)
        print(f"  PROPFIND returned {len(propfind_results)} calendar(s)")
    except Exception as e:
        print(f"  Warning: CalDAV PROPFIND failed: {e}")
        print("  Falling back to local-only discovery.")

    # Step 4: Handle subscribed calendars with source URLs
    # Scan current local dirs from both base paths
    def _scan_local_dirs():
        dirs = set()
        if os.path.isdir(cal_base):
            dirs |= {e for e in os.listdir(cal_base)
                      if os.path.isdir(os.path.join(cal_base, e))}
        if os.path.isdir(sub_cal_base):
            dirs |= {e for e in os.listdir(sub_cal_base)
                      if os.path.isdir(os.path.join(sub_cal_base, e))}
        return dirs

    local_dirs = _scan_local_dirs()

    # Load existing subscribed_sources and check for new ones from PROPFIND
    subscribed_sources = dict(raw.get("subscribed_sources", {}))
    sources_changed = False

    if propfind_results:
        for cal in propfind_results:
            source_url = cal.get("source_url")
            if not source_url:
                continue
            dir_id = cal["dir_id"]
            if dir_id not in subscribed_sources:
                subscribed_sources[dir_id] = source_url
                sources_changed = True

    # If we have subscribed sources with missing local dirs, regenerate
    # vdirsyncer config with HTTP pairs and re-sync to create them
    if subscribed_sources:
        missing_dirs = [d for d in subscribed_sources if d not in local_dirs]
        if missing_dirs or sources_changed:
            print(f"  Regenerating vdirsyncer config with {len(subscribed_sources)} "
                  f"HTTP feed(s)...")
            generate_vdirsyncer_config(apple_id, auth_path,
                                       subscribed_sources=subscribed_sources)
            if missing_dirs:
                print(f"  Syncing {len(missing_dirs)} new subscribed calendar(s)...")
                fetch_and_sanitize_feeds(config)
                run_vdirsyncer_discover(vdirsyncer_bin)
            # Re-scan after sync created new dirs
            local_dirs = _scan_local_dirs()

    # Step 5: Cross-reference PROPFIND results against local filesystem
    calendars = dict(raw.get("calendars", {}))
    subscribed_calendars = dict(raw.get("subscribed_calendars", {}))
    disabled = raw.get("disabled_calendars", [])

    mapped_dirs = {}
    for name, dir_id in calendars.items():
        mapped_dirs[dir_id] = name
    for name, dir_id in subscribed_calendars.items():
        mapped_dirs[dir_id] = name

    all_names = set(calendars.keys()) | set(subscribed_calendars.keys())

    added = []
    already_mapped = 0
    skipped_no_dir = 0

    if propfind_results:
        for cal in propfind_results:
            dir_id = cal["dir_id"]

            if dir_id in mapped_dirs:
                already_mapped += 1
                continue

            if dir_id not in local_dirs:
                skipped_no_dir += 1
                continue

            name = cal["name"]
            if name in all_names:
                suffix = 2
                while f"{name} ({suffix})" in all_names:
                    suffix += 1
                name = f"{name} ({suffix})"

            if cal["subscribed"]:
                subscribed_calendars[name] = dir_id
            else:
                calendars[name] = dir_id

            all_names.add(name)
            added.append({"name": name, "dir_id": dir_id,
                           "type": "subscribed" if cal["subscribed"] else "owned"})

    # Step 6: Detect stale mappings (dir_ids in config but not on disk)
    stale = []
    for name, dir_id in list(calendars.items()) + list(subscribed_calendars.items()):
        if dir_id not in local_dirs:
            stale.append({"name": name, "dir_id": dir_id})

    # Step 7: Save if anything changed
    changed = False
    if added:
        save_config_field("calendars", calendars)
        save_config_field("subscribed_calendars", subscribed_calendars)
        changed = True

    if sources_changed or (subscribed_sources and "subscribed_sources" not in raw):
        save_config_field("subscribed_sources", subscribed_sources)
        save_config_field("subscribed_calendar_base",
                          "~/.local/share/vdirsyncer/subscriptions")
        changed = True

    if changed:
        generate_khal_config(
            calendars, cal_base, raw.get("default_calendar", ""),
            tz=raw.get("timezone"),
            subscribed_calendars=subscribed_calendars,
            disabled_calendars=disabled,
            subscribed_cal_base=sub_cal_base,
        )

    # Step 8: Print summary
    print(f"\nRefresh summary:")
    print(f"  Already mapped: {already_mapped}")
    if added:
        print(f"  Newly added ({len(added)}):")
        for a in added:
            print(f"    + {a['name']} ({a['type']})")
    else:
        print(f"  Newly added: 0")
    if skipped_no_dir:
        print(f"  Skipped (not on disk): {skipped_no_dir}")
    if stale:
        print(f"  Stale mappings (dir missing from disk):")
        for s in stale:
            print(f"    ! {s['name']} → {s['dir_id']}")
        print("  (Use 'calendar disable' to suppress or remove manually from config.json)")
    if disabled:
        print(f"  Disabled: {len(disabled)} ({', '.join(disabled)})")
    if not propfind_results and not added:
        unmapped_local = local_dirs - set(mapped_dirs.keys())
        if unmapped_local:
            print(f"\n  Unmapped local directories (couldn't resolve names without PROPFIND):")
            for d in sorted(unmapped_local):
                print(f"    ? {d}")
            print("  Retry 'calendar refresh' or map manually in config.json")


# --- Setup Commands ---

def cmd_setup_discover(args, config):
    """Discover calendars and cross-reference with config.json."""
    cal_base = config["calendar_base"]
    configured = config.get("calendars", {})
    subscribed = config.get("subscribed_calendars", {})
    id_to_name = {v: k for k, v in configured.items()}
    for name, dir_id in subscribed.items():
        id_to_name[dir_id] = f"{name} (subscribed)"

    print(f"Calendar base: {cal_base}\n")
    print(f"{'Directory':<45} {'ICS Files':<12} {'Mapped As'}")
    print("-" * 75)

    if not os.path.isdir(cal_base):
        print(f"Error: Calendar base not found: {cal_base}", file=sys.stderr)
        sys.exit(1)

    for entry in sorted(os.listdir(cal_base)):
        entry_path = os.path.join(cal_base, entry)
        if not os.path.isdir(entry_path):
            continue
        ics_count = sum(1 for f in os.listdir(entry_path) if f.endswith(".ics"))
        mapped = id_to_name.get(entry, "UNMAPPED")
        print(f"{entry:<45} {ics_count:<12} {mapped}")

    total_configured = len(configured) + len(subscribed)
    print(f"\nConfigured calendars: {total_configured} ({len(configured)} owned, {len(subscribed)} subscribed)")
    unmapped = [e for e in os.listdir(cal_base)
                if os.path.isdir(os.path.join(cal_base, e)) and e not in id_to_name]
    if unmapped:
        print(f"Unmapped directories: {', '.join(unmapped)}")
    else:
        print("All directories mapped.")


# --- Self-Test ---

def run_self_test():
    """Inline assertion tests for helper functions."""
    print("Running self-tests...")

    tz = "America/Regina"  # Always UTC-6, no DST

    assert local_to_utc("2026-03-15", "14:00", tz) == "20260315T200000Z"
    assert local_to_utc("2026-03-15", "23:00", tz) == "20260316T050000Z"
    assert local_to_utc("2026-03-15", "00:00", tz) == "20260315T060000Z"
    assert local_to_utc("2026-03-15", "18:00", tz) == "20260316T000000Z"

    # DST: America/New_York is UTC-4 in summer, UTC-5 in winter
    assert local_to_utc("2026-07-04", "12:00", "America/New_York") == "20260704T160000Z"
    assert local_to_utc("2026-01-15", "12:00", "America/New_York") == "20260115T170000Z"

    assert fold_line("SUMMARY:Short") == "SUMMARY:Short"
    long_line = "SUMMARY:" + "A" * 100
    assert "\r\n " in fold_line(long_line)

    assert escape_ics_text("a;b,c\\d\ne") == "a\\;b\\,c\\\\d\\ne"

    ics = generate_ics("Test", "20260315T200000Z", "20260315T210000Z", "test-uid-123")
    assert "VTIMEZONE" not in ics
    assert "DTSTART:20260315T200000Z" in ics
    assert "DTEND:20260315T210000Z" in ics
    assert "UID:test-uid-123" in ics
    assert "SUMMARY:Test" in ics

    ics_ad = generate_allday_ics("Holiday", "2026-03-15", "allday-uid-456")
    assert "DTSTART;VALUE=DATE:20260315" in ics_ad
    assert "DTEND;VALUE=DATE:20260316" in ics_ad
    assert "VTIMEZONE" not in ics_ad

    # --- Feed validation tests ---

    valid_feed = (
        "BEGIN:VCALENDAR\r\nVERSION:2.0\r\n"
        "BEGIN:VEVENT\r\nUID:test\r\nSUMMARY:Test\r\nEND:VEVENT\r\n"
        "END:VCALENDAR\r\n"
    )
    assert _validate_ics_feed(valid_feed, "test") is True

    # Reject empty content
    try:
        _validate_ics_feed("", "empty")
        assert False, "Should reject empty"
    except ValueError:
        pass

    # Reject binary content
    try:
        _validate_ics_feed("BEGIN:VCALENDAR\x00binary", "bin")
        assert False, "Should reject binary"
    except ValueError:
        pass

    # Reject missing VCALENDAR
    try:
        _validate_ics_feed("just some text", "bad")
        assert False, "Should reject non-ICS"
    except ValueError:
        pass

    # Reject mismatched BEGIN/END
    try:
        _validate_ics_feed("BEGIN:VCALENDAR\r\nBEGIN:VEVENT\r\nEND:VCALENDAR\r\n", "mismatch")
        assert False, "Should reject mismatched"
    except ValueError:
        pass

    # DTEND must not false-match as END: (regression test)
    feed_with_dtend = (
        "BEGIN:VCALENDAR\r\nVERSION:2.0\r\n"
        "BEGIN:VEVENT\r\nUID:dt1\r\nDTSTART:20260315T080000Z\r\n"
        "DTEND:20260315T200000Z\r\nSUMMARY:Shift\r\nEND:VEVENT\r\n"
        "END:VCALENDAR\r\n"
    )
    assert _validate_ics_feed(feed_with_dtend, "dtend") is True

    # Reject oversized (mock via lowered limit not practical, just verify the check exists)
    try:
        _validate_ics_feed("x" * (MAX_FEED_SIZE + 1), "huge")
        assert False, "Should reject oversized"
    except ValueError:
        pass

    # URL scheme validation
    assert _validate_feed_url("https://example.com/feed.ics") == "https://example.com/feed.ics"
    assert _validate_feed_url("http://example.com/feed.ics") == "http://example.com/feed.ics"
    try:
        _validate_feed_url("file:///etc/passwd")
        assert False, "Should reject file:// scheme"
    except ValueError:
        pass
    try:
        _validate_feed_url("ftp://example.com/feed.ics")
        assert False, "Should reject ftp:// scheme"
    except ValueError:
        pass

    # dir_id validation
    try:
        _validate_dir_id("../../../.ssh", "test")
        assert False, "Should reject path traversal"
    except SystemExit:
        pass
    try:
        _validate_dir_id("foo/bar", "test")
        assert False, "Should reject slashes"
    except SystemExit:
        pass

    # --- Feed sanitization tests ---

    # Multi-event ICS with a VCALENDAR-level UID (like MetricAid feeds)
    feed_with_cal_uid = (
        "BEGIN:VCALENDAR\r\n"
        "VERSION:2.0\r\n"
        "PRODID:-//Test//Test//EN\r\n"
        "UID:calendar-level-uid-bad\r\n"
        "BEGIN:VEVENT\r\n"
        "UID:event-uid-001\r\n"
        "SUMMARY:Shift A\r\n"
        "DTSTART:20260315T080000Z\r\n"
        "DTEND:20260315T200000Z\r\n"
        "END:VEVENT\r\n"
        "BEGIN:VEVENT\r\n"
        "UID:event-uid-002\r\n"
        "SUMMARY:Shift B\r\n"
        "DTSTART:20260316T080000Z\r\n"
        "DTEND:20260316T200000Z\r\n"
        "END:VEVENT\r\n"
        "END:VCALENDAR\r\n"
    )
    sanitized = sanitize_feed_ics(feed_with_cal_uid)
    assert "calendar-level-uid-bad" not in sanitized, "VCALENDAR UID not stripped"
    assert "UID:event-uid-001" in sanitized, "VEVENT UID 001 was wrongly stripped"
    assert "UID:event-uid-002" in sanitized, "VEVENT UID 002 was wrongly stripped"
    assert "BEGIN:VCALENDAR" in sanitized
    assert "VERSION:2.0" in sanitized
    assert "PRODID:-//Test//Test//EN" in sanitized

    # UID with parameters (UID;VALUE=TEXT:...) should also be stripped
    feed_with_param_uid = (
        "BEGIN:VCALENDAR\r\n"
        "UID;VALUE=TEXT:param-uid-bad\r\n"
        "BEGIN:VEVENT\r\n"
        "UID:event-uid-003\r\n"
        "SUMMARY:Test\r\n"
        "END:VEVENT\r\n"
        "END:VCALENDAR\r\n"
    )
    sanitized2 = sanitize_feed_ics(feed_with_param_uid)
    assert "param-uid-bad" not in sanitized2, "UID;param not stripped"
    assert "UID:event-uid-003" in sanitized2

    # Folded UID continuation line should be stripped too
    feed_with_folded_uid = (
        "BEGIN:VCALENDAR\r\n"
        "UID:very-long-uid-that-gets\r\n"
        " -folded-onto-next-line\r\n"
        "BEGIN:VEVENT\r\n"
        "UID:event-uid-004\r\n"
        "SUMMARY:Folded\r\n"
        "END:VEVENT\r\n"
        "END:VCALENDAR\r\n"
    )
    sanitized3 = sanitize_feed_ics(feed_with_folded_uid)
    assert "very-long-uid" not in sanitized3, "Folded UID not stripped"
    assert "folded-onto-next-line" not in sanitized3, "Folded continuation not stripped"
    assert "UID:event-uid-004" in sanitized3

    # Feed without VCALENDAR-level UID should pass through unchanged
    clean_feed = (
        "BEGIN:VCALENDAR\r\n"
        "VERSION:2.0\r\n"
        "BEGIN:VEVENT\r\n"
        "UID:clean-uid\r\n"
        "SUMMARY:Clean\r\n"
        "END:VEVENT\r\n"
        "END:VCALENDAR\r\n"
    )
    sanitized4 = sanitize_feed_ics(clean_feed)
    assert sanitized4 == clean_feed, "Clean feed was modified"

    # --- vCard tests ---

    # escape_vcard_text
    assert escape_vcard_text("a;b,c\\d\ne") == "a\\;b\\,c\\\\d\\ne"

    # Basic vCard generation
    vcf = generate_vcf(n="Doe;John;;;", fn="John Doe", uid="test-uid-vcf")
    assert "BEGIN:VCARD" in vcf
    assert "VERSION:3.0" in vcf
    assert "N:Doe;John;;;" in vcf
    assert "FN:John Doe" in vcf
    assert "UID:test-uid-vcf" in vcf
    assert "END:VCARD" in vcf

    # vCard with all optional fields
    vcf_full = generate_vcf(
        n="Doe;John;;;",
        fn="John Doe",
        uid="full-uid",
        email=[{"value": "john@example.com", "params": "type=INTERNET;type=HOME"}],
        tel=[{"value": "+15551234567", "params": "type=CELL"}],
        org="Acme Corp",
        title="Engineer",
        note="A note",
        nickname="Johnny",
        bday="1990-01-15",
        adr=[{"value": ";;123 Main St;City;ST;12345;US", "params": "type=HOME"}],
        url=[{"value": "https://example.com", "params": ""}],
        categories=["friend", "work"],
    )
    assert "ORG:Acme Corp" in vcf_full
    assert "TITLE:Engineer" in vcf_full
    assert "BDAY:1990-01-15" in vcf_full
    assert "CATEGORIES:friend,work" in vcf_full
    assert "EMAIL;type=INTERNET;type=HOME:john@example.com" in vcf_full
    assert "TEL;type=CELL:+15551234567" in vcf_full

    # Org-only contact (no name, fn override)
    vcf_org = generate_vcf(n=";;;;", fn="Acme Corp", uid="org-uid", org="Acme Corp")
    assert "N:;;;;" in vcf_org
    assert "FN:Acme Corp" in vcf_org

    # Multi-value fields
    vcf_multi = generate_vcf(
        n="Doe;John;;;", fn="John Doe", uid="multi-uid",
        email=[
            {"value": "john@work.com", "params": "type=WORK"},
            {"value": "john@home.com", "params": "type=HOME"},
        ],
        tel=[
            {"value": "+1111", "params": "type=CELL"},
            {"value": "+2222", "params": "type=HOME"},
        ],
    )
    assert "john@work.com" in vcf_multi
    assert "john@home.com" in vcf_multi
    assert "+1111" in vcf_multi
    assert "+2222" in vcf_multi

    # parse_vcf basic
    parsed = parse_vcf(vcf_full)
    assert parsed["fn"] == "John Doe"
    assert parsed["n"] == "Doe;John;;;"
    assert parsed["uid"] == "full-uid"
    assert parsed["org"] == "Acme Corp"
    assert parsed["title"] == "Engineer"
    assert parsed["bday"] == "1990-01-15"
    assert len(parsed["email"]) == 1
    assert parsed["email"][0]["value"] == "john@example.com"
    assert len(parsed["tel"]) == 1
    assert parsed["categories"] == ["friend", "work"]

    # Lossless round-trip: X- properties survive parse → generate cycle
    vcf_with_extra = "BEGIN:VCARD\r\nVERSION:3.0\r\nN:Doe;Jane;;;\r\nFN:Jane Doe\r\nUID:lossless-uid\r\nEMAIL;type=HOME:jane@example.com\r\nX-ABLabel:Home\r\nX-APPLE-SUBLOCALITY:Downtown\r\nPHOTO;ENCODING=b;TYPE=JPEG:base64data\r\nEND:VCARD\r\n"
    parsed_extra = parse_vcf(vcf_with_extra)
    assert len(parsed_extra["_extra_lines"]) == 3
    assert "X-ABLabel:Home" in parsed_extra["_extra_lines"]
    assert "X-APPLE-SUBLOCALITY:Downtown" in parsed_extra["_extra_lines"]
    regenerated = generate_vcf(**parsed_extra)
    assert "X-ABLabel:Home" in regenerated
    assert "X-APPLE-SUBLOCALITY:Downtown" in regenerated
    assert "PHOTO;ENCODING=b;TYPE=JPEG:base64data" in regenerated
    assert "FN:Jane Doe" in regenerated
    assert "EMAIL;type=HOME:jane@example.com" in regenerated

    # find_vcf_by_uid with temp directory
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        ab_dir = os.path.join(tmpdir, "test-ab")
        os.makedirs(ab_dir)
        # File where filename != UID
        with open(os.path.join(ab_dir, "random-filename.vcf"), "w") as f:
            f.write("BEGIN:VCARD\r\nUID:actual-uid-123\r\nFN:Test\r\nEND:VCARD\r\n")
        # File where filename == UID
        with open(os.path.join(ab_dir, "match-uid.vcf"), "w") as f:
            f.write("BEGIN:VCARD\r\nUID:match-uid\r\nFN:Match\r\nEND:VCARD\r\n")

        test_config = {
            "contacts_base": tmpdir,
            "addressbooks": {"TestAB": "test-ab"},
        }

        # Find by content scan (filename doesn't match)
        result = find_vcf_by_uid("actual-uid-123", test_config)
        assert result is not None
        assert result[1] == "TestAB"

        # Find where filename matches
        result2 = find_vcf_by_uid("match-uid", test_config)
        assert result2 is not None

        # Missing UID
        result3 = find_vcf_by_uid("nonexistent-uid", test_config)
        assert result3 is None

    print("All tests passed!")


# --- CLI ---

def build_parser():
    parser = argparse.ArgumentParser(
        prog="icloud.py",
        description="Unified iCloud Calendar + Email CLI for OpenClaw",
    )
    parser.add_argument("--test", action="store_true", help="Run self-tests")
    subparsers = parser.add_subparsers(dest="command")

    # Calendar
    cal_parser = subparsers.add_parser("calendar", help="Calendar operations")
    cal_sub = cal_parser.add_subparsers(dest="cal_command")

    cal_list = cal_sub.add_parser("list", help="List upcoming events")
    cal_list.add_argument("--days", type=int, help="Number of days (default: 1)")
    cal_list.add_argument("--calendar", help="Filter by calendar name")

    cal_search = cal_sub.add_parser("search", help="Search events")
    cal_search.add_argument("query", help="Search query")

    cal_create = cal_sub.add_parser("create", help="Create a timed event")
    cal_create.add_argument("calendar", help="Calendar name")
    cal_create.add_argument("date", help="Date (YYYY-MM-DD)")
    cal_create.add_argument("start", help="Start time (HH:MM)")
    cal_create.add_argument("end", help="End time (HH:MM)")
    cal_create.add_argument("title", help="Event title")
    cal_create.add_argument("--location", help="Event location")
    cal_create.add_argument("--description", help="Event description")

    cal_allday = cal_sub.add_parser("create-allday", help="Create an all-day event")
    cal_allday.add_argument("calendar", help="Calendar name")
    cal_allday.add_argument("date", help="Date (YYYY-MM-DD)")
    cal_allday.add_argument("title", help="Event title")
    cal_allday.add_argument("--description", help="Event description")

    cal_delete = cal_sub.add_parser("delete", help="Delete event by UID")
    cal_delete.add_argument("uid", help="Event UID")

    cal_sub.add_parser("sync", help="Manual sync with iCloud")

    cal_disable = cal_sub.add_parser("disable", help="Disable a calendar from listings")
    cal_disable.add_argument("name", help="Calendar name to disable")

    cal_enable = cal_sub.add_parser("enable", help="Re-enable a disabled calendar")
    cal_enable.add_argument("name", help="Calendar name to enable")

    cal_sub.add_parser("refresh", help="Re-discover calendars via CalDAV PROPFIND")

    # Email
    email_parser = subparsers.add_parser("email", help="Email operations")
    email_sub = email_parser.add_subparsers(dest="email_command")

    email_list = email_sub.add_parser("list", help="List emails")
    email_list.add_argument("--count", type=int, help="Number of emails (default: 10)")
    email_list.add_argument("--folder", help="Folder name")
    email_list.add_argument("--query", help="Search query")
    email_list.add_argument("--unread", action="store_true", help="Only unread")

    email_read = email_sub.add_parser("read", help="Read an email")
    email_read.add_argument("id", help="Email ID")
    email_read.add_argument("--folder", help="Folder containing the message (default: INBOX)")

    email_send = email_sub.add_parser("send", help="Send an email")
    email_send.add_argument("to", help="Recipient email")
    email_send.add_argument("subject", help="Email subject")
    email_send.add_argument("body", help="Email body")

    email_reply = email_sub.add_parser("reply", help="Reply to an email")
    email_reply.add_argument("id", help="Email ID to reply to")
    email_reply.add_argument("body", help="Reply body")
    email_reply.add_argument("--all", action="store_true", help="Reply to all recipients")
    email_reply.add_argument("--folder", help="Folder containing the message (default: INBOX)")

    email_search = email_sub.add_parser("search", help="Search emails")
    email_search.add_argument("query", help="Search query")
    email_search.add_argument("--folder", help="Folder to search (default: INBOX)")

    email_move = email_sub.add_parser("move", help="Move email to folder")
    email_move.add_argument("folder", help="Destination folder")
    email_move.add_argument("id", help="Email ID")
    email_move.add_argument("--source", help="Source folder (default: INBOX)")

    email_delete = email_sub.add_parser("delete", help="Delete email (move to Trash)")
    email_delete.add_argument("id", help="Email ID")
    email_delete.add_argument("--folder", help="Folder containing the message (default: INBOX)")

    # Folder
    folder_parser = subparsers.add_parser("folder", help="Folder operations")
    folder_sub = folder_parser.add_subparsers(dest="folder_command")

    folder_purge = folder_sub.add_parser("purge", help="Purge all emails from a folder")
    folder_purge.add_argument("folder", help="Folder to purge")

    # Contact
    contact_parser = subparsers.add_parser("contact", help="Contact operations")
    contact_sub = contact_parser.add_subparsers(dest="contact_command")

    contact_list = contact_sub.add_parser("list", help="List contacts")
    contact_list.add_argument("--addressbook", help="Filter by address book")
    contact_list.add_argument("--count", type=int, help="Limit number of results")

    contact_show = contact_sub.add_parser("show", help="Show contact details")
    contact_show.add_argument("query", help="Contact UID or search term")

    contact_search = contact_sub.add_parser("search", help="Search contacts")
    contact_search.add_argument("query", help="Search query")

    contact_create = contact_sub.add_parser("create", help="Create a contact")
    contact_create.add_argument("first", nargs="?", help="First name")
    contact_create.add_argument("last", nargs="?", help="Last name")
    contact_create.add_argument("--fn", help="Full name override (for org-only contacts)")
    contact_create.add_argument("--email", action="append", help="Email address (repeatable)")
    contact_create.add_argument("--phone", action="append", help="Phone number (repeatable)")
    contact_create.add_argument("--org", help="Organization")
    contact_create.add_argument("--title", help="Job title")
    contact_create.add_argument("--note", help="Note")
    contact_create.add_argument("--nickname", help="Nickname")
    contact_create.add_argument("--birthday", help="Birthday (YYYY-MM-DD)")
    contact_create.add_argument("--category", action="append", help="Category (repeatable)")
    contact_create.add_argument("--addressbook", help="Address book name")

    contact_edit = contact_sub.add_parser("edit", help="Edit a contact")
    contact_edit.add_argument("uid", help="Contact UID")
    contact_edit.add_argument("--first", help="First name")
    contact_edit.add_argument("--last", help="Last name")
    contact_edit.add_argument("--fn", help="Full name override")
    contact_edit.add_argument("--email", action="append", help="Replace all emails (repeatable)")
    contact_edit.add_argument("--phone", action="append", help="Replace all phones (repeatable)")
    contact_edit.add_argument("--add-email", action="append", help="Add email (repeatable)")
    contact_edit.add_argument("--remove-email", action="append", help="Remove email (repeatable)")
    contact_edit.add_argument("--add-phone", action="append", help="Add phone (repeatable)")
    contact_edit.add_argument("--remove-phone", action="append", help="Remove phone (repeatable)")
    contact_edit.add_argument("--org", help="Organization")
    contact_edit.add_argument("--title", help="Job title")
    contact_edit.add_argument("--note", help="Note")
    contact_edit.add_argument("--nickname", help="Nickname")
    contact_edit.add_argument("--birthday", help="Birthday (YYYY-MM-DD)")

    contact_delete = contact_sub.add_parser("delete", help="Delete a contact")
    contact_delete.add_argument("uid", help="Contact UID")

    contact_sub.add_parser("sync", help="Manual sync with iCloud")

    # Setup
    setup_parser = subparsers.add_parser("setup", help="Setup utilities")
    setup_sub = setup_parser.add_subparsers(dest="setup_command")
    setup_sub.add_parser("discover-calendars", help="Discover and map calendars")
    setup_sub.add_parser("init", help="Interactive setup wizard")

    setup_configure = setup_sub.add_parser("configure", help="Configure credentials and discover calendars")
    setup_configure.add_argument("--email", required=True, help="Sending address (From header)")
    setup_configure.add_argument("--apple-id", help="Apple ID for iCloud auth (defaults to --email)")
    setup_configure.add_argument("--name", required=True, help="Display name for sent emails")
    setup_configure.add_argument("--timezone", help="IANA timezone (auto-detected if omitted)")

    setup_finalize = setup_sub.add_parser("finalize", help="Write config files after calendar mapping")
    setup_finalize.add_argument("--email", required=True, help="Sending address (From header)")
    setup_finalize.add_argument("--apple-id", help="Apple ID for iCloud auth (defaults to --email)")
    setup_finalize.add_argument("--name", required=True, help="Display name for sent emails")
    setup_finalize.add_argument("--timezone", required=True, help="IANA timezone")
    setup_finalize.add_argument("--calendars", help='JSON mapping (optional — auto-discovered via PROPFIND if omitted)')
    setup_finalize.add_argument("--default", required=True, help="Default calendar name")
    setup_finalize.add_argument("--addressbooks", help='JSON mapping: \'{"Name": "dir_id", ...}\'')
    setup_finalize.add_argument("--default-addressbook", help="Default address book name")
    setup_finalize.add_argument("--subscribed-calendars", help='JSON mapping: \'{"Name": "dir_id", ...}\'')

    setup_sub.add_parser("verify", help="Run verification against current config")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.test:
        run_self_test()
        return

    if not args.command:
        parser.print_help()
        return

    script_dir = Path(__file__).resolve().parent
    config_path = script_dir.parent / "config" / "config.json"

    if args.command == "setup":
        setup_cmd = getattr(args, "setup_command", None)
        if not setup_cmd:
            print("Usage: icloud.py setup {init|configure|finalize|verify|discover-calendars}")
            return

        if setup_cmd == "init":
            from setup import setup_wizard
            setup_wizard(script_dir)
            return
        elif setup_cmd == "configure":
            from setup import cmd_setup_configure
            cmd_setup_configure(args, script_dir)
            return
        elif setup_cmd == "finalize":
            from setup import cmd_setup_finalize
            cmd_setup_finalize(args, script_dir)
            return
        elif setup_cmd == "verify":
            from setup import cmd_setup_verify
            cmd_setup_verify(args, script_dir)
            return

    if not config_path.exists():
        print("SETUP_REQUIRED")
        print("This skill needs to be configured before use.")
        print("Run: setup init (interactive) or follow the First-Time Setup instructions in SKILL.md")
        sys.exit(1)

    config = load_config()

    if args.command == "calendar":
        if not args.cal_command:
            print("Usage: icloud.py calendar {list|search|create|create-allday|delete|sync|enable|disable|refresh}")
            return
        handlers = {
            "create": cmd_calendar_create,
            "create-allday": cmd_calendar_create_allday,
            "list": cmd_calendar_list,
            "search": cmd_calendar_search,
            "delete": cmd_calendar_delete,
            "sync": cmd_calendar_sync,
            "disable": cmd_calendar_disable,
            "enable": cmd_calendar_enable,
            "refresh": cmd_calendar_refresh,
        }
        handlers[args.cal_command](args, config)

    elif args.command == "email":
        if not args.email_command:
            print("Usage: icloud.py email {list|read|send|reply|search|move|delete}")
            return
        handlers = {
            "list": cmd_email_list,
            "read": cmd_email_read,
            "send": cmd_email_send,
            "reply": cmd_email_reply,
            "search": cmd_email_search,
            "move": cmd_email_move,
            "delete": cmd_email_delete,
        }
        handlers[args.email_command](args, config)

    elif args.command == "contact":
        if not getattr(args, "contact_command", None):
            print("Usage: icloud.py contact {list|show|search|create|edit|delete|sync}")
            return
        handlers = {
            "list": cmd_contact_list,
            "show": cmd_contact_show,
            "search": cmd_contact_search,
            "sync": cmd_contact_sync,
            "create": cmd_contact_create,
            "delete": cmd_contact_delete,
            "edit": cmd_contact_edit,
        }
        handlers[args.contact_command](args, config)

    elif args.command == "folder":
        if not getattr(args, "folder_command", None):
            print("Usage: icloud.py folder {purge}")
            return
        if args.folder_command == "purge":
            cmd_folder_purge(args, config)

    elif args.command == "setup":
        if args.setup_command == "discover-calendars":
            cmd_setup_discover(args, config)


if __name__ == "__main__":
    main()
