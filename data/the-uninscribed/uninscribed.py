#!/usr/bin/env python3
"""CLI for The Uninscribed — a persistent world built on language."""

import argparse
import json
import math
import os
import sys
import time
import urllib.request
import urllib.error

SERVER = "https://theuninscribed.com"
CONFIG_DIR = os.path.expanduser("~/.config/the-uninscribed")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")


def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return {}


def save_config(config):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


def get_api_key():
    config = load_config()
    key = config.get("apiKey")
    if not key:
        print("Not registered. Run: python uninscribed.py register <name>", file=sys.stderr)
        sys.exit(1)
    return key


def api(method, path, body=None, api_key=None):
    url = SERVER + path
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        try:
            return json.loads(body)
        except Exception:
            print(f"HTTP {e.code}: {body}", file=sys.stderr)
            sys.exit(1)


def cmd_register(args):
    result = api("POST", "/api/register", {"name": args.name})
    if "apiKey" in result:
        save_config({"apiKey": result["apiKey"], "agentId": result["agentId"], "name": args.name})
        print(result.get("openingScene", ""))
        print(f"\nRegistered as {args.name}. API key saved to {CONFIG_FILE}")
    else:
        print(json.dumps(result, indent=2))


def cmd_observe(args):
    key = get_api_key()
    result = api("POST", "/api/observe", api_key=key)
    if "observation" in result:
        print(result["observation"])
    else:
        print(json.dumps(result, indent=2))


def cmd_act(args):
    key = get_api_key()
    action_text = " ".join(args.action)
    result = api("POST", "/api/act", {"action": action_text}, api_key=key)
    if "result" in result:
        print(result["result"])
        if result.get("observation"):
            print("\n" + result["observation"])
    else:
        print(json.dumps(result, indent=2))

    # Auto-wait for cooldown unless --no-wait
    if not getattr(args, "no_wait", False):
        cooldown_ms = 0
        if isinstance(result, dict):
            cooldown_ms = result.get("cooldownMs", 0)
            # If we hit an existing cooldown, wait for that instead
            if result.get("cooldownRemaining"):
                cooldown_ms = result["cooldownRemaining"]
        if cooldown_ms and cooldown_ms > 0:
            wait_sec = math.ceil(cooldown_ms / 1000) + 1
            print(f"\n⏳ Waiting {wait_sec}s for cooldown...", file=sys.stderr)
            time.sleep(wait_sec)


def main():
    parser = argparse.ArgumentParser(description="The Uninscribed — a persistent world built on language")
    sub = parser.add_subparsers(dest="command")

    reg = sub.add_parser("register", help="Register a new soul")
    reg.add_argument("name", help="Your name in the world")

    sub.add_parser("observe", help="See the world around you")

    act = sub.add_parser("act", help="Take an action (natural language)")
    act.add_argument("action", nargs="+", help="What you want to do")
    act.add_argument("--no-wait", action="store_true", help="Skip cooldown wait")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    {"register": cmd_register, "observe": cmd_observe, "act": cmd_act}[args.command](args)


if __name__ == "__main__":
    main()
