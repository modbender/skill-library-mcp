#!/usr/bin/env python3
"""
applecal.py — Pro Apple Calendar CLI via CalDAV (RFC 4791, 8607)
Part of the apple-calendar-pro OpenClaw skill.

Features:
- Event CRUD (List, Create, Update, Delete)
- RFC 8607 Managed Attachments (iPhone/iPad compatible)
- Free/Busy lookup (CalDAV scheduling + event-derived fallback)
- Keychain-based auth (no plaintext passwords)
- JSON-stable output for easy agent consumption

Requirements:
    pip3 install requests

Usage:
    python3 applecal.py --apple-id your@icloud.com <command> [options]

Run 'python3 applecal.py --help' for full usage.
"""

import argparse
import json
import logging
import mimetypes
import os
import re
import subprocess
import sys
import uuid
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional
from urllib.parse import quote, urljoin, urlparse

try:
    import requests
    from requests.auth import HTTPBasicAuth
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
except ImportError:
    print(json.dumps({"error": "Missing dependency: requests. Run 'pip3 install requests'"}))
    sys.exit(1)

__version__ = "1.1.1"
PRODID = "-//OpenClaw//AppleCalPro 1.1.1//EN"
UID_SAFE_RE = re.compile(r"^[A-Za-z0-9._@:+-]{1,255}$")
MANAGED_ID_SAFE_RE = re.compile(r"^[A-Za-z0-9._:+-]{1,255}$")

ALLOWED_ATTACHMENT_EXTENSIONS = {
    ".pdf", ".txt", ".md", ".csv", ".tsv", ".json",
    ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    ".rtf", ".odt", ".ods", ".odp",
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".heic", ".heif",
    ".mp3", ".wav", ".m4a", ".mp4", ".mov",
    ".zip",
}

SENSITIVE_DIR_SEGMENTS = {
    ".ssh", ".gnupg", ".aws", ".azure", ".kube", ".config", "keychains",
}

SENSITIVE_NAME_PATTERNS = [
    r"^\.env($|\.)",
    r"(^|[_\-.])credentials?([_\-.]|$)",
    r"(^|[_\-.])secret(s)?([_\-.]|$)",
    r"(^|[_\-.])token(s)?([_\-.]|$)",
    r"(^|[_\-.])keychain([_\-.]|$)",
    r"^id_(rsa|ed25519|ecdsa)(\.pub)?$",
    r"\.(pem|key|p12|pfx|p8)$",
]

# --- Logging ---
logger = logging.getLogger("applecal")

# --- Constants & Namespaces ---
ICLOUD_WELL_KNOWN = "https://caldav.icloud.com/.well-known/caldav"
DEFAULT_TIMEOUT = 30  # seconds
MAX_RETRIES = 3

NS = {
    "d": "DAV:",
    "cal": "urn:ietf:params:xml:ns:caldav",
    "cs": "http://calendarserver.org/ns/",
    "apple": "http://apple.com/ns/ical/",
}

# Register namespaces for ET
for prefix, uri in NS.items():
    ET.register_namespace(prefix, uri)

# --- Utility Functions ---

class JSONArgumentParser(argparse.ArgumentParser):
    """ArgumentParser that always emits JSON errors."""

    def error(self, message):
        raise ValueError(message)


def _json_error(message: str, indent: Optional[int] = None) -> None:
    print(json.dumps({"error": message}, indent=indent, sort_keys=True))


def require_non_empty(value: Optional[str], field_name: str) -> str:
    if value is None:
        raise ValueError(f"{field_name} is required")
    clean = value.strip()
    if not clean:
        raise ValueError(f"{field_name} must not be empty")
    return clean


def validate_uid(uid: str) -> str:
    clean = require_non_empty(uid, "uid")
    if not UID_SAFE_RE.fullmatch(clean):
        raise ValueError("Invalid UID format")
    return clean


def validate_managed_id(managed_id: str) -> str:
    clean = require_non_empty(managed_id, "managed-id")
    if not MANAGED_ID_SAFE_RE.fullmatch(clean):
        raise ValueError("Invalid managed-id format")
    return clean


def validate_time_range(start_value: str, end_value: str, *, all_day: bool = False) -> None:
    if all_day:
        start_date = datetime.strptime(iso_to_caldav_date(start_value), "%Y%m%d")
        end_date = datetime.strptime(iso_to_caldav_date(end_value), "%Y%m%d")
    else:
        start_date = parse_iso_datetime(start_value)
        end_date = parse_iso_datetime(end_value)
        if not start_date or not end_date:
            raise ValueError("Invalid datetime format. Use ISO 8601 (e.g. 2026-03-05T09:00:00Z)")

    if all_day:
        if end_date < start_date:
            raise ValueError("--to/--end must be same day or later for all-day events")
    elif end_date <= start_date:
        raise ValueError("--to/--end must be later than --from/--start")


def escape_ical_text(value: Optional[str]) -> str:
    if value is None:
        return ""
    escaped = value.replace("\\", "\\\\")
    escaped = escaped.replace("\r\n", "\\n").replace("\n", "\\n").replace("\r", "\\n")
    escaped = escaped.replace(";", "\\;").replace(",", "\\,")
    return escaped


