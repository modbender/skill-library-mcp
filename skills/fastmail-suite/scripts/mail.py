#!/usr/bin/env python3
"""Fastmail email CLI (JMAP) — safe-by-default.

Read ops use FASTMAIL_TOKEN.
Send uses FASTMAIL_TOKEN_SEND if set (recommended), else FASTMAIL_TOKEN.
Write ops require FASTMAIL_ENABLE_WRITES=1.

Examples:
  python3 scripts/email.py inbox --limit 20
  python3 scripts/email.py search "invoice" --limit 10
  python3 scripts/email.py read <email-id>
  FASTMAIL_ENABLE_WRITES=1 FASTMAIL_TOKEN_SEND=... python3 scripts/email.py send --to a@b.com --subject "Hi" --body "Hello"

Flags:
  --json        JSON output (still redacted unless --raw)
  --raw         disable redaction for output (be careful)
  --full        for read: print full body (still redacted unless --raw)

Env:
  FASTMAIL_MAX_BODY_BYTES (default 5000 for read)
"""

from __future__ import annotations

import argparse
import os
from typing import Any, Dict, List, Optional

from jmap_client import (
    FastmailError,
    FastmailJMAP,
    USING_CORE_MAIL,
    USING_CORE_MAIL_SEND,
    exit_with_error,
    get_required_env,
    redact_text,
    safe_print,
)


def _mask_email_addr(addr: Optional[str]) -> str:
    if not addr:
        return "?"
    return redact_text(addr)


def _extract_text_body(email_obj: Dict[str, Any]) -> str:
    body_values = email_obj.get("bodyValues") or {}

    def _collect(parts: List[Dict[str, Any]]) -> str:
        out = ""
        for part in parts or []:
            pid = part.get("partId")
            if not pid:
                continue
            val = body_values.get(pid) or {}
            if val.get("value"):
                out += val["value"]
        return out

    text = _collect(email_obj.get("textBody") or [])
    if text:
        return text
    html = _collect(email_obj.get("htmlBody") or [])
    return html


def cmd_mailboxes(client: FastmailJMAP, *, raw: bool) -> None:
    resp = client.call([
        [
            "Mailbox/get",
            {"accountId": None, "properties": ["name", "role", "totalEmails", "unreadEmails"]},
            "0",
        ]
    ])
    lst = resp["methodResponses"][0][1].get("list") or []
    for mb in sorted(lst, key=lambda m: m.get("name") or ""):
        safe_print(
            {
                "name": mb.get("name"),
                "role": mb.get("role"),
                "total": mb.get("totalEmails"),
                "unread": mb.get("unreadEmails"),
            },
            raw=raw,
        )


def _list(client: FastmailJMAP, filt: Dict[str, Any], *, limit: int, json_out: bool, raw: bool) -> None:
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
                    "properties": [
                        "id",
                        "subject",
                        "from",
                        "receivedAt",
                        "preview",
                        "keywords",
                    ],
                },
                "g",
            ],
        ],
        using=USING_CORE_MAIL,
    )
    total = resp["methodResponses"][0][1].get("total")
    emails = resp["methodResponses"][1][1].get("list") or []

    if json_out:
        out = []
        for e in emails:
            fr = None
            if e.get("from"):
                fr = e["from"][0].get("email")
            out.append(
                {
                    "id": e.get("id"),
                    "from": fr,
                    "subject": e.get("subject") or "",
                    "receivedAt": e.get("receivedAt"),
                    "unread": "$seen" not in (e.get("keywords") or {}),
                    "preview": e.get("preview") or "",
                }
            )
        safe_print({"total": total, "items": out}, raw=raw)
        return

    print(f"Showing {len(emails)} of {total} results\n")
    for e in emails:
        fr = e.get("from")
        fr_addr = fr[0].get("email") if fr else None
        unread = "$seen" not in (e.get("keywords") or {})
        flag = "UNREAD" if unread else "read"
        dt = (e.get("receivedAt") or "")[:16].replace("T", " ")
        subj = e.get("subject") or "(no subject)"
        preview = e.get("preview") or ""
        if not raw:
            subj = redact_text(subj)
            preview = redact_text(preview)
        print(f"[{flag}] {dt}  {_mask_email_addr(fr_addr)}")
        print(f"  {subj}")
        print(f"  {preview[:140]}")
        print(f"  id: {e.get('id')}\n")


