#!/usr/bin/env python3
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request


BASE_URL = "https://dievio.com"
SEARCH_PATH = "/api/public/search"
LINKEDIN_LOOKUP_PATH = "/api/linkedin/lookup"


def _safe_json(raw):
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"raw": raw}


def _request(method, path, headers, payload, timeout):
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(
        url=f"{BASE_URL}{path}",
        data=data,
        headers=headers,
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.getcode(), _safe_json(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8") if exc.fp else ""
        return exc.code, _safe_json(body)
    except urllib.error.URLError as exc:
        return 0, {"error": f"network_error: {exc}"}


def _load_json_file(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        raise ValueError(f"JSON file not found: {path}") from None
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in file {path}: {exc}") from None


def _build_headers(auth_mode, api_key=None):
    headers = {"Content-Type": "application/json"}
    key = api_key or os.getenv("DIEVIO_API_KEY")
    if not key:
        raise ValueError("Missing API key. Set --api-key or DIEVIO_API_KEY.")

    if auth_mode == "x-api-key":
        headers["X-API-Key"] = key
    else:
        headers["Authorization"] = f"Bearer {key}"
    return headers


def _override_paging(payload, page=None, per_page=None, max_results=None):
    out = dict(payload)
    if page is not None:
        out["_page"] = page
    if per_page is not None:
        out["_per_page"] = per_page
    if max_results is not None:
        out["max_results"] = max_results
    return out


def _summarize_payload(data):
    if not isinstance(data, dict):
        return data

    summary = {}
    passthrough_keys = [
        "success",
        "message",
        "count",
        "preview_count",
        "total_count",
        "page",
        "per_page",
        "total_pages",
        "has_more",
        "next_page",
        "max_results",
        "search_id",
        "counting",
        "error",
    ]
    for key in passthrough_keys:
        if key in data:
            summary[key] = data[key]

    if "preview_data" in data and isinstance(data["preview_data"], list):
        summary["preview_data_rows"] = len(data["preview_data"])
    if "data" in data and isinstance(data["data"], list):
        summary["data_rows"] = len(data["data"])

    if not summary:
        return data
    return summary


def _emit(status_code, data, raw_output=False):
    payload = data if raw_output else _summarize_payload(data)
    print(json.dumps({"status_code": status_code, "data": payload}, indent=2, ensure_ascii=True))


def _paginate(path, payload, headers, timeout, max_pages, sleep_seconds):
    page = int(payload.get("_page", 1))
    merged = []
    pages = []
    fetched = 0

    while True:
        req_payload = dict(payload)
        req_payload["_page"] = page
        status_code, data = _request("POST", path, headers, req_payload, timeout)
        pages.append({"page": page, "status_code": status_code, "data": data})
        fetched += 1

        if status_code >= 400 or status_code == 0:
            return status_code, {
                "success": False,
                "error": "pagination_request_failed",
                "failed_page": page,
                "pages_fetched": fetched,
                "pages": pages,
            }

        rows = data.get("preview_data")
        if rows is None:
            rows = data.get("data", [])
        if isinstance(rows, list):
            merged.extend(rows)

        has_more = bool(data.get("has_more"))
        next_page = data.get("next_page")
        if not has_more or next_page in (None, 0):
            break
        if max_pages and fetched >= max_pages:
            break

        page = int(next_page)
        if sleep_seconds > 0:
            time.sleep(sleep_seconds)

    return 200, {
        "success": True,
        "pages_fetched": fetched,
        "rows_merged": len(merged),
        "results": merged,
        "last_page": pages[-1]["data"] if pages else {},
    }


def cmd_search(args):
    body = _load_json_file(args.body_file) if args.body_file else {}
    body = _override_paging(body, args.page, args.per_page, args.max_results)
    headers = _build_headers(args.auth_mode, api_key=args.api_key)

    if args.auto_paginate:
        status_code, data = _paginate(
            SEARCH_PATH,
            body,
            headers,
            args.timeout,
            args.max_pages,
            args.sleep_seconds,
        )
    else:
        status_code, data = _request("POST", SEARCH_PATH, headers, body, args.timeout)

    _emit(status_code, data, raw_output=args.raw_output)
    return 0 if status_code and status_code < 400 else 1


def cmd_linkedin_lookup(args):
    if args.body_file:
        body = _load_json_file(args.body_file)
    else:
        if not args.linkedin_url:
            raise ValueError("Provide --body-file or at least one --linkedin-url.")
        body = {
            "linkedinUrls": args.linkedin_url,
            "includeWorkEmails": args.include_work_emails,
            "includePersonalEmails": args.include_personal_emails,
            "onlyWithEmails": args.only_with_emails,
            "includePhones": args.include_phones,
        }

    body = _override_paging(body, args.page, args.per_page, args.max_results)
    headers = _build_headers(args.auth_mode, api_key=args.api_key)

    if args.auto_paginate:
        status_code, data = _paginate(
            LINKEDIN_LOOKUP_PATH,
            body,
            headers,
            args.timeout,
            args.max_pages,
            args.sleep_seconds,
        )
    else:
        status_code, data = _request("POST", LINKEDIN_LOOKUP_PATH, headers, body, args.timeout)

    _emit(status_code, data, raw_output=args.raw_output)
    return 0 if status_code and status_code < 400 else 1


def build_parser():
    parser = argparse.ArgumentParser(
        description="Dievio API utility for lead search and LinkedIn lookup."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    search = sub.add_parser("search", help="Run POST /api/public/search.")
    search.add_argument("--body-file", help="Path to JSON request body.")
    search.add_argument("--api-key", help="Override DIEVIO_API_KEY.")
    search.add_argument(
        "--auth-mode",
        choices=["bearer", "x-api-key"],
        default="bearer",
        help="Authentication header mode for API key.",
    )
    search.add_argument("--page", type=int, help="Override _page.")
    search.add_argument("--per-page", type=int, help="Override _per_page.")
    search.add_argument("--max-results", type=int, help="Override max_results.")
    search.add_argument("--auto-paginate", action="store_true", help="Follow has_more across pages.")
    search.add_argument("--max-pages", type=int, default=0, help="Cap pages when auto-paginating (0 = no cap).")
    search.add_argument("--sleep-seconds", type=float, default=0.0, help="Delay between page requests.")
    search.add_argument("--timeout", type=int, default=60, help="HTTP timeout in seconds.")
    search.add_argument(
        "--raw-output",
        action="store_true",
        help="Print full API payload (may include PII).",
    )
    search.set_defaults(func=cmd_search)

    linkedin = sub.add_parser("linkedin-lookup", help="Run POST /api/linkedin/lookup.")
    linkedin.add_argument("--body-file", help="Path to JSON request body.")
    linkedin.add_argument("--linkedin-url", action="append", help="LinkedIn URL (repeatable).")
    linkedin.add_argument(
        "--include-work-emails",
        action=argparse.BooleanOptionalAction,
        default=True,
    )
    linkedin.add_argument(
        "--include-personal-emails",
        action=argparse.BooleanOptionalAction,
        default=True,
    )
    linkedin.add_argument(
        "--only-with-emails",
        action=argparse.BooleanOptionalAction,
        default=True,
    )
    linkedin.add_argument(
        "--include-phones",
        action=argparse.BooleanOptionalAction,
        default=False,
    )
    linkedin.add_argument("--api-key", help="Override DIEVIO_API_KEY.")
    linkedin.add_argument(
        "--auth-mode",
        choices=["bearer", "x-api-key"],
        default="bearer",
        help="Authentication mode.",
    )
    linkedin.add_argument("--page", type=int, help="Override _page.")
    linkedin.add_argument("--per-page", type=int, help="Override _per_page.")
    linkedin.add_argument("--max-results", type=int, help="Override max_results.")
    linkedin.add_argument("--auto-paginate", action="store_true", help="Follow has_more across pages.")
    linkedin.add_argument("--max-pages", type=int, default=0, help="Cap pages when auto-paginating (0 = no cap).")
    linkedin.add_argument("--sleep-seconds", type=float, default=0.0, help="Delay between page requests.")
    linkedin.add_argument("--timeout", type=int, default=60, help="HTTP timeout in seconds.")
    linkedin.add_argument(
        "--raw-output",
        action="store_true",
        help="Print full API payload (may include PII).",
    )
    linkedin.set_defaults(func=cmd_linkedin_lookup)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    try:
        return args.func(args)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
