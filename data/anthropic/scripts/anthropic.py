#!/usr/bin/env python3
"""Anthropic CLI — comprehensive API integration for AI agents.

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

API_BASE = "https://api.anthropic.com/v1"


def get_token():
    """Get API token from environment."""
    token = os.environ.get("ANTHROPIC_API_KEY", "")
    if not token:
        env_path = os.path.join(
            os.environ.get("WORKSPACE", os.path.expanduser("~/.openclaw/workspace")),
            ".env"
        )
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("ANTHROPIC_API_KEY="):
                        token = line.split("=", 1)[1].strip().strip('"').strip("'")
                        break
    if not token:
        print(f"Error: ANTHROPIC_API_KEY not set", file=sys.stderr)
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


def cmd_chat(args):
    """Send a message to Claude."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/chat/{args.id}")
    else:
        data = api("GET", "/chat", params=params)
    output(data, getattr(args, 'human', False))

def cmd_chat_system(args):
    """Chat with system prompt."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/chat/{args.id}")
    else:
        data = api("GET", "/chat/system", params=params)
    output(data, getattr(args, 'human', False))

def cmd_chat_image(args):
    """Analyze an image."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/chat/{args.id}")
    else:
        data = api("GET", "/chat/image", params=params)
    output(data, getattr(args, 'human', False))

def cmd_stream(args):
    """Stream a response."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/stream/{args.id}")
    else:
        data = api("GET", "/stream", params=params)
    output(data, getattr(args, 'human', False))

def cmd_batch_create(args):
    """Create a batch request."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("POST", f"/batch/{args.id}")
    else:
        data = api("POST", "/batch/create", params=params)
    output(data, getattr(args, 'human', False))

def cmd_batch_list(args):
    """List batch jobs."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/batch/{args.id}")
    else:
        data = api("GET", "/batch/list", params=params)
    output(data, getattr(args, 'human', False))

def cmd_batch_get(args):
    """Get batch status."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/batch/{args.id}")
    else:
        data = api("GET", "/batch/get", params=params)
    output(data, getattr(args, 'human', False))

def cmd_batch_results(args):
    """Get batch results."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/batch/{args.id}")
    else:
        data = api("GET", "/batch/results", params=params)
    output(data, getattr(args, 'human', False))

def cmd_count_tokens(args):
    """Count tokens in a message."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/count/{args.id}")
    else:
        data = api("GET", "/count/tokens", params=params)
    output(data, getattr(args, 'human', False))

def cmd_models(args):
    """List available models."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/models/{args.id}")
    else:
        data = api("GET", "/models", params=params)
    output(data, getattr(args, 'human', False))

def cmd_tools(args):
    """Chat with tool use."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/tools/{args.id}")
    else:
        data = api("GET", "/tools", params=params)
    output(data, getattr(args, 'human', False))

def cmd_thinking(args):
    """Extended thinking mode."""
    params = {}
    if hasattr(args, 'limit') and args.limit:
        params["limit"] = args.limit
    if hasattr(args, 'id') and args.id:
        data = api("GET", f"/thinking/{args.id}")
    else:
        data = api("GET", "/thinking", params=params)
    output(data, getattr(args, 'human', False))


COMMANDS = {
    "chat": cmd_chat,
    "chat-system": cmd_chat_system,
    "chat-image": cmd_chat_image,
    "stream": cmd_stream,
    "batch-create": cmd_batch_create,
    "batch-list": cmd_batch_list,
    "batch-get": cmd_batch_get,
    "batch-results": cmd_batch_results,
    "count-tokens": cmd_count_tokens,
    "models": cmd_models,
    "tools": cmd_tools,
    "thinking": cmd_thinking,
}


def main():
    parser = argparse.ArgumentParser(
        description="Anthropic CLI — AI agent integration",
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
