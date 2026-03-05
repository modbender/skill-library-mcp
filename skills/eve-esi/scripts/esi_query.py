#!/usr/bin/env python3
"""EVE ESI API query helper.

Usage:
    python esi_query.py --token <ACCESS_TOKEN> --endpoint /characters/12345/wallet/
    python esi_query.py --token <ACCESS_TOKEN> --endpoint /characters/12345/assets/ --pages
    python esi_query.py --token <ACCESS_TOKEN> --endpoint /characters/12345/contacts/ --method POST --body '[{"contact_id":123,"standing":10}]'

Requires: Python 3.8+ (uses only stdlib)
"""

import argparse
import json
import sys
import time
import urllib.error
import urllib.request

BASE_URL = "https://esi.evetech.net/latest"
USER_AGENT = "OpenClaw-ESI-Skill/1.0 (https://github.com/openclaw/openclaw)"


def esi_request(endpoint: str, token: str, method: str = "GET",
                body: str | None = None, page: int | None = None) -> tuple[dict | list | str, dict]:
    """Make a single ESI request. Returns (parsed_body, headers)."""
    url = f"{BASE_URL}{endpoint}"
    sep = "&" if "?" in url else "?"
    if page is not None:
        url += f"{sep}page={page}"

    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
    }

    data = None
    if body is not None:
        headers["Content-Type"] = "application/json"
        data = body.encode("utf-8")

    req = urllib.request.Request(url, data=data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req) as resp:
            resp_headers = {k.lower(): v for k, v in resp.getheaders()}
            raw = resp.read().decode("utf-8")
            try:
                parsed = json.loads(raw)
            except json.JSONDecodeError:
                parsed = raw
            return parsed, resp_headers
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        remain = e.headers.get("X-ESI-Error-Limit-Remain", "?")
        reset = e.headers.get("X-ESI-Error-Limit-Reset", "?")
        print(f"HTTP {e.code}: {error_body}", file=sys.stderr)
        print(f"Error limit remaining: {remain}, resets in: {reset}s", file=sys.stderr)
        if e.code == 420:
            wait = int(reset) if reset.isdigit() else 60
            print(f"Rate limited. Waiting {wait}s...", file=sys.stderr)
            time.sleep(wait)
            return esi_request(endpoint, token, method, body, page)
        sys.exit(1)


def esi_request_all_pages(endpoint: str, token: str) -> list:
    """Fetch all pages of a paginated GET endpoint."""
    first_page, headers = esi_request(endpoint, token, page=1)
    total_pages = int(headers.get("x-pages", "1"))
    if not isinstance(first_page, list):
        return [first_page]

    all_results = list(first_page)
    for p in range(2, total_pages + 1):
        page_data, _ = esi_request(endpoint, token, page=p)
        if isinstance(page_data, list):
            all_results.extend(page_data)
        expires = headers.get("expires", "")
        print(f"  Page {p}/{total_pages} fetched ({len(page_data)} items)", file=sys.stderr)
    return all_results


def main():
    parser = argparse.ArgumentParser(description="Query EVE ESI API endpoints")
    parser.add_argument("--token", required=True, help="ESI access token (Bearer)")
    parser.add_argument("--endpoint", required=True,
                        help="ESI endpoint path, e.g. /characters/12345/wallet/")
    parser.add_argument("--method", default="GET", choices=["GET", "POST", "PUT", "DELETE"],
                        help="HTTP method (default: GET)")
    parser.add_argument("--body", default=None, help="JSON body for POST/PUT requests")
    parser.add_argument("--pages", action="store_true",
                        help="Automatically fetch all pages (GET only)")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    args = parser.parse_args()

    endpoint = args.endpoint
    if not endpoint.startswith("/"):
        endpoint = "/" + endpoint

    if args.pages and args.method == "GET":
        result = esi_request_all_pages(endpoint, args.token)
    else:
        result, headers = esi_request(endpoint, args.token, args.method, args.body)
        expires = headers.get("expires", "unknown")
        print(f"Cache expires: {expires}", file=sys.stderr)

    indent = 2 if args.pretty else None
    if isinstance(result, (dict, list)):
        print(json.dumps(result, indent=indent, ensure_ascii=False))
    else:
        print(result)


if __name__ == "__main__":
    main()