def unescape_ical_text(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    return re.sub(r"\\([\\;,])", r"\1", value.replace("\\n", "\n").replace("\\N", "\n"))


def fold_ical_line(line: str, limit: int = 75) -> list[str]:
    if len(line.encode("utf-8")) <= limit:
        return [line]

    chunks = []
    current_chars = []
    current_len = 0

    for ch in line:
        ch_len = len(ch.encode("utf-8"))
        if current_chars and current_len + ch_len > limit:
            chunks.append("".join(current_chars))
            current_chars = [ch]
            current_len = ch_len
        else:
            current_chars.append(ch)
            current_len += ch_len

    if current_chars:
        chunks.append("".join(current_chars))

    folded = [chunks[0]]
    for chunk in chunks[1:]:
        folded.append(f" {chunk}")
    return folded


def build_ical_text(lines: list[str]) -> str:
    folded = []
    for line in lines:
        folded.extend(fold_ical_line(line))
    return "\r\n".join(folded) + "\r\n"


def build_content_disposition_filename(filename: str) -> str:
    """Build a safe Content-Disposition value supporting non-ASCII filenames."""
    clean = filename.replace("\r", "_").replace("\n", "_").replace('"', "'").strip() or "attachment"
    encoded = quote(clean, safe="")
    return f"attachment; filename=\"{clean}\"; filename*=UTF-8''{encoded}"


def resolve_attachment_path(file_path: str) -> Path:
    """Resolve and validate attachment path against extension, sensitivity, and optional base-dir rules."""
    clean_path = require_non_empty(file_path, "file")
    try:
        path = Path(clean_path).expanduser().resolve(strict=True)
    except FileNotFoundError:
        raise ValueError(f"Attachment file not found: {clean_path}")

    if not path.is_file():
        raise ValueError(f"Attachment file not found: {clean_path}")

    suffix = path.suffix.lower()
    if suffix not in ALLOWED_ATTACHMENT_EXTENSIONS:
        allowed = ", ".join(sorted(ALLOWED_ATTACHMENT_EXTENSIONS))
        raise ValueError(f"Blocked attachment type '{suffix or '[none]'}'. Allowed extensions: {allowed}")

    lowered_parts = {part.lower() for part in path.parts}
    if lowered_parts & SENSITIVE_DIR_SEGMENTS:
        raise ValueError("Blocked sensitive file path")

    name = path.name.lower()
    if any(re.search(pattern, name) for pattern in SENSITIVE_NAME_PATTERNS):
        raise ValueError("Blocked sensitive file name")

    safe_root_raw = os.environ.get("APPLECAL_ATTACH_DIR", "").strip()
    if safe_root_raw:
        try:
            safe_root = Path(safe_root_raw).expanduser().resolve(strict=True)
        except FileNotFoundError:
            raise ValueError("APPLECAL_ATTACH_DIR does not exist")
        try:
            path.relative_to(safe_root)
        except ValueError:
            raise ValueError(f"Attachment must be inside APPLECAL_ATTACH_DIR: {safe_root}")

    return path


def get_keychain_password(server: str, account: str) -> str:
    """Retrieve iCloud CalDAV password.

    Resolution order:
    1. APPLECAL_PASSWORD environment variable (cross-platform)
    2. macOS Keychain (macOS only)

    To set via environment variable:
        export APPLECAL_PASSWORD="your-app-specific-password"

    To set via macOS Keychain:
        security add-internet-password -s 'caldav.icloud.com' -a 'you@icloud.com' -w 'your-app-specific-password'
    """
    # 1. Check environment variable first (cross-platform)
    env_password = os.environ.get("APPLECAL_PASSWORD", "").strip()
    if env_password:
        logger.debug("Auth: using APPLECAL_PASSWORD environment variable")
        return env_password

    # 2. Optional keyring backend (Linux/Windows/macOS)
    try:
        import keyring  # type: ignore

        keyring_password = keyring.get_password(server, account)
        if keyring_password:
            logger.debug("Auth: using keyring backend")
            return keyring_password.strip()
    except Exception:
        # keyring is optional; continue to platform-specific fallback
        pass

    # 3. Fall back to macOS Keychain
    if sys.platform != "darwin":
        raise RuntimeError(
            "No password found. Set APPLECAL_PASSWORD (recommended), or install/configure python keyring.\n"
            "  export APPLECAL_PASSWORD='your-app-specific-password'\n"
            "Generate an app-specific password at: https://appleid.apple.com"
        )

    try:
        result = subprocess.run(
            ["security", "find-internet-password", "-s", server, "-a", account, "-w"],
            capture_output=True, text=True, timeout=10
        )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError("Timed out while reading password from macOS Keychain") from exc

    if result.returncode != 0:
        raise RuntimeError(
            f"Keychain entry not found for {account}@{server}.\n"
            f"Option 1 — Environment variable (cross-platform):\n"
            f"  export APPLECAL_PASSWORD='your-app-specific-password'\n"
            f"Option 2 — macOS Keychain:\n"
            f"  security add-internet-password -s '{server}' -a '{account}' -w 'YOUR_APP_SPECIFIC_PASSWORD'\n"
            f"Generate an app-specific password at: https://appleid.apple.com"
        )
    logger.debug("Auth: using macOS Keychain")
    return result.stdout.strip()

def parse_xml(text):
    try:
        return ET.fromstring(text)
    except ET.ParseError as e:
        raise ValueError(f"Invalid XML response from CalDAV server: {e}") from e

def get_href(element):
    if element is None:
        return None
    h = element.find(".//{DAV:}href")
    if h is None or not h.text:
        return None
    return h.text.strip()

def iso_to_caldav(iso_str):
    """Convert ISO 8601 to CalDAV UTC format YYYYMMDDTHHMMSSZ."""
    dt = parse_iso_datetime(iso_str)
    if dt is None:
        raise ValueError(f"Invalid datetime format: {iso_str}")
    return dt.strftime("%Y%m%dT%H%M%SZ")

def caldav_to_iso(cal_str):
    """Convert CalDAV UTC format YYYYMMDDTHHMMSSZ to ISO 8601."""
    if not cal_str: return None
    clean = re.sub(r'[^0-9T]', '', cal_str)
    try:
        dt = datetime.strptime(clean, "%Y%m%dT%H%M%S")
        return dt.replace(tzinfo=timezone.utc).isoformat()
    except Exception:
        return cal_str

def parse_iso_datetime(value):
    """Robust ISO 8601 parser with UTC normalization."""
    if not value: return None
    if re.fullmatch(r"\d{8}", value):
        return datetime.strptime(value, "%Y%m%d").replace(tzinfo=timezone.utc)
    # Handle Z and offset
    clean = value.replace('Z', '+00:00')
    try:
        dt = datetime.fromisoformat(clean)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        return None

def clip_to_range(start_dt, end_dt, query_start, query_end):
    """Clip a time range to within query bounds. Returns None if no overlap."""
    clipped_start = max(start_dt, query_start)
    clipped_end = min(end_dt, query_end)
    if clipped_start >= clipped_end:
        return None
    return {"start": clipped_start.isoformat(), "end": clipped_end.isoformat()}

def unfold_ics_lines(ics_text):
    lines = []
    for line in ics_text.splitlines():
        if line.startswith(" ") or line.startswith("\t"):
            if lines:
                lines[-1] += line[1:]
        else:
            lines.append(line)
    return lines


def parse_ics_simple(ics_text):
    """Very basic ICS parser for common fields. Supports folded lines."""
    data = {}
    current_vevent = False
    for line in unfold_ics_lines(ics_text):
        if line == "BEGIN:VEVENT":
            current_vevent = True
            continue
        if line == "END:VEVENT":
            current_vevent = False
            continue

        if current_vevent and ":" in line:
            key_part, val = line.split(":", 1)
            key = key_part.split(";")[0]
            data[key] = unescape_ical_text(val)
    return data


def parse_ics_event(ics_text):
    parsed = parse_ics_simple(ics_text)
    lines = unfold_ics_lines(ics_text)
    start_raw = None
    end_raw = None
    start_is_all_day = False
    end_is_all_day = False

    in_event = False
    for line in lines:
        if line == "BEGIN:VEVENT":
            in_event = True
            continue
        if line == "END:VEVENT":
            in_event = False
            continue
        if not in_event or ":" not in line:
            continue

        key_part, val = line.split(":", 1)
        key_upper = key_part.upper()
        if key_upper.startswith("DTSTART"):
            start_raw = val
            if "VALUE=DATE" in key_upper:
                start_is_all_day = True
        elif key_upper.startswith("DTEND"):
            end_raw = val
            if "VALUE=DATE" in key_upper:
                end_is_all_day = True

    start_val = start_raw if start_raw is not None else parsed.get("DTSTART")
    end_val = end_raw if end_raw is not None else parsed.get("DTEND")
    is_all_day = start_is_all_day or end_is_all_day

    if is_all_day:
        start_iso = caldav_date_to_iso(start_val)
        end_iso = caldav_date_to_iso(end_val)
    else:
        start_iso = caldav_to_iso(start_val)
        end_iso = caldav_to_iso(end_val)

    return {
        "uid": parsed.get("UID"),
        "summary": parsed.get("SUMMARY"),
        "start": start_iso,
        "end": end_iso,
        "location": parsed.get("LOCATION"),
        "description": parsed.get("DESCRIPTION"),
        "status": parsed.get("STATUS"),
        "all_day": is_all_day,
    }


def caldav_date_to_iso(cal_str):
    if not cal_str:
        return None
    clean = re.sub(r"[^0-9]", "", cal_str)
    try:
        dt = datetime.strptime(clean, "%Y%m%d")
        return dt.date().isoformat()
    except Exception:
        return cal_str


def iso_to_caldav_date(date_str):
    if not date_str:
        raise ValueError("Date value is required for all-day events")
    value = date_str.strip()
    if re.fullmatch(r"\d{8}", value):
        return value
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return datetime.strptime(value, "%Y-%m-%d").strftime("%Y%m%d")

    dt = parse_iso_datetime(value)
    if not dt:
        raise ValueError(f"Invalid date format for all-day event: {date_str}")
    return dt.strftime("%Y%m%d")


def normalize_all_day_range(start_value, end_value):
    start_date = datetime.strptime(iso_to_caldav_date(start_value), "%Y%m%d")
    end_date = datetime.strptime(iso_to_caldav_date(end_value), "%Y%m%d")

    if end_date <= start_date:
        end_date = start_date + timedelta(days=1)

    return start_date.strftime("%Y%m%d"), end_date.strftime("%Y%m%d")

# --- CalDAV Client Class ---

class AppleCalClient:
    """CalDAV client for Apple Calendar / iCloud."""

    def __init__(self, apple_id: str, user_agent: str = f"AppleCalPro/{__version__}"):
        if not apple_id or "@" not in apple_id:
            raise ValueError("Invalid Apple ID — must be a valid email address (e.g. your@icloud.com)")
        self.apple_id = apple_id
        self.password = get_keychain_password("caldav.icloud.com", apple_id)
        self.session = requests.Session()
        self.session.auth = HTTPBasicAuth(self.apple_id, self.password)
        self.session.headers.update({"User-Agent": user_agent, "Content-Type": "application/xml"})

        # Retry on transient network errors (prefer idempotent methods to avoid duplicate writes)
        retry = Retry(
            total=MAX_RETRIES,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["GET", "HEAD", "OPTIONS", "PROPFIND", "REPORT"],
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

        self.principal_url = None
        self.home_url = None
        self.outbox_url = None
        self.user_addresses = []
        self._discover()

    def _request(self, method: str, url: str, **kwargs) -> requests.Response:
        """Wrapper around session.request with default timeout."""
        kwargs.setdefault("timeout", DEFAULT_TIMEOUT)
        logger.debug("%s %s", method, url)
        resp = self.session.request(method, url, **kwargs)
        logger.debug("→ %s", resp.status_code)
        return resp

    def _discover(self):
        # 1. Principal
        resp = self._request("PROPFIND", ICLOUD_WELL_KNOWN, headers={"Depth": "0"},
                             data='<?xml version="1.0"?><d:propfind xmlns:d="DAV:"><d:prop><d:current-user-principal/></d:prop></d:propfind>')
        resp.raise_for_status()
        root = parse_xml(resp.text)
        href = get_href(root)
        if not href:
            raise RuntimeError("Discovery failed: missing current-user-principal href")
        parsed = urlparse(resp.url)
        server_root = f"{parsed.scheme}://{parsed.netloc}"
        self.principal_url = href if href.startswith("http") else urljoin(server_root, href)

        # 2. Calendar Home, Outbox, and User Addresses
        body = '''<?xml version="1.0"?>
<d:propfind xmlns:d="DAV:" xmlns:c="urn:ietf:params:xml:ns:caldav">
    <d:prop>
        <c:calendar-home-set/>
        <c:schedule-outbox-URL/>
        <c:calendar-user-address-set/>
    </d:prop>
</d:propfind>'''
        resp = self._request("PROPFIND", self.principal_url, headers={"Depth": "0"}, data=body)
        resp.raise_for_status()
        root = parse_xml(resp.text)
        
        # Home
        home_el = root.find(".//{urn:ietf:params:xml:ns:caldav}calendar-home-set")
        home_href = get_href(home_el)
        if not home_href:
            raise RuntimeError("Discovery failed: missing calendar-home-set href")
        self.home_url = home_href if home_href.startswith("http") else urljoin(server_root, home_href)
        
        # Outbox
        outbox_el = root.find(".//{urn:ietf:params:xml:ns:caldav}schedule-outbox-URL")
        outbox_href = get_href(outbox_el)
        if outbox_href:
            # For iCloud, use the server from home_url for the outbox if it's relative or on caldav.icloud.com
            home_parsed = urlparse(self.home_url)
            home_server = f"{home_parsed.scheme}://{home_parsed.netloc}"
            self.outbox_url = outbox_href if outbox_href.startswith("http") else urljoin(home_server, outbox_href)
            
        # User Addresses
        addr_el = root.find(".//{urn:ietf:params:xml:ns:caldav}calendar-user-address-set")
        if addr_el is not None:
            for href_el in addr_el.findall("{DAV:}href"):
                self.user_addresses.append(href_el.text)

    def list_calendars(self):
        body = '<?xml version="1.0"?><d:propfind xmlns:d="DAV:" xmlns:c="urn:ietf:params:xml:ns:caldav"><d:prop><d:displayname/><c:supported-calendar-component-set/></d:prop></d:propfind>'
        resp = self._request("PROPFIND", self.home_url, headers={"Depth": "1"}, data=body)
        resp.raise_for_status()
        root = parse_xml(resp.text)
        parsed = urlparse(self.home_url)
        server_root = f"{parsed.scheme}://{parsed.netloc}"
        
        cals = []
        for response in root.findall("{DAV:}response"):
            href = get_href(response)
            name_el = response.find(".//{DAV:}displayname")
            comps = response.findall(".//{urn:ietf:params:xml:ns:caldav}comp")
            is_cal = any(c.get("name") == "VEVENT" for c in comps)
            if is_cal and name_el is not None:
                cals.append({
                    "name": name_el.text,
                    "url": href if href.startswith("http") else urljoin(server_root, href)
                })
        return cals

    def get_calendar_url(self, name):
        cals = self.list_calendars()
        for c in cals:
            if c["name"] and c["name"].lower() == name.lower():
                return c["url"]
        raise ValueError(f"Calendar '{name}' not found.")

    def list_events(self, calendar_url, start_iso, end_iso, query=None, max_items=None):
        start = iso_to_caldav(start_iso)
        end = iso_to_caldav(end_iso)

        body = f'''<?xml version="1.0" encoding="utf-8" ?>
<c:calendar-query xmlns:d="DAV:" xmlns:c="urn:ietf:params:xml:ns:caldav">
    <d:prop>
        <d:getetag />
        <c:calendar-data />
    </d:prop>
    <c:filter>
        <c:comp-filter name="VCALENDAR">
            <c:comp-filter name="VEVENT">
                <c:time-range start="{start}" end="{end}"/>
            </c:comp-filter>
        </c:comp-filter>
    </c:filter>
</c:calendar-query>'''
        resp = self._request("REPORT", calendar_url, headers={"Depth": "1"}, data=body)
        resp.raise_for_status()
        root = parse_xml(resp.text)

        events = []
        for response in root.findall("{DAV:}response"):
            data_el = response.find(".//{urn:ietf:params:xml:ns:caldav}calendar-data")
            if data_el is not None and data_el.text:
                ev = parse_ics_event(data_el.text)
                ev["url"] = get_href(response)
                events.append(ev)

        if query:
            q = query.lower()
            events = [
                e for e in events
                if q in (e.get("summary") or "").lower()
                or q in (e.get("location") or "").lower()
                or q in (e.get("description") or "").lower()
            ]

        events.sort(key=lambda e: (e.get("start") or "", e.get("uid") or ""))
        if max_items is not None:
            if max_items < 0:
                raise ValueError("--max must be >= 0")
            events = events[:max_items]

        return events

    def list_events_multi(self, calendar_names, start_iso, end_iso, query=None, max_items=None):
        if not calendar_names:
            raise ValueError("At least one --calendar must be provided")

        combined_events = []
        for cal_name in calendar_names:
            try:
                cal_url = self.get_calendar_url(cal_name)
                per_calendar_max = max_items if len(calendar_names) == 1 else None
                events = self.list_events(cal_url, start_iso, end_iso, query=query, max_items=per_calendar_max)
                for e in events:
                    e["calendar"] = cal_name
                combined_events.extend(events)
            except Exception as e:
                # Log error for specific calendar but continue
                combined_events.append({"calendar": cal_name, "error": str(e)})

        combined_events.sort(key=lambda e: (e.get("start") or "", e.get("uid") or ""))

        if max_items is not None:
            if max_items < 0:
                raise ValueError("--max must be >= 0")
            combined_events = combined_events[:max_items]

        return combined_events

    def _mail_addresses(self):
        mailto_addrs = [a for a in self.user_addresses if isinstance(a, str) and a.lower().startswith("mailto:")]
        if not mailto_addrs:
            return [f"mailto:{self.apple_id}"]
        primary = f"mailto:{self.apple_id}".lower()
        ordered = [a for a in mailto_addrs if a.lower() == primary]
        ordered += [a for a in mailto_addrs if a.lower() != primary]
        return ordered

    def _build_freebusy_payload(self, start, end, user_addr):
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        vfb = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            f"PRODID:{PRODID}",
            "METHOD:REQUEST",
            "BEGIN:VFREEBUSY",
            f"UID:{uuid.uuid4()}",
            f"DTSTAMP:{stamp}",
            f"DTSTART:{start}",
            f"DTEND:{end}",
            f"ORGANIZER;CN=AppleCalPro:{user_addr}",
            f"ATTENDEE;CN=AppleCalPro;CUTYPE=INDIVIDUAL;PARTSTAT=NEEDS-ACTION;RSVP=TRUE:{user_addr}",
            "END:VFREEBUSY",
            "END:VCALENDAR"
        ]
        return "\r\n".join(vfb)

    def _outbox_headers(self, user_addr):
        return {
            "Content-Type": "text/calendar; charset=utf-8",
            "Originator": user_addr,
            "Recipient": user_addr,
        }

    def get_event(self, calendar_url, uid):
        # Try direct access by UID
        event_url = urljoin(calendar_url, f"{uid}.ics")
        resp = self._request("GET", event_url)
        if resp.status_code == 200:
            return {"url": event_url, "ics": resp.text, "etag": resp.headers.get("ETag")}
        
        # Fallback search
        body = f'''<?xml version="1.0" encoding="utf-8" ?>
<c:calendar-query xmlns:d="DAV:" xmlns:c="urn:ietf:params:xml:ns:caldav">
    <d:prop><d:getetag /><c:calendar-data /></d:prop>
    <c:filter>
        <c:comp-filter name="VCALENDAR">
            <c:comp-filter name="VEVENT">
                <c:prop-filter name="UID">
                    <c:text-match collation="i;octet">{uid}</c:text-match>
                </c:prop-filter>
            </c:comp-filter>
        </c:comp-filter>
    </c:filter>
</c:calendar-query>'''
        resp = self._request("REPORT", calendar_url, headers={"Depth": "1"}, data=body)
        resp.raise_for_status()
        root = parse_xml(resp.text)
        response = root.find("{DAV:}response")
        if response is not None:
            data_el = response.find(".//{urn:ietf:params:xml:ns:caldav}calendar-data")
            etag_el = response.find(".//{DAV:}getetag")
            return {
                "url": get_href(response),
                "ics": data_el.text if data_el is not None else None,
                "etag": etag_el.text if etag_el is not None else None
            }
        return None

    def get_event_details(self, calendar_url, uid):
        event = self.get_event(calendar_url, uid)
        if not event:
            return None
        parsed = parse_ics_event(event["ics"] or "")
        parsed["etag"] = event.get("etag")
        parsed["url"] = event.get("url")
        return parsed

    def _build_dt_fields(self, start_value, end_value, all_day=False):
        if all_day:
            s, e = normalize_all_day_range(start_value, end_value)
            return f"DTSTART;VALUE=DATE:{s}", f"DTEND;VALUE=DATE:{e}"
        return f"DTSTART:{iso_to_caldav(start_value)}", f"DTEND:{iso_to_caldav(end_value)}"

    def create_event(self, calendar_url, summary, start_iso, end_iso, location=None, description=None, all_day=False):
        uid = str(uuid.uuid4()).upper()
        start_line, end_line = self._build_dt_fields(start_iso, end_iso, all_day=all_day)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

        ics = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            f"PRODID:{PRODID}",
            "BEGIN:VEVENT",
            f"UID:{uid}",
            f"DTSTAMP:{stamp}",
            start_line,
            end_line,
            f"SUMMARY:{escape_ical_text(summary)}"
        ]
        if location:
            ics.append(f"LOCATION:{escape_ical_text(location)}")
        if description:
            ics.append(f"DESCRIPTION:{escape_ical_text(description)}")
        ics.extend(["END:VEVENT", "END:VCALENDAR"])
        
        ics_text = build_ical_text(ics)
        event_url = urljoin(calendar_url, f"{uid}.ics")
        resp = self._request("PUT", event_url, data=ics_text, headers={"Content-Type": "text/calendar; charset=utf-8"})
        resp.raise_for_status()
        return {"uid": uid, "url": event_url, "status": "created"}

    def update_event(
        self,
        calendar_url,
        uid,
        summary=None,
        start_iso=None,
        end_iso=None,
        location=None,
        description=None,
        all_day=None,
        clear_location=False,
        clear_description=False,
        ics_body=None,
    ):
        event = self.get_event(calendar_url, uid)
        if not event: raise ValueError(f"Event {uid} not found.")

        if ics_body:
            new_ics_text = ics_body
        else:
            ics_text = event["ics"]
            parsed = parse_ics_simple(ics_text)
            parsed_event = parse_ics_event(ics_text)

            new_summary = summary if summary is not None else parsed.get("SUMMARY", "")
            current_start = parsed_event.get("start")
            current_end = parsed_event.get("end")
            new_start_input = start_iso if start_iso is not None else current_start
            new_end_input = end_iso if end_iso is not None else current_end
            if clear_location and location is not None:
                raise ValueError("Use either --location or --clear-location, not both")
            if clear_description and description is not None:
                raise ValueError("Use either --description or --clear-description, not both")

            new_loc = None if clear_location else (location if location is not None else parsed.get("LOCATION"))
            new_desc = None if clear_description else (description if description is not None else parsed.get("DESCRIPTION"))
            new_all_day = parsed_event.get("all_day", False) if all_day is None else all_day

            if not new_start_input or not new_end_input:
                raise ValueError("Event start/end could not be determined for update")

            start_line, end_line = self._build_dt_fields(new_start_input, new_end_input, all_day=new_all_day)
            stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

            # Preserve VEVENT properties by patching only mutable fields.
            # This keeps RRULE/EXDATE/VALARM/ATTACH/CLASS/TRANSP/custom properties intact.
            updated_lines = []
            in_vevent = False
            replaced_fields_inserted = False
            replaceable_prefixes = ("DTSTART", "DTEND", "DTSTAMP", "SUMMARY", "LOCATION", "DESCRIPTION")

            def _insert_replaced_fields(target_lines):
                target_lines.append(f"DTSTAMP:{stamp}")
                target_lines.append(start_line)
                target_lines.append(end_line)
                target_lines.append(f"SUMMARY:{escape_ical_text(new_summary)}")
                if new_loc:
                    target_lines.append(f"LOCATION:{escape_ical_text(new_loc)}")
                if new_desc:
                    target_lines.append(f"DESCRIPTION:{escape_ical_text(new_desc)}")

            for line in unfold_ics_lines(ics_text):
                if line == "BEGIN:VEVENT":
                    in_vevent = True
                    replaced_fields_inserted = False
                    updated_lines.append(line)
                    _insert_replaced_fields(updated_lines)
                    replaced_fields_inserted = True
                    continue

                if line == "END:VEVENT":
                    if in_vevent and not replaced_fields_inserted:
                        _insert_replaced_fields(updated_lines)
                    in_vevent = False
                    updated_lines.append(line)
                    continue

                if in_vevent:
                    prop_name = line.split(":", 1)[0].split(";", 1)[0].upper()
                    if prop_name.startswith(replaceable_prefixes):
                        continue

                updated_lines.append(line)

            new_ics_text = build_ical_text(updated_lines)

        headers = {"Content-Type": "text/calendar; charset=utf-8"}
        if event["etag"]:
            headers["If-Match"] = event["etag"]
            
        resp = self._request("PUT", event["url"], data=new_ics_text, headers=headers)
        resp.raise_for_status()
        return {"uid": uid, "url": event["url"], "status": "updated"}

    def delete_event(self, calendar_url, uid):
        event = self.get_event(calendar_url, uid)
        if not event: raise ValueError(f"Event {uid} not found.")
        
        headers = {}
        if event["etag"]: headers["If-Match"] = event["etag"]
            
        resp = self._request("DELETE", event["url"], headers=headers)
        resp.raise_for_status()
        return {"uid": uid, "status": "deleted"}

    def freebusy(self, calendar_url, start_iso, end_iso):
        start = iso_to_caldav(start_iso)
        end = iso_to_caldav(end_iso)
        q_start = parse_iso_datetime(start_iso)
        q_end = parse_iso_datetime(end_iso)
        attempts = []

        # 1. Try Scheduling POST (RFC 6638)
        if self.outbox_url:
            for addr in self._mail_addresses():
                ics_body = self._build_freebusy_payload(start, end, addr)
                headers = self._outbox_headers(addr)
                try:
                    resp = self._request("POST", self.outbox_url, data=ics_body, headers=headers)
                    attempts.append({
                        "method": "outbox_post",
                        "url": self.outbox_url,
                        "httpStatus": resp.status_code,
                        "result": resp.text[:200] if resp.text else ""
                    })
                    if resp.status_code in (200, 201) and "FREEBUSY" in resp.text:
                        fb_res = self._parse_freebusy_ics(resp.text, "outbox_post")
                        fb_res["attempts"] = attempts
                        return fb_res
                    if resp.status_code != 403:
                        break # Only retry on 403
                except Exception as e:
                    attempts.append({"method": "outbox_post", "url": self.outbox_url, "error": str(e)})
                    break

        # 2. Try CalDAV REPORT (free-busy-query)
        body = f'''<?xml version="1.0" encoding="utf-8" ?>
<c:free-busy-query xmlns:c="urn:ietf:params:xml:ns:caldav">
    <c:time-range start="{start}" end="{end}"/>
</c:free-busy-query>'''
        
        try:
            report_url = calendar_url
            if "caldav.icloud.com" in calendar_url:
                 home_parsed = urlparse(self.home_url)
                 home_server = f"{home_parsed.scheme}://{home_parsed.netloc}"
                 parsed_cal = urlparse(calendar_url)
                 report_url = urljoin(home_server, parsed_cal.path)

            resp = self._request("REPORT", report_url, data=body)
            attempts.append({
                "method": "caldav_report",
                "url": report_url,
                "httpStatus": resp.status_code,
                "result": resp.text[:200] if resp.text else ""
            })
            if resp.status_code == 200 and "FREEBUSY" in resp.text:
                fb_res = self._parse_freebusy_ics(resp.text, "caldav_report")
                fb_res["attempts"] = attempts
                return fb_res
        except Exception as e:
            attempts.append({"method": "caldav_report", "url": report_url, "error": str(e)})

        # 3. Fallback to event-derived busy
        try:
            events = self.list_events(calendar_url, start_iso, end_iso)
            busy = []
            for e in events:
                if e.get("status") == "CANCELLED":
                    continue
                e_start = parse_iso_datetime(e["start"])
                e_end = parse_iso_datetime(e["end"])
                if e_start and e_end:
                    clipped = clip_to_range(e_start, e_end, q_start, q_end)
                    if clipped:
                        busy.append({
                            "start": clipped["start"],
                            "end": clipped["end"],
                            "summary": e.get("summary")
                        })
            return {
                "busy": busy, 
                "method": "event_fallback", 
                "attempts": attempts,
                "fallback_reason": "CalDAV scheduling and report methods failed or returned no data"
            }
        except Exception as e:
            return {"error": str(e), "method": "failed", "attempts": attempts}

    def freebusy_multi(self, calendar_names, start_iso, end_iso):
        if not calendar_names:
            raise ValueError("At least one --calendar must be provided")

        combined_busy = []
        calendars = []
        for cal_name in calendar_names:
            cal_url = self.get_calendar_url(cal_name)
            fb = self.freebusy(cal_url, start_iso, end_iso)
            cal_entry = {
                "calendar": cal_name,
                "method": fb.get("method"),
                "attempts": fb.get("attempts", []),
                "busy": fb.get("busy", [])
            }
            if fb.get("fallback_reason"):
                cal_entry["fallback_reason"] = fb.get("fallback_reason")
            if fb.get("error"):
                cal_entry["error"] = fb.get("error")

            calendars.append(cal_entry)

            for interval in fb.get("busy", []):
                combined_busy.append({
                    "calendar": cal_name,
                    "start": interval.get("start"),
                    "end": interval.get("end"),
                    "summary": interval.get("summary")
                })

        combined_busy.sort(key=lambda b: ((b.get("start") or ""), (b.get("end") or ""), (b.get("calendar") or "")))
        return {
            "busy": combined_busy,
            "calendars": calendars,
            "method": "multi_calendar_aggregate"
        }

    def _parse_freebusy_ics(self, ics_text, method_name):
        busy = []
        # Support folded lines
        lines = []
        for line in ics_text.splitlines():
            if line.startswith(" ") or line.startswith("\t"):
                if lines: lines[-1] += line[1:]
            else:
                lines.append(line)
        
        for line in lines:
            if line.startswith("FREEBUSY"):
                parts = line.split(":", 1)
                if len(parts) > 1:
                    fb_val = parts[1]
                    # Handle multiple intervals separated by comma
                    intervals = fb_val.split(",")
                    for interval in intervals:
                        times = interval.split("/")
                        if len(times) == 2:
                            busy.append({
                                "start": caldav_to_iso(times[0]),
                                "end": caldav_to_iso(times[1])
                            })
        return {"busy": busy, "method": method_name}

    def attach_add(self, calendar_url, uid, file_path):
        event = self.get_event(calendar_url, uid)
        if not event: raise ValueError(f"Event {uid} not found.")
        
        path = resolve_attachment_path(file_path)
        mime, _ = mimetypes.guess_type(str(path))
        mime = mime or "application/octet-stream"
        
        upload_url = f"{event['url']}?action=attachment-add"
        with open(path, "rb") as f:
            headers = {
                "Content-Type": mime,
                "Content-Disposition": build_content_disposition_filename(path.name),
                "Prefer": "return=representation"
            }
            resp = self._request("POST", upload_url, data=f, headers=headers)
        
        resp.raise_for_status()
        attach_url = resp.headers.get("Location")
        
        # Now re-fetch event to find the MANAGED-ID
        event = self.get_event(calendar_url, uid)
        ics_text = event["ics"]
        
        # Unfold lines
        lines = []
        current_line = ""
        for line in ics_text.splitlines():
            if line.startswith(" ") or line.startswith("\t"):
                current_line += line[1:]
            else:
                if current_line: lines.append(current_line)
                current_line = line
        if current_line: lines.append(current_line)

        managed_id = ""
        for line in lines:
            if line.startswith("ATTACH") and attach_url in line:
                match = re.search(r'MANAGED-ID=([^:;]+)', line)
                if match:
                    managed_id = match.group(1)
                    break
        
        return {"uid": uid, "managed_id": managed_id, "attach_url": attach_url, "status": "attached"}

    def attach_remove(self, calendar_url, uid, managed_id):
        event = self.get_event(calendar_url, uid)
        if not event: raise ValueError(f"Event {uid} not found.")
        
        # 1. Attempt removal via API
        remove_url = f"{event['url']}?action=attachment-remove&managed-id={managed_id}"
        resp = self._request("POST", remove_url)
        if resp.status_code >= 400:
             remove_url = f"{event['url']}?managed-id={managed_id}"
             resp = self._request("DELETE", remove_url)
             
        # 2. Robust Verification and Manual Cleanup
        event = self.get_event(calendar_url, uid)
        ics_text = event["ics"]
        
        lines = []
        current_line = ""
        attachment_found = False
        
        # Parse and filter lines
        new_ics_lines = []
        in_vevent = False
        
        raw_lines = ics_text.splitlines()
        i = 0
        while i < len(raw_lines):
            line = raw_lines[i]
            # Unfold
            full_line = line
            while i + 1 < len(raw_lines) and (raw_lines[i+1].startswith(" ") or raw_lines[i+1].startswith("\t")):
                i += 1
                full_line += raw_lines[i][1:]
            
            if full_line == "BEGIN:VEVENT": in_vevent = True
            
            if in_vevent and full_line.startswith("ATTACH") and f"MANAGED-ID={managed_id}" in full_line:
                attachment_found = True
            else:
                new_ics_lines.append(full_line)
            
            if full_line == "END:VEVENT": in_vevent = False
            i += 1

        if attachment_found:
            # If still found after API call, manually update event
            new_ics = "\r\n".join(new_ics_lines)
            self.update_event(calendar_url, uid, ics_body=new_ics)
            
            # Final verify
            event = self.get_event(calendar_url, uid)
            if f"MANAGED-ID={managed_id}" in event["ics"]:
                raise RuntimeError(json.dumps({"error": f"Failed to remove attachment {managed_id} after manual attempt", "uid": uid}))

        return {"uid": uid, "managed_id": managed_id, "status": "removed"}

