#!/usr/bin/env python3
import argparse
import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone

BASE_URL = "https://beaconcha.in"


def post_json(url: str, api_key: str, payload: dict, timeout: int = 20):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "openclaw-beaconchain-skill/0.3",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main():
    parser = argparse.ArgumentParser(
        description="Check Beaconcha.in dashboard health using BeaconScore from performance-aggregate."
    )
    parser.add_argument("--dashboard-id", default=os.getenv("BEACONCHAIN_DASHBOARD_ID"))
    parser.add_argument("--api-key", default=os.getenv("BEACONCHAIN_API_KEY"))
    parser.add_argument("--chain", default=os.getenv("BEACONCHAIN_CHAIN", "mainnet"))
    parser.add_argument(
        "--window",
        default=os.getenv("BEACONCHAIN_WINDOW", "24h"),
        choices=["24h", "7d", "30d", "90d", "all_time"],
        help="Evaluation window supported by Beaconcha.in performance-aggregate.",
    )
    parser.add_argument(
        "--warn-threshold",
        type=float,
        default=float(os.getenv("BEACONCHAIN_WARN_THRESHOLD", "95")),
        help="BeaconScore threshold (0-100 or 0-1). Default 95%.",
    )
    parser.add_argument("--timeout", type=int, default=20)
    parser.add_argument("--json", action="store_true", help="Print detailed JSON output")
    args = parser.parse_args()

    if not args.dashboard_id or not args.api_key:
        print("ERROR: Set BEACONCHAIN_DASHBOARD_ID and BEACONCHAIN_API_KEY (or pass --dashboard-id/--api-key).")
        return 1

    threshold = args.warn_threshold / 100.0 if args.warn_threshold > 1 else args.warn_threshold

    result = {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "dashboard_id": int(args.dashboard_id),
        "chain": args.chain,
        "window": args.window,
        "epoch": None,
        "beaconscore": {
            "total": None,
            "attestation": None,
            "proposal": None,
            "sync_committee": None,
        },
        "duty_missed": {"attestation": 0, "proposal": 0, "sync_committee": 0},
        "finality": None,
        "status": "unknown",
        "summary": "",
        "errors": [],
    }

    try:
        payload = post_json(
            f"{BASE_URL}/api/v2/ethereum/validators/performance-aggregate",
            args.api_key,
            {
                "chain": args.chain,
                "validator": {"dashboard_id": int(args.dashboard_id)},
                "range": {"evaluation_window": args.window},
            },
            timeout=args.timeout,
        )
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        result["errors"].append({"source": "performance-aggregate", "http_status": e.code, "body": body[:400]})
        result["status"] = "error"
        result["summary"] = "performance-aggregate request failed."
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"status=error summary={result['summary']}")
        return 1
    except Exception as e:
        result["errors"].append({"source": "performance-aggregate", "error": str(e)})
        result["status"] = "error"
        result["summary"] = "performance-aggregate request failed."
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"status=error summary={result['summary']}")
        return 1

    data = payload.get("data") or {}
    bs = data.get("beaconscore") or {}
    duties = data.get("duties") or {}

    for k in ["total", "attestation", "proposal", "sync_committee"]:
        v = bs.get(k)
        if isinstance(v, (int, float)):
            result["beaconscore"][k] = float(v)

    result["duty_missed"]["attestation"] = int(((duties.get("attestation") or {}).get("missed") or 0))
    result["duty_missed"]["proposal"] = int(((duties.get("proposal") or {}).get("missed") or 0))
    result["duty_missed"]["sync_committee"] = int(((duties.get("sync_committee") or {}).get("missed") or 0))

    result["finality"] = data.get("finality")

    try:
        result["epoch"] = int(payload.get("range", {}).get("epoch", {}).get("end"))
    except Exception:
        result["epoch"] = None

    total = result["beaconscore"]["total"]
    if total is not None:
        if total >= threshold:
            result["status"] = "good"
            result["summary"] = f"BeaconScore {total*100:.2f}% (threshold {threshold*100:.2f}%)"
            exit_code = 0
        else:
            result["status"] = "bad"
            result["summary"] = f"BeaconScore {total*100:.2f}% below threshold {threshold*100:.2f}%"
            exit_code = 2
    else:
        missed_total = sum(result["duty_missed"].values())
        if missed_total > 0:
            result["status"] = "bad"
            result["summary"] = f"No BeaconScore total returned; missed duties detected ({missed_total})."
            exit_code = 2
        else:
            result["status"] = "good"
            result["summary"] = "No BeaconScore total returned; no missed duties detected."
            exit_code = 0

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"status={result['status']} summary={result['summary']}")
        if total is not None:
            print(
                "beaconscore="
                f"total:{result['beaconscore']['total']*100:.2f}% "
                f"att:{(result['beaconscore']['attestation']*100 if result['beaconscore']['attestation'] is not None else float('nan')):.2f}% "
                f"prop:{(result['beaconscore']['proposal']*100 if result['beaconscore']['proposal'] is not None else float('nan')):.2f}% "
                f"sync:{(result['beaconscore']['sync_committee']*100 if result['beaconscore']['sync_committee'] is not None else float('nan')):.2f}%"
            )
        print(
            "missed_duties="
            f"att:{result['duty_missed']['attestation']} "
            f"prop:{result['duty_missed']['proposal']} "
            f"sync:{result['duty_missed']['sync_committee']}"
        )
        if result["epoch"] is not None:
            print(f"epoch_end={result['epoch']} finality={result['finality']}")
        if result["errors"]:
            print(f"errors={len(result['errors'])} (use --json for details)")

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
