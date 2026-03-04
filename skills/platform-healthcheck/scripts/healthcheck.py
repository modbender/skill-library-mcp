#!/usr/bin/env python3
"""
Platform Health Check — Agent API Status Dashboard
Tests 20+ agent platforms for availability, response time, auth, and Cloudflare blocking.
"""

import argparse
import json
import os
import ssl
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

VERSION = "1.0.0"
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "data"
PLATFORMS_FILE = DATA_DIR / "platforms.json"
HISTORY_FILE = DATA_DIR / "history.json"

TIMEOUT = 10
MAX_WORKERS = 8

CF_MARKERS = [
    "cf-ray",
    "cf-cache-status",
    "cloudflare",
    "__cf_bm",
    "cf-mitigated",
]


@dataclass
class CheckResult:
    name: str
    url: str
    category: str
    status: str  # UP, DOWN, DEGRADED, BLOCKED, ERROR
    http_code: int = 0
    response_time_ms: int = 0
    auth_status: str = "N/A"  # OK, FAIL, N/A
    cloudflare: bool = False
    ssl_valid: bool = True
    error: str = ""
    checked_at: str = ""


def load_platforms():
    if PLATFORMS_FILE.exists():
        with open(PLATFORMS_FILE) as f:
            return json.load(f).get("platforms", [])
    return []


def load_auth_token(config_path, key):
    """Load an auth token from a config file."""
    expanded = os.path.expanduser(config_path)
    try:
        with open(expanded) as f:
            data = json.load(f)
        return data.get(key, "")
    except (OSError, json.JSONDecodeError, KeyError):
        return ""


def check_platform(platform):
    """Check a single platform's health."""
    name = platform["name"]
    url = platform["url"]
    category = platform.get("category", "other")
    method = platform.get("method", "GET")
    body = platform.get("body")
    is_local = platform.get("local", False)

    result = CheckResult(
        name=name,
        url=url,
        category=category,
        status="ERROR",
        checked_at=datetime.now(timezone.utc).isoformat(),
    )

    # Build request
    headers = {"User-Agent": "PlatformHealthCheck/1.0 (AgentBot)"}
    if body:
        headers["Content-Type"] = "application/json"

    req = Request(url, method=method, headers=headers)
    if body:
        req.data = body.encode()

    # Make the request
    start = time.monotonic()
    try:
        ctx = ssl.create_default_context()
        if is_local:
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

        resp = urlopen(req, timeout=TIMEOUT, context=ctx)
        elapsed = (time.monotonic() - start) * 1000

        result.http_code = resp.status
        result.response_time_ms = int(elapsed)

        # Check for Cloudflare
        resp_headers = {k.lower(): v for k, v in resp.headers.items()}
        for marker in CF_MARKERS:
            if marker in resp_headers or marker in resp_headers.get("server", "").lower():
                result.cloudflare = True
                break

        # Read response body for additional checks
        try:
            resp_body = resp.read(4096).decode("utf-8", errors="replace")
        except Exception:
            resp_body = ""

        if "cloudflare" in resp_body.lower() and "challenge" in resp_body.lower():
            result.cloudflare = True
            result.status = "BLOCKED"
        elif resp.status == 403 and result.cloudflare:
            result.status = "BLOCKED"
        elif resp.status < 400:
            result.status = "UP"
        elif resp.status < 500:
            result.status = "DEGRADED"
        else:
            result.status = "DOWN"

    except HTTPError as e:
        elapsed = (time.monotonic() - start) * 1000
        result.http_code = e.code
        result.response_time_ms = int(elapsed)

        resp_headers = {k.lower(): v for k, v in e.headers.items()}
        for marker in CF_MARKERS:
            if marker in resp_headers:
                result.cloudflare = True
                break

        if e.code == 403 and result.cloudflare and not platform.get("auth_config"):
            result.status = "BLOCKED"
        elif e.code in (401, 403):
            result.status = "UP"  # API is up, just needs auth
        elif e.code < 500:
            result.status = "DEGRADED"
        else:
            result.status = "DOWN"

        result.error = f"HTTP {e.code}"

    except ssl.SSLError as e:
        result.ssl_valid = False
        result.status = "DOWN"
        result.error = f"SSL: {str(e)[:100]}"

    except URLError as e:
        result.status = "DOWN"
        result.error = str(e.reason)[:100]

    except Exception as e:
        result.status = "ERROR"
        result.error = str(e)[:100]

    # Auth check (separate request)
    auth_url = platform.get("auth_url")
    auth_config = platform.get("auth_config")
    auth_key = platform.get("auth_key")
    if auth_url and auth_config and auth_key:
        token = load_auth_token(auth_config, auth_key)
        if token:
            auth_header = platform.get("auth_header", "Authorization")
            auth_prefix = platform.get("auth_prefix", "Bearer ")
            auth_req = Request(auth_url, headers={
                "User-Agent": "PlatformHealthCheck/1.0",
                auth_header: f"{auth_prefix}{token}",
            })
            try:
                auth_resp = urlopen(auth_req, timeout=TIMEOUT)
                result.auth_status = "OK" if auth_resp.status < 400 else "FAIL"
            except HTTPError as e:
                result.auth_status = "FAIL" if e.code in (401, 403) else "OK"
            except Exception:
                result.auth_status = "ERROR"
        else:
            result.auth_status = "NO_KEY"

    return result


