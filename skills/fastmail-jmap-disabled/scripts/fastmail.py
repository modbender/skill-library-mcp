#!/usr/bin/env python3
"""Fastmail JMAP CLI — check, search, read, and manage emails.

Usage:
    fastmail.py inbox [--limit N] [--unread]
    fastmail.py unread
    fastmail.py search <query> [--limit N] [--from ADDR] [--after DATE] [--before DATE] [--json] [--ids]
    fastmail.py read <email-id>
    fastmail.py mailboxes
    fastmail.py send <to> <subject> <body> [--from ADDR]
    fastmail.py move <email-id> <mailbox-name>
    fastmail.py mark-read <email-id>
    fastmail.py mark-unread <email-id>
    fastmail.py trash <email-id>

Env: FASTMAIL_TOKEN (API token with Email + Email Submission scopes)
     FASTMAIL_IDENTITY (optional — sender email for send command)
"""

import json, os, sys, urllib.request

TOKEN = os.environ.get("FASTMAIL_TOKEN")
if not TOKEN:
    print("Error: FASTMAIL_TOKEN env var not set.", file=sys.stderr)
    print("Get one at: https://app.fastmail.com/settings/security/tokens", file=sys.stderr)
    sys.exit(1)

API = "https://api.fastmail.com/jmap/api/"
USING = ["urn:ietf:params:jmap:core", "urn:ietf:params:jmap:mail"]
USING_SEND = ["urn:ietf:params:jmap:core", "urn:ietf:params:jmap:mail", "urn:ietf:params:jmap:submission"]
ACCOUNT = None
IDENTITY = None


def _session():
    global ACCOUNT, IDENTITY
    if ACCOUNT:
        return
    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    req = urllib.request.Request("https://api.fastmail.com/jmap/session", headers=headers)
    session = json.loads(urllib.request.urlopen(req).read())
    ACCOUNT = list(session["accounts"].keys())[0]


def _call(method_calls, using=None):
    _session()
    for mc in method_calls:
        if isinstance(mc[1], dict) and mc[1].get("accountId") is None:
            mc[1]["accountId"] = ACCOUNT
    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    body = json.dumps({"using": using or USING, "methodCalls": method_calls}).encode()
    req = urllib.request.Request(API, body, headers, method="POST")
    resp = json.loads(urllib.request.urlopen(req).read())
    # Check for errors
    for mr in resp.get("methodResponses", []):
        if mr[0] == "error":
            print(f"Error: {mr[1].get('type', 'unknown')} — {mr[1].get('description', '')}", file=sys.stderr)
            sys.exit(1)
    return resp


def _mailbox_map():
    """Return {name_lower: id}, {role: id}, {id: name} dicts."""
    resp = _call([["Mailbox/get", {"accountId": None, "properties": ["name", "role", "parentId"]}, "0"]])
    by_name, by_role, by_id = {}, {}, {}
    for mb in resp["methodResponses"][0][1]["list"]:
        by_name[mb["name"].lower()] = mb["id"]
        if mb.get("role"):
            by_role[mb["role"]] = mb["id"]
        by_id[mb["id"]] = mb["name"]
    return by_name, by_role, by_id


def _get_identity():
    """Get the first identity (sender address) for the account."""
    override = os.environ.get("FASTMAIL_IDENTITY")
    if override:
        return override
    resp = _call([["Identity/get", {"accountId": None}, "0"]],
                 using=USING_SEND)
    identities = resp["methodResponses"][0][1]["list"]
    if not identities:
        print("Error: No sending identities found.", file=sys.stderr)
        sys.exit(1)
    return identities[0]["id"], identities[0]["email"]


# ─── Commands ───────────────────────────────────────────────────

def cmd_mailboxes():
    resp = _call([
        ["Mailbox/get", {"accountId": None,
                         "properties": ["name", "role", "totalEmails", "unreadEmails"]}, "0"]
    ])
    for mb in sorted(resp["methodResponses"][0][1]["list"], key=lambda m: m["name"]):
        role = mb.get("role") or ""
        print(f"  {mb['name']:25s} role={role:12s} total={mb['totalEmails']:5d} unread={mb['unreadEmails']}")


def cmd_inbox(limit=10, unread_only=False, output_format="human"):
    _, by_role, _ = _mailbox_map()
    inbox_id = by_role.get("inbox")
    if not inbox_id:
        print("Error: No inbox mailbox found.", file=sys.stderr)
        return
    filt = {"inMailbox": inbox_id}
    if unread_only:
        filt["notKeyword"] = "$seen"
    _list_emails(filt, limit, output_format=output_format)


