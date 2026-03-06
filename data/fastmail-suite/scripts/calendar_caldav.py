#!/usr/bin/env python3
"""Fastmail calendar CLI (CalDAV) — safe-by-default.

No external deps (stdlib only). Uses a Fastmail *app password*.

Read ops:
  FASTMAIL_CALDAV_USER, FASTMAIL_CALDAV_PASS required.
Write ops require FASTMAIL_ENABLE_WRITES=1.

What works in v1:
  - list calendars
  - upcoming events (REPORT calendar-query with time-range)
  - create event (PUT)  [writes enabled]
  - reschedule/update (PUT with If-Match) [writes enabled]
  - cancel/delete (DELETE with If-Match)  [writes enabled]

Note: For update/delete, this tool expects an event href + etag (shown in upcoming --debug).

Examples:
  python3 scripts/calendar_caldav.py calendars
  python3 scripts/calendar_caldav.py upcoming --days 7

  # Create:
  FASTMAIL_ENABLE_WRITES=1 python3 scripts/calendar_caldav.py create \
    --calendar-name "Personal" --summary "Dentist" --start "2026-03-01T09:00:00" --end "2026-03-01T09:30:00" --tz "Australia/Hobart"

  # Update (reschedule):
  FASTMAIL_ENABLE_WRITES=1 python3 scripts/calendar_caldav.py update --href "/dav/calendars/user/.../event.ics" --etag "..." --start ... --end ...

  # Cancel:
  FASTMAIL_ENABLE_WRITES=1 python3 scripts/calendar_caldav.py delete --href "/dav/calendars/user/.../event.ics" --etag "..."

Env:
  FASTMAIL_CALDAV_BASE_URL (optional; default: https://caldav.fastmail.com)
  FASTMAIL_REDACT (default: 1)
"""

from __future__ import annotations

import argparse
import base64
import datetime as dt
import os
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from jmap_client import FastmailError, _env_flag, exit_with_error, redact_text


DEFAULT_BASE = "https://caldav.fastmail.com"  # Fastmail CalDAV host; actual endpoint is usually under /dav/
NS = {
    "d": "DAV:",
    "cs": "http://calendarserver.org/ns/",
    "c": "urn:ietf:params:xml:ns:caldav",
}


def _basic_auth_header(user: str, password: str) -> str:
    tok = base64.b64encode(f"{user}:{password}".encode()).decode()
    return f"Basic {tok}"


@dataclass
class Calendar:
    name: str
    url: str  # absolute


def _req(method: str, url: str, *, user: str, password: str, body: Optional[bytes] = None, headers: Optional[Dict[str, str]] = None):
    h = {
        "Authorization": _basic_auth_header(user, password),
        "User-Agent": "openclaw-fastmail-suite/1.0",
    }
    if headers:
        h.update(headers)
    return urllib.request.Request(url, data=body, headers=h, method=method)


def _urlopen(req: urllib.request.Request) -> Tuple[int, Dict[str, str], bytes]:
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.getcode(), dict(r.headers.items()), r.read()
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers.items()), e.read() or b""


def _get_env(name: str) -> str:
    v = os.environ.get(name)
    if not v:
        raise FastmailError(f"Missing env var {name}")
    return v


def _base_url() -> str:
    return (os.environ.get("FASTMAIL_CALDAV_BASE_URL") or DEFAULT_BASE).rstrip("/")


