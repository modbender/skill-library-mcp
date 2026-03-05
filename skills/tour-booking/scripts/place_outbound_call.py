#!/usr/bin/env python3
"""Place outbound call through ElevenLabs API, or dry-run."""

from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_OUTBOUND_URL = "https://api.elevenlabs.io/v1/convai/phone-calls"


def post_json(url: str, headers: dict[str, str], payload: dict) -> dict:
    req = urllib.request.Request(
        url=url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Call listing office via ElevenLabs.")
    parser.add_argument("--payload", required=True, help="Prepared payload JSON.")
    parser.add_argument("--output", required=True, help="Output result JSON path.")
    parser.add_argument("--dry-run", action="store_true", help="Only emit prepared request.")
    parser.add_argument("--live", action="store_true", help="Execute live API call.")
    args = parser.parse_args()

    if args.dry_run and args.live:
        raise SystemExit("Choose --dry-run or --live, not both.")
    if not args.dry_run and not args.live:
        args.dry_run = True

    payload = json.loads(Path(args.payload).read_text())

    if args.dry_run:
        result = {
            "mode": "dry_run",
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "request_payload": payload,
            "status": "queued",
        }
    else:
        api_key = os.environ.get("ELEVENLABS_API_KEY")
        agent_id = os.environ.get("ELEVENLABS_AGENT_ID")
        if not api_key or not agent_id:
            raise SystemExit("Set ELEVENLABS_API_KEY and ELEVENLABS_AGENT_ID for --live mode.")

        outbound_url = os.environ.get("ELEVENLABS_OUTBOUND_URL", DEFAULT_OUTBOUND_URL)
        request_payload = {
            "agent_id": agent_id,
            "to_number": payload["to_number"],
            "system_prompt": payload["system_prompt"],
            "metadata": payload.get("metadata", {}),
        }
        headers = {
            "Content-Type": "application/json",
            "xi-api-key": api_key,
        }
        try:
            api_response = post_json(outbound_url, headers, request_payload)
            result = {
                "mode": "live",
                "created_at_utc": datetime.now(timezone.utc).isoformat(),
                "status": "submitted",
                "request_payload": request_payload,
                "api_response": api_response,
            }
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            result = {
                "mode": "live",
                "created_at_utc": datetime.now(timezone.utc).isoformat(),
                "status": "error",
                "http_status": exc.code,
                "error_body": body,
                "request_payload": request_payload,
            }
        except Exception as exc:  # noqa: BLE001
            result = {
                "mode": "live",
                "created_at_utc": datetime.now(timezone.utc).isoformat(),
                "status": "error",
                "error": str(exc),
            }

    out = Path(args.output)
    out.write_text(json.dumps(result, indent=2))
    print(str(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
