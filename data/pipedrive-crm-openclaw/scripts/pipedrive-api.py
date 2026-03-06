#!/usr/bin/env python3
"""Pipedrive API v1 helper for OpenClaw CRM operations.

Usage:
  python3 pipedrive-api.py <command> [args...]

Environment:
  PIPEDRIVE_API_TOKEN     API token auth (query param)
  PIPEDRIVE_ACCESS_TOKEN  OAuth bearer auth
  PIPEDRIVE_COMPANY_DOMAIN  e.g. "acme" for https://acme.pipedrive.com
  PIPEDRIVE_API_BASE      Optional full override; must include /api/v1
  PIPEDRIVE_TIMEOUT       Request timeout seconds (default: 30)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, Optional

MAX_RETRIES = 3
_SAFE_ID = re.compile(r"^[a-zA-Z0-9_-]{1,128}$")
ENTITY_ENDPOINTS = {
    "persons": "/persons",
    "organizations": "/organizations",
    "deals": "/deals",
    "leads": "/leads",
    "activities": "/activities",
    "notes": "/notes",
    "products": "/products",
    "users": "/users",
    "pipelines": "/pipelines",
    "stages": "/stages",
}
SEARCH_ENDPOINTS = {
    "persons": "/persons/search",
    "organizations": "/organizations/search",
    "deals": "/deals/search",
    "leads": "/leads/search",
    "products": "/products/search",
}


def _env(name: str) -> str:
    return os.environ.get(name, "").strip()


def _base_url() -> str:
    custom = _env("PIPEDRIVE_API_BASE")
    if custom:
        return custom.rstrip("/")

    company = _env("PIPEDRIVE_COMPANY_DOMAIN")
    if not company:
        raise ValueError(
            "Missing PIPEDRIVE_COMPANY_DOMAIN (or set PIPEDRIVE_API_BASE explicitly)."
        )
    if not re.match(r"^[a-zA-Z0-9-]{1,100}$", company):
        raise ValueError("Invalid PIPEDRIVE_COMPANY_DOMAIN format.")
    return f"https://{company}.pipedrive.com/api/v1"


def _auth_headers() -> Dict[str, str]:
    token = _env("PIPEDRIVE_ACCESS_TOKEN")
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}


def _auth_query() -> Dict[str, str]:
    bearer = _env("PIPEDRIVE_ACCESS_TOKEN")
    if bearer:
        return {}

    api_token = _env("PIPEDRIVE_API_TOKEN")
    if not api_token:
        raise ValueError(
            "Set either PIPEDRIVE_ACCESS_TOKEN (OAuth) or PIPEDRIVE_API_TOKEN (token auth)."
        )
    return {"api_token": api_token}


def _timeout() -> int:
    raw = _env("PIPEDRIVE_TIMEOUT")
    if not raw:
        return 30
    try:
        val = int(raw)
        if val < 5:
            return 5
        return min(val, 300)
    except ValueError:
        return 30


def _validate_id(value: str, name: str = "id") -> str:
    if not _SAFE_ID.match(value):
        raise ValueError(f"Invalid {name}: {value!r}")
    return value


def _parse_json(raw: Optional[str], field_name: str) -> Optional[Dict[str, Any]]:
    if raw is None:
        return None
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {field_name}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"{field_name} must be a JSON object")
    return data


def _build_url(path: str, query: Optional[Dict[str, Any]] = None) -> str:
    base = _base_url()
    clean_path = path if path.startswith("/") else f"/{path}"
    query_items: Dict[str, Any] = {}
    if query:
        query_items.update(query)
    query_items.update(_auth_query())
    encoded = urllib.parse.urlencode({k: v for k, v in query_items.items() if v is not None})
    return f"{base}{clean_path}" + (f"?{encoded}" if encoded else "")


def _request(
    method: str,
    path: str,
    query: Optional[Dict[str, Any]] = None,
    body: Optional[Dict[str, Any]] = None,
    retries: int = MAX_RETRIES,
) -> Dict[str, Any]:
    method = method.upper().strip()
    if method not in {"GET", "POST", "PUT", "PATCH", "DELETE"}:
        return {"error": "invalid_method", "message": f"Unsupported method: {method}"}

    url = _build_url(path, query)
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "OpenClaw-Pipedrive-Skill/1.0.0 (stdlib-only)",
    }
    headers.update(_auth_headers())
    data = json.dumps(body).encode("utf-8") if body is not None else None

    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, data=data, headers=headers, method=method)
            with urllib.request.urlopen(req, timeout=_timeout()) as response:
                raw = response.read().decode("utf-8")
                if not raw:
                    return {"success": True, "status": response.status}
                parsed = json.loads(raw)
                if isinstance(parsed, dict):
                    return parsed
                return {"success": True, "data": parsed}
        except urllib.error.HTTPError as exc:
            payload = ""
            try:
                payload = exc.read().decode("utf-8") if exc.fp else ""
            except Exception:
                payload = ""

            if exc.code == 429 and attempt < retries - 1:
                retry_after = exc.headers.get("Retry-After", "")
                wait = int(retry_after) if retry_after.isdigit() else (2 ** (attempt + 1))
                time.sleep(wait)
                continue
            if exc.code >= 500 and attempt < retries - 1:
                time.sleep(2 ** attempt)
                continue

            msg = payload
            try:
                parsed_error = json.loads(payload) if payload else {}
                msg = parsed_error
            except json.JSONDecodeError:
                pass
            return {"error": exc.code, "message": msg}
        except urllib.error.URLError as exc:
            if attempt < retries - 1:
                time.sleep(2)
                continue
            return {"error": "connection_failed", "message": str(exc.reason)}
        except Exception as exc:  # pragma: no cover
            return {"error": "unexpected", "message": str(exc)}

    return {"error": "max_retries_exceeded"}


def _print(result: Dict[str, Any]) -> None:
    print(json.dumps(result, indent=2, ensure_ascii=True))


def cmd_test_connection(_: argparse.Namespace) -> Dict[str, Any]:
    return _request("GET", "/users/me")


def _entity_path(entity: str) -> str:
    if entity not in ENTITY_ENDPOINTS:
        raise ValueError(f"Unsupported entity: {entity}")
    return ENTITY_ENDPOINTS[entity]


def cmd_list(args: argparse.Namespace) -> Dict[str, Any]:
    path = _entity_path(args.entity)
    query = {
        "start": args.start,
        "limit": args.limit,
    }
    if args.extra_query:
        query.update(_parse_json(args.extra_query, "extra_query") or {})
    return _request("GET", path, query=query)


def cmd_get(args: argparse.Namespace) -> Dict[str, Any]:
    path = _entity_path(args.entity)
    item_id = _validate_id(args.id)
    return _request("GET", f"{path}/{item_id}")


def cmd_create(args: argparse.Namespace) -> Dict[str, Any]:
    path = _entity_path(args.entity)
    payload = _parse_json(args.payload, "payload") or {}
    return _request("POST", path, body=payload)


def cmd_update(args: argparse.Namespace) -> Dict[str, Any]:
    path = _entity_path(args.entity)
    item_id = _validate_id(args.id)
    payload = _parse_json(args.payload, "payload") or {}
    method = args.method.upper()
    return _request(method, f"{path}/{item_id}", body=payload)


def cmd_delete(args: argparse.Namespace) -> Dict[str, Any]:
    path = _entity_path(args.entity)
    item_id = _validate_id(args.id)
    return _request("DELETE", f"{path}/{item_id}")


def cmd_search(args: argparse.Namespace) -> Dict[str, Any]:
    endpoint = SEARCH_ENDPOINTS.get(args.entity)
    if not endpoint:
        return {
            "error": "unsupported_search",
            "message": f"Search not wrapped for entity: {args.entity}. Use request command.",
        }
    query = {
        "term": args.term,
        "limit": args.limit,
        "exact_match": 1 if args.exact_match else 0,
    }
    if args.fields:
        query["fields"] = args.fields
    if args.extra_query:
        query.update(_parse_json(args.extra_query, "extra_query") or {})
    return _request("GET", endpoint, query=query)


def cmd_move_deal_stage(args: argparse.Namespace) -> Dict[str, Any]:
    deal_id = _validate_id(args.deal_id, "deal_id")
    stage_id = _validate_id(args.stage_id, "stage_id")
    payload: Dict[str, Any] = {"stage_id": int(stage_id) if stage_id.isdigit() else stage_id}
    if args.status:
        payload["status"] = args.status
    return _request("PUT", f"/deals/{deal_id}", body=payload)


def cmd_add_note(args: argparse.Namespace) -> Dict[str, Any]:
    payload: Dict[str, Any] = {"content": args.content}
    if args.deal_id:
        payload["deal_id"] = int(_validate_id(args.deal_id, "deal_id")) if args.deal_id.isdigit() else args.deal_id
    if args.person_id:
        payload["person_id"] = int(_validate_id(args.person_id, "person_id")) if args.person_id.isdigit() else args.person_id
    if args.org_id:
        payload["org_id"] = int(_validate_id(args.org_id, "org_id")) if args.org_id.isdigit() else args.org_id
    if args.lead_id:
        payload["lead_id"] = _validate_id(args.lead_id, "lead_id")
    return _request("POST", "/notes", body=payload)


def cmd_request(args: argparse.Namespace) -> Dict[str, Any]:
    query = _parse_json(args.query, "query") if args.query else None
    body = _parse_json(args.body, "body") if args.body else None
    return _request(args.method, args.path, query=query, body=body)


def _entity_choices() -> list[str]:
    return sorted(list(ENTITY_ENDPOINTS.keys()))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Pipedrive API v1 helper for OpenClaw")
    sub = parser.add_subparsers(dest="command", required=True)

    p_test = sub.add_parser("test_connection", help="Validate credentials")
    p_test.set_defaults(func=cmd_test_connection)

    p_list = sub.add_parser("list", help="List entities")
    p_list.add_argument("entity", choices=_entity_choices())
    p_list.add_argument("--start", type=int, default=0)
    p_list.add_argument("--limit", type=int, default=100)
    p_list.add_argument("--extra-query", help="JSON object merged into query params")
    p_list.set_defaults(func=cmd_list)

    p_get = sub.add_parser("get", help="Get one record by id")
    p_get.add_argument("entity", choices=_entity_choices())
    p_get.add_argument("id")
    p_get.set_defaults(func=cmd_get)

    p_create = sub.add_parser("create", help="Create a record")
    p_create.add_argument("entity", choices=_entity_choices())
    p_create.add_argument("payload", help="JSON object payload")
    p_create.set_defaults(func=cmd_create)

    p_update = sub.add_parser("update", help="Update a record")
    p_update.add_argument("entity", choices=_entity_choices())
    p_update.add_argument("id")
    p_update.add_argument("payload", help="JSON object payload")
    p_update.add_argument("--method", choices=["PUT", "PATCH"], default="PUT")
    p_update.set_defaults(func=cmd_update)

    p_delete = sub.add_parser("delete", help="Delete a record")
    p_delete.add_argument("entity", choices=_entity_choices())
    p_delete.add_argument("id")
    p_delete.set_defaults(func=cmd_delete)

    p_search = sub.add_parser("search", help="Search wrapped entities")
    p_search.add_argument("entity", choices=_entity_choices())
    p_search.add_argument("term")
    p_search.add_argument("--limit", type=int, default=25)
    p_search.add_argument("--fields", help="Comma-separated search fields")
    p_search.add_argument("--exact-match", action="store_true")
    p_search.add_argument("--extra-query", help="JSON object merged into query params")
    p_search.set_defaults(func=cmd_search)

    p_move = sub.add_parser("move_deal_stage", help="Move deal to another stage")
    p_move.add_argument("deal_id")
    p_move.add_argument("stage_id")
    p_move.add_argument("--status", choices=["open", "won", "lost", "deleted"])
    p_move.set_defaults(func=cmd_move_deal_stage)

    p_note = sub.add_parser("add_note", help="Create note attached to CRM objects")
    p_note.add_argument("content")
    p_note.add_argument("--deal-id")
    p_note.add_argument("--person-id")
    p_note.add_argument("--org-id")
    p_note.add_argument("--lead-id")
    p_note.set_defaults(func=cmd_add_note)

    p_req = sub.add_parser("request", help="Call any endpoint path")
    p_req.add_argument("method", choices=["GET", "POST", "PUT", "PATCH", "DELETE"])
    p_req.add_argument("path", help="Endpoint path such as /deals/123")
    p_req.add_argument("--query", help="JSON object query params")
    p_req.add_argument("--body", help="JSON object request body")
    p_req.set_defaults(func=cmd_request)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        result = args.func(args)
    except ValueError as exc:
        _print({"error": "validation", "message": str(exc)})
        return 2
    except Exception as exc:  # pragma: no cover
        _print({"error": "runtime", "message": str(exc)})
        return 1

    _print(result)
    if isinstance(result, dict) and result.get("error"):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