def _principal_url(user: str, password: str) -> str:
    # Discover current-user-principal.
    # Fastmail returns 404 on bare "/"; real endpoints are typically:
    #   /.well-known/caldav
    #   /dav/
    body = b"""<?xml version='1.0' encoding='utf-8'?>
<d:propfind xmlns:d='DAV:'>
  <d:prop><d:current-user-principal/></d:prop>
</d:propfind>"""

    candidates = [
        _base_url().rstrip("/") + "/.well-known/caldav",
        _base_url().rstrip("/") + "/dav/",
        _base_url().rstrip("/") + "/dav",
    ]

    last_err: Optional[str] = None
    for url in candidates:
        req = _req(
            "PROPFIND",
            url,
            user=user,
            password=password,
            body=body,
            headers={"Depth": "0", "Content-Type": "application/xml"},
        )
        code, _, data = _urlopen(req)
        if code not in (200, 207):
            last_err = f"HTTP {code} {data[:120]!r}"
            continue

        root = ET.fromstring(data)
        el = root.find(".//d:current-user-principal/d:href", NS)
        if el is None or not el.text:
            last_err = "Missing current-user-principal in response"
            continue

        href = el.text
        if href.startswith("http"):
            return href
        return _base_url().rstrip("/") + href

    raise FastmailError(f"PROPFIND base failed on all endpoints. Last error: {last_err}")


def _calendar_home_set(user: str, password: str) -> str:
    principal = _principal_url(user, password)
    body = b"""<?xml version='1.0' encoding='utf-8'?>
<d:propfind xmlns:d='DAV:' xmlns:c='urn:ietf:params:xml:ns:caldav'>
  <d:prop><c:calendar-home-set/></d:prop>
</d:propfind>"""
    req = _req(
        "PROPFIND",
        principal,
        user=user,
        password=password,
        body=body,
        headers={"Depth": "0", "Content-Type": "application/xml"},
    )
    code, _, data = _urlopen(req)
    if code not in (200, 207):
        raise FastmailError(f"PROPFIND principal failed: HTTP {code} {data[:200]!r}")
    root = ET.fromstring(data)
    el = root.find(".//c:calendar-home-set/d:href", NS)
    if el is None or not el.text:
        raise FastmailError("Could not discover calendar-home-set")
    href = el.text
    if href.startswith("http"):
        return href
    return _base_url() + href


def list_calendars(user: str, password: str) -> List[Calendar]:
    home = _calendar_home_set(user, password)
    body = b"""<?xml version='1.0' encoding='utf-8'?>
<d:propfind xmlns:d='DAV:' xmlns:cs='http://calendarserver.org/ns/'>
  <d:prop>
    <d:displayname/>
    <cs:getctag/>
  </d:prop>
</d:propfind>"""
    req = _req(
        "PROPFIND",
        home,
        user=user,
        password=password,
        body=body,
        headers={"Depth": "1", "Content-Type": "application/xml"},
    )
    code, _, data = _urlopen(req)
    if code not in (200, 207):
        raise FastmailError(f"PROPFIND calendars failed: HTTP {code} {data[:200]!r}")

    root = ET.fromstring(data)
    out: List[Calendar] = []
    for resp in root.findall("d:response", NS):
        href_el = resp.find("d:href", NS)
        name_el = resp.find(".//d:displayname", NS)
        if href_el is None or not href_el.text:
            continue
        href = href_el.text
        if href.rstrip("/") == home.rstrip("/"):
            continue
        name = (name_el.text or "").strip() if name_el is not None else ""
        if not name:
            # fallback: last path component
            name = href.rstrip("/").split("/")[-1]
        url = href if href.startswith("http") else _base_url() + href
        out.append(Calendar(name=name, url=url))
    return out


def _utc_range(days: int) -> Tuple[str, str]:
    now = dt.datetime.now(dt.UTC)
    end = now + dt.timedelta(days=days)
    return now.strftime("%Y%m%dT%H%M%SZ"), end.strftime("%Y%m%dT%H%M%SZ")


def _parse_ics_events(ics: str) -> List[Dict[str, str]]:
    # Very small parser: find VEVENT blocks and extract a few fields.
    events: List[Dict[str, str]] = []
    for block in re.findall(r"BEGIN:VEVENT(.*?)END:VEVENT", ics, flags=re.S | re.I):
        def field(name: str) -> Optional[str]:
            m = re.search(rf"\n{name}(?:;[^:]*)?:([^\n\r]*)", "\n" + block, flags=re.I)
            return m.group(1).strip() if m else None

        events.append(
            {
                "uid": field("UID") or "",
                "summary": field("SUMMARY") or "",
                "dtstart": field("DTSTART") or "",
                "dtend": field("DTEND") or "",
            }
        )
    return events


