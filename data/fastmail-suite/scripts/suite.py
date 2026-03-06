#!/usr/bin/env python3
"""Fastmail Suite v0.2 CLI.

Subcommands:
  status
  triage today|last-7d
  search <query>
  thread <id-or-snippet>

Safe defaults:
  - Redaction enabled unless FASTMAIL_REDACT=0
  - Read-only operations only
"""

from __future__ import annotations

import argparse
import datetime as dt
import os
import shlex
from collections import Counter
from typing import Any, Dict, List

from calendar_caldav import list_calendars
from jmap_client import FastmailError, FastmailJMAP, _env_flag, redact_text


USING_CONTACTS = ["urn:ietf:params:jmap:core", "urn:ietf:params:jmap:contacts"]


ACTION_KEYWORDS = [
    "invoice",
    "bill",
    "billing",
    "payment",
    "due",
    "confirm",
    "action required",
    "reminder",
    "overdue",
    "statement",
]


def _is_redact() -> bool:
    return _env_flag("FASTMAIL_REDACT", True)


def _mask(s: str) -> str:
    return redact_text(s) if _is_redact() else s


def _fmt_person(item: Dict[str, Any]) -> str:
    name = (item.get("name") or "").strip()
    email = (item.get("email") or "").strip()
    if name and email:
        out = f"{name} <{email}>"
    elif email:
        out = email
    elif name:
        out = name
    else:
        out = "?"
    return _mask(out)


def _fmt_sender(from_field: Any) -> str:
    if isinstance(from_field, list) and from_field:
        return _fmt_person(from_field[0])
    return "?"


def _fmt_sender_key(from_field: Any) -> str:
    if isinstance(from_field, list) and from_field:
        p = from_field[0]
        email = (p.get("email") or "").strip().lower()
        name = (p.get("name") or "").strip()
        base = email or name or "unknown"
        return _mask(base)
    return "unknown"


def _utc_now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def _start_of_today_utc() -> dt.datetime:
    now = _utc_now()
    return dt.datetime(now.year, now.month, now.day, tzinfo=dt.timezone.utc)


def _iso_z(ts: dt.datetime) -> str:
    return ts.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _build_client() -> FastmailJMAP:
    token = os.environ.get("FASTMAIL_TOKEN")
    if not token:
        raise FastmailError("Missing FASTMAIL_TOKEN")
    return FastmailJMAP(token)


def _jmap_ok_status() -> str:
    token = os.environ.get("FASTMAIL_TOKEN")
    if not token:
        return "MISSING TOKEN"
    try:
        client = FastmailJMAP(token)
        client.call([["Mailbox/get", {"accountId": None, "ids": None, "properties": ["id"]}, "m"]])
        return "OK"
    except Exception as e:
        msg = str(e).lower()
        if "401" in msg or "403" in msg or "auth" in msg or "forbidden" in msg or "unauthorized" in msg:
            return "AUTH FAILED"
        return f"ERROR ({_mask(str(e))})"




def _contacts_ok_status() -> str:
    token = os.environ.get("FASTMAIL_TOKEN")
    if not token:
        return "MISSING TOKEN"
    try:
        client = FastmailJMAP(token)
        resp = client.call(
            [["ContactCard/query", {"accountId": None, "limit": 1}, "q"]],
            using=USING_CONTACTS,
        )
        q = resp["methodResponses"][0][1]
        ids = q.get("ids") or []
        if ids:
            client.call(
                [[
                    "ContactCard/get",
                    {"accountId": None, "ids": [ids[0]], "properties": ["id"]},
                    "g",
                ]],
                using=USING_CONTACTS,
            )
        return "OK"
    except Exception as e:
        msg = str(e).lower()
        if "401" in msg or "403" in msg or "auth" in msg or "forbidden" in msg or "unauthorized" in msg:
            return "AUTH FAILED"
        return f"ERROR ({_mask(str(e))})"


