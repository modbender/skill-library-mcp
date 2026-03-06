#!/usr/bin/env python3
"""Prepare a structured outbound-call payload from a booking job."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Build outbound payload from job JSON.")
    parser.add_argument("--job", required=True, help="Path to a single call job JSON.")
    parser.add_argument("--output", required=True, help="Path for outbound payload JSON.")
    args = parser.parse_args()

    job = json.loads(Path(args.job).read_text())
    listing = job["listing"]
    prompt = (
        "You are calling a listing office to book a property showing. "
        "State you are an AI assistant calling for a realtor and ask for available showing "
        f"slots for {listing['address']} for client {job['client_name']}. "
        f"Preferred windows: {job.get('preferred_windows_text', 'not provided')}. "
        "If unavailable, request the next two alternatives and callback instructions. "
        "Repeat the final agreed slot before ending."
    )

    payload = {
        "job_id": job["job_id"],
        "to_number": listing["office_phone"],
        "metadata": {
            "job_id": job["job_id"],
            "client_name": job["client_name"],
            "address": listing["address"],
            "listing_id": listing.get("listing_id"),
            "timezone": job.get("timezone", "America/Toronto"),
        },
        "system_prompt": prompt,
    }

    out = Path(args.output)
    out.write_text(json.dumps(payload, indent=2))
    print(str(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
