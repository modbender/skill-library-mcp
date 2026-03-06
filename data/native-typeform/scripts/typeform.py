#!/usr/bin/env python3
"""
Typeform API — calls api.typeform.com directly.
No third-party proxy.
"""
import argparse
import json
import os
import sys
import urllib.parse
import urllib.request

BASE_URL = "https://api.typeform.com"


# ── Auth ──────────────────────────────────────────────────────────────────────

def get_token():
    token = os.environ.get("TYPEFORM_TOKEN")
    if not token:
        print("Error: TYPEFORM_TOKEN not set.", file=sys.stderr)
        print("Get a personal access token at: https://admin.typeform.com/account#/section/tokens", file=sys.stderr)
        sys.exit(1)
    return token


def request(method, path, params=None, body=None):
    token = get_token()
    url = BASE_URL + path
    if params:
        url += "?" + urllib.parse.urlencode(params)

    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(req) as resp:
            raw = resp.read()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"Error {e.code}: {body}", file=sys.stderr)
        sys.exit(1)


# ── Commands ──────────────────────────────────────────────────────────────────

def cmd_list_forms(args):
    params = {}
    if args.search:
        params["search"] = args.search
    if args.page:
        params["page"] = args.page
    params["page_size"] = args.limit
    result = request("GET", "/forms", params=params)
    forms = result.get("items", [])
    for f in forms:
        print(f"{f['id']}\t{f['title']}\t{f.get('_links', {}).get('display', '')}")


def cmd_get_form(args):
    result = request("GET", f"/forms/{args.form_id}")
    print(json.dumps(result, indent=2))


def cmd_responses(args):
    params = {"page_size": args.limit}
    if args.since:
        params["since"] = args.since
    if args.until:
        params["until"] = args.until
    if args.completed is not None:
        params["completed"] = str(args.completed).lower()
    result = request("GET", f"/forms/{args.form_id}/responses", params=params)
    responses = result.get("items", [])
    total = result.get("total_items", len(responses))
    print(f"# {len(responses)} of {total} responses\n")
    for r in responses:
        submitted = r.get("submitted_at", "")
        answers = r.get("answers", [])
        print(f"submitted: {submitted}")
        for a in answers:
            field = a.get("field", {}).get("ref", a.get("field", {}).get("id", "?"))
            atype = a.get("type", "")
            value = a.get(atype, a.get("text", a.get("choice", {}).get("label", "")))
            print(f"  {field}: {value}")
        print()


def cmd_insights(args):
    result = request("GET", f"/insights/{args.form_id}/summary")
    print(json.dumps(result, indent=2))


def cmd_me(args):
    result = request("GET", "/me")
    print(json.dumps(result, indent=2))


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Typeform CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    # list-forms
    p = sub.add_parser("list-forms", help="List all forms in your account")
    p.add_argument("--search", help="Search forms by title")
    p.add_argument("--limit", type=int, default=25, help="Results per page (default 25)")
    p.add_argument("--page", type=int, help="Page number")

    # get-form
    p = sub.add_parser("get-form", help="Get form definition")
    p.add_argument("form_id", help="Form ID")

    # responses
    p = sub.add_parser("responses", help="Get responses for a form")
    p.add_argument("form_id", help="Form ID")
    p.add_argument("--limit", type=int, default=25, help="Number of responses (default 25, max 1000)")
    p.add_argument("--since", help="ISO 8601 datetime, e.g. 2026-01-01T00:00:00Z")
    p.add_argument("--until", help="ISO 8601 datetime")
    p.add_argument("--completed", type=bool, default=None, help="Filter by completed status")

    # insights
    p = sub.add_parser("insights", help="Get form insights/summary stats")
    p.add_argument("form_id", help="Form ID")

    # me
    sub.add_parser("me", help="Get your account info")

    args = parser.parse_args()
    {
        "list-forms": cmd_list_forms,
        "get-form": cmd_get_form,
        "responses": cmd_responses,
        "insights": cmd_insights,
        "me": cmd_me,
    }[args.cmd](args)


if __name__ == "__main__":
    main()
