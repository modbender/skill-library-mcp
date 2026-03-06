#!/usr/bin/env python3
"""
Alpaca API Helper Script

Usage:
  python3 alpaca_api.py <method> <endpoint> [--data JSON] [--params JSON] [--timeout SECONDS]

Example:
  python3 alpaca_api.py GET /v2/account
  python3 alpaca_api.py GET /v2/orders --params '{"status":"open","limit":10}'
  python3 alpaca_api.py POST /v2/orders --data '{"symbol":"AAPL","qty":"1","side":"buy","type":"market","time_in_force":"gtc"}'
  python3 alpaca_api.py PATCH /v2/orders/<order_id> --data '{"qty":"2"}'

Set environment variables:
  ALPACA_API_KEY=your_key
  ALPACA_API_SECRET=your_secret
  ALPACA_BASE_URL=https://paper-api.alpaca.markets  # or https://api.alpaca.markets
"""

import argparse
import json
import os
import sys
import requests


def build_parser():
    parser = argparse.ArgumentParser(description="Call Alpaca Trading API endpoints.")
    parser.add_argument("method", help="HTTP method: GET, POST, PATCH, PUT, DELETE")
    parser.add_argument("endpoint", help="Endpoint path such as /v2/account")
    parser.add_argument("--data", help="JSON request body string", default=None)
    parser.add_argument("--params", help="JSON query string params", default=None)
    parser.add_argument("--timeout", type=float, default=15.0, help="Request timeout in seconds")
    return parser


def parse_json_arg(arg_name, value):
    if value is None:
        return None
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError as exc:
        print(f"Invalid JSON for {arg_name}: {exc}", file=sys.stderr)
        sys.exit(2)
    if not isinstance(parsed, dict):
        print(f"{arg_name} must be a JSON object", file=sys.stderr)
        sys.exit(2)
    return parsed


def make_request(method, endpoint, data=None, params=None, timeout=15.0):
    base_url = os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")
    api_key = os.getenv("ALPACA_API_KEY")
    api_secret = os.getenv("ALPACA_API_SECRET")

    if not api_key or not api_secret:
        print("Error: Set ALPACA_API_KEY and ALPACA_API_SECRET environment variables", file=sys.stderr)
        sys.exit(1)

    if not endpoint.startswith("/"):
        print("Error: endpoint must start with '/' (example: /v2/account)", file=sys.stderr)
        sys.exit(2)

    url = f"{base_url}{endpoint}"
    headers = {
        "APCA-API-KEY-ID": api_key,
        "APCA-API-SECRET-KEY": api_secret,
        "Content-Type": "application/json",
    }
    allowed_methods = {"GET", "POST", "PUT", "PATCH", "DELETE"}
    method = method.upper()

    if method not in allowed_methods:
        print(f"Unsupported method: {method}. Supported: {', '.join(sorted(allowed_methods))}", file=sys.stderr)
        sys.exit(2)

    try:
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            json=data,
            timeout=timeout,
        )
        response.raise_for_status()

        content_type = response.headers.get("content-type", "")
        if "application/json" in content_type:
            print(json.dumps(response.json(), indent=2))
        else:
            print(response.text)
        return 0
    except requests.exceptions.HTTPError:
        error_body = response.text if response is not None else "No response body"
        print(f"Error {response.status_code}: {error_body}", file=sys.stderr)
        return 1
    except requests.exceptions.RequestException as exc:
        print(f"Request failed: {exc}", file=sys.stderr)
        return 1


def main():
    parser = build_parser()
    args = parser.parse_args()
    data = parse_json_arg("--data", args.data)
    params = parse_json_arg("--params", args.params)
    code = make_request(args.method, args.endpoint, data=data, params=params, timeout=args.timeout)
    sys.exit(code)


if __name__ == "__main__":
    main()