def _caldav_ok_status() -> str:
    user = os.environ.get("FASTMAIL_CALDAV_USER")
    password = os.environ.get("FASTMAIL_CALDAV_PASS")
    if not user or not password:
        return "MISSING APP PASSWORD"
    try:
        _ = list_calendars(user, password)
        return "OK"
    except Exception as e:
        msg = str(e).lower()
        if "401" in msg or "403" in msg or "auth" in msg or "forbidden" in msg or "unauthorized" in msg:
            return "AUTH FAILED"
        return f"ERROR ({_mask(str(e))})"


def cmd_status() -> int:
    print(f"Mail (JMAP): {_jmap_ok_status()}")
    print(f"Calendar (CalDAV): {_caldav_ok_status()}")
    print(f"Contacts (JMAP): {_contacts_ok_status()}")
    return 0


def _inbox_id(client: FastmailJMAP) -> str:
    _, by_role, _ = client.mailbox_map()
    inbox_id = by_role.get("inbox")
    if not inbox_id:
        raise FastmailError("No inbox mailbox found")
    return inbox_id


def _query_emails(client: FastmailJMAP, *, filt: Dict[str, Any], limit: int = 200) -> List[Dict[str, Any]]:
    resp = client.call(
        [
            [
                "Email/query",
                {
                    "accountId": None,
                    "filter": filt,
                    "sort": [{"property": "receivedAt", "isAscending": False}],
                    "limit": limit,
                },
                "q",
            ],
            [
                "Email/get",
                {
                    "accountId": None,
                    "#ids": {"resultOf": "q", "name": "Email/query", "path": "/ids"},
                    "properties": ["id", "threadId", "subject", "from", "receivedAt", "preview", "keywords", "hasAttachment"],
                },
                "g",
            ],
        ]
    )
    return resp["methodResponses"][1][1].get("list") or []


def _subject_flags(subject: str) -> List[str]:
    s = (subject or "").lower()
    hits = [k for k in ACTION_KEYWORDS if k in s]
    if "friends.tas.edu.au" in s:
        hits.append("friends.tas.edu.au")
    return list(dict.fromkeys(hits))


def cmd_triage(window: str, *, limit: int) -> int:
    client = _build_client()
    inbox_id = _inbox_id(client)

    if window == "today":
        after = _start_of_today_utc()
    elif window == "last-7d":
        after = _utc_now() - dt.timedelta(days=7)
    else:
        raise FastmailError(f"Unsupported triage window: {window}")

    filt = {"operator": "AND", "conditions": [{"inMailbox": inbox_id}, {"after": _iso_z(after)}]}
    emails = _query_emails(client, filt=filt, limit=limit)

    sender_counts: Counter[str] = Counter()
    flagged: List[Dict[str, Any]] = []
    bills: List[Dict[str, Any]] = []

    for e in emails:
        sender_counts[_fmt_sender_key(e.get("from"))] += 1
        subj = e.get("subject") or ""
        flags = _subject_flags(subj)
        if flags:
            flagged.append({"email": e, "flags": flags})
        if any(k in subj.lower() for k in ("invoice", "bill", "billing", "payment", "due", "statement")):
            bills.append(e)

    print(f"Triage ({window}) — {len(emails)} message(s) scanned")

    top = sender_counts.most_common(8)
    print("- Top senders:")
    if not top:
        print("  - none")
    else:
        for sender, n in top:
            print(f"  - {sender}: {n}")

    print("- Action-needed subjects:")
    if not flagged:
        print("  - none")
    else:
        for item in flagged[:12]:
            e = item["email"]
            subj = _mask(e.get("subject") or "(no subject)")
            sender = _fmt_sender(e.get("from"))
            dt_short = (e.get("receivedAt") or "")[:16].replace("T", " ")
            marks = ", ".join(item["flags"])
            print(f"  - [{dt_short}] {sender} — {subj}  ({marks})")

    print("- Highlights:")
    special = [i for i in flagged if "friends.tas.edu.au" in i["flags"]]
    if special:
        for item in special[:6]:
            e = item["email"]
            print(f"  - friends.tas.edu.au: {_mask(e.get('subject') or '(no subject)')}")
    else:
        print("  - friends.tas.edu.au: none")

    if bills:
        for e in bills[:6]:
            print(f"  - bill/payment: {_mask(e.get('subject') or '(no subject)')}")
    else:
        print("  - bills: none")

    return 0


