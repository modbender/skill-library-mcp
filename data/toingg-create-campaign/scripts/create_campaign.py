#!/usr/bin/env python3
"""Create a Toingg campaign via the public API."""
import argparse
import json
import os
import sys
import textwrap
from typing import Any, Dict

import requests

API_URL = "https://prepodapi.toingg.com/api/v3/create_campaign"
ENV_TOKEN_KEY = "TOINGG_API_TOKEN"


def load_payload(path: str) -> Dict[str, Any]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError as exc:
        raise SystemExit(f"Payload file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON in payload file {path}: {exc}") from exc


def create_campaign(payload: Dict[str, Any]) -> Dict[str, Any]:
    token = os.getenv(ENV_TOKEN_KEY)
    if not token:
        raise SystemExit(
            textwrap.dedent(
                f"""
                Missing {ENV_TOKEN_KEY} environment variable.
                Export your Toingg bearer token before running this script, e.g.:
                  export {ENV_TOKEN_KEY}=your_token_here
                """
            ).strip()
        )

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
    try:
        response.raise_for_status()
    except requests.HTTPError as exc:
        details = response.text
        raise SystemExit(
            f"Request failed: {exc}. Response body:\n{details}"
        ) from exc

    try:
        return response.json()
    except json.JSONDecodeError:
        return {"raw": response.text}


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a Toingg campaign")
    parser.add_argument(
        "payload",
        help="Path to a JSON file that matches the Toingg create_campaign schema",
    )
    args = parser.parse_args()

    payload = load_payload(args.payload)
    result = create_campaign(payload)
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