# --- CLI Implementation ---

def main():
    parser = JSONArgumentParser(
        description="Apple Calendar Pro CLI — manage iCloud calendars via CalDAV.",
        epilog="Example: python3 applecal.py --apple-id you@icloud.com events list --calendar Family --from 2026-03-01 --to 2026-03-07"
    )
    parser.add_argument("--apple-id", default="", help="Your iCloud account email (required)")
    parser.add_argument("--json-indent", type=int, default=None, help="Pretty-print JSON output with this indent level")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose debug logging")
    parser.add_argument("--version", action="version", version=f"applecal {__version__}")
    
    subparsers = parser.add_subparsers(dest="command", required=True)

    # doctor
    subparsers.add_parser("doctor")

    # calendars list
    cal_p = subparsers.add_parser("calendars")
    cal_sub = cal_p.add_subparsers(dest="subcommand", required=True)
    cal_sub.add_parser("list")

    # events ...
    ev_p = subparsers.add_parser("events")
    ev_sub = ev_p.add_subparsers(dest="subcommand", required=True)
    
    # events list
    ev_list = ev_sub.add_parser("list")
    ev_list.add_argument("--calendar", action="append", required=True)
    ev_list.add_argument("--from", dest="start", default=datetime.now(timezone.utc).isoformat())
    ev_list.add_argument("--to", dest="end", default=(datetime.now(timezone.utc) + timedelta(days=7)).isoformat())
    ev_list.add_argument("--query")
    ev_list.add_argument("--max", type=int, dest="max_items")

    # events create
    ev_create = ev_sub.add_parser("create")
    ev_create.add_argument("--calendar", required=True)
    ev_create.add_argument("--summary", required=True)
    ev_create.add_argument("--start", required=True)
    ev_create.add_argument("--end", required=True)
    ev_create.add_argument("--location")
    ev_create.add_argument("--description")
    ev_create.add_argument("--all-day", action="store_true")

    # events update
    ev_update = ev_sub.add_parser("update")
    ev_update.add_argument("--calendar", required=True)
    ev_update.add_argument("--uid", required=True)
    ev_update.add_argument("--summary")
    ev_update.add_argument("--start")
    ev_update.add_argument("--end")
    ev_update.add_argument("--location")
    ev_update.add_argument("--description")
    ev_update.add_argument("--clear-location", action="store_true", help="Remove LOCATION from the event")
    ev_update.add_argument("--clear-description", action="store_true", help="Remove DESCRIPTION from the event")
    ev_update.add_argument("--all-day", action="store_true")

    # events delete
    ev_del = ev_sub.add_parser("delete")
    ev_del.add_argument("--calendar", required=True)
    ev_del.add_argument("--uid", required=True)

    # event get
    event_p = subparsers.add_parser("event")
    event_sub = event_p.add_subparsers(dest="subcommand", required=True)
    event_get = event_sub.add_parser("get")
    event_get.add_argument("--calendar", required=True)
    event_get.add_argument("--uid", required=True)

    # freebusy
    fb = subparsers.add_parser("freebusy")
    fb.add_argument("--calendar", action="append", required=True)
    fb.add_argument("--from", dest="start", required=True)
    fb.add_argument("--to", dest="end", required=True)

    # attach ...
    at_p = subparsers.add_parser("attach")
    at_sub = at_p.add_subparsers(dest="subcommand", required=True)
    
    # attach add
    at_add = at_sub.add_parser("add")
    at_add.add_argument("--calendar", required=True)
    at_add.add_argument("--uid", required=True)
    at_add.add_argument("--file", required=True)
    
    # attach remove
    at_rem = at_sub.add_parser("remove")
    at_rem.add_argument("--calendar", required=True)
    at_rem.add_argument("--uid", required=True)
    at_rem.add_argument("--managed-id", required=True)

    try:
        args = parser.parse_args()
    except Exception as e:
        _json_error(str(e))
        sys.exit(2)

    # Configure logging
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG, format="[%(levelname)s] %(message)s")
    else:
        logging.basicConfig(level=logging.WARNING)

    if args.json_indent is not None and args.json_indent < 0:
        _json_error("--json-indent must be >= 0")
        sys.exit(1)

    if not args.apple_id:
        _json_error("Missing --apple-id. Provide your iCloud account email, e.g. --apple-id you@icloud.com", indent=args.json_indent)
        sys.exit(1)

    try:
        apple_id = require_non_empty(args.apple_id, "apple-id")
        client = AppleCalClient(apple_id)
        result = None

        if args.command == "events":
            if args.subcommand in ("create", "update", "delete"):
                args.uid = validate_uid(args.uid) if getattr(args, "uid", None) else None
            if args.subcommand == "create":
                args.summary = require_non_empty(args.summary, "summary")
                validate_time_range(args.start, args.end, all_day=args.all_day)
            elif args.subcommand == "update":
                if args.location is not None and args.clear_location:
                    raise ValueError("Use either --location or --clear-location, not both")
                if args.description is not None and args.clear_description:
                    raise ValueError("Use either --description or --clear-description, not both")
                if not any([
                    args.summary,
                    args.start,
                    args.end,
                    args.location,
                    args.description,
                    args.all_day,
                    args.clear_location,
                    args.clear_description,
                ]):
                    raise ValueError("events update requires at least one field to modify")
                if args.start and args.end:
                    validate_time_range(args.start, args.end, all_day=args.all_day)
            elif args.subcommand == "list":
                validate_time_range(args.start, args.end)
                args.calendar = [require_non_empty(c, "calendar") for c in args.calendar]
            else:
                args.calendar = require_non_empty(args.calendar, "calendar")
        elif args.command == "freebusy":
            validate_time_range(args.start, args.end)
            args.calendar = [require_non_empty(c, "calendar") for c in args.calendar]
        elif args.command == "event":
            args.uid = validate_uid(args.uid)
            args.calendar = require_non_empty(args.calendar, "calendar")
        elif args.command == "attach":
            args.uid = validate_uid(args.uid)
            args.calendar = require_non_empty(args.calendar, "calendar")
            if args.subcommand == "remove":
                args.managed_id = validate_managed_id(args.managed_id)
            elif args.subcommand == "add":
                args.file = require_non_empty(args.file, "file")

        if args.command == "doctor":
            result = {
                "status": "ok",
                "apple_id": apple_id,
                "principal": client.principal_url,
                "home": client.home_url,
                "outbox": client.outbox_url,
                "addresses": client.user_addresses
            }
        
        elif args.command == "calendars" and args.subcommand == "list":
            result = client.list_calendars()
            
        elif args.command == "events":
            if args.subcommand == "list":
                result = client.list_events_multi(args.calendar, args.start, args.end, query=args.query, max_items=args.max_items)
            else:
                url = client.get_calendar_url(require_non_empty(args.calendar, "calendar"))
                if args.subcommand == "create":
                    result = client.create_event(url, args.summary, args.start, args.end, args.location, args.description, all_day=args.all_day)
                elif args.subcommand == "update":
                    result = client.update_event(
                        url,
                        args.uid,
                        args.summary,
                        args.start,
                        args.end,
                        args.location,
                        args.description,
                        all_day=True if args.all_day else None,
                        clear_location=args.clear_location,
                        clear_description=args.clear_description,
                    )
                elif args.subcommand == "delete":
                    result = client.delete_event(url, args.uid)

        elif args.command == "event" and args.subcommand == "get":
            url = client.get_calendar_url(args.calendar)
            result = client.get_event_details(url, args.uid)
            if not result:
                raise ValueError(f"Event {args.uid} not found.")

        elif args.command == "freebusy":
            result = client.freebusy_multi(args.calendar, args.start, args.end)
            
        elif args.command == "attach":
            url = client.get_calendar_url(args.calendar)
            if args.subcommand == "add":
                result = client.attach_add(url, args.uid, args.file)
            elif args.subcommand == "remove":
                result = client.attach_remove(url, args.uid, args.managed_id)

        if result is not None:
            print(json.dumps(result, indent=args.json_indent, sort_keys=True))

    except Exception as e:
        # Check if e is already JSON (from RuntimeError in attach_remove)
        try:
            err_data = json.loads(str(e))
            print(json.dumps(err_data, sort_keys=True))
        except json.JSONDecodeError:
            print(json.dumps({"error": str(e)}, sort_keys=True))
        sys.exit(1)

if __name__ == "__main__":
    main()