def _parse_date_token(value: str, *, end_of_day: bool) -> str:
    d = dt.datetime.strptime(value, "%Y-%m-%d")
    if end_of_day:
        d = d.replace(hour=23, minute=59, second=59, tzinfo=dt.timezone.utc)
    else:
        d = d.replace(hour=0, minute=0, second=0, tzinfo=dt.timezone.utc)
    return _iso_z(d)


def _parse_search_query(raw_query: str) -> Dict[str, Any]:
    tokens = shlex.split(raw_query)
    conds: List[Dict[str, Any]] = []
    bare_terms: List[str] = []

    for t in tokens:
        low = t.lower()
        if low.startswith("from:"):
            v = t.split(":", 1)[1].strip()
            if v:
                conds.append({"from": v})
        elif low.startswith("subject:"):
            v = t.split(":", 1)[1].strip()
            if v:
                conds.append({"subject": v})
        elif low == "has:attachment":
            conds.append({"hasAttachment": True})
        elif low.startswith("last:"):
            v = low.split(":", 1)[1]
            if v.endswith("d") and v[:-1].isdigit():
                days = int(v[:-1])
                conds.append({"after": _iso_z(_utc_now() - dt.timedelta(days=days))})
        elif low.startswith("before:"):
            v = t.split(":", 1)[1].strip()
            if v:
                conds.append({"before": _parse_date_token(v, end_of_day=True)})
        elif low.startswith("after:"):
            v = t.split(":", 1)[1].strip()
            if v:
                conds.append({"after": _parse_date_token(v, end_of_day=False)})
        else:
            bare_terms.append(t)

    for term in bare_terms:
        conds.append({"text": term})

    if not conds:
        return {"text": raw_query}
    if len(conds) == 1:
        return conds[0]
    return {"operator": "AND", "conditions": conds}


def cmd_search(query: str, *, limit: int) -> int:
    client = _build_client()
    filt = _parse_search_query(query)
    emails = _query_emails(client, filt=filt, limit=limit)

    print(f"Search results ({len(emails)}):")
    for e in emails:
        when = (e.get("receivedAt") or "")[:16].replace("T", " ")
        sender = _fmt_sender(e.get("from"))
        subj = _mask(e.get("subject") or "(no subject)")
        snip = _mask((e.get("preview") or "").strip().replace("\n", " "))
        print(f"- {when} | {sender}")
        print(f"  {subj}")
        if snip:
            print(f"  {snip[:140]}")
        print(f"  id: {e.get('id')}")
    if not emails:
        print("- No matches")
    return 0


def _resolve_thread_id(client: FastmailJMAP, needle: str) -> str:
    try:
        resp = client.call(
            [["Email/get", {"accountId": None, "ids": [needle], "properties": ["id", "threadId", "subject"]}, "g"]]
        )
        got = resp["methodResponses"][0][1].get("list") or []
        if got and got[0].get("threadId"):
            return got[0]["threadId"]
    except Exception:
        pass

    recent = _query_emails(client, filt={"after": _iso_z(_utc_now() - dt.timedelta(days=60))}, limit=250)
    for e in recent:
        if e.get("threadId") == needle:
            return needle

    resp = client.call(
        [
            [
                "Email/query",
                {
                    "accountId": None,
                    "filter": {"operator": "OR", "conditions": [{"subject": needle}, {"text": needle}]},
                    "sort": [{"property": "receivedAt", "isAscending": False}],
                    "limit": 1,
                },
                "q",
            ],
            [
                "Email/get",
                {
                    "accountId": None,
                    "#ids": {"resultOf": "q", "name": "Email/query", "path": "/ids"},
                    "properties": ["id", "threadId", "subject"],
                },
                "g",
            ],
        ]
    )
    emails = resp["methodResponses"][1][1].get("list") or []
    if not emails:
        raise FastmailError("No matching email/thread found")
    tid = emails[0].get("threadId")
    if not tid:
        raise FastmailError("Matched email does not have threadId")
    return tid


