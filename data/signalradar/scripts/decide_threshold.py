#!/usr/bin/env python3
"""Compute SignalEvent objects from normalized snapshots and baseline cache."""

from __future__ import annotations

import argparse
import json
import math
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from error_utils import emit_error


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def entry_id_for(row: dict[str, Any]) -> str:
    return f"{row['source']}:{row['market_id']}:{row['slug']}:{row['event_id']}"


def safe_name(entry_id: str) -> str:
    return entry_id.replace("/", "_")


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write("\n")


def is_inactive(row: dict[str, Any]) -> bool:
    status = str(row.get("status", "active")).lower()
    return status in {"closed", "resolved", "inactive", "expired"}


def compute_rel_pct(current: float, baseline: float) -> float:
    if baseline == 0:
        return 0.0
    return (current - baseline) / baseline * 100.0


def parse_iso_ts(value: str) -> datetime | None:
    text = value.strip()
    if not text:
        return None
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00"))
    except Exception:
        return None


def cleanup_baselines(
    baseline_dir: Path,
    active_entry_ids: set[str],
    *,
    ttl_days: int,
    dry_run: bool,
) -> int:
    if not baseline_dir.exists():
        return 0
    now = datetime.now(timezone.utc)
    removed = 0
    for path in baseline_dir.glob("*.json"):
        try:
            payload = load_json(path, {})
        except Exception:
            continue
        if not isinstance(payload, dict):
            continue
        entry_id = str(payload.get("entry_id", "")).strip()
        baseline_ts = parse_iso_ts(str(payload.get("baseline_ts", "")))
        expired_by_inactive = bool(entry_id) and entry_id not in active_entry_ids
        expired_by_ttl = False
        if baseline_ts is not None and ttl_days > 0:
            expired_by_ttl = (now - baseline_ts).days >= ttl_days
        if not expired_by_inactive and not expired_by_ttl:
            continue
        removed += 1
        if not dry_run:
            try:
                path.unlink()
            except Exception:
                removed -= 1
    return removed


