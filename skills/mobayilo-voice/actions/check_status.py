#!/usr/bin/env python3
import argparse
import json
from typing import Any, Dict

from lib.adapter import MobayiloVoiceAdapter, mask_phone


def cents_to_currency(cents: Any) -> str:
    try:
        value = int(cents)
    except (TypeError, ValueError):
        return "unknown"
    return f"${value / 100:.2f}"


def build_summary(status: Dict[str, Any]) -> Dict[str, str]:
    auth = status.get("auth", {}) or {}
    account = auth.get("account", {}) or {}
    actor = auth.get("actor", {}) or {}
    balance = status.get("balance", {}) or {}
    update = status.get("update", {}) or {}

    email = actor.get("email") or "unknown"
    authenticated = "Yes" if auth.get("authenticated") else "No"

    balance_cents = balance.get("available_balance_cents")
    if balance_cents is None:
        balance_cents = balance.get("balance_cents")
    if balance_cents is None:
        balance_cents = account.get("available_balance_cents")
    balance_human = cents_to_currency(balance_cents)

    caller_id = mask_phone(account.get("caller_id_e164")) or "unknown"
    caller_status = account.get("caller_id_status") or "unknown"
    caller_verified = "Yes" if caller_status == "verified" else "No"

    ready = "Yes" if status.get("ready") else "No"
    update_state = "Yes" if update.get("needs_update") else "No"
    warnings = "; ".join(status.get("warnings", [])) if status.get("warnings") else "None"

    return {
        "Authenticated": authenticated,
        "Email": email,
        "Balance": balance_human,
        "Caller ID": caller_id,
        "Verified": caller_verified,
        "CLI Update Available": update_state,
        "Warnings": warnings,
        "Ready to dial": ready,
    }


def render_ascii_table(summary: Dict[str, str]) -> str:
    headers = ["Field", "Value"]
    rows = [[key, value] for key, value in summary.items()]
    col_widths = [
        max(len(headers[0]), *(len(row[0]) for row in rows)),
        max(len(headers[1]), *(len(str(row[1])) for row in rows)),
    ]

    def line(char: str = "-") -> str:
        return "+" + "+".join(char * (w + 2) for w in col_widths) + "+"

    def fmt_row(left: str, right: str) -> str:
        return f"| {left.ljust(col_widths[0])} | {str(right).ljust(col_widths[1])} |"

    output = [line(), fmt_row(headers[0], headers[1]), line()] + [
        fmt_row(row[0], row[1]) for row in rows
    ] + [line()]
    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(description="Check Mobayilo voice adapter readiness")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    args = parser.parse_args()

    adapter = MobayiloVoiceAdapter()
    status = adapter.get_status()
    summary = build_summary(status)

    adapter.log_event("check_status", {"summary": summary})
    adapter.emit_metric("mobayilo.status.checked", 1, tags={"ready": status.get("ready")})

    if args.pretty or args.json:
        if args.pretty:
            print(json.dumps(status, indent=2))
        else:
            print(json.dumps(status))
        return

    print(render_ascii_table(summary))


if __name__ == "__main__":
    main()
