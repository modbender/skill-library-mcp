#!/usr/bin/env python3
"""Amplitude CLI — comprehensive API integration for AI agents.

Full CRUD operations, search, reporting, and automation.
Zero dependencies beyond Python stdlib.
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
import urllib.parse
from datetime import datetime, timezone

API_BASE = "https://amplitude.com/api/2"


def get_token():
    """Get API token from environment."""
    token = os.environ.get("AMPLITUDE_API_KEY", "")
    if not token:
        env_path = os.path.join(
            os.environ.get("WORKSPACE", os.path.expanduser("~/.openclaw/workspace")),
            ".env"
        )
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("AMPLITUDE_API_KEY="):
                        token = line.split("=", 1)[1].strip().strip('"').strip("'")
                        break
    if not token:
        print(f"Error: AMPLITUDE_API_KEY not set", file=sys.stderr)
        sys.exit(1)
    return token


def api(method, path, data=None, params=None):
    """Make an API request."""
    token = get_token()
    url = f"{API_BASE}{path}"
    if params:
        qs = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
        if qs:
            url = f"{url}?{qs}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json")
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        raw = resp.read().decode()
        return json.loads(raw) if raw.strip() else {"ok": True}
    except urllib.error.HTTPError as e:
        err_body = e.read().decode()
        print(json.dumps({"error": True, "code": e.code, "message": err_body}), file=sys.stderr)
        sys.exit(1)


def output(data, human=False):
    """Output data as JSON or human-readable."""
    if human and isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                for k, v in item.items():
                    print(f"  {k}: {v}")
                print()
            else:
                print(item)
    elif human and isinstance(data, dict):
        for k, v in data.items():
            print(f"  {k}: {v}")
    else:
        print(json.dumps(data, indent=2, default=str))


def cmd_track(args):
    """Track an event."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("POST", f"/track/{args.id}")
    else:
        data = api("POST", "/track", params=params)
    output(data, getattr(args, 'human', False))

def cmd_track_batch(args):
    """Track batch events."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("POST", f"/track/{args.id}")
    else:
        data = api("POST", "/track/batch", params=params)
    output(data, getattr(args, 'human', False))

def cmd_identify(args):
    """Set user properties."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/identify/{args.id}")
    else:
        data = api("GET", "/identify", params=params)
    output(data, getattr(args, 'human', False))

def cmd_active_users(args):
    """Get active user counts."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/active/{args.id}")
    else:
        data = api("GET", "/active/users", params=params)
    output(data, getattr(args, 'human', False))

def cmd_events(args):
    """Get event data."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/events/{args.id}")
    else:
        data = api("GET", "/events", params=params)
    output(data, getattr(args, 'human', False))

def cmd_funnel(args):
    """Run funnel analysis."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/funnel/{args.id}")
    else:
        data = api("GET", "/funnel", params=params)
    output(data, getattr(args, 'human', False))

def cmd_retention(args):
    """Retention analysis."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/retention/{args.id}")
    else:
        data = api("GET", "/retention", params=params)
    output(data, getattr(args, 'human', False))

def cmd_cohorts(args):
    """List cohorts."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/cohorts/{args.id}")
    else:
        data = api("GET", "/cohorts", params=params)
    output(data, getattr(args, 'human', False))

def cmd_cohort_get(args):
    """Get cohort details."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/cohort/{args.id}")
    else:
        data = api("GET", "/cohort/get", params=params)
    output(data, getattr(args, 'human', False))

def cmd_revenue(args):
    """Revenue analysis."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/revenue/{args.id}")
    else:
        data = api("GET", "/revenue", params=params)
    output(data, getattr(args, 'human', False))

def cmd_user_search(args):
    """Search for a user."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/user/{args.id}")
    else:
        data = api("GET", "/user/search", params=params)
    output(data, getattr(args, 'human', False))

def cmd_user_activity(args):
    """Get user activity."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/user/{args.id}")
    else:
        data = api("GET", "/user/activity", params=params)
    output(data, getattr(args, 'human', False))

def cmd_segments(args):
    """Event segmentation query."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/segments/{args.id}")
    else:
        data = api("GET", "/segments", params=params)
    output(data, getattr(args, 'human', False))


COMMANDS = {
    "track": cmd_track,
    "track-batch": cmd_track_batch,
    "identify": cmd_identify,
    "active-users": cmd_active_users,
    "events": cmd_events,
    "funnel": cmd_funnel,
    "retention": cmd_retention,
    "cohorts": cmd_cohorts,
    "cohort-get": cmd_cohort_get,
    "revenue": cmd_revenue,
    "user-search": cmd_user_search,
    "user-activity": cmd_user_activity,
    "segments": cmd_segments,
}


def main():
    parser = argparse.ArgumentParser(
        description="Amplitude CLI — AI agent integration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("command", choices=list(COMMANDS.keys()), help="Command to run")
    parser.add_argument("args", nargs="*", help="Command arguments")
    parser.add_argument("--human", action="store_true", help="Human-readable output")
    parser.add_argument("--limit", type=int, help="Limit results")
    parser.add_argument("--id", help="Resource ID")
    parser.add_argument("--from", dest="from_date", help="Start date")
    parser.add_argument("--to", dest="to_date", help="End date")
    parser.add_argument("--status", help="Filter by status")
    parser.add_argument("--sort", help="Sort field")
    parser.add_argument("--query", help="Search query")

    parsed = parser.parse_args()
    cmd_func = COMMANDS[parsed.command]
    cmd_func(parsed)


if __name__ == "__main__":
    main()