def _collect_events(user: str, password: str, *, days: int) -> List[Dict[str, str]]:
    ignore = {x.strip().lower() for x in (os.environ.get("FASTMAIL_CALENDAR_IGNORE") or "").split(",") if x.strip()}
    cals = [c for c in list_calendars(user, password) if c.name.strip().lower() not in ignore]
    start_utc, end_utc = _utc_range(days)

    body_tpl = """<?xml version='1.0' encoding='utf-8'?>
<c:calendar-query xmlns:d='DAV:' xmlns:c='urn:ietf:params:xml:ns:caldav'>
  <d:prop>
    <d:getetag/>
    <c:calendar-data/>
  </d:prop>
  <c:filter>
    <c:comp-filter name='VCALENDAR'>
      <c:comp-filter name='VEVENT'>
        <c:time-range start='{start}' end='{end}'/>
      </c:comp-filter>
    </c:comp-filter>
  </c:filter>
</c:calendar-query>""".format(start=start_utc, end=end_utc).encode()

    all_items: List[Dict[str, str]] = []

    for cal in cals:
        req = _req(
            "REPORT",
            cal.url,
            user=user,
            password=password,
            body=body_tpl,
            headers={"Depth": "1", "Content-Type": "application/xml"},
        )
        code, _, data = _urlopen(req)
        if code not in (200, 207):
            continue

        root = ET.fromstring(data)
        for resp in root.findall("d:response", NS):
            href_el = resp.find("d:href", NS)
            etag_el = resp.find(".//d:getetag", NS)
            caldata_el = resp.find(".//c:calendar-data", NS)
            if href_el is None or caldata_el is None or not href_el.text or not caldata_el.text:
                continue
            href = href_el.text
            etag = (etag_el.text or "") if etag_el is not None else ""
            ics = caldata_el.text
            for ev in _parse_ics_events(ics):
                item = {
                    "calendar": cal.name,
                    "href": href,
                    "etag": etag,
                    **ev,
                }
                all_items.append(item)

    all_items.sort(key=lambda x: x.get("dtstart") or "")
    return all_items


def resolve_uid(user: str, password: str, *, uid: str, days: int) -> Dict[str, str]:
    items = _collect_events(user, password, days=days)
    for it in items:
        if (it.get("uid") or "").strip() == uid.strip():
            return it
    raise FastmailError(f"UID not found in upcoming window: {uid}")


def upcoming(user: str, password: str, *, days: int, raw: bool, debug: bool) -> None:
    ignore = {x.strip().lower() for x in (os.environ.get("FASTMAIL_CALENDAR_IGNORE") or "").split(",") if x.strip()}
    all_items = [it for it in _collect_events(user, password, days=days) if (it.get("calendar") or "").strip().lower() not in ignore]

    for idx, it in enumerate(all_items, start=1):
        summary = it.get("summary") or "(no summary)"
        if not raw:
            summary = redact_text(summary)
        print(f"{idx:>3}. [{it.get('calendar')}] {it.get('dtstart')}  {summary}")
        if debug:
            et = it.get("etag") or ""
            print(f"     uid:  {it.get('uid')}\n     href: {it.get('href')}\n     etag: {et}")


def _ics_event(*, uid: str, summary: str, start: str, end: str, tz: str) -> str:
    # start/end are local time, e.g. 2026-03-01T09:00:00
    # Use TZID to avoid guessing UTC offsets.
    now = dt.datetime.now(dt.UTC).strftime("%Y%m%dT%H%M%SZ")
    def to_local(v: str) -> str:
        # naive conversion: strip separators
        # 2026-03-01T09:00:00 -> 20260301T090000
        vv = v.replace("-", "").replace(":", "")
        return vv.replace("T", "T")

    s = to_local(start)
    e = to_local(end)

    return "\r\n".join(
        [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//openclaw//fastmail-suite//EN",
            "CALSCALE:GREGORIAN",
            "BEGIN:VEVENT",
            f"UID:{uid}",
            f"DTSTAMP:{now}",
            f"DTSTART;TZID={tz}:{s}",
            f"DTEND;TZID={tz}:{e}",
            f"SUMMARY:{summary}",
            "END:VEVENT",
            "END:VCALENDAR",
            "",
        ]
    )


