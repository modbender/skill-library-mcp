#!/usr/bin/env python3
import argparse
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def approx_coord(x: float, decimals: int) -> float:
    return round(x, decimals)


def load_items(path: Optional[str]) -> List[Dict[str, Any]]:
    raw = ""
    if path:
        with open(path, "r", encoding="utf-8") as f:
            raw = f.read()
    else:
        raw = sys.stdin.read()

    raw = raw.strip()
    if not raw:
        raise SystemExit("input is empty (provide --input or pipe JSON to stdin)")

    obj = json.loads(raw)
    if isinstance(obj, dict) and isinstance(obj.get("items"), list):
        return list(obj["items"])
    if isinstance(obj, list):
        return list(obj)
    raise SystemExit("input must be a JSON array of items, or an object with an 'items' array")


def redact_media(items: List[Dict[str, Any]]) -> None:
    for it in items:
        it.pop("media", None)


def apply_location_policy(items: List[Dict[str, Any]], *, no_location: bool, approx_decimals: Optional[int]) -> None:
    for it in items:
        if no_location:
            it.pop("lat", None)
            it.pop("lng", None)
            continue
        if approx_decimals is not None:
            if "lat" in it and isinstance(it["lat"], (int, float)):
                it["lat"] = approx_coord(float(it["lat"]), approx_decimals)
            if "lng" in it and isinstance(it["lng"], (int, float)):
                it["lng"] = approx_coord(float(it["lng"]), approx_decimals)


def post_json(url: str, token: str, payload: Dict[str, Any], timeout_sec: int) -> Tuple[int, str]:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("content-type", "application/json")
    req.add_header("authorization", f"Bearer {token}")
    req.add_header("user-agent", "cleanapp-ingest-skill/1.0.1")
    with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
        body = resp.read().decode("utf-8", errors="replace")
        return int(resp.status), body


def main() -> int:
    ap = argparse.ArgumentParser(description="Submit bulk problem signals to CleanApp /v1/reports:bulkIngest.")
    ap.add_argument("--base-url", default=os.environ.get("CLEANAPP_BASE_URL", "https://live.cleanapp.io"),
                    help="Base URL for CleanApp report-listener (default: https://live.cleanapp.io)")
    ap.add_argument("--input", help="Path to JSON file (or omit to read stdin)")
    ap.add_argument("--dry-run", action="store_true", help="Print payload and exit without sending")
    ap.add_argument("--no-media", action="store_true", help="Drop 'media' entries (recommended default)")
    ap.add_argument("--no-location", action="store_true", help="Remove lat/lng entirely")
    ap.add_argument("--approx-location", action="store_true", help="Round lat/lng to reduce precision (recommended default)")
    ap.add_argument("--approx-decimals", type=int, default=2, help="Decimals for --approx-location (default: 2)")
    ap.add_argument("--timeout", type=int, default=20, help="HTTP timeout seconds (default: 20)")

    args = ap.parse_args()

    token = os.environ.get("CLEANAPP_API_TOKEN", "").strip()
    if not token:
        raise SystemExit("missing required secret env CLEANAPP_API_TOKEN")

    items = load_items(args.input)

    if args.no_media:
        redact_media(items)
    approx_decimals = args.approx_decimals if args.approx_location else None
    apply_location_policy(items, no_location=args.no_location, approx_decimals=approx_decimals)

    # Ensure required source_id exists for each item.
    missing = [i for i, it in enumerate(items) if not str(it.get("source_id", "")).strip()]
    if missing:
        raise SystemExit(f"missing source_id for items at indexes: {missing}")

    payload = {"items": items}
    url = args.base_url.rstrip("/") + "/v1/reports:bulkIngest"

    if args.dry_run:
        out = {
            "url": url,
            "ts": utc_now_iso(),
            "items": items,
        }
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return 0

    status, body = post_json(url, token, payload, timeout_sec=args.timeout)
    print(body)
    if status >= 400:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
