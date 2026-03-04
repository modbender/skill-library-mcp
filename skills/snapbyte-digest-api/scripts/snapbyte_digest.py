#!/usr/bin/env python3

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any


BASE_URL = os.environ.get("SNAPBYTE_BASE_URL", "https://api.snapbyte.dev")


def build_url(path: str, query: dict[str, Any] | None = None) -> str:
    base = BASE_URL.rstrip("/")
    if not query:
        return f"{base}{path}"
    filtered = {k: v for k, v in query.items() if v is not None}
    return f"{base}{path}?{urllib.parse.urlencode(filtered)}"


def api_request(path: str, query: dict[str, Any] | None = None) -> Any:
    api_key = os.environ.get("SNAPBYTE_API_KEY")
    if not api_key:
        print("Missing SNAPBYTE_API_KEY", file=sys.stderr)
        sys.exit(2)

    request = urllib.request.Request(build_url(path, query), method="GET")
    request.add_header("Authorization", f"Bearer {api_key}")
    request.add_header("Accept", "application/json")

    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            body = response.read().decode("utf-8")
            if not body:
                return {}
            return json.loads(body)
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8") if error.fp else ""
        message = body
        code = None
        if body:
            try:
                parsed = json.loads(body)
                message = parsed.get("error", body)
                code = parsed.get("code")
            except json.JSONDecodeError:
                message = body
        suffix = f" ({code})" if code else ""
        print(f"HTTP {error.code}: {message}{suffix}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as error:
        print(f"Network error: {error.reason}", file=sys.stderr)
        sys.exit(1)


def print_markdown(data: Any, command: str) -> None:
    if command == "configurations":
        print("# Snapbyte Digest Configurations")
        if not data:
            print("No digest configurations found.")
            return
        for config in data:
            print(f"- **{config.get('name', 'Unnamed')}** (`{config.get('id', '-')}`)")
            print(f"  - status: `{config.get('status', '-')}`")
            print(f"  - timezone: `{config.get('timezone', '-')}`")
            print(f"  - sources: {', '.join(config.get('sources', [])) or '-'}")
            print(f"  - tags: {', '.join(config.get('tags', [])) or '-'}")
        return

    if command == "latest":
        if isinstance(data, list):
            print("# Latest Digests")
            if not data:
                print("No latest digests found.")
                return
            for digest in data:
                print_digest_block(digest)
            return
        print("# Latest Digest")
        print_digest_block(data)
        return

    if command == "history":
        print("# Digest History")
        items = data.get("items", [])
        if not items:
            print("No historical digests found.")
            return
        print(
            f"Page {data.get('page', 1)} of {data.get('totalPages', 1)} "
            f"(total: {data.get('total', len(items))})"
        )
        for digest in items:
            print_digest_block(digest)
        return

    if command == "digest":
        print("# Digest")
        print_digest_block(data)
        return

    if command == "items":
        print("# Digest Items")
        items = data.get("items", [])
        if not items:
            print("No digest items found.")
            return
        print(
            f"Page {data.get('page', 1)} of {data.get('totalPages', 1)} "
            f"(total: {data.get('total', len(items))})"
        )
        for item in items:
            title = item.get("title", "Untitled")
            url = item.get("url", "")
            summary = item.get("summary", "")
            score = item.get("score", "-")
            sources = ", ".join(item.get("sources", [])) or "-"
            tags = ", ".join(item.get("tags", [])) or "-"
            print(f"- **{title}**")
            if url:
                print(f"  - url: {url}")
            print(f"  - score: {score}")
            print(f"  - sources: {sources}")
            print(f"  - tags: {tags}")
            if summary:
                print(f"  - summary: {summary}")
        return

    print(json.dumps(data, indent=2, ensure_ascii=True))


def print_digest_block(digest: dict[str, Any]) -> None:
    digest_id = digest.get("id", "-")
    title = digest.get("title", "Untitled digest")
    name = digest.get("name", "")
    date = digest.get("date", "")
    intro = digest.get("introduction", "")
    count = digest.get("contentCount", "-")

    print(f"- **{title}** (`{digest_id}`)")
    if name:
        print(f"  - configuration: {name}")
    if date:
        print(f"  - date: {date}")
    print(f"  - content count: {count}")
    if intro:
        print(f"  - intro: {intro}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Snapbyte Digest API helper for OpenClaw skill"
    )
    parser.add_argument("--raw", action="store_true", help="Print raw JSON output")

    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("configurations", help="Get digest configurations")

    latest = subparsers.add_parser("latest", help="Get latest digests")
    latest.add_argument("--configuration-id", help="Filter by configuration id")

    history = subparsers.add_parser("history", help="Get digest history")
    history.add_argument("--configuration-id", required=True)
    history.add_argument("--page", type=int, default=1)
    history.add_argument("--limit", type=int, default=10)

    digest = subparsers.add_parser("digest", help="Get one digest by id")
    digest.add_argument("--id", required=True)

    items = subparsers.add_parser("items", help="Get digest items")
    items.add_argument("--digest-id", required=True)
    items.add_argument("--page", type=int, default=1)
    items.add_argument("--limit", type=int, default=10)

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.command == "configurations":
        data = api_request("/digests/configurations")
    elif args.command == "latest":
        data = api_request(
            "/digests/latest", {"configurationId": args.configuration_id}
        )
    elif args.command == "history":
        data = api_request(
            f"/digests/history/{args.configuration_id}",
            {"page": args.page, "limit": args.limit},
        )
    elif args.command == "digest":
        data = api_request(f"/digests/{args.id}")
    elif args.command == "items":
        data = api_request(
            f"/digests/{args.digest_id}/items", {"page": args.page, "limit": args.limit}
        )
    else:
        print(f"Unknown command: {args.command}", file=sys.stderr)
        sys.exit(2)

    if args.raw:
        print(json.dumps(data, indent=2, ensure_ascii=True))
    else:
        print_markdown(data, args.command)


if __name__ == "__main__":
    main()