def cmd_unread():
    """Show unread count per mailbox, then list unread inbox emails."""
    resp = _call([
        ["Mailbox/get", {"accountId": None,
                         "properties": ["name", "role", "unreadEmails"]}, "0"]
    ])
    total = 0
    for mb in resp["methodResponses"][0][1]["list"]:
        if mb["unreadEmails"] > 0:
            print(f"  {mb['name']:25s} {mb['unreadEmails']} unread")
            total += mb["unreadEmails"]
    if total == 0:
        print("  No unread emails.")
        return
    print(f"\n  Total: {total} unread\n")
    cmd_inbox(limit=min(total, 50), unread_only=True)


def cmd_search(query, limit=10, from_addr=None, after=None, before=None, output_format="human"):
    filt = {"text": query}
    if from_addr:
        filt["from"] = from_addr
    if after:
        filt["after"] = f"{after}T00:00:00Z"
    if before:
        filt["before"] = f"{before}T23:59:59Z"
    _list_emails(filt, limit, output_format=output_format)


def cmd_read(email_id):
    resp = _call([
        ["Email/get", {
            "accountId": None,
            "ids": [email_id],
            "properties": ["subject", "from", "to", "cc", "receivedAt", "textBody", "htmlBody",
                           "bodyValues", "keywords", "mailboxIds"],
            "fetchTextBodyValues": True,
            "fetchHTMLBodyValues": True,
            "maxBodyValueBytes": 50000
        }, "g"],
    ])
    emails = resp["methodResponses"][0][1]["list"]
    if not emails:
        print(f"  Email {email_id} not found.")
        return
    e = emails[0]
    fr = e["from"][0]["email"] if e.get("from") else "?"
    fr_name = e["from"][0].get("name", "") if e.get("from") else ""
    to = ", ".join(f"{r.get('name', '')} <{r['email']}>" for r in e.get("to", []))
    cc = ", ".join(f"{r.get('name', '')} <{r['email']}>" for r in e.get("cc", [])) if e.get("cc") else ""
    unread = "$seen" not in e.get("keywords", {})

    print(f"  Subject: {e['subject']}")
    print(f"  From:    {fr_name} <{fr}>")
    print(f"  To:      {to}")
    if cc:
        print(f"  CC:      {cc}")
    print(f"  Date:    {e['receivedAt']}")
    print(f"  Status:  {'UNREAD' if unread else 'read'}")
    print(f"  {'─' * 60}")

    body_text = ""
    for part in e.get("textBody", []):
        val = e.get("bodyValues", {}).get(part["partId"], {})
        if val.get("value"):
            body_text += val["value"]
    if not body_text:
        for part in e.get("htmlBody", []):
            val = e.get("bodyValues", {}).get(part["partId"], {})
            if val.get("value"):
                body_text += val["value"]
    print(body_text[:5000] if body_text else "  (no body)")


def cmd_move(email_id, mailbox_name):
    by_name, by_role, _ = _mailbox_map()
    target_id = by_name.get(mailbox_name.lower()) or by_role.get(mailbox_name.lower())
    if not target_id:
        print(f"Error: Mailbox '{mailbox_name}' not found.", file=sys.stderr)
        print(f"Available: {', '.join(sorted(by_name.keys()))}", file=sys.stderr)
        sys.exit(1)

    # Get current mailboxIds
    resp = _call([["Email/get", {"accountId": None, "ids": [email_id], "properties": ["mailboxIds"]}, "g"]])
    emails = resp["methodResponses"][0][1]["list"]
    if not emails:
        print(f"Error: Email {email_id} not found.", file=sys.stderr)
        sys.exit(1)

    new_mailboxes = {target_id: True}
    _call([["Email/set", {
        "accountId": None,
        "update": {email_id: {"mailboxIds": new_mailboxes}}
    }, "m"]])
    print(f"  ✅ Moved to {mailbox_name}")


def cmd_mark(email_id, read=True):
    keyword_patch = {"keywords/$seen": read}
    _call([["Email/set", {
        "accountId": None,
        "update": {email_id: keyword_patch}
    }, "m"]])
    print(f"  ✅ Marked {'read' if read else 'unread'}")


def cmd_trash(email_id):
    _, by_role, _ = _mailbox_map()
    trash_id = by_role.get("trash")
    if not trash_id:
        print("Error: No trash mailbox found.", file=sys.stderr)
        sys.exit(1)
    cmd_move(email_id, "trash")


