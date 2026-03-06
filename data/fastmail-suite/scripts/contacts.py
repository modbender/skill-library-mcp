#!/usr/bin/env python3
"""Fastmail contacts CLI (JMAP) — safe-by-default.

Read ops use FASTMAIL_TOKEN.
Write ops (create/update/delete) are intentionally NOT implemented in v1.

Examples:
  python3 scripts/contacts.py list --limit 20
  python3 scripts/contacts.py search "alice"
  python3 scripts/contacts.py get <contact-id>

Flags:
  --json    JSON output (still redacted unless --raw)
  --raw     disable redaction for output
"""

from __future__ import annotations

import argparse
from typing import Any, Dict, List

from jmap_client import (
    FastmailError,
    FastmailJMAP,
    exit_with_error,
    get_required_env,
    redact_text,
    safe_print,
)


USING_CONTACTS = ["urn:ietf:params:jmap:core", "urn:ietf:params:jmap:contacts"]

# Fastmail's JMAP Contacts implementation uses ContactCard/* methods.


def _client() -> FastmailJMAP:
    return FastmailJMAP(get_required_env("FASTMAIL_TOKEN"))


def _full_name(name_obj: Dict[str, Any]) -> str:
    # Fastmail ContactCard name is an object: { full, given, surname, ... }
    full = (name_obj.get("full") or "").strip()
    if full:
        return full
    given = (name_obj.get("given") or "").strip()
    surname = (name_obj.get("surname") or "").strip()
    combo = (given + " " + surname).strip()
    return combo or "(no name)"


def _summarize(contact: Dict[str, Any], *, raw: bool) -> Dict[str, Any]:
    name_obj = contact.get("name") or {}
    emails_obj = contact.get("emails") or {}
    phones_obj = contact.get("phones") or {}
    orgs_obj = contact.get("organizations") or {}

    emails = [v.get("address") for v in emails_obj.values() if isinstance(v, dict) and v.get("address")]
    # Fastmail ContactCard phone field is usually "number" (not "value").
    phones = [
        (v.get("number") or v.get("value"))
        for v in phones_obj.values()
        if isinstance(v, dict) and (v.get("number") or v.get("value"))
    ]
    org = next((v.get("name") for v in orgs_obj.values() if isinstance(v, dict) and v.get("name")), "")

    out = {
        "id": contact.get("id"),
        "name": _full_name(name_obj),
        "org": org,
        "emails": emails,
        "phones": phones,
    }
    if not raw:
        out["name"] = redact_text(out["name"])
        out["org"] = redact_text(out["org"])
    return out


def cmd_list(*, limit: int, json_out: bool, raw: bool) -> None:
    c = _client()
    resp = c.call(
        [
            [
                "ContactCard/query",
                {"accountId": None, "limit": limit},
                "q",
            ],
            [
                "ContactCard/get",
                {
                    "accountId": None,
                    "#ids": {"resultOf": "q", "name": "ContactCard/query", "path": "/ids"},
                    "properties": ["id", "name", "emails", "phones", "organizations"],
                },
                "g",
            ],
        ],
        using=USING_CONTACTS,
    )

    total = resp["methodResponses"][0][1].get("total")
    items = resp["methodResponses"][1][1].get("list") or []

    out_items = [_summarize(x, raw=raw) for x in items]
    out_items.sort(key=lambda x: (x.get("name") or "").lower())
    if json_out:
        safe_print({"total": total, "items": out_items}, raw=raw)
        return

    print(f"Showing {len(out_items)} of {total} contacts\n")
    for it in out_items:
        name = it.get("name") or ""
        emails = ", ".join(it.get("emails") or [])
        phones = ", ".join(it.get("phones") or [])
        if not raw:
            emails = redact_text(emails)
            phones = redact_text(phones)
        print(f"- {name} (id: {it.get('id')})")
        if emails:
            print(f"    emails: {emails}")
        if phones:
            print(f"    phones: {phones}")


