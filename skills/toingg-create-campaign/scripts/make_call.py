#!/usr/bin/env python3
"""Trigger the Toingg make_call endpoint for a specific recipient."""
from __future__ import annotations

import argparse
import json
import os
import sys
import textwrap
from typing import Any, Dict

import requests

API_URL = "https://prepodapi.toingg.com/api/v3/make_call"
ENV_TOKEN_KEY = "TOINGG_API_TOKEN"


def make_call(name: str, phone_number: str, camp_id: str) -> Dict[str, Any]:
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

    payload: Dict[str, Any] = {
        "name": name,
        "phoneNumber": phone_number,
        "campID": camp_id,
        "asr": "AZURE",
        "startMessage": True,
        "clearMemory": False,
        "extraParams": {},
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
    parser = argparse.ArgumentParser(description="Trigger the Toingg make_call endpoint")
    parser.add_argument("name", help="Recipient name that appears inside Toingg logs")
    parser.add_argument("phone_number", help="Recipient phone number in international format")
    parser.add_argument("camp_id", help="Campaign ID to associate with the call")

    args = parser.parse_args()

    result = make_call(name=args.name, phone_number=args.phone_number, camp_id=args.camp_id)
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
