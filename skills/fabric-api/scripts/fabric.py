#!/usr/bin/env python3
"""Fabric API helper (Python)

Cross-platform wrapper for calling the Fabric HTTP API without relying on bash.

Usage:
  python3 scripts/fabric.py GET /v2/user/me

  python3 scripts/fabric.py POST /v2/notepads --json '{"name":"Test","text":"Hello","parentId":"@alias::inbox"}'

  python3 scripts/fabric.py POST /v2/notepads --file payload.json

  type payload.json | python scripts/fabric.py POST /v2/notepads   # Windows cmd.exe

Env:
  FABRIC_API_KEY  (required for API paths like /v2/..., unless --no-key)
  FABRIC_BASE     (optional, default: https://api.fabric.so)

Notes:
  * If the target is an absolute URL (https://...), the script will NOT send X-Api-Key unless --with-key.
  * This script uses only Python's standard library (urllib).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Dict, List, Tuple


def is_absolute_url(s: str) -> bool:
    return re.match(r"^https?://", s, re.IGNORECASE) is not None


def join_base(base: str, path: str) -> str:
    b = base.rstrip("/")
    p = path if path.startswith("/") else f"/{path}"
    return f"{b}{p}"


def parse_header_line(line: str) -> Tuple[str, str]:
    if ":" not in line:
        raise ValueError(f"Invalid --header value (missing ':'): {line}")
    key, value = line.split(":", 1)
    key = key.strip()
    value = value.strip()
    if not key:
        raise ValueError(f"Invalid --header key: {line}")
    return key, value


def has_header(headers: Dict[str, str], name: str) -> bool:
    name_l = name.lower()
    return any(k.lower() == name_l for k in headers.keys())


def main() -> int:
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument("method", help="HTTP method, e.g. GET/POST/PUT/PATCH/DELETE")
    parser.add_argument("target", help="API path (e.g. /v2/notepads) or absolute URL (https://...)")
    parser.add_argument("--base", default=os.environ.get("FABRIC_BASE", "https://api.fabric.so"))
    parser.add_argument("--json", dest="json_body", default=None, help="Request body as literal string (typically JSON)")
    parser.add_argument("--file", dest="file_path", default=None, help="Request body from file")
    parser.add_argument("--raw", action="store_true", help="With --file, send raw bytes (octet-stream)")
    parser.add_argument("--header", action="append", default=[], help="Header line 'K: V' (repeatable)")
    parser.add_argument("--no-key", action="store_true", help="Do not attach X-Api-Key (useful for presigned URLs)")
    parser.add_argument("--with-key", action="store_true", help="Force attaching X-Api-Key even for absolute URLs")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON responses")
    parser.add_argument("--no-pretty", action="store_true", help="Do not pretty-print JSON responses")

    args = parser.parse_args()

    method = (args.method or "").upper().strip()
    if not method:
        sys.stderr.write("ERROR: missing method\n")
        return 2

    abs_url = is_absolute_url(args.target)
    url = args.target if abs_url else join_base(args.base, args.target)

    # Default: don't leak API keys to presigned URLs
    should_send_key = (not args.no_key) and ((not abs_url) or args.with_key)

    api_key = os.environ.get("FABRIC_API_KEY", "").strip()
    if should_send_key and not api_key:
        sys.stderr.write("ERROR: FABRIC_API_KEY is not set.\n")
        sys.stderr.write("Set it in the environment or via OpenClaw skills config (skills.entries.fabric-api.apiKey).\n")
        return 2

    headers: Dict[str, str] = {}
    for h in args.header:
        k, v = parse_header_line(h)
        headers[k] = v

    if not has_header(headers, "Accept"):
        headers["Accept"] = "application/json"

    if should_send_key:
        headers["X-Api-Key"] = api_key

    body: bytes | None = None
    inferred_ct: str | None = None

    if args.json_body is not None:
        body = args.json_body.encode("utf-8")
        inferred_ct = "application/json"
    elif args.file_path is not None:
        p = Path(args.file_path)
        if args.raw:
            body = p.read_bytes()
            inferred_ct = "application/octet-stream"
        else:
            body = p.read_text(encoding="utf-8").encode("utf-8")
            inferred_ct = "application/json"
    elif not sys.stdin.isatty():
        data = sys.stdin.buffer.read()
        if data:
            body = data
            inferred_ct = "application/json"

    if body is not None and (not has_header(headers, "Content-Type")) and inferred_ct:
        headers["Content-Type"] = inferred_ct

    req = urllib.request.Request(url=url, data=body, method=method, headers=headers)

    try:
        with urllib.request.urlopen(req) as resp:
            resp_body = resp.read() or b""
            ct = resp.headers.get("Content-Type", "") or ""
            is_json = "json" in ct.lower()

            pretty = args.pretty or (sys.stdout.isatty() and (not args.no_pretty))
            if resp_body and pretty and is_json:
                try:
                    obj = json.loads(resp_body.decode("utf-8"))
                    sys.stdout.write(json.dumps(obj, indent=2, ensure_ascii=False))
                    sys.stdout.write("\n")
                    return 0
                except Exception:
                    pass

            if resp_body:
                sys.stdout.buffer.write(resp_body)
                if sys.stdout.isatty():
                    sys.stdout.write("\n")
            return 0

    except urllib.error.HTTPError as e:
        err_body = e.read() or b""
        sys.stderr.write(f"HTTP {e.code} {e.reason}\n")
        if err_body:
            sys.stdout.buffer.write(err_body)
            if sys.stdout.isatty():
                sys.stdout.write("\n")
        return 1

    except Exception as e:
        sys.stderr.write(f"ERROR: request failed: {e}\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
