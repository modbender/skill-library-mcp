#!/usr/bin/env python3
import argparse
import json
import sys

from lib.adapter import MobayiloVoiceAdapter
from lib.cli_runner import MobayiloCliError


def build_operator_summary(result: dict) -> str:
    mode = result.get("mode", "unknown")
    masked = result.get("destination_masked", "unknown")

    if result.get("dry_run"):
        return f"OUTCOME: dry_run (no execution) | mode={mode} | to={masked}"

    outcome = result.get("call_outcome") or {}
    outcome_state = (outcome.get("state") or "unknown").lower()
    definitive = outcome.get("definitive")

    if definitive is True:
        confidence = "definitive"
    elif definitive is False:
        confidence = "non_definitive"
    else:
        confidence = "unknown_confidence"

    if outcome_state != "unknown":
        note = outcome.get("note")
        summary = f"OUTCOME: {outcome_state} ({confidence}) | mode={mode} | to={masked}"
        if note:
            summary += f" | note={note}"
        return summary

    payload = result.get("payload") or {}
    payload_status = str(payload.get("status", "")).lower()
    if payload_status:
        return f"OUTCOME: {payload_status} (from_payload) | mode={mode} | to={masked}"

    return f"OUTCOME: unknown | mode={mode} | to={masked}"


def main():
    parser = argparse.ArgumentParser(description="Start a Mobayilo call via adapter")
    parser.add_argument("--destination", required=True, help="Destination phone number")
    parser.add_argument("--country", help="Country ISO or name")
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Execute a real call (default is safe dry-run mode)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Compatibility flag; dry-run is already the default unless --execute is set",
    )
    parser.add_argument(
        "--approved",
        action="store_true",
        help="Explicit approval token (required only when MOBY_REQUIRE_APPROVAL=1)",
    )
    parser.add_argument(
        "--callback",
        action="store_true",
        help="Use Mobayilo callback-to-phone mode (no local desktop mic/audio session)",
    )
    parser.add_argument(
        "--fallback-callback",
        action="store_true",
        help="In agent mode, automatically fallback to callback mode if local agent is not ready",
    )
    parser.add_argument(
        "--require-agent-ready",
        action="store_true",
        help="Fail fast in agent mode unless local agent UI is fully ready",
    )
    args = parser.parse_args()

    adapter = MobayiloVoiceAdapter()
    try:
        result = adapter.start_call(
            destination=args.destination,
            country=args.country,
            dry_run=not args.execute,
            approved=args.approved,
            callback=args.callback,
            fallback_callback=args.fallback_callback,
            require_agent_ready=args.require_agent_ready,
        )
        print(build_operator_summary(result), file=sys.stderr)
        print(json.dumps(result, indent=2))
    except MobayiloCliError as exc:
        error_payload = {
            "error": exc.args[0],
            "exit_code": exc.exit_code,
            "stdout": exc.stdout,
            "stderr": exc.stderr,
        }
        print("OUTCOME: failed", file=sys.stderr)
        print(json.dumps(error_payload, indent=2))


if __name__ == "__main__":
    main()
