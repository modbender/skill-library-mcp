#!/usr/bin/env python3
"""Append structured events to the OpenClaw operations ledger."""

from __future__ import annotations

import argparse
import datetime as dt
import re
from pathlib import Path

EVENT_CHOICES = {
    "scope_lock",
    "predeploy_validation",
    "deploy_complete",
    "security_gate",
    "handover",
    "incident",
}

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def parse_csv(value: str) -> str:
    parts = [part.strip() for part in value.split(",") if part.strip()]
    return ",".join(parts) if parts else "none"


def ensure_ledger_exists(path: Path) -> None:
    if path.exists():
        return

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "# OpenClaw Manager Operations Ledger\n\n"
        "This file records operational metadata for OpenClaw management workflows.\n\n"
        "Required schema: `docs/product/skills/openclaw-manager/references/openclaw-ops-ledger-schema.md`\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Append an OpenClaw ops ledger event")
    parser.add_argument("--ledger-file", required=True, help="Path to ledger markdown file")
    parser.add_argument("--event", required=True, choices=sorted(EVENT_CHOICES))
    parser.add_argument("--operator", required=True)
    parser.add_argument("--mode", required=True)
    parser.add_argument("--provider", required=True)
    parser.add_argument("--os", required=True)
    parser.add_argument("--environment", required=True)
    parser.add_argument("--secrets-profile", required=True)
    parser.add_argument("--channels", default="")
    parser.add_argument("--integrations", default="")
    parser.add_argument("--security-status", required=True, choices=["pending", "passed", "failed"])
    parser.add_argument("--blocking-issues", default="none")
    parser.add_argument("--rollback-tested", required=True, choices=["yes", "no"])
    parser.add_argument("--next-owner", required=True)
    parser.add_argument("--next-action-date", required=True, help="YYYY-MM-DD")

    args = parser.parse_args()

    if not DATE_RE.match(args.next_action_date):
        print("[ERROR] --next-action-date must be in YYYY-MM-DD format")
        return 1

    # Also validate logical date formatting.
    try:
        dt.date.fromisoformat(args.next_action_date)
    except ValueError:
        print("[ERROR] --next-action-date is not a valid date")
        return 1

    ledger_path = Path(args.ledger_file)
    ensure_ledger_exists(ledger_path)

    timestamp = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    channels = parse_csv(args.channels)
    integrations = parse_csv(args.integrations)

    entry = (
        f"\n## {timestamp} | {args.event}\n"
        f"- operator: {args.operator}\n"
        f"- mode: {args.mode}\n"
        f"- provider: {args.provider}\n"
        f"- os: {args.os}\n"
        f"- environment: {args.environment}\n"
        f"- secrets_profile: {args.secrets_profile}\n"
        f"- channels: {channels}\n"
        f"- integrations: {integrations}\n"
        f"- security_status: {args.security_status}\n"
        f"- blocking_issues: {args.blocking_issues}\n"
        f"- rollback_tested: {args.rollback_tested}\n"
        f"- next_owner: {args.next_owner}\n"
        f"- next_action_date: {args.next_action_date}\n"
    )

    with ledger_path.open("a", encoding="utf-8") as handle:
        handle.write(entry)

    print(f"[OK] Appended ledger event: {args.event}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
