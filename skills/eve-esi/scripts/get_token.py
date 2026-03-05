#!/usr/bin/env python3
"""EVE ESI token refresh helper.

Reads refresh_token from ~/.openclaw/eve-tokens.json and returns a fresh access_token.

Usage:
    python get_token.py --char main          # prints access token to stdout
    python get_token.py --char main --json   # prints full token response as JSON
    python get_token.py --list               # list all stored characters
"""
import argparse
import json
import os
import sys
import urllib.parse
import urllib.request

TOKENS_FILE = os.path.expanduser("~/.openclaw/eve-tokens.json")


def load_tokens():
    if not os.path.exists(TOKENS_FILE):
        print(f"ERROR: Tokens file not found: {TOKENS_FILE}", file=sys.stderr)
        print("Run auth_flow.py first to authenticate.", file=sys.stderr)
        sys.exit(1)
    with open(TOKENS_FILE) as f:
        return json.load(f)


def refresh_access_token(refresh_token, client_id):
    data = urllib.parse.urlencode({
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": client_id,
    }).encode()
    req = urllib.request.Request(
        "https://login.eveonline.com/v2/oauth/token",
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"ERROR: Token refresh failed ({e.code}): {body}", file=sys.stderr)
        sys.exit(1)


def save_tokens(data):
    with open(TOKENS_FILE, "w") as f:
        json.dump(data, f, indent=2)
    os.chmod(TOKENS_FILE, 0o600)


def main():
    parser = argparse.ArgumentParser(description="Get a fresh EVE ESI access token")
    parser.add_argument("--char", default="main",
                        help="Character key to use (default: main)")
    parser.add_argument("--json", action="store_true",
                        help="Output full token response as JSON")
    parser.add_argument("--list", action="store_true",
                        help="List all stored characters")
    args = parser.parse_args()

    tokens = load_tokens()
    chars = tokens.get("characters", {})

    if args.list:
        if not chars:
            print("No characters stored. Run auth_flow.py first.")
            return
        for key, c in chars.items():
            print(f"  {key}: {c.get('character_name')} (ID: {c.get('character_id')})")
        return

    if args.char not in chars:
        print(f"ERROR: Character '{args.char}' not found.", file=sys.stderr)
        print(f"Available: {', '.join(chars.keys()) or 'none'}", file=sys.stderr)
        print("Run auth_flow.py --char-name <name> to authenticate.", file=sys.stderr)
        sys.exit(1)

    char = chars[args.char]
    token_data = refresh_access_token(char["refresh_token"], char["client_id"])

    # Save updated refresh_token (EVE rotates it on each refresh)
    if "refresh_token" in token_data:
        chars[args.char]["refresh_token"] = token_data["refresh_token"]
        save_tokens(tokens)

    if args.json:
        print(json.dumps(token_data, indent=2))
    else:
        print(token_data["access_token"])


if __name__ == "__main__":
    main()
