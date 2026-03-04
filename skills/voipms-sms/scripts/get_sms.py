#!/usr/bin/env python3
import argparse
import json
import os
import sys
from datetime import date, timedelta
import urllib.parse
import urllib.request

API_URL = "https://voip.ms/api/v1/rest.php"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch SMS messages via VoIP.ms API")
    parser.add_argument("--did", help="Source VoIP.ms DID (optional)")
    parser.add_argument(
        "--days",
        type=int,
        default=1,
        help="Number of days back to fetch (default: 1)",
    )
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


def date_range(days: int) -> tuple[str, str]:
    if days < 1:
        print("Error: --days must be at least 1.", file=sys.stderr)
        sys.exit(1)

    today = date.today()
    start_date = today - timedelta(days=days)
    return start_date.isoformat(), today.isoformat()


def main() -> None:
    args = parse_args()
    username, password = get_credentials()
    date_from, date_to = date_range(args.days)

    params = {
        "api_username": username,
        "api_password": password,
        "method": "getSMS",
        "from": date_from,
        "to": date_to,
        "content_type": "json",
    }
    if args.did:
        params["did"] = args.did

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
