#!/usr/bin/env python3
"""Fetch Toingg campaigns with optional pagination."""
from __future__ import annotations

import argparse
import json
import os
import sys
import textwrap
from typing import Any, Dict

import requests

API_URL = "https://prepodapi.toingg.com/api/v3/get_campaigns"
ENV_TOKEN_KEY = "TOINGG_API_TOKEN"
DEFAULT_LIMIT = 10


def fetch_campaigns(skip: int, limit: int, sort: int) -> Dict[str, Any]:
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
    }
    params = {
        "skip": skip,
        "limit": limit,
        "sort": sort,
    }

    response = requests.get(API_URL, headers=headers, params=params, timeout=60)
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
    parser = argparse.ArgumentParser(
        description="Fetch campaigns from Toingg with optional pagination"
    )
    parser.add_argument("--skip", type=int, default=0, help="Number of records to skip")
    parser.add_argument(
        "--limit",
        type=int,
        default=DEFAULT_LIMIT,
        help=f"Number of records to fetch (default {DEFAULT_LIMIT})",
    )
    parser.add_argument(
        "--sort",
        type=int,
        default=-1,
        help="Sort order accepted by the API (default -1 for descending)",
    )

    args = parser.parse_args()

    result = fetch_campaigns(skip=args.skip, limit=args.limit, sort=args.sort)
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
