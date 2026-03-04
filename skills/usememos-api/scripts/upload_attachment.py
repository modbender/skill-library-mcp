#!/usr/bin/env python3
"""Upload an attachment to UseMemos."""
import os
import sys
import json
import base64
import urllib.request
import urllib.error

def main():
    base_url = os.environ.get('USEMEMOS_URL', '').rstrip('/')
    token = os.environ.get('USEMEMOS_TOKEN', '')

    if not base_url or not token:
        print("Error: USEMEMOS_URL and USEMEMOS_TOKEN must be set", file=sys.stderr)
        sys.exit(1)

    if len(sys.argv) < 2:
        print("Usage: upload_attachment.py <filepath> [filename] [type]", file=sys.stderr)
        sys.exit(1)

    filepath = sys.argv[1]
    filename = sys.argv[2] if len(sys.argv) > 2 else os.path.basename(filepath)
    filetype = sys.argv[3] if len(sys.argv) > 3 else 'image/jpeg'

    with open(filepath, 'rb') as f:
        raw = f.read()

    encoded = base64.b64encode(raw).decode('utf-8')

    payload = json.dumps({
        'filename': filename,
        'content': encoded,
        'type': filetype
    }).encode()

    req = urllib.request.Request(
        f"{base_url}/api/v1/attachments",
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
            att_id = data['name'].split('/')[-1]
            print(f"Uploaded [{att_id}] {data['filename']} ({data.get('size', '?')} bytes)")
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} - {e.read().decode()}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