def _pick_calendar_url(user: str, password: str, *, calendar_name: str) -> str:
    cals = list_calendars(user, password)
    for c in cals:
        if c.name.lower() == calendar_name.lower():
            return c.url
    raise FastmailError(f"Calendar not found: {calendar_name}")


def create_event(user: str, password: str, *, calendar_name: str, summary: str, start: str, end: str, tz: str) -> None:
    if not _env_flag("FASTMAIL_ENABLE_WRITES", False):
        raise FastmailError("Write operation blocked. Set FASTMAIL_ENABLE_WRITES=1")

    import uuid

    uid = str(uuid.uuid4())
    cal_url = _pick_calendar_url(user, password, calendar_name=calendar_name)
    href = cal_url.rstrip("/") + f"/{uid}.ics"
    ics = _ics_event(uid=uid, summary=summary, start=start, end=end, tz=tz)

    req = _req(
        "PUT",
        href,
        user=user,
        password=password,
        body=ics.encode("utf-8"),
        headers={"Content-Type": "text/calendar; charset=utf-8"},
    )
    code, hdrs, data = _urlopen(req)
    if code not in (200, 201, 204):
        raise FastmailError(f"PUT failed: HTTP {code} {data[:200]!r}")

    print(f"Created event UID={uid}")


def _pick_event(user: str, password: str, *, pick: int, days: int) -> Dict[str, str]:
    if pick <= 0:
        raise FastmailError("pick must be >= 1")
    items = _collect_events(user, password, days=days)
    if pick > len(items):
        raise FastmailError(f"pick out of range: {pick} (only {len(items)} events)")
    return items[pick - 1]


def update_event(
    user: str,
    password: str,
    *,
    href: Optional[str],
    etag: Optional[str],
    uid: Optional[str],
    pick: Optional[int],
    resolve_days: int,
    summary: str,
    start: str,
    end: str,
    tz: str,
) -> None:
    if not _env_flag("FASTMAIL_ENABLE_WRITES", False):
        raise FastmailError("Write operation blocked. Set FASTMAIL_ENABLE_WRITES=1")

    if pick and (not href or not etag):
        it = _pick_event(user, password, pick=pick, days=resolve_days)
        href = it.get("href")
        etag = it.get("etag")
        uid = it.get("uid") or uid

    if uid and (not href or not etag):
        it = resolve_uid(user, password, uid=uid, days=resolve_days)
        href = it.get("href")
        etag = it.get("etag")

    if not href or not etag:
        raise FastmailError("update requires (--href and --etag) or --uid or --pick")

    url = href if href.startswith("http") else _base_url() + href
    event_uid = uid or href.rstrip("/").split("/")[-1].replace(".ics", "")
    ics = _ics_event(uid=event_uid, summary=summary, start=start, end=end, tz=tz)

    req = _req(
        "PUT",
        url,
        user=user,
        password=password,
        body=ics.encode("utf-8"),
        headers={"Content-Type": "text/calendar; charset=utf-8", "If-Match": etag},
    )
    code, _, data = _urlopen(req)
    if code not in (200, 201, 204):
        raise FastmailError(f"Update failed: HTTP {code} {data[:200]!r}")
    print("Updated event.")


