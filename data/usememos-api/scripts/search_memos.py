#!/usr/bin/env python3
"""Search memos by keyword in UseMemos."""
import os
import sys
import json
import urllib.request
import urllib.error
import urllib.parse

def main():
    base_url = os.environ.get('USEMEMOS_URL', '').rstrip('/')
    token = os.environ.get('USEMEMOS_TOKEN', '')

    if not base_url or not token:
        print("Error: USEMEMOS_URL and USEMEMOS_TOKEN must be set", file=sys.stderr)
        sys.exit(1)

    if len(sys.argv) < 2:
        print("Usage: search_memos.py '<query>' [limit]", file=sys.stderr)
        sys.exit(1)

    query = sys.argv[1]
    limit = sys.argv[2] if len(sys.argv) > 2 else '20'

    if not limit.isdigit():
        print("Error: limit must be a positive integer", file=sys.stderr)
        sys.exit(1)

    # Escape double quotes in query to prevent filter injection
    safe_query = query.replace('\\', '\\\\').replace('"', '\\"')
    params = {
        'pageSize': limit,
        'filter': f'content.contains("{safe_query}")'
    }
    url = f"{base_url}/api/v1/memos?{urllib.parse.urlencode(params)}"

    req = urllib.request.Request(
        url,
        headers={
            'Authorization': f'Bearer {token}',
            'Accept': 'application/json'
        }
    )

    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            memos = data.get('memos', [])
            if not memos:
                print("No memos found")
                return
            for m in memos:
                memo_id = m['name'].split('/')[-1]
                snippet = m['content'][:100].replace('\n', ' ')
                print(f"[{memo_id}] {snippet}...")
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} - {e.read().decode()}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
