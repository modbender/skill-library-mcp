#!/usr/bin/env python3
"""Upload contacts to a Toingg contact list."""
from __future__ import annotations

import argparse
import json
import os
import sys
import textwrap
from pathlib import Path
from typing import Any, List

import requests

API_URL = "https://prepodapi.toingg.com/api/v3/add_contacts"
ENV_TOKEN_KEY = "TOINGG_API_TOKEN"


def load_contacts(path: Path) -> List[Any]:
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except FileNotFoundError as exc:
        raise SystemExit(f"Contacts file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON in {path}: {exc}") from exc

    if not isinstance(data, list):
        raise SystemExit("Contacts JSON must be an array")
    return data


def add_contacts(contact_list: str, contacts: List[Any]) -> None:
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

    url = f"{API_URL}?contactList={contact_list}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    response = requests.post(url, headers=headers, json=contacts, timeout=60)
    try:
        response.raise_for_status()
    except requests.HTTPError as exc:
        raise SystemExit(
            f"add_contacts request failed: {exc}\nResponse body:\n{response.text}"
        ) from exc

    print(f"Uploaded {len(contacts)} contacts to list '{contact_list}'.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Create/update a Toingg contact list")
    parser.add_argument("contact_list", help="Name of the contact list (e.g., ClawTest)")
    parser.add_argument(
        "contacts_json",
        help="Path to JSON array produced by xlsx_to_contacts.py",
    )
    args = parser.parse_args()

    contacts = load_contacts(Path(args.contacts_json))
    add_contacts(args.contact_list, contacts)


if __name__ == "__main__":
    main()