def cmd_search(*, query: str, limit: int, json_out: bool, raw: bool) -> None:
    # Fastmail ContactCard/query has limited server-side filtering; do client-side matching.
    # Fetch a bounded working set to avoid huge pulls on large accounts.
    fetch_limit = min(max(limit * 20, 100), 1000)

    c = _client()
    resp = c.call(
        [
            ["ContactCard/query", {"accountId": None, "limit": fetch_limit}, "q"],
            [
                "ContactCard/get",
                {
                    "accountId": None,
                    "#ids": {"resultOf": "q", "name": "ContactCard/query", "path": "/ids"},
                    "properties": ["id", "name", "emails", "phones", "organizations"],
                },
                "g",
            ],
        ],
        using=USING_CONTACTS,
    )

    items = resp["methodResponses"][1][1].get("list") or []
    q = query.strip().lower()

    def match(x: Dict[str, Any]) -> bool:
        name = _full_name(x.get("name") or {}).lower()
        if q in name:
            return True
        orgs = x.get("organizations") or {}
        for v in orgs.values():
            if isinstance(v, dict) and q in (v.get("name") or "").lower():
                return True
        emails_obj = x.get("emails") or {}
        for v in emails_obj.values():
            if isinstance(v, dict) and q in (v.get("address") or "").lower():
                return True
        phones_obj = x.get("phones") or {}
        for v in phones_obj.values():
            if isinstance(v, dict) and q in ((v.get("number") or v.get("value") or "").lower()):
                return True
        return False

    filtered = [x for x in items if match(x)][:limit]
    out_items = [_summarize(x, raw=raw) for x in filtered]

    if json_out:
        safe_print({"items": out_items}, raw=raw)
        return

    for it in out_items:
        name = it.get("name") or ""
        org = it.get("org") or ""
        emails = ", ".join(it.get("emails") or [])
        phones = ", ".join(it.get("phones") or [])
        if not raw:
            emails = redact_text(emails)
            phones = redact_text(phones)
            org = redact_text(org)
        line = f"- {name}"
        if org:
            line += f" [{org}]"
        line += f" (id: {it.get('id')})"
        print(line)
        if emails:
            print(f"    emails: {emails}")
        if phones:
            print(f"    phones: {phones}")


def _fmt_value(v: str, *, raw: bool) -> str:
    return v if raw else redact_text(v)


def _fmt_contexts(ctx_obj: Any) -> str:
    # Fastmail ContactCard often uses: { contexts: { home: true, work: true } }
    if not isinstance(ctx_obj, dict):
        return ""
    keys = sorted([k for k, vv in ctx_obj.items() if vv])
    return ",".join(keys)


def _fmt_address(addr: Dict[str, Any]) -> str:
    # Fastmail uses either direct keys OR a components array.
    # Example components: [{kind: name, value: ...}, {kind: locality, value: ...}, ...]
    if isinstance(addr.get("components"), list):
        comp_map: Dict[str, List[str]] = {}
        for c in addr.get("components") or []:
            if not isinstance(c, dict):
                continue
            kind = (c.get("kind") or "").strip()
            val = (c.get("value") or "").strip()
            if not val:
                continue
            comp_map.setdefault(kind, []).append(val)

        # Prefer a stable order
        ordered_kinds = ["name", "street", "locality", "region", "postcode", "country"]
        parts: List[str] = []
        for k in ordered_kinds:
            parts.extend(comp_map.get(k, []))
        # Include any remaining kinds
        for k in sorted(set(comp_map.keys()) - set(ordered_kinds)):
            parts.extend(comp_map[k])
        return ", ".join(parts)

    parts = [addr.get("street"), addr.get("locality"), addr.get("region"), addr.get("postcode"), addr.get("country")]
    parts = [p.strip() for p in parts if isinstance(p, str) and p.strip()]
    return ", ".join(parts)


