#!/usr/bin/env python3
"""Fetch Toingg campaign analytics and print JSON to stdout."""
from __future__ import annotations

import json
import os
import sys
import textwrap
from typing import Any, Dict

import requests

API_URL = "https://prepodapi.toingg.com/api/v3/get_campaign_analytics"
ENV_TOKEN_KEY = "TOINGG_API_TOKEN"


def fetch_analytics() -> Dict[str, Any]:
    token = os.getenv(ENV_TOKEN_KEY)
    if not token:
        raise SystemExit(
            textwrap.dedent(
                f"""
                Missing {ENV_TOKEN_KEY}. Export your Toingg bearer token, e.g.:
                  export {ENV_TOKEN_KEY}=<token>
                """
            ).strip()
        )

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }
    response = requests.get(API_URL, headers=headers, timeout=60)
    try:
        response.raise_for_status()
    except requests.HTTPError as exc:
        raise SystemExit(
            f"Analytics request failed: {exc}\nResponse body:\n{response.text}"
        ) from exc

    try:
        return response.json()
    except json.JSONDecodeError:
        return {"raw": response.text}


def main() -> None:
    data = fetch_analytics()
    json.dump(data, sys.stdout, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