def cmd_thread(needle: str) -> int:
    client = _build_client()
    thread_id = _resolve_thread_id(client, needle)

    tr = client.call([["Thread/get", {"accountId": None, "ids": [thread_id]}, "t"]])
    threads = tr["methodResponses"][0][1].get("list") or []
    if not threads:
        raise FastmailError("Thread not found")

    email_ids = threads[0].get("emailIds") or []
    if not email_ids:
        raise FastmailError("Thread has no emails")

    er = client.call(
        [[
            "Email/get",
            {
                "accountId": None,
                "ids": email_ids,
                "properties": ["id", "threadId", "subject", "from", "to", "receivedAt", "preview"],
            },
            "e",
        ]]
    )
    emails = er["methodResponses"][0][1].get("list") or []
    emails.sort(key=lambda x: x.get("receivedAt") or "")

    participants: Counter[str] = Counter()
    for e in emails:
        for p in (e.get("from") or [])[:1]:
            participants[_fmt_person(p)] += 1
        for p in (e.get("to") or [])[:3]:
            participants[_fmt_person(p)] += 1

    first_ts = emails[0].get("receivedAt") if emails else ""
    last_ts = emails[-1].get("receivedAt") if emails else ""

    print(f"Thread: {thread_id}")
    print(f"- Messages: {len(emails)}")
    print(f"- Timeline: {(first_ts or '')[:16].replace('T', ' ')} -> {(last_ts or '')[:16].replace('T', ' ')}")
    top_parts = ", ".join([f"{p} ({n})" for p, n in participants.most_common(6)]) or "unknown"
    print(f"- Participants: {top_parts}")

    print("- Latest messages:")
    for e in emails[-2:]:
        when = (e.get("receivedAt") or "")[:16].replace("T", " ")
        sender = _fmt_sender(e.get("from"))
        subj = _mask(e.get("subject") or "(no subject)")
        prev = _mask((e.get("preview") or "").strip())
        print(f"  - [{when}] {sender} — {subj}")
        if prev:
            print(f"    {prev[:220]}")

    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Fastmail Suite v0.2 helper CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("status", help="Check JMAP token and CalDAV credentials")

    p_triage = sub.add_parser("triage", help="Inbox triage summary")
    p_triage.add_argument("window", choices=["today", "last-7d"])
    p_triage.add_argument("--limit", type=int, default=200, help="Max messages to scan")

    p_search = sub.add_parser("search", help="Search email with tiny query DSL")
    p_search.add_argument("query", nargs="+", help="Query, e.g. from:foo last:7d invoice")
    p_search.add_argument("--limit", type=int, default=20)

    p_thread = sub.add_parser("thread", help="Summarize a conversation thread")
    p_thread.add_argument("needle", help="Email id, thread id, or subject snippet")

    args = parser.parse_args()

    try:
        if args.cmd == "status":
            raise SystemExit(cmd_status())
        if args.cmd == "triage":
            raise SystemExit(cmd_triage(args.window, limit=args.limit))
        if args.cmd == "search":
            raise SystemExit(cmd_search(" ".join(args.query), limit=args.limit))
        if args.cmd == "thread":
            raise SystemExit(cmd_thread(args.needle))
    except FastmailError as e:
        print(f"Error: {_mask(str(e))}")
        raise SystemExit(1)
    except ValueError as e:
        print(f"Error: {_mask(str(e))}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
