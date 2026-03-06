#!/usr/bin/env python3
"""Build call queue and booking plan from intake JSON."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a showing orchestration plan.")
    parser.add_argument("--intake", required=True, help="Path to intake JSON.")
    parser.add_argument("--output", required=True, help="Path to output plan JSON.")
    args = parser.parse_args()

    intake = json.loads(Path(args.intake).read_text())
    listings = intake.get("listings", [])

    call_queue = []
    blocked = []
    for idx, listing in enumerate(listings, start=1):
        if listing.get("office_phone"):
            call_queue.append(
                {
                    "job_id": f"showing-{idx:03d}",
                    "client_name": intake.get("client_name"),
                    "timezone": intake.get("timezone", "America/Toronto"),
                    "listing": listing,
                    "preferred_windows_text": intake.get("preferred_windows_text"),
                    "status": "queued",
                }
            )
        else:
            blocked.append(
                {
                    "listing": listing,
                    "reason": "missing_office_phone",
                    "status": "blocked",
                }
            )

    plan = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "client_name": intake.get("client_name"),
        "call_queue": call_queue,
        "blocked": blocked,
        "calendar_candidates": [],
    }

    out = Path(args.output)
    out.write_text(json.dumps(plan, indent=2))
    print(str(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
