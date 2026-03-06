#!/usr/bin/env python3
"""
Corpus API helper for OpenClaw skill execution.

This script targets the planned /api/skill/* facade first, then falls back
to current API endpoints where possible.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional


DEFAULT_BASE_URL = "https://corpusai.app"
DEFAULT_TIMEOUT = 30.0


class CorpusApiError(RuntimeError):
    """Raised when all API candidates fail."""


@dataclass
class RequestCandidate:
    path: str
    payload: Optional[Dict[str, Any]] = None
    query: Optional[Dict[str, Any]] = None


class CorpusClient:
    def __init__(self, base_url: str, token: str, timeout: float) -> None:
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.timeout = timeout

    def request(self, method: str, candidate: RequestCandidate) -> Any:
        url = f"{self.base_url}{candidate.path}"
        if candidate.query:
            pairs = []
            for key, value in candidate.query.items():
                if value is None:
                    continue
                pairs.append((key, str(value)))
            if pairs:
                url = f"{url}?{urllib.parse.urlencode(pairs)}"

        data = None
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json",
        }
        if candidate.payload is not None:
            data = json.dumps(candidate.payload).encode("utf-8")
            headers["Content-Type"] = "application/json"

        req = urllib.request.Request(url=url, data=data, headers=headers, method=method.upper())

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                raw = response.read().decode("utf-8", errors="replace")
                if not raw:
                    return {}
                try:
                    return json.loads(raw)
                except json.JSONDecodeError:
                    return {"raw": raw}
        except urllib.error.HTTPError as err:
            raw = err.read().decode("utf-8", errors="replace")
            detail: Any
            try:
                detail = json.loads(raw) if raw else {}
            except json.JSONDecodeError:
                detail = raw
            raise CorpusApiError(
                f"{method.upper()} {candidate.path} failed with {err.code}: {detail}"
            ) from err
        except urllib.error.URLError as err:
            raise CorpusApiError(f"{method.upper()} {candidate.path} failed: {err.reason}") from err

    def request_candidates(self, method: str, candidates: Iterable[RequestCandidate]) -> Dict[str, Any]:
        last_error: Optional[Exception] = None
        for candidate in candidates:
            try:
                response = self.request(method, candidate)
                return {
                    "endpoint": candidate.path,
                    "response": response,
                }
            except Exception as exc:  # noqa: BLE001
                last_error = exc
        raise CorpusApiError(str(last_error) if last_error else "No request candidates were provided.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Corpus API helper")
    parser.add_argument(
        "--base-url",
        default=os.getenv("CORPUS_API_BASE_URL", DEFAULT_BASE_URL),
        help=f"Corpus API base URL (default: {DEFAULT_BASE_URL})",
    )
    parser.add_argument(
        "--token",
        default=os.getenv("CORPUS_API_TOKEN", ""),
        help="Corpus API token (default: CORPUS_API_TOKEN env var)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=float(os.getenv("CORPUS_TIMEOUT_SECONDS", DEFAULT_TIMEOUT)),
        help=f"HTTP timeout seconds (default: {DEFAULT_TIMEOUT})",
    )
    parser.add_argument(
        "--compact",
        action="store_true",
        help="Print compact JSON instead of pretty JSON",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("profile", help="Get user profile/usage info")

    list_parser = subparsers.add_parser("list-content", help="List user content")
    list_parser.add_argument("--limit", type=int, default=20, help="Result limit")
    list_parser.add_argument("--cursor", default="", help="Cursor for /api/skill/content")

    search_parser = subparsers.add_parser("search", help="Search corpus content")
    search_parser.add_argument("--query", required=True, help="Search query")
    search_parser.add_argument("--limit", type=int, default=8, help="Result limit")
    search_parser.add_argument(
        "--include-citations",
        action="store_true",
        help="Request citation payload when available",
    )

    content_parser = subparsers.add_parser("content", help="Get content details by user content id")
    content_parser.add_argument("--user-content-id", required=True, help="User content id")

    save_parser = subparsers.add_parser("save-url", help="Save URL to Corpus")
    save_parser.add_argument("--url", required=True, help="URL to save")
    save_parser.add_argument("--user-note", default="", help="Optional user note")

    reminder_parser = subparsers.add_parser("create-reminder", help="Create reminder")
    reminder_parser.add_argument("--title", required=True, help="Reminder title")
    reminder_parser.add_argument("--description", default="", help="Reminder description")
    reminder_parser.add_argument(
        "--scheduled-date-utc",
        required=True,
        help='UTC timestamp, ex: "2026-02-18T16:00:00Z"',
    )
    reminder_parser.add_argument("--user-content-id", default="", help="Optional user content id")

    return parser


def print_json(data: Dict[str, Any], compact: bool) -> None:
    if compact:
        print(json.dumps(data, separators=(",", ":")))
    else:
        print(json.dumps(data, indent=2))


def handle_profile(client: CorpusClient) -> Dict[str, Any]:
    return client.request_candidates(
        "GET",
        [
            RequestCandidate(path="/api/skill/profile"),
            RequestCandidate(path="/api/user-usage/dashboard"),
        ],
    )


def handle_list_content(client: CorpusClient, limit: int, cursor: str) -> Dict[str, Any]:
    safe_limit = max(1, min(limit, 50))
    return client.request_candidates(
        "GET",
        [
            RequestCandidate(
                path="/api/skill/content",
                query={"limit": safe_limit, "cursor": cursor or None},
            ),
            RequestCandidate(
                path="/api/content/user-content",
                query={"page": 1, "pageSize": safe_limit},
            ),
        ],
    )


def handle_search(
    client: CorpusClient, query: str, limit: int, include_citations: bool
) -> Dict[str, Any]:
    safe_limit = max(1, min(limit, 20))
    return client.request_candidates(
        "POST",
        [
            RequestCandidate(
                path="/api/skill/search",
                payload={
                    "query": query,
                    "limit": safe_limit,
                    "includeCitations": include_citations,
                },
            ),
            RequestCandidate(
                path="/api/content/search",
                payload={
                    "query": query,
                },
            ),
        ],
    )


def handle_content(client: CorpusClient, user_content_id: str) -> Dict[str, Any]:
    return client.request_candidates(
        "GET",
        [
            RequestCandidate(path=f"/api/skill/content/{user_content_id}"),
            RequestCandidate(path=f"/api/content/user-content/{user_content_id}/details"),
        ],
    )


def handle_save_url(client: CorpusClient, url: str, user_note: str) -> Dict[str, Any]:
    return client.request_candidates(
        "POST",
        [
            RequestCandidate(
                path="/api/skill/save-url",
                payload={
                    "url": url,
                    "userNote": user_note or None,
                    "source": "openclaw-skill",
                },
            ),
            RequestCandidate(
                path="/api/content/upload",
                payload={
                    "url": url,
                    "userNote": user_note or None,
                    "sourceType": "url",
                },
            ),
        ],
    )


def handle_create_reminder(
    client: CorpusClient,
    title: str,
    description: str,
    scheduled_date_utc: str,
    user_content_id: str,
) -> Dict[str, Any]:
    skill_payload: Dict[str, Any] = {
        "title": title,
        "description": description,
        "scheduledDateUtc": scheduled_date_utc,
    }
    fallback_payload: Dict[str, Any] = {
        "title": title,
        "description": description,
        "scheduledDate": scheduled_date_utc,
    }
    if user_content_id:
        skill_payload["userContentId"] = user_content_id
        fallback_payload["userContentId"] = user_content_id

    return client.request_candidates(
        "POST",
        [
            RequestCandidate(path="/api/skill/reminders", payload=skill_payload),
            RequestCandidate(path="/api/reminders", payload=fallback_payload),
        ],
    )


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if not args.token:
        parser.error("Missing token. Set CORPUS_API_TOKEN or pass --token.")

    client = CorpusClient(base_url=args.base_url, token=args.token, timeout=args.timeout)

    try:
        if args.command == "profile":
            result = handle_profile(client)
        elif args.command == "list-content":
            result = handle_list_content(client, limit=args.limit, cursor=args.cursor)
        elif args.command == "search":
            result = handle_search(
                client,
                query=args.query,
                limit=args.limit,
                include_citations=args.include_citations,
            )
        elif args.command == "content":
            result = handle_content(client, user_content_id=args.user_content_id)
        elif args.command == "save-url":
            result = handle_save_url(client, url=args.url, user_note=args.user_note)
        elif args.command == "create-reminder":
            result = handle_create_reminder(
                client,
                title=args.title,
                description=args.description,
                scheduled_date_utc=args.scheduled_date_utc,
                user_content_id=args.user_content_id,
            )
        else:
            parser.error(f"Unknown command: {args.command}")
            return 2
    except CorpusApiError as err:
        print(json.dumps({"error": str(err)}, indent=2), file=sys.stderr)
        return 1

    print_json(result, compact=args.compact)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
