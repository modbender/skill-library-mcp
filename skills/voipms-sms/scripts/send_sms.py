#!/usr/bin/env python3
import argparse
import json
import os
import sys
import urllib.parse
import urllib.request

API_URL = "https://voip.ms/api/v1/rest.php"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Send an SMS via VoIP.ms API")
    parser.add_argument("--did", required=True, help="Source VoIP.ms DID")
    parser.add_argument("--dst", required=True, help="Destination phone number")
    parser.add_argument("--message", required=True, help="Message text")
    return parser.parse_args()


def get_credentials() -> tuple[str, str]:
    username = os.environ.get("VOIPMS_API_USERNAME")
    password = os.environ.get("VOIPMS_API_PASSWORD")

    if not username or not password:
        print(
            "Error: Missing VOIPMS_API_USERNAME or VOIPMS_API_PASSWORD "
            "environment variable.",
            file=sys.stderr,
        )
        sys.exit(1)

    return username, password


def main() -> None:
    args = parse_args()
    username, password = get_credentials()

    params = {
        "api_username": username,
        "api_password": password,
        "method": "sendSMS",
        "did": args.did,
        "dst": args.dst,
        "message": args.message,
        "content_type": "json",
    }
    data = urllib.parse.urlencode(params)
    url = f"{API_URL}?{data}"
    
    req = urllib.request.Request(url, headers={'User-Agent': 'OpenClaw/1.0'})

    try:
        with urllib.request.urlopen(req) as response:
            body = response.read().decode("utf-8")
    except Exception as exc:
        print(f"Error: API request failed: {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        parsed = json.loads(body)
        print(json.dumps(parsed, indent=2))
    except json.JSONDecodeError:
        print(body)


if __name__ == "__main__":
    main()