def cmd_get(*, contact_id: str, json_out: bool, raw: bool, dump: bool) -> None:
    c = _client()

    # When dump=true, request all properties (properties=None) so we can see Fastmail's full shape.
    props = None if dump else [
        "id",
        "name",
        "emails",
        "phones",
        "organizations",
        "addresses",
        "notes",
        "birthday",
        "anniversaries",
    ]

    resp = c.call(
        [[
            "ContactCard/get",
            {
                "accountId": None,
                "ids": [contact_id],
                "properties": props,
            },
            "g",
        ]],
        using=USING_CONTACTS,
    )
    items = resp["methodResponses"][0][1].get("list") or []
    if not items:
        raise FastmailError(f"Contact not found: {contact_id}")

    obj = items[0]
    if dump:
        safe_print(obj, raw=raw)
        return

    summary = _summarize(obj, raw=raw)

    if json_out:
        # Keep JSON stable (summary fields), but include labeled entries when available.
        emails_obj = obj.get("emails") or {}
        phones_obj = obj.get("phones") or {}
        addrs_obj = obj.get("addresses") or {}
        notes_obj = obj.get("notes") or {}

        summary["emails_labeled"] = [
            {"address": v.get("address"), "contexts": sorted((v.get("contexts") or {}).keys())}
            for v in emails_obj.values()
            if isinstance(v, dict) and v.get("address")
        ]
        summary["phones_labeled"] = [
            {
                "number": (v.get("number") or v.get("value")),
                "contexts": sorted((v.get("contexts") or {}).keys()),
                "features": v.get("features") if isinstance(v.get("features"), dict) else None,
            }
            for v in phones_obj.values()
            if isinstance(v, dict) and (v.get("number") or v.get("value"))
        ]
        summary["addresses_labeled"] = [
            {
                "address": _fmt_address(v),
                "contexts": sorted((v.get("contexts") or {}).keys()),
            }
            for v in addrs_obj.values()
            if isinstance(v, dict) and _fmt_address(v)
        ]
        summary["notes"] = [
            v.get("note")
            for v in notes_obj.values()
            if isinstance(v, dict) and v.get("note")
        ]

        # Birthday is represented as an anniversary with kind="birth".
        ann = obj.get("anniversaries") or {}
        birth = None
        for v in ann.values():
            if isinstance(v, dict) and v.get("kind") == "birth" and isinstance(v.get("date"), dict):
                d = v["date"]
                birth = {
                    "year": d.get("year"),
                    "month": d.get("month"),
                    "day": d.get("day"),
                }
                break
        summary["birthday"] = birth

        safe_print(summary, raw=raw)
        return

    print(f"Name: {summary.get('name')}")
    if summary.get("org"):
        print(f"Org:  {summary.get('org')}")

    emails_obj = obj.get("emails") or {}
    if emails_obj:
        print("Emails:")
        for v in emails_obj.values():
            if not isinstance(v, dict) or not v.get("address"):
                continue
            addr = _fmt_value(v["address"], raw=raw)
            ctx = _fmt_contexts(v.get("contexts"))
            suffix = f" [{ctx}]" if ctx else ""
            print(f"  - {addr}{suffix}")

    phones_obj = obj.get("phones") or {}
    if phones_obj:
        printed = False
        for v in phones_obj.values():
            if not isinstance(v, dict):
                continue
            num = v.get("number") or v.get("value")
            if not num:
                continue
            if not printed:
                print("Phones:")
                printed = True
            val = _fmt_value(str(num), raw=raw)
            ctx = _fmt_contexts(v.get("contexts"))
            suffix = f" [{ctx}]" if ctx else ""
            print(f"  - {val}{suffix}")

    addrs_obj = obj.get("addresses") or {}
    if addrs_obj:
        printed = False
        for v in addrs_obj.values():
            if not isinstance(v, dict):
                continue
            addr = _fmt_address(v)
            if not addr:
                continue
            if not printed:
                print("Addresses:")
                printed = True
            addr = _fmt_value(addr, raw=raw)
            ctx = _fmt_contexts(v.get("contexts"))
            suffix = f" [{ctx}]" if ctx else ""
            print(f"  - {addr}{suffix}")

    notes_obj = obj.get("notes") or {}
    if notes_obj:
        notes = [v.get("note") for v in notes_obj.values() if isinstance(v, dict) and v.get("note")]
        if notes:
            print("Notes:")
            for n in notes:
                print(f"  - {_fmt_value(n, raw=raw)}")

    ann = obj.get("anniversaries") or {}
    birth = None
    for v in ann.values():
        if isinstance(v, dict) and v.get("kind") == "birth" and isinstance(v.get("date"), dict):
            d = v["date"]
            y = d.get("year")
            m = d.get("month")
            dd = d.get("day")
            if m and dd:
                birth = f"{y or '????'}-{int(m):02d}-{int(dd):02d}"
            break
    if birth:
        print(f"Birthday: {birth}")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--json", action="store_true")
    p.add_argument("--raw", action="store_true")
    sp = p.add_subparsers(dest="cmd", required=True)

    p_list = sp.add_parser("list")
    p_list.add_argument("--limit", type=int, default=50)

    p_search = sp.add_parser("search")
    p_search.add_argument("query")
    p_search.add_argument("--limit", type=int, default=25)

    p_get = sp.add_parser("get")
    p_get.add_argument("contact_id")
    p_get.add_argument("--dump", action="store_true", help="Print raw ContactCard JSON returned by Fastmail")

    args = p.parse_args()

    try:
        if args.cmd == "list":
            cmd_list(limit=args.limit, json_out=args.json, raw=args.raw)
        elif args.cmd == "search":
            cmd_search(query=args.query, limit=args.limit, json_out=args.json, raw=args.raw)
        elif args.cmd == "get":
            cmd_get(contact_id=args.contact_id, json_out=args.json, raw=args.raw, dump=args.dump)
    except Exception as e:
        exit_with_error(e)


if __name__ == "__main__":
    main()
