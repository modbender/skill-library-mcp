#!/usr/bin/env python3
"""Fastmail JMAP Contacts CLI — search and read contacts.

Usage:
    contacts.py list [--limit N]
    contacts.py search <query>
    contacts.py get <contact-id>

Env: FASTMAIL_TOKEN (API token with Contacts scope)
"""

import json, os, sys, urllib.request

TOKEN = os.environ.get("FASTMAIL_TOKEN")
if not TOKEN:
    print("Error: FASTMAIL_TOKEN env var not set.", file=sys.stderr)
    sys.exit(1)

USING = ["urn:ietf:params:jmap:core", "urn:ietf:params:jmap:contacts"]
ACCOUNT = None


def _session():
    global ACCOUNT
    if ACCOUNT:
        return
    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    req = urllib.request.Request("https://api.fastmail.com/jmap/session", headers=headers)
    session = json.loads(urllib.request.urlopen(req).read())
    ACCOUNT = list(session["accounts"].keys())[0]


def _call(method_calls):
    _session()
    for mc in method_calls:
        if isinstance(mc[1], dict) and mc[1].get("accountId") is None:
            mc[1]["accountId"] = ACCOUNT
    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    body = json.dumps({"using": USING, "methodCalls": method_calls}).encode()
    req = urllib.request.Request("https://api.fastmail.com/jmap/api/", body, headers, method="POST")
    resp = json.loads(urllib.request.urlopen(req).read())
    for mr in resp.get("methodResponses", []):
        if mr[0] == "error":
            print(f"Error: {mr[1].get('type')} — {mr[1].get('description', '')}", file=sys.stderr)
            sys.exit(1)
    return resp


def _format_contact(c):
    name = c.get("name", {})
    full = name.get("full") or f"{name.get('given', '')} {name.get('surname', '')}".strip() or "(no name)"
    emails = [v["address"] for v in c.get("emails", {}).values() if "address" in v]
    phones = [v["value"] for v in c.get("phones", {}).values() if "value" in v]
    org = next((v.get("name", "") for v in c.get("organizations", {}).values()), "")
    return full, emails, phones, org


def cmd_list(limit=50):
    resp = _call([
        ["ContactCard/query", {"accountId": None, "limit": limit, "sort": [{"property": "name/full"}]}, "0"],
        ["ContactCard/get", {"accountId": None,
                              "#ids": {"resultOf": "0", "name": "ContactCard/query", "path": "/ids"},
                              "properties": ["name", "emails", "phones", "organizations"]}, "1"]
    ])
    total = resp["methodResponses"][0][1].get("total", 0)
    contacts = resp["methodResponses"][1][1]["list"]
    print(f"Showing {len(contacts)} of {total} contacts\n")
    for c in contacts:
        full, emails, phones, org = _format_contact(c)
        parts = [full]
        if org:
            parts.append(f"[{org}]")
        if emails:
            parts.append(emails[0])
        if phones:
            parts.append(phones[0])
        print("  " + "  |  ".join(parts))


def cmd_search(query):
    # Fetch all and filter client-side (JMAP Contacts search support varies)
    resp = _call([
        ["ContactCard/query", {"accountId": None, "limit": 500}, "0"],
        ["ContactCard/get", {"accountId": None,
                              "#ids": {"resultOf": "0", "name": "ContactCard/query", "path": "/ids"},
                              "properties": ["name", "emails", "phones", "organizations"]}, "1"]
    ])
    contacts = resp["methodResponses"][1][1]["list"]
    q = query.lower()
    results = []
    for c in contacts:
        full, emails, phones, org = _format_contact(c)
        haystack = " ".join([full, org] + emails + phones).lower()
        if q in haystack:
            results.append((c["id"], full, emails, phones, org))

    if not results:
        print(f"No contacts found matching '{query}'")
        return

    print(f"{len(results)} contact(s) matching '{query}':\n")
    for cid, full, emails, phones, org in results:
        print(f"  {full}", end="")
        if org:
            print(f"  [{org}]", end="")
        if emails:
            print(f"  |  {', '.join(emails)}", end="")
        if phones:
            print(f"  |  {', '.join(phones)}", end="")
        print(f"  (id: {cid})")


def cmd_get(contact_id):
    resp = _call([
        ["ContactCard/get", {"accountId": None, "ids": [contact_id]}, "0"]
    ])
    contacts = resp["methodResponses"][0][1]["list"]
    if not contacts:
        print(f"Contact '{contact_id}' not found.")
        sys.exit(1)
    c = contacts[0]
    name = c.get("name", {})
    full = name.get("full") or f"{name.get('given', '')} {name.get('surname', '')}".strip() or "(no name)"
    print(f"Name:   {full}")
    if name.get("given"):
        print(f"Given:  {name['given']}")
    if name.get("surname"):
        print(f"Family: {name['surname']}")
    for v in c.get("organizations", {}).values():
        print(f"Org:    {v.get('name', '')}")
    for v in c.get("emails", {}).values():
        ctx = list(v.get("contexts", {}).keys())
        label = f"[{ctx[0]}]" if ctx else ""
        print(f"Email:  {v.get('address', '')}  {label}")
    for v in c.get("phones", {}).values():
        ctx = list(v.get("contexts", {}).keys())
        label = f"[{ctx[0]}]" if ctx else ""
        print(f"Phone:  {v.get('value', '')}  {label}")
    for v in c.get("addresses", {}).values():
        parts = [v.get("street",""), v.get("locality",""), v.get("region",""), v.get("country","")]
        addr = ", ".join(p for p in parts if p)
        if addr:
            print(f"Addr:   {addr}")
    if c.get("notes"):
        for v in c["notes"].values():
            print(f"Notes:  {v.get('note','')}")


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(0)

    cmd = args[0]
    limit = 50
    if "--limit" in args:
        idx = args.index("--limit")
        limit = int(args[idx + 1])

    if cmd == "list":
        cmd_list(limit=limit)
    elif cmd == "search" and len(args) >= 2:
        cmd_search(args[1])
    elif cmd == "get" and len(args) >= 2:
        cmd_get(args[1])
    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