def main() -> int:
    parser = argparse.ArgumentParser(description="SignalRadar decide step")
    parser.add_argument("--snapshots", required=True, help="Normalized snapshots JSON file")
    parser.add_argument("--out-events", required=True, help="Output SignalEvent JSON file")
    parser.add_argument("--baseline-dir", default="cache/baselines", help="Baseline storage directory")
    parser.add_argument("--audit-log", default="cache/events/signal_events.jsonl", help="Audit log JSONL path")
    parser.add_argument("--threshold-abs-pp", type=float, default=5.0, help="Default abs_pp threshold")
    parser.add_argument("--threshold-rel-pct", type=float, default=5.0, help="Aux rel_pct threshold")
    parser.add_argument("--emit-baseline-events", action="store_true", help="Emit baseline init records")
    parser.add_argument("--cleanup-expired", action="store_true", help="Cleanup baselines for inactive/expired entries")
    parser.add_argument("--cleanup-ttl-days", type=int, default=45, help="TTL days for baseline cleanup")
    parser.add_argument("--dry-run", action="store_true", help="Compute events without mutating baseline/audit state")
    args = parser.parse_args()

    snapshots_path = Path(args.snapshots)
    baseline_dir = Path(args.baseline_dir)
    out_events_path = Path(args.out_events)
    audit_log_path = Path(args.audit_log)

    try:
        rows = load_json(snapshots_path, [])
        if not isinstance(rows, list):
            raise ValueError("snapshots must be a JSON array")

        events: list[dict[str, Any]] = []
        audit_log_path.parent.mkdir(parents=True, exist_ok=True)
        active_entry_ids: set[str] = set()

        for row in rows:
            if not isinstance(row, dict):
                continue
            if is_inactive(row):
                continue

            try:
                current = float(row["probability"])
            except Exception:
                continue
            source = str(row.get("source", "polymarket"))
            market_id = str(row["market_id"])
            slug = str(row["slug"])
            event_id = str(row["event_id"])
            question = str(row.get("question", ""))
            entry_id = f"{source}:{market_id}:{slug}:{event_id}"
            active_entry_ids.add(entry_id)
            baseline_file = baseline_dir / f"{safe_name(entry_id)}.json"
            baseline_doc = load_json(baseline_file, None)

            request_id = str(uuid.uuid4())
            now = utc_now()

            if baseline_doc is None:
                baseline_doc = {
                    "entry_id": entry_id,
                    "source": source,
                    "baseline": current,
                    "baseline_ts": now,
                    "updated_by": "decide_threshold.py",
                    "update_reason": "baseline init",
                    "version": 1,
                }
                if not args.dry_run:
                    save_json(baseline_file, baseline_doc)
                decision = "BASELINE"
                event = None
                if args.emit_baseline_events:
                    event = {
                        "schema_version": "1.0.0",
                        "request_id": request_id,
                        "entry_id": entry_id,
                        "source": source,
                        "question": question,
                        "current": current,
                        "baseline": current,
                        "abs_pp": 0.0,
                        "rel_pct": 0.0,
                        "threshold_abs_pp": args.threshold_abs_pp,
                        "threshold_rel_pct": args.threshold_rel_pct,
                        "confidence": "low",
                        "reason": "baseline initialized",
                        "ts": now,
                        "baseline_ts": now,
                    }
                    events.append(event)
            else:
                baseline = float(baseline_doc.get("baseline", current))
                baseline_ts = str(baseline_doc.get("baseline_ts", now))
                abs_pp = abs(current - baseline)
                rel_pct = compute_rel_pct(current, baseline)
                row_threshold = row.get("threshold_abs_pp")
                try:
                    threshold_abs = float(row_threshold) if row_threshold is not None else float(args.threshold_abs_pp)
                except (TypeError, ValueError):
                    threshold_abs = float(args.threshold_abs_pp)
                hit = abs_pp >= threshold_abs
                decision = "HIT" if hit else "SILENT"
                event = None
                if hit:
                    event = {
                        "schema_version": "1.0.0",
                        "request_id": request_id,
                        "entry_id": entry_id,
                        "source": source,
                        "question": question,
                        "current": round(current, 6),
                        "baseline": round(baseline, 6),
                        "abs_pp": round(abs_pp, 6),
                        "rel_pct": round(rel_pct, 6),
                        "threshold_abs_pp": threshold_abs,
                        "threshold_rel_pct": args.threshold_rel_pct,
                        "confidence": "high" if abs_pp >= max(2 * threshold_abs, 10.0) else "medium",
                        "reason": "abs_pp crossed threshold",
                        "ts": now,
                        "baseline_ts": baseline_ts,
                        "volume_24h": row.get("volume_24h"),
                    }
                    events.append(event)

                    next_version = int(baseline_doc.get("version", 1)) + 1
                    baseline_doc = {
                        "entry_id": entry_id,
                        "source": source,
                        "baseline": current,
                        "baseline_ts": now,
                        "updated_by": "decide_threshold.py",
                        "update_reason": "HIT triggered, new baseline set",
                        "version": next_version,
                    }
                    if not args.dry_run:
                        save_json(baseline_file, baseline_doc)

            if not args.dry_run:
                with audit_log_path.open("a", encoding="utf-8") as af:
                    af.write(
                        json.dumps(
                            {
                                "ts": now,
                                "request_id": request_id,
                                "entry_id": entry_id,
                                "decision": decision,
                                "source": source,
                            },
                            ensure_ascii=False,
                        )
                        + "\n"
                    )

        removed = 0
        if args.cleanup_expired:
            removed = cleanup_baselines(
                baseline_dir,
                active_entry_ids,
                ttl_days=args.cleanup_ttl_days,
                dry_run=args.dry_run,
            )
        save_json(out_events_path, events)
        mode = "dry_run" if args.dry_run else "live"
        print(f"processed={len(rows)} events={len(events)} cleanup_removed={removed} mode={mode} out={out_events_path}")
        return 0
    except Exception as exc:  # noqa: BLE001
        return emit_error(
            "SR_VALIDATION_ERROR",
            f"decide failed: {exc}",
            retryable=False,
            details={"script": "decide_threshold.py", "snapshots": str(snapshots_path)},
        )


if __name__ == "__main__":
    raise SystemExit(main())
