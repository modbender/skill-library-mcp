#!/usr/bin/env python3
"""Create a new memo in UseMemos."""
import os
import sys
import json
import urllib.request
import urllib.error

def main():
    base_url = os.environ.get('USEMEMOS_URL', '').rstrip('/')
    token = os.environ.get('USEMEMOS_TOKEN', '')

    if not base_url or not token:
        print("Error: USEMEMOS_URL and USEMEMOS_TOKEN must be set", file=sys.stderr)
        sys.exit(1)

    if len(sys.argv) < 2:
        print("Usage: create_memo.py '<content>' [visibility]", file=sys.stderr)
        sys.exit(1)

    content = sys.argv[1]
    visibility = sys.argv[2] if len(sys.argv) > 2 else 'PRIVATE'

    payload = json.dumps({
        'content': content,
        'visibility': visibility
    }).encode()

    req = urllib.request.Request(
        f"{base_url}/api/v1/memos",
        data=payload,
        headers={
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        },
        method='POST'
    )

    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            memo_name = data['name']
            memo_id = memo_name.split('/')[-1]
            print(f"Created memo [{memo_id}]")
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} - {e.read().decode()}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
