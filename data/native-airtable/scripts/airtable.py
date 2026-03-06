#!/usr/bin/env python3
"""
Airtable API — calls api.airtable.com directly.
No third-party proxy.
"""
import argparse
import json
import os
import sys
import urllib.parse
import urllib.request

BASE_URL = "https://api.airtable.com/v0"
META_URL = "https://api.airtable.com/v0/meta"


# ── Auth ──────────────────────────────────────────────────────────────────────

def get_token():
    token = os.environ.get("AIRTABLE_PAT")
    if not token:
        print("Error: AIRTABLE_PAT not set.", file=sys.stderr)
        print("Get a token at: https://airtable.com/create/tokens", file=sys.stderr)
        sys.exit(1)
    return token


def request(method, url, params=None, body=None):
    token = get_token()
    if params:
        url += "?" + urllib.parse.urlencode(params)

    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        print(f"Error {e.code}: {e.read().decode()}", file=sys.stderr)
        sys.exit(1)


# ── Commands ──────────────────────────────────────────────────────────────────

def cmd_list_bases(args):
    result = request("GET", f"{META_URL}/bases")
    bases = result.get("bases", [])
    print(f"# {len(bases)} bases\n")
    for b in bases:
        print(f"{b['id']}\t{b['name']}\t{b.get('permissionLevel', '')}")


def cmd_list_tables(args):
    result = request("GET", f"{META_URL}/bases/{args.base_id}/tables")
    tables = result.get("tables", [])
    print(f"# {len(tables)} tables\n")
    for t in tables:
        fields = [f["name"] for f in t.get("fields", [])]
        print(f"{t['id']}\t{t['name']}\t[{', '.join(fields[:5])}{'...' if len(fields) > 5 else ''}]")


def cmd_list_records(args):
    params = {"pageSize": args.limit}
    if args.view:
        params["view"] = args.view
    if args.filter:
        params["filterByFormula"] = args.filter
    if args.fields:
        for f in args.fields.split(","):
            params[f"fields[]"] = f.strip()

    result = request("GET", f"{BASE_URL}/{args.base_id}/{urllib.parse.quote(args.table)}", params=params)
    records = result.get("records", [])
    offset = result.get("offset")
    print(f"# {len(records)} records\n")
    for r in records:
        row = {"id": r["id"]}
        row.update(r.get("fields", {}))
        print(json.dumps(row))
    if offset:
        print(f"\n# More results — use --offset '{offset}' to continue")


def cmd_get_record(args):
    result = request("GET", f"{BASE_URL}/{args.base_id}/{urllib.parse.quote(args.table)}/{args.record_id}")
    print(json.dumps(result, indent=2))


def cmd_search_records(args):
    # Use SEARCH() formula to find records matching a string in any field
    formula = f"SEARCH(\"{args.query}\", ARRAYJOIN(VALUES({{}}), \" \"))"
    # Simpler: search in a specific field if provided
    if args.field:
        formula = f"SEARCH(\"{args.query}\", {{{args.field}}})"

    params = {"filterByFormula": formula, "pageSize": args.limit}
    result = request("GET", f"{BASE_URL}/{args.base_id}/{urllib.parse.quote(args.table)}", params=params)
    records = result.get("records", [])
    print(f"# {len(records)} results\n")
    for r in records:
        row = {"id": r["id"]}
        row.update(r.get("fields", {}))
        print(json.dumps(row))


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Airtable CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list-bases", help="List all bases you have access to")

    p = sub.add_parser("list-tables", help="List tables in a base")
    p.add_argument("base_id", help="Base ID (starts with 'app')")

    p = sub.add_parser("list-records", help="List records in a table")
    p.add_argument("base_id", help="Base ID (starts with 'app')")
    p.add_argument("table", help="Table name or ID")
    p.add_argument("--limit", type=int, default=25)
    p.add_argument("--view", help="View name to use")
    p.add_argument("--filter", help="Airtable formula to filter records, e.g. \"{Status}='Active'\"")
    p.add_argument("--fields", help="Comma-separated field names to return")

    p = sub.add_parser("get-record", help="Get a specific record")
    p.add_argument("base_id", help="Base ID")
    p.add_argument("table", help="Table name or ID")
    p.add_argument("record_id", help="Record ID (starts with 'rec')")

    p = sub.add_parser("search-records", help="Search records")
    p.add_argument("base_id", help="Base ID")
    p.add_argument("table", help="Table name or ID")
    p.add_argument("query", help="Search string")
    p.add_argument("--field", help="Field name to search in (default: all)")
    p.add_argument("--limit", type=int, default=25)

    args = parser.parse_args()
    {
        "list-bases": cmd_list_bases,
        "list-tables": cmd_list_tables,
        "list-records": cmd_list_records,
        "get-record": cmd_get_record,
        "search-records": cmd_search_records,
    }[args.cmd](args)


if __name__ == "__main__":
    main()