def cmd_send(to_addr, subject, body, from_addr=None):
    identity_id, identity_email = _get_identity()
    sender = from_addr or identity_email

    # Create draft
    draft = {
        "from": [{"email": sender}],
        "to": [{"email": to_addr}],
        "subject": subject,
        "textBody": [{"partId": "body", "type": "text/plain"}],
        "bodyValues": {"body": {"value": body}},
        "keywords": {"$draft": True},
        "mailboxIds": {}
    }

    # Get drafts mailbox
    _, by_role, _ = _mailbox_map()
    drafts_id = by_role.get("drafts")
    if drafts_id:
        draft["mailboxIds"][drafts_id] = True

    resp = _call([
        ["Email/set", {"accountId": None, "create": {"draft1": draft}}, "c"],
        ["EmailSubmission/set", {
            "accountId": None,
            "create": {"sub1": {
                "emailId": "#draft1",
                "identityId": identity_id,
            }},
            "onSuccessUpdateEmail": {"#sub1": {
                "mailboxIds/" + (by_role.get("sent") or ""): True,
                "mailboxIds/" + (drafts_id or ""): None,
                "keywords/$draft": None,
            }}
        }, "s"]
    ], using=USING_SEND)

    # Check for creation errors
    created = resp["methodResponses"][0][1].get("created", {})
    if "draft1" in created:
        print(f"  ✅ Sent to {to_addr}")
    else:
        not_created = resp["methodResponses"][0][1].get("notCreated", {})
        print(f"  ❌ Send failed: {json.dumps(not_created, indent=2)}", file=sys.stderr)
        sys.exit(1)


# ─── Helpers ────────────────────────────────────────────────────

def _list_emails(filt, limit, output_format="human"):
    resp = _call([
        ["Email/query", {
            "accountId": None,
            "filter": filt,
            "sort": [{"property": "receivedAt", "isAscending": False}],
            "limit": limit
        }, "q"],
        ["Email/get", {
            "accountId": None,
            "#ids": {"resultOf": "q", "name": "Email/query", "path": "/ids"},
            "properties": ["id", "subject", "from", "to", "receivedAt", "preview", "keywords", "size"]
        }, "g"],
    ])
    total = resp["methodResponses"][0][1].get("total", "?")
    emails = resp["methodResponses"][1][1]["list"]

    if output_format == "ids":
        for e in emails:
            print(e["id"])
        return

    if output_format == "json":
        import json as _json
        out = []
        for e in emails:
            out.append({
                "id": e["id"],
                "from": e["from"][0]["email"] if e.get("from") else None,
                "subject": e.get("subject", ""),
                "receivedAt": e.get("receivedAt", ""),
                "unread": "$seen" not in e.get("keywords", {}),
            })
        print(_json.dumps(out, indent=2))
        return

    print(f"  Showing {len(emails)} of {total} results\n")
    for e in emails:
        fr = e["from"][0]["email"] if e.get("from") else "?"
        fr_name = e["from"][0].get("name", "") if e.get("from") else ""
        unread = "$seen" not in e.get("keywords", {})
        flag = "🔴" if unread else "  "
        dt = e["receivedAt"][:16].replace("T", " ")
        subj = e.get("subject", "(no subject)")
        print(f"  {flag} {dt} | {fr:30s} | {subj}")
        print(f"       {e['preview'][:120]}")
        print(f"       id: {e['id']}")
        print()


# ─── Main ───────────────────────────────────────────────────────

def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return

    cmd = args[0]

    # Parse common flags
    limit = 10
    output_format = "human"
    from_addr = after = before = None
    for i, a in enumerate(args):
        if a == "--limit" and i + 1 < len(args):
            limit = int(args[i + 1])
        if a == "--from" and i + 1 < len(args):
            from_addr = args[i + 1]
        if a == "--after" and i + 1 < len(args):
            after = args[i + 1]
        if a == "--before" and i + 1 < len(args):
            before = args[i + 1]
        if a == "--format" and i + 1 < len(args):
            output_format = args[i + 1]  # human, json, ids
        if a == "--ids":
            output_format = "ids"
        if a == "--json":
            output_format = "json"

    if cmd == "mailboxes":
        cmd_mailboxes()
    elif cmd == "inbox":
        unread = "--unread" in args
        cmd_inbox(limit=limit, unread_only=unread, output_format=output_format)
    elif cmd == "unread":
        cmd_unread()
    elif cmd == "search" and len(args) >= 2:
        cmd_search(args[1], limit=limit, from_addr=from_addr, after=after, before=before, output_format=output_format)
    elif cmd == "read" and len(args) >= 2:
        cmd_read(args[1])
    elif cmd == "move" and len(args) >= 3:
        cmd_move(args[1], args[2])
    elif cmd == "mark-read" and len(args) >= 2:
        cmd_mark(args[1], read=True)
    elif cmd == "mark-unread" and len(args) >= 2:
        cmd_mark(args[1], read=False)
    elif cmd == "trash" and len(args) >= 2:
        cmd_trash(args[1])
    elif cmd == "send" and len(args) >= 4:
        cmd_send(args[1], args[2], args[3], from_addr=from_addr)
    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