def run_checks(platforms, only=None):
    """Run health checks concurrently."""
    if only:
        filter_terms = {n.strip().lower() for n in only.split(",")}
        platforms = [p for p in platforms
                     if any(t in p["name"].lower() for t in filter_terms)
                     or p.get("category", "").lower() in filter_terms]

    results = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {pool.submit(check_platform, p): p for p in platforms}
        for future in as_completed(futures):
            try:
                results.append(future.result())
            except Exception as e:
                p = futures[future]
                results.append(CheckResult(
                    name=p["name"], url=p["url"],
                    category=p.get("category", ""),
                    status="ERROR", error=str(e)[:100],
                    checked_at=datetime.now(timezone.utc).isoformat(),
                ))
    return sorted(results, key=lambda r: r.name)


def save_history(results):
    """Append results to history file."""
    history = []
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE) as f:
                history = json.load(f)
        except (json.JSONDecodeError, OSError):
            history = []

    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "results": [asdict(r) for r in results],
        "summary": {
            "total": len(results),
            "up": sum(1 for r in results if r.status == "UP"),
            "down": sum(1 for r in results if r.status == "DOWN"),
            "blocked": sum(1 for r in results if r.status == "BLOCKED"),
            "degraded": sum(1 for r in results if r.status == "DEGRADED"),
        },
    }
    history.append(entry)

    # Keep last 500 entries
    history = history[-500:]

    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)


# ─── OUTPUT ─────────────────────────────────────────────────────────

RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[36m"
GRAY = "\033[90m"

STATUS_COLORS = {
    "UP": GREEN,
    "DOWN": RED,
    "BLOCKED": YELLOW,
    "DEGRADED": YELLOW,
    "ERROR": RED,
}


def print_table(results):
    print(f"\n{BOLD}{'Platform':<25} {'Status':>8} {'Time':>8} {'Auth':>7} {'CF':>4} {'Code':>5}{RESET}")
    print("-" * 62)

    for r in results:
        sc = STATUS_COLORS.get(r.status, "")
        cf = "Yes" if r.cloudflare else "No"
        time_str = f"{r.response_time_ms}ms" if r.response_time_ms else "-"
        auth_color = GREEN if r.auth_status == "OK" else RED if r.auth_status == "FAIL" else GRAY
        print(
            f"{r.name:<25} {sc}{r.status:>8}{RESET} {time_str:>8} "
            f"{auth_color}{r.auth_status:>7}{RESET} {cf:>4} {r.http_code or '-':>5}"
        )
        if r.error and r.status in ("DOWN", "ERROR"):
            print(f"  {GRAY}└─ {r.error}{RESET}")

    print()
    up = sum(1 for r in results if r.status == "UP")
    down = sum(1 for r in results if r.status in ("DOWN", "ERROR"))
    blocked = sum(1 for r in results if r.status == "BLOCKED")
    degraded = sum(1 for r in results if r.status == "DEGRADED")
    total = len(results)
    print(f"Total: {total} | {GREEN}UP: {up}{RESET} | {RED}DOWN: {down}{RESET} | "
          f"{YELLOW}BLOCKED: {blocked}{RESET} | {YELLOW}DEGRADED: {degraded}{RESET}")
    print()


def print_history(days=7):
    if not HISTORY_FILE.exists():
        print("No history data. Run a check first.")
        return

    with open(HISTORY_FILE) as f:
        history = json.load(f)

    cutoff = datetime.now(timezone.utc).timestamp() - (days * 86400)
    recent = [h for h in history
              if datetime.fromisoformat(h["timestamp"]).timestamp() > cutoff]

    if not recent:
        print(f"No checks in the last {days} days.")
        return

    print(f"\n{BOLD}Health Check History (last {days} days, {len(recent)} checks){RESET}")
    print(f"{'Timestamp':<22} {'UP':>4} {'DOWN':>5} {'BLOCKED':>8} {'DEGRADED':>9}")
    print("-" * 52)
    for h in recent[-20:]:  # Show last 20
        s = h["summary"]
        ts = h["timestamp"][:19].replace("T", " ")
        print(f"{ts:<22} {s['up']:>4} {s['down']:>5} {s['blocked']:>8} {s['degraded']:>9}")
    print()


# ─── CLI ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Platform Health Check — Agent API Status Dashboard",
    )
    parser.add_argument("--version", action="version", version=f"Platform Health Check {VERSION}")
    sub = parser.add_subparsers(dest="command", required=True)

    p_check = sub.add_parser("check", help="Run health checks")
    p_check.add_argument("--json", action="store_true", help="Output JSON")
    p_check.add_argument("--only", help="Comma-separated platform names or categories")
    p_check.add_argument("--no-history", action="store_true", help="Don't save to history")

    p_hist = sub.add_parser("history", help="Show check history")
    p_hist.add_argument("--days", type=int, default=7, help="Days of history")

    args = parser.parse_args()

    if args.command == "check":
        platforms = load_platforms()
        if not platforms:
            print("No platforms configured.", file=sys.stderr)
            sys.exit(1)

        results = run_checks(platforms, only=args.only)

        if not args.no_history:
            save_history(results)

        if args.json:
            output = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "results": [asdict(r) for r in results],
                "summary": {
                    "total": len(results),
                    "up": sum(1 for r in results if r.status == "UP"),
                    "down": sum(1 for r in results if r.status in ("DOWN", "ERROR")),
                    "blocked": sum(1 for r in results if r.status == "BLOCKED"),
                },
            }
            print(json.dumps(output, indent=2))
        else:
            print_table(results)

        has_down = any(r.status in ("DOWN", "ERROR") for r in results
                       if not r.url.startswith("http://127."))
        sys.exit(1 if has_down else 0)

    elif args.command == "history":
        print_history(days=args.days)


if __name__ == "__main__":
    main()