def delete_event(
    user: str,
    password: str,
    *,
    href: Optional[str],
    etag: Optional[str],
    uid: Optional[str],
    pick: Optional[int],
    resolve_days: int,
) -> None:
    if not _env_flag("FASTMAIL_ENABLE_WRITES", False):
        raise FastmailError("Write operation blocked. Set FASTMAIL_ENABLE_WRITES=1")

    if pick and (not href or not etag):
        it = _pick_event(user, password, pick=pick, days=resolve_days)
        href = it.get("href")
        etag = it.get("etag")
        uid = it.get("uid") or uid

    if uid and (not href or not etag):
        it = resolve_uid(user, password, uid=uid, days=resolve_days)
        href = it.get("href")
        etag = it.get("etag")

    if not href or not etag:
        raise FastmailError("delete requires (--href and --etag) or --uid or --pick")

    url = href if href.startswith("http") else _base_url() + href
    req = _req("DELETE", url, user=user, password=password, headers={"If-Match": etag})
    code, _, data = _urlopen(req)
    if code not in (200, 204):
        raise FastmailError(f"Delete failed: HTTP {code} {data[:200]!r}")
    print("Deleted event.")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--raw", action="store_true", help="Disable redaction in output")

    sp = p.add_subparsers(dest="cmd", required=True)

    sp.add_parser("calendars")

    p_up = sp.add_parser("upcoming")
    p_up.add_argument("--days", type=int, default=7)
    p_up.add_argument("--debug", action="store_true")

    p_create = sp.add_parser("create")
    p_create.add_argument("--calendar-name", required=True)
    p_create.add_argument("--summary", required=True)
    p_create.add_argument("--start", required=True, help="YYYY-MM-DDTHH:MM:SS")
    p_create.add_argument("--end", required=True, help="YYYY-MM-DDTHH:MM:SS")
    p_create.add_argument("--tz", required=True)

    p_upd = sp.add_parser("update")
    p_upd.add_argument("--pick", type=int, help="Pick event number from upcoming list (1-based)")
    p_upd.add_argument("--uid", help="Event UID to update (auto-resolves href+etag from upcoming window)")
    p_upd.add_argument("--resolve-days", type=int, default=90, help="Search window for --uid/--pick resolution")
    p_upd.add_argument("--href", help="Event href (from upcoming --debug)")
    p_upd.add_argument("--etag", help="Event etag (from upcoming --debug)")
    p_upd.add_argument("--summary", required=True)
    p_upd.add_argument("--start", required=True)
    p_upd.add_argument("--end", required=True)
    p_upd.add_argument("--tz", required=True)

    p_del = sp.add_parser("delete")
    p_del.add_argument("--pick", type=int, help="Pick event number from upcoming list (1-based)")
    p_del.add_argument("--uid", help="Event UID to delete (auto-resolves href+etag from upcoming window)")
    p_del.add_argument("--resolve-days", type=int, default=90, help="Search window for --uid/--pick resolution")
    p_del.add_argument("--href", help="Event href (from upcoming --debug)")
    p_del.add_argument("--etag", help="Event etag (from upcoming --debug)")

    args = p.parse_args()

    user = _get_env("FASTMAIL_CALDAV_USER")
    password = _get_env("FASTMAIL_CALDAV_PASS")

    try:
        if args.cmd == "calendars":
            cals = list_calendars(user, password)
            for c in cals:
                name = c.name if args.raw else redact_text(c.name)
                print(f"- {name}")
        elif args.cmd == "upcoming":
            upcoming(user, password, days=args.days, raw=args.raw, debug=args.debug)
        elif args.cmd == "create":
            create_event(user, password, calendar_name=args.calendar_name, summary=args.summary, start=args.start, end=args.end, tz=args.tz)
        elif args.cmd == "update":
            update_event(
                user,
                password,
                href=args.href,
                etag=args.etag,
                uid=args.uid,
                pick=args.pick,
                resolve_days=args.resolve_days,
                summary=args.summary,
                start=args.start,
                end=args.end,
                tz=args.tz,
            )
        elif args.cmd == "delete":
            delete_event(
                user,
                password,
                href=args.href,
                etag=args.etag,
                uid=args.uid,
                pick=args.pick,
                resolve_days=args.resolve_days,
            )
    except Exception as e:
        exit_with_error(e)


if __name__ == "__main__":
    main()
