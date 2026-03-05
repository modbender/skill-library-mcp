#!/usr/bin/env python3
"""Upload a file to a Slack channel using the v2 upload API.

Usage:
    python3 slack_file_upload.py --channel C123ABC --file /path/to/file.png [--title "My File"] [--message "Here's the report"]
"""

import argparse
import json
import mimetypes
import os
import sys
import urllib.request
import urllib.parse
import urllib.error

CONFIG_PATH = os.path.expanduser("~/.openclaw/openclaw.json")


def get_bot_token():
    with open(CONFIG_PATH) as f:
        config = json.load(f)
    token = config.get("channels", {}).get("slack", {}).get("botToken")
    if not token:
        print("Error: No botToken found in", CONFIG_PATH, file=sys.stderr)
        sys.exit(1)
    return token


def slack_api_form(token, method, params):
    """POST with application/x-www-form-urlencoded (for methods like files.*)."""
    url = f"https://slack.com/api/{method}"
    headers = {"Authorization": f"Bearer {token}"}
    body = urllib.parse.urlencode(params).encode()
    req = urllib.request.Request(url, data=body, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"Error: HTTP {e.code} from {method}: {error_body}", file=sys.stderr)
        sys.exit(1)


def slack_api_json(token, method, data):
    """POST with application/json (for methods like files.completeUploadExternal)."""
    url = f"https://slack.com/api/{method}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
    }
    body = json.dumps(data).encode()
    req = urllib.request.Request(url, data=body, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"Error: HTTP {e.code} from {method}: {error_body}", file=sys.stderr)
        sys.exit(1)


def upload_to_url(upload_url, file_path, filename):
    """POST file content to the presigned upload URL."""
    with open(file_path, "rb") as f:
        file_data = f.read()

    content_type = mimetypes.guess_type(file_path)[0] or "application/octet-stream"

    # Build multipart form data
    boundary = "----OpenClawUploadBoundary"
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        f"Content-Type: {content_type}\r\n"
        f"\r\n"
    ).encode() + file_data + f"\r\n--{boundary}--\r\n".encode()

    headers = {
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        "Content-Length": str(len(body)),
    }
    req = urllib.request.Request(upload_url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"Error: Upload failed (HTTP {e.code}): {error_body}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Upload a file to Slack")
    parser.add_argument("--channel", required=True, help="Channel ID (e.g. C123ABC)")
    parser.add_argument("--file", required=True, help="Path to file to upload")
    parser.add_argument("--title", help="Title for the file (defaults to filename)")
    parser.add_argument("--message", help="Initial comment/message with the file")
    args = parser.parse_args()

    file_path = os.path.abspath(args.file)
    if not os.path.isfile(file_path):
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    filename = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)
    title = args.title or filename
    token = get_bot_token()

    # Step 1: Get upload URL (form-encoded)
    get_url_resp = slack_api_form(token, "files.getUploadURLExternal", {
        "filename": filename,
        "length": file_size,
    })
    if not get_url_resp.get("ok"):
        print(f"Error: files.getUploadURLExternal failed: {get_url_resp.get('error', 'unknown')}", file=sys.stderr)
        sys.exit(1)

    upload_url = get_url_resp["upload_url"]
    file_id = get_url_resp["file_id"]

    # Step 2: Upload file to presigned URL
    upload_to_url(upload_url, file_path, filename)

    # Step 3: Complete the upload and share to channel (JSON)
    complete_data = {
        "files": [{"id": file_id, "title": title}],
        "channel_id": args.channel,
    }
    if args.message:
        complete_data["initial_comment"] = args.message

    complete_resp = slack_api_json(token, "files.completeUploadExternal", complete_data)
    if not complete_resp.get("ok"):
        print(f"Error: files.completeUploadExternal failed: {complete_resp.get('error', 'unknown')}", file=sys.stderr)
        sys.exit(1)

    # Output result
    files = complete_resp.get("files", [])
    result = {
        "ok": True,
        "file_id": file_id,
        "title": title,
        "channel": args.channel,
    }
    if files:
        result["permalink"] = files[0].get("permalink", "")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