def cmd_inbox(client: FastmailJMAP, *, limit: int, unread_only: bool, json_out: bool, raw: bool) -> None:
    _, by_role, _ = client.mailbox_map()
    inbox_id = by_role.get("inbox")
    if not inbox_id:
        raise FastmailError("No inbox mailbox found")
    filt: Dict[str, Any] = {"inMailbox": inbox_id}
    if unread_only:
        filt["notKeyword"] = "$seen"
    _list(client, filt, limit=limit, json_out=json_out, raw=raw)


def cmd_search(
    client: FastmailJMAP,
    *,
    query: str,
    limit: int,
    from_addr: Optional[str],
    after: Optional[str],
    before: Optional[str],
    json_out: bool,
    raw: bool,
) -> None:
    filt: Dict[str, Any] = {"text": query}
    if from_addr:
        filt["from"] = from_addr
    if after:
        filt["after"] = f"{after}T00:00:00Z"
    if before:
        filt["before"] = f"{before}T23:59:59Z"
    _list(client, filt, limit=limit, json_out=json_out, raw=raw)


def cmd_read(client: FastmailJMAP, *, email_id: str, full: bool, raw: bool) -> None:
    max_bytes = int(os.environ.get("FASTMAIL_MAX_BODY_BYTES") or (50000 if full else 5000))
    resp = client.call(
        [
            [
                "Email/get",
                {
                    "accountId": None,
                    "ids": [email_id],
                    "properties": [
                        "subject",
                        "from",
                        "to",
                        "cc",
                        "receivedAt",
                        "textBody",
                        "htmlBody",
                        "bodyValues",
                        "keywords",
                    ],
                    "fetchTextBodyValues": True,
                    "fetchHTMLBodyValues": True,
                    "maxBodyValueBytes": max_bytes,
                },
                "g",
            ]
        ],
        using=USING_CORE_MAIL,
    )
    emails = resp["methodResponses"][0][1].get("list") or []
    if not emails:
        print("Email not found")
        return

    e = emails[0]
    fr = e.get("from") or []
    fr_addr = fr[0].get("email") if fr else None
    to_list = e.get("to") or []
    to_line = ", ".join((x.get("email") or "?") for x in to_list)
    unread = "$seen" not in (e.get("keywords") or {})

    subj = e.get("subject") or ""
    body = _extract_text_body(e) or "(no body)"
    if not raw:
        subj = redact_text(subj)
        body = redact_text(body)
        to_line = redact_text(to_line)

    print(f"Subject: {subj}")
    print(f"From:    {_mask_email_addr(fr_addr)}")
    print(f"To:      {to_line}")
    print(f"Date:    {e.get('receivedAt')}")
    print(f"Status:  {'UNREAD' if unread else 'read'}")
    print("-" * 72)
    print(body)


def _pick_identity(client: FastmailJMAP) -> str:
    identity_id = os.environ.get("FASTMAIL_IDENTITY_ID")
    identity_email = os.environ.get("FASTMAIL_IDENTITY_EMAIL")

    resp = client.call([["Identity/get", {"accountId": None}, "i"]], using=USING_CORE_MAIL_SEND)
    identities = resp["methodResponses"][0][1].get("list") or []
    if not identities:
        raise FastmailError("No sending identities found")

    if identity_id:
        for it in identities:
            if it.get("id") == identity_id:
                return identity_id
        raise FastmailError("FASTMAIL_IDENTITY_ID not found in Identity/get")

    if identity_email:
        for it in identities:
            if (it.get("email") or "").lower() == identity_email.lower():
                return it.get("id")
        raise FastmailError("FASTMAIL_IDENTITY_EMAIL not found in Identity/get")

    return identities[0].get("id")


