#!/usr/bin/env python3
"""Build DeliveryEnvelope objects and execute minimal delivery adapters."""

from __future__ import annotations

import argparse
import json
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from error_utils import emit_error


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def parse_ts(value: str) -> datetime:
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    return datetime.fromisoformat(value)


def human_text(event: dict[str, Any], route_primary: str) -> str:
    return (
        f"Market: {event.get('question') or event.get('entry_id')}\n"
        f"Current: {event.get('current')}%\n"
        f"Baseline: {event.get('baseline')}%\n"
        f"Absolute Change: {event.get('abs_pp')}pp\n"
        f"Relative Change: {event.get('rel_pct')}%\n"
        f"Reason: {event.get('reason', '')}\n"
        f"Baseline Time (UTC): {event.get('baseline_ts', '')}\n"
        f"Event Time (UTC): {event.get('ts', '')}\n"
        f"Entry ID: {event.get('entry_id')}\n"
        f"Request ID: {event.get('request_id')}\n"
        f"Route: {route_primary}\n"
        "— Powered by SignalRadar"
    )


def dedup_key(event: dict[str, Any]) -> str:
    return f"{event.get('entry_id')}:{event.get('reason', 'hit')}"


def severity_for_event(event: dict[str, Any]) -> str:
    try:
        abs_pp = float(event.get("abs_pp", 0))
    except (TypeError, ValueError):
        abs_pp = 0.0
    if abs_pp >= 20:
        return "P0"
    if abs_pp >= 10:
        return "P1"
    return "P2"


def should_suppress(event: dict[str, Any], dedup_dir: Path, dedup_window_minutes: int, *, severity: str, dry_run: bool) -> bool:
    if dedup_window_minutes <= 0 or severity in {"P0", "P1"}:
        return False
    key = dedup_key(event).replace("/", "_")
    path = dedup_dir / f"{key}.json"
    now = utc_now()
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            payload = json.load(f)
        ts = parse_ts(payload["ts"])
        if now - ts < timedelta(minutes=dedup_window_minutes):
            return True
    if dry_run:
        return False
    dedup_dir.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"ts": now.isoformat().replace("+00:00", "Z"), "severity": severity}) + "\n", encoding="utf-8")
    return False


def _route_parts(route: str) -> tuple[str, str]:
    if ":" not in route:
        return route.strip().lower(), ""
    left, right = route.split(":", 1)
    return left.strip().lower(), right.strip()


def deliver_envelope(envelope: dict[str, Any], route: str, timeout_sec: int) -> dict[str, Any]:
    channel, target = _route_parts(route)
    if channel == "openclaw":
        return {"ok": True, "status": "accepted", "adapter": "openclaw", "target": target or "direct"}
    if channel == "file":
        if not target:
            return {"ok": False, "status": "error", "adapter": "file", "error": "missing file target"}
        out = Path(target)
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("a", encoding="utf-8") as f:
            f.write(json.dumps(envelope, ensure_ascii=False) + "\n")
        return {"ok": True, "status": "delivered", "adapter": "file", "target": str(out)}
    if channel == "webhook":
        if not target.startswith("http://") and not target.startswith("https://"):
            return {"ok": False, "status": "error", "adapter": "webhook", "target": target, "error": "invalid webhook url"}
        body = json.dumps(envelope, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(target, data=body, method="POST", headers={"Content-Type": "application/json", "User-Agent": "signalradar/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
                code = int(getattr(resp, "status", 200))
            return {"ok": 200 <= code < 300, "status": "delivered" if 200 <= code < 300 else "error", "adapter": "webhook", "target": target, "http_status": code}
        except Exception as exc:  # noqa: BLE001
            return {"ok": False, "status": "error", "adapter": "webhook", "target": target, "error": str(exc)}
    return {"ok": False, "status": "error", "adapter": channel, "target": target, "error": f"unsupported adapter: {channel}"}


def attempt_delivery(envelope: dict[str, Any], routes: list[str], timeout_sec: int) -> dict[str, Any]:
    attempts: list[dict[str, Any]] = []
    for route in routes:
        result = deliver_envelope(envelope, route, timeout_sec)
        result["route"] = route
        attempts.append(result)
        if result.get("ok"):
            return {"ok": True, "status": result.get("status", "delivered"), "route": route, "attempts": attempts}
    return {"ok": False, "status": "error", "route": routes[0] if routes else "", "attempts": attempts}


def main() -> int:
    p = argparse.ArgumentParser(description="SignalRadar route step")
    p.add_argument("--events", required=True)
    p.add_argument("--out-envelopes", required=True)
    p.add_argument("--delivery-result", default="")
    p.add_argument("--route-primary", required=True)
    p.add_argument("--route-fallback", action="append", default=[])
    p.add_argument("--dedup-window-minutes", type=int, default=0)
    p.add_argument("--dedup-dir", default="cache/dedup")
    p.add_argument("--timeout-sec", type=int, default=8)
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    try:
        events = json.loads(Path(args.events).read_text(encoding="utf-8"))
        if not isinstance(events, list):
            raise ValueError("events must be a JSON array")

        dedup_dir = Path(args.dedup_dir)
        envelopes: list[dict[str, Any]] = []
        results: list[dict[str, Any]] = []
        now = utc_now().isoformat().replace("+00:00", "Z")

        for event in events:
            if not isinstance(event, dict):
                continue
            sev = severity_for_event(event)
            if should_suppress(event, dedup_dir, args.dedup_window_minutes, severity=sev, dry_run=args.dry_run):
                continue
            envelope = {
                "schema_version": "1.1.0",
                "delivery_id": f"del:{event.get('request_id')}",
                "request_id": event.get("request_id"),
                "idempotency_key": f"sr:{event.get('entry_id')}:{event.get('ts')}",
                "severity": sev,
                "route": {"primary": args.route_primary, "fallback": args.route_fallback},
                "human_text": human_text(event, args.route_primary),
                "machine_payload": {"signal_event": event},
                "ts": now,
            }
            envelopes.append(envelope)

            if args.dry_run:
                results.append({"request_id": envelope.get("request_id"), "ok": True, "status": "dry_run", "route": args.route_primary, "attempts": []})
            else:
                outcome = attempt_delivery(envelope, [args.route_primary] + list(args.route_fallback), timeout_sec=args.timeout_sec)
                results.append({"request_id": envelope.get("request_id"), **outcome})

        Path(args.out_envelopes).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out_envelopes).write_text(json.dumps(envelopes, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        if args.delivery_result:
            out = Path(args.delivery_result)
            out.parent.mkdir(parents=True, exist_ok=True)
            delivered = len([r for r in results if r.get("ok")])
            payload = {"schema_version": "1.0.0", "total": len(results), "delivered": delivered, "failed": len(results) - delivered, "results": results}
            out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        delivered = len([r for r in results if r.get("ok")])
        mode = "dry_run" if args.dry_run else "live"
        print(f"envelopes={len(envelopes)} delivered={delivered} failed={len(results)-delivered} mode={mode} out={args.out_envelopes}")
        return 0
    except Exception as exc:  # noqa: BLE001
        return emit_error("SR_ROUTE_FAILURE", f"route failed: {exc}", retryable=True, details={"script": "route_delivery.py", "events": args.events})


if __name__ == "__main__":
    raise SystemExit(main())
