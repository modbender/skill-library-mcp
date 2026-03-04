#!/usr/bin/env python3

import argparse
import json
import os
import sys
import urllib.parse
import urllib.request

DEFAULT_BASE = "https://openalexandria.vercel.app"

DEFAULT_API_KEY = os.environ.get("OPENALEXANDRIA_API_KEY")


def base_url() -> str:
    return os.environ.get("OPENALEXANDRIA_BASE_URL", DEFAULT_BASE).rstrip("/")


def http_json(method: str, url: str, payload=None, api_key: str | None = None):
    data = None
    headers = {"Accept": "application/json"}

    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    if payload is not None:
        raw = json.dumps(payload).encode("utf-8")
        data = raw
        headers["Content-Type"] = "application/json; charset=utf-8"

    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode("utf-8")
            if not body.strip():
                return {}
            return json.loads(body)
    except urllib.error.HTTPError as e:
        err_body = None
        try:
            err_body = e.read().decode("utf-8")
        except Exception:
            pass
        raise RuntimeError(f"HTTP {e.code} {e.reason}: {err_body or ''}".strip())


def cmd_wellknown(_args):
    url = base_url() + "/.well-known/openalexandria.json"
    return http_json("GET", url)


def cmd_query(args):
    q = args.q
    k = args.k
    qs = urllib.parse.urlencode({"q": q, "k": str(k)})
    url = base_url() + "/v1/query?" + qs
    return http_json("GET", url)


def cmd_entry(args):
    entry_id = urllib.parse.quote(args.id, safe="")
    url = base_url() + f"/v1/entry/{entry_id}"
    return http_json("GET", url)


def cmd_feed(args):
    params = {}
    if args.since:
        params["since"] = args.since
    qs = ("?" + urllib.parse.urlencode(params)) if params else ""
    url = base_url() + "/v1/feed" + qs
    return http_json("GET", url)


def cmd_whoami(args):
    api_key = args.api_key or DEFAULT_API_KEY
    if not api_key:
        raise SystemExit("Missing API key. Set OPENALEXANDRIA_API_KEY or pass --api-key.")
    url = base_url() + "/v1/whoami"
    return http_json("GET", url, api_key=api_key)


def cmd_submission(args):
    api_key = args.api_key or DEFAULT_API_KEY
    # submission status can be polled by submitter key; if not provided, attempt unauth (may fail)
    url = base_url() + f"/v1/submission/{urllib.parse.quote(args.id, safe='')}"
    return http_json("GET", url, api_key=api_key)


def cmd_submit(args):
    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            payload = json.load(f)
    else:
        payload = json.load(sys.stdin)

    api_key = args.api_key or DEFAULT_API_KEY
    if not api_key:
        raise SystemExit("Missing API key. Set OPENALEXANDRIA_API_KEY or pass --api-key.")

    url = base_url() + "/v1/submit"
    return http_json("POST", url, payload=payload, api_key=api_key)


def main():
    p = argparse.ArgumentParser(description="OpenAlexandria Protocol CLI")
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("wellknown", help="Fetch node discovery document")
    sp.set_defaults(fn=cmd_wellknown)

    sp = sub.add_parser("query", help="Query entries")
    sp.add_argument("q", help="Query string")
    sp.add_argument("--k", type=int, default=5, help="Max results (default: 5)")
    sp.set_defaults(fn=cmd_query)

    sp = sub.add_parser("entry", help="Fetch an entry by id")
    sp.add_argument("id", help="Entry id")
    sp.set_defaults(fn=cmd_entry)

    sp = sub.add_parser("feed", help="Fetch feed")
    sp.add_argument("--since", help="Cursor from previous feed response", default=None)
    sp.set_defaults(fn=cmd_feed)

    sp = sub.add_parser("whoami", help="Validate API key and view limits")
    sp.add_argument("--api-key", dest="api_key", default=None, help="OpenAlexandria API key (or set OPENALEXANDRIA_API_KEY)")
    sp.set_defaults(fn=cmd_whoami)

    sp = sub.add_parser("submission", help="Get submission status + feedback")
    sp.add_argument("id", help="Submission id (sub_...) ")
    sp.add_argument("--api-key", dest="api_key", default=None, help="OpenAlexandria API key (or set OPENALEXANDRIA_API_KEY)")
    sp.set_defaults(fn=cmd_submission)

    sp = sub.add_parser("submit", help="Submit a bundle")
    sp.add_argument("--file", help="JSON bundle file; if omitted, reads from stdin", default=None)
    sp.add_argument("--api-key", dest="api_key", default=None, help="OpenAlexandria API key (or set OPENALEXANDRIA_API_KEY)")
    sp.set_defaults(fn=cmd_submit)

    args = p.parse_args()
    out = args.fn(args)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
