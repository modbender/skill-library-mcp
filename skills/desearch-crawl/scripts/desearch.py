#!/usr/bin/env python3
"""
Desearch Crawl CLI - Extract content from any webpage URL.

Usage:
    desearch crawl "<url>" [options]

Environment:
    DESEARCH_API_KEY - Required API key from desearch.ai
"""

import argparse
import json
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

DESEARCH_BASE = "https://api.desearch.ai"


def get_api_key() -> str:
    key = os.environ.get("DESEARCH_API_KEY")
    if not key:
        print("Error: DESEARCH_API_KEY environment variable not set", file=sys.stderr)
        print("Get your key at https://console.desearch.ai", file=sys.stderr)
        sys.exit(1)
    return key


def api_request(
    method: str, path: str, params: dict = None, body: dict = None
) -> dict | str:
    api_key = get_api_key()
    url = f"{DESEARCH_BASE}{path}"

    if method == "GET" and params:
        filtered = {k: v for k, v in params.items() if v is not None}
        if filtered:
            url = f"{url}?{urlencode(filtered, doseq=True)}"

    headers = {
        "Authorization": f"{api_key}",
        "Content-Type": "application/json",
        "User-Agent": "Desearch-Clawdbot/1.0",
    }

    data = None
    if method == "POST" and body:
        data = json.dumps(body).encode()

    try:
        req = Request(url, data=data, headers=headers, method=method)
        with urlopen(req, timeout=60) as response:
            raw = response.read().decode()
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                return raw
    except HTTPError as e:
        error_body = e.read().decode() if e.fp else ""
        try:
            return json.loads(error_body)
        except (json.JSONDecodeError, Exception):
            return {"error": f"HTTP {e.code}: {e.reason}", "details": error_body}
    except URLError as e:
        return {"error": f"Connection failed: {e.reason}"}
    except Exception as e:
        return {"error": str(e)}


def cmd_crawl(args):
    params = {
        "url": args.url,
        "format": args.crawl_format,
    }
    return api_request("GET", "/web/crawl", params=params)


def main():
    parser = argparse.ArgumentParser(
        description="Desearch Crawl CLI - Extract content from any webpage",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "command", choices=["crawl"], help="Command to execute"
    )
    parser.add_argument("url", help="URL to crawl")

    parser.add_argument(
        "--crawl-format",
        choices=["text", "html"],
        default="text",
        help="Crawl output format (default: text)",
    )

    args = parser.parse_args()
    results = cmd_crawl(args)

    if isinstance(results, str):
        print(results)
    else:
        print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
