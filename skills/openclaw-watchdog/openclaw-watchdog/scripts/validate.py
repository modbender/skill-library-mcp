#!/usr/bin/env python3
"""Validate a Telegram bot token by calling getMe."""
import urllib.request, json, sys

if len(sys.argv) < 2:
    print("Usage: validate.py <telegram_token>", file=sys.stderr)
    sys.exit(1)

token = sys.argv[1]

# Validate token format (digits:alphanumeric)
import re
if not re.match(r'^\d+:[A-Za-z0-9_-]+$', token):
    print("Error: Token format invalid. Expected format: 123456:ABC-DEF...", file=sys.stderr)
    sys.exit(1)

try:
    resp = json.loads(urllib.request.urlopen(f'https://api.telegram.org/bot{token}/getMe').read())
    if resp.get('ok'):
        print(f"Token valid: @{resp['result']['username']}")
    else:
        print("Error: Token rejected by Telegram API", file=sys.stderr)
        sys.exit(1)
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)
