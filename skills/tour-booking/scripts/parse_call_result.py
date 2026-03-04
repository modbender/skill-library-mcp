#!/usr/bin/env python3
"""Normalize raw call result into booking status."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def classify_status(call: dict) -> str:
    if call.get("mode") == "dry_run":
        return "pending"

    signal_fields = {
        "status": call.get("status"),
        "api_response": call.get("api_response"),
        "error_body": call.get("error_body"),
        "error": call.get("error"),
    }
    text = json.dumps(signal_fields).lower()
    if "confirmed" in text or "booked" in text:
        return "confirmed"
    if "callback" in text or "call back" in text:
        return "pending_callback"
    if "no answer" in text or "voicemail" in text:
        return "no_answer"
    if call.get("status") == "error":
        return "failed"
    return "pending"


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize call result JSON.")
    parser.add_argument("--input", required=True, help="Call result JSON.")
    parser.add_argument("--output", required=True, help="Normalized result JSON.")
    args = parser.parse_args()

    call = json.loads(Path(args.input).read_text())
    normalized = {
        "processed_at_utc": datetime.now(timezone.utc).isoformat(),
        "job_id": call.get("request_payload", {}).get("metadata", {}).get("job_id"),
        "booking_status": classify_status(call),
        "raw_status": call.get("status"),
        "raw_result": call,
    }

    out = Path(args.output)
    out.write_text(json.dumps(normalized, indent=2))
    print(str(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
