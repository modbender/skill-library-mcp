#!/usr/bin/env python3
import argparse
import json
import sys

import requests


def redact_secret(value):
    if not value:
        return None
    if len(value) <= 12:
        return "*" * len(value)
    return f"{value[:6]}...{value[-4:]}"


def onboard(agent_name, tenant_name=None, contact_email=None, inbox_prefix=None, source="human", reveal_api_key=False):
    url = "https://api.thrd.email/v1/onboarding/instant"
    payload = {"agent_name": agent_name, "source": source}
    if tenant_name:
        payload["tenant_name"] = tenant_name
    if contact_email:
        payload["contact_email"] = contact_email
    if inbox_prefix:
        payload["inbox_prefix"] = inbox_prefix

    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()

        # IMPORTANT: Do NOT write secrets to disk.
        # Store api_key in your secret manager (set THRD_API_KEY in your runtime environment).
        api_key = data.get("api_key")
        out = {
            "ok": True,
            "tenant": data.get("tenant"),
            "agent": data.get("agent"),
            "inbox": data.get("inbox"),
            "api_key_present": bool(api_key),
            "api_key_redacted": redact_secret(api_key),
            "scopes": data.get("scopes"),
            "machine_bootstrap": data.get("machine_bootstrap"),
        }
        if reveal_api_key and api_key:
            out["api_key"] = api_key
        print(json.dumps(out, indent=2))

        # Human-readable hints go to stderr to keep stdout machine-parseable.
        agent_id = (data.get("agent") or {}).get("id")
        inbox_addr = (data.get("inbox") or {}).get("address")
        print("Onboarding successful.", file=sys.stderr)
        if inbox_addr:
            print(f"Inbox: {inbox_addr}", file=sys.stderr)
        if reveal_api_key:
            print("Next: set THRD_API_KEY to the api_key value returned above.", file=sys.stderr)
        else:
            print("API key is redacted by default. Re-run with --reveal-api-key only in a trusted terminal.", file=sys.stderr)
        if agent_id:
            print(f"Public trust profile: https://thrd.email/a/{agent_id}", file=sys.stderr)
    except Exception as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Provision a Thrd tenant + agent inbox (sandbox) and return api_key once."
    )
    parser.add_argument("--agent-name", required=True, help="Required display/sender name for the agent.")
    parser.add_argument("--tenant-name", help="Optional tenant display name.")
    parser.add_argument("--contact-email", help="Optional contact email (for rate limiting / audit).")
    parser.add_argument("--inbox-prefix", help="Optional inbox local-part prefix (server adds a short suffix).")
    parser.add_argument(
        "--source",
        default="human",
        choices=["human", "agent"],
        help="Provisioning source (default: human).",
    )
    parser.add_argument(
        "--reveal-api-key",
        action="store_true",
        help="Include raw api_key in stdout JSON (default is redacted output).",
    )
    args = parser.parse_args()

    onboard(
        agent_name=args.agent_name,
        tenant_name=args.tenant_name,
        contact_email=args.contact_email,
        inbox_prefix=args.inbox_prefix,
        source=args.source,
        reveal_api_key=args.reveal_api_key,
    )