def cmd_send(client: FastmailJMAP, *, to_addr: str, subject: str, body: str, from_addr: Optional[str]) -> None:
    client.require_writes_enabled()

    identity_id = _pick_identity(client)

    # Determine sender
    sender = from_addr or os.environ.get("FASTMAIL_IDENTITY_EMAIL")
    if not sender:
        # Fetch email for identity_id
        resp = client.call([["Identity/get", {"accountId": None}, "i"]], using=USING_CORE_MAIL_SEND)
        identities = resp["methodResponses"][0][1].get("list") or []
        for it in identities:
            if it.get("id") == identity_id:
                sender = it.get("email")
                break
    if not sender:
        raise FastmailError("Could not determine sender email; set FASTMAIL_IDENTITY_EMAIL")

    # Build draft
    _, by_role, _ = client.mailbox_map()
    drafts_id = by_role.get("drafts")

    draft: Dict[str, Any] = {
        "from": [{"email": sender}],
        "to": [{"email": to_addr}],
        "subject": subject,
        "textBody": [{"partId": "body", "type": "text/plain"}],
        "bodyValues": {"body": {"value": body}},
        "keywords": {"$draft": True},
        "mailboxIds": {},
    }
    if drafts_id:
        draft["mailboxIds"][drafts_id] = True

    on_success_update: Dict[str, Any] = {"keywords/$draft": None}
    sent_id = by_role.get("sent")
    if sent_id:
        on_success_update[f"mailboxIds/{sent_id}"] = True
    if drafts_id:
        on_success_update[f"mailboxIds/{drafts_id}"] = None

    resp = client.call(
        [
            ["Email/set", {"accountId": None, "create": {"draft1": draft}}, "c"],
            [
                "EmailSubmission/set",
                {
                    "accountId": None,
                    "create": {"sub1": {"emailId": "#draft1", "identityId": identity_id}},
                    "onSuccessUpdateEmail": {"#sub1": on_success_update},
                },
                "s",
            ],
        ],
        using=USING_CORE_MAIL_SEND,
    )

    created = resp["methodResponses"][0][1].get("created") or {}
    if "draft1" not in created:
        not_created = resp["methodResponses"][0][1].get("notCreated") or {}
        raise FastmailError(f"Send failed: {not_created}")

    print("Sent.")


def build_client_for_read() -> FastmailJMAP:
    token = get_required_env("FASTMAIL_TOKEN")
    return FastmailJMAP(token)


def build_client_for_send() -> FastmailJMAP:
    token = os.environ.get("FASTMAIL_TOKEN_SEND") or get_required_env("FASTMAIL_TOKEN")
    return FastmailJMAP(token)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--json", action="store_true")
    p.add_argument("--raw", action="store_true", help="Disable redaction in output")

    sp = p.add_subparsers(dest="cmd", required=True)

    p_inbox = sp.add_parser("inbox")
    p_inbox.add_argument("--limit", type=int, default=10)
    p_inbox.add_argument("--unread", action="store_true")

    p_unread = sp.add_parser("unread")
    p_unread.add_argument("--limit", type=int, default=50)

    p_search = sp.add_parser("search")
    p_search.add_argument("query")
    p_search.add_argument("--limit", type=int, default=10)
    p_search.add_argument("--from", dest="from_addr")
    p_search.add_argument("--after")
    p_search.add_argument("--before")

    p_read = sp.add_parser("read")
    p_read.add_argument("email_id")
    p_read.add_argument("--full", action="store_true")

    sp.add_parser("mailboxes")

    p_send = sp.add_parser("send")
    p_send.add_argument("--to", required=True)
    p_send.add_argument("--subject", required=True)
    p_send.add_argument("--body", required=True)
    p_send.add_argument("--from", dest="from_addr")

    args = p.parse_args()

    try:
        if args.cmd in ("send",):
            client = build_client_for_send()
        else:
            client = build_client_for_read()

        if args.cmd == "mailboxes":
            cmd_mailboxes(client, raw=args.raw)
        elif args.cmd == "inbox":
            cmd_inbox(client, limit=args.limit, unread_only=args.unread, json_out=args.json, raw=args.raw)
        elif args.cmd == "unread":
            cmd_inbox(client, limit=args.limit, unread_only=True, json_out=args.json, raw=args.raw)
        elif args.cmd == "search":
            cmd_search(
                client,
                query=args.query,
                limit=args.limit,
                from_addr=args.from_addr,
                after=args.after,
                before=args.before,
                json_out=args.json,
                raw=args.raw,
            )
        elif args.cmd == "read":
            cmd_read(client, email_id=args.email_id, full=args.full, raw=args.raw)
        elif args.cmd == "send":
            cmd_send(client, to_addr=args.to, subject=args.subject, body=args.body, from_addr=args.from_addr)
    except Exception as e:
        exit_with_error(e)


if __name__ == "__main__":
    main()
