#!/usr/bin/env python3
"""Send a test message via Telegram to verify bot + chat ID work."""
import urllib.request, json, sys, re

if len(sys.argv) < 3:
    print("Usage: test-message.py <telegram_token> <chat_id>", file=sys.stderr)
    sys.exit(1)

token = sys.argv[1]
chat_id = sys.argv[2]

# Validate token format
if not re.match(r'^\d+:[A-Za-z0-9_-]+$', token):
    print("Error: Token format invalid.", file=sys.stderr)
    sys.exit(1)

# Validate chat_id is numeric (positive or negative)
if not re.match(r'^-?\d+$', chat_id):
    print("Error: Chat ID must be numeric.", file=sys.stderr)
    sys.exit(1)

try:
    data = json.dumps({
        'chat_id': chat_id,
        'text': '\U0001f415 Watch Dog connected successfully! Monitoring your gateway 24/7.'
    }).encode()
    req = urllib.request.Request(
        f'https://api.telegram.org/bot{token}/sendMessage',
        data=data,
        headers={'Content-Type': 'application/json'}
    )
    resp = json.loads(urllib.request.urlopen(req).read())
    if resp.get('ok'):
        print('Test message sent!')
    else:
        print(f"Error: {resp}", file=sys.stderr)
        sys.exit(1)
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)
