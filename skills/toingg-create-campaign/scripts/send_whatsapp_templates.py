#!/usr/bin/env python3
"""Trigger Toingg WhatsApp templates for a contact list."""
from __future__ import annotations

import argparse
import json
import os
import sys
import textwrap
from typing import Any, List

import requests

API_URL = "https://prepodapi.toingg.com/api/v3/send_whatsapp_templates"
ENV_TOKEN_KEY = "TOINGG_API_TOKEN"


def send_templates(
    campaign_id: str,
    template_name: str,
    lang_code: str,
    contact_list: str,
    resend: bool,
    payload: List[Any],
) -> Any:
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

    params = {
        "campaignId": campaign_id,
        "templateName": template_name,
        "langCode": lang_code,
        "contactList": contact_list,
        "resend": str(resend).lower(),
    }
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    response = requests.post(API_URL, headers=headers, params=params, json=payload, timeout=60)
    try:
        response.raise_for_status()
    except requests.HTTPError as exc:
        raise SystemExit(
            f"send_whatsapp_templates failed: {exc}\nResponse body:\n{response.text}"
        ) from exc

    try:
        return response.json()
    except json.JSONDecodeError:
        return {"raw": response.text}


def main() -> None:
    parser = argparse.ArgumentParser(description="Send WhatsApp templates via Toingg")
    parser.add_argument("campaign_id", help="Toingg campaign ID")
    parser.add_argument("template_name", help="WhatsApp template name")
    parser.add_argument("lang_code", help="Template language code (e.g., en-US)")
    parser.add_argument("contact_list", help="Contact list name")
    parser.add_argument(
        "--resend",
        action="store_true",
        help="Set if re-sending to contacts who already received the template",
    )
    parser.add_argument(
        "--payload",
        help="Optional JSON array of template variables (default: [])",
    )
    args = parser.parse_args()

    payload: List[Any] = []
    if args.payload:
        try:
            with open(args.payload, "r", encoding="utf-8") as fh:
                payload = json.load(fh)
        except FileNotFoundError as exc:
            raise SystemExit(f"Payload file not found: {args.payload}") from exc
        except json.JSONDecodeError as exc:
            raise SystemExit(f"Invalid JSON payload: {exc}") from exc
        if not isinstance(payload, list):
            raise SystemExit("Payload must be a JSON array")

    result = send_templates(
        campaign_id=args.campaign_id,
        template_name=args.template_name,
        lang_code=args.lang_code,
        contact_list=args.contact_list,
        resend=args.resend,
        payload=payload,
    )
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
