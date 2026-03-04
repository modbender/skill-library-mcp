#!/usr/bin/env python3
"""
conflict_detector.py — Detect calendar conflicts and overloaded days.

Reads scan_calendar.py JSON from stdin or --file.
Outputs conflicts with human-readable messages.

Usage:
  python3 scan_calendar.py | python3 conflict_detector.py
  python3 conflict_detector.py --file last_scan.json
  python3 conflict_detector.py --file last_scan.json --days-ahead 3
"""

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

if sys.version_info < (3, 8):
    print(json.dumps({"error": "python_version_too_old", "detail": f"Python 3.8+ required."}))
    sys.exit(1)

SKILL_DIR = Path.home() / ".openclaw/workspace/skills/proactive-claw"


def parse_dt(s: str) -> datetime:
    dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def detect_overlaps(events: list) -> list:
    """Find events whose times overlap."""
    conflicts = []
    timed = []
    for e in events:
        start_raw = e.get("start", "")
        end_raw = e.get("end", "")
        if not start_raw or "T" not in start_raw:
            continue  # skip all-day
        try:
            s = parse_dt(start_raw)
            en = parse_dt(end_raw)
            timed.append((s, en, e))
        except Exception:
            continue

    # Sort by start
    timed.sort(key=lambda x: x[0])

    for i in range(len(timed)):
        for j in range(i + 1, len(timed)):
            s1, e1, ev1 = timed[i]
            s2, e2, ev2 = timed[j]
            if s2 >= e1:
                break  # no more overlaps for this event
            # Overlap detected
            overlap_min = int((min(e1, e2) - max(s1, s2)).total_seconds() / 60)
            t1 = ev1.get("summary") or ev1.get("title", "")
            t2 = ev2.get("summary") or ev2.get("title", "")
            conflicts.append({
                "type": "overlap",
                "key": f"overlap_{ev1.get('id','')}_{ev2.get('id','')}",
                "events": [t1, t2],
                "overlap_minutes": overlap_min,
                "message": (
                    f"⚠️ Conflict: *{t1}* and *{t2}* "
                    f"overlap by {overlap_min} min on "
                    f"{s1.strftime('%a %b %d')}. Which should move?"
                ),
            })

    return conflicts


def detect_overloaded_days(events: list, threshold: int = 4) -> list:
    """Flag days with more than `threshold` timed events."""
    from collections import defaultdict
    day_events = defaultdict(list)
    for e in events:
        start_raw = e.get("start", "")
        if not start_raw:
            continue
        try:
            date_str = start_raw[:10]
            day_events[date_str].append(e)
        except Exception:
            continue

    overloaded = []
    for date_str, evs in day_events.items():
        if len(evs) >= threshold:
            titles = ", ".join(e.get("summary") or e.get("title", "") for e in evs[:3])
            more = len(evs) - 3
            overloaded.append({
                "type": "overloaded_day",
                "key": f"overloaded_{date_str}",
                "date": date_str,
                "event_count": len(evs),
                "message": (
                    f"📅 Heavy day on {date_str}: {len(evs)} events "
                    f"({titles}{'...' if more > 0 else ''}). "
                    f"Want to reschedule anything?"
                ),
            })
    return overloaded


def detect_back_to_back(events: list, gap_minutes: int = 10) -> list:
    """Flag runs of 3+ events with < gap_minutes between them."""
    timed = []
    for e in events:
        start_raw = e.get("start", "")
        end_raw = e.get("end", "")
        if not start_raw or "T" not in start_raw:
            continue
        try:
            s = parse_dt(start_raw)
            en = parse_dt(end_raw)
            timed.append((s, en, e))
        except Exception:
            continue

    timed.sort(key=lambda x: x[0])
    conflicts = []
    run = [timed[0]] if timed else []

    for i in range(1, len(timed)):
        prev_end = run[-1][1]
        curr_start = timed[i][0]
        gap = (curr_start - prev_end).total_seconds() / 60
        if gap <= gap_minutes:
            run.append(timed[i])
        else:
            if len(run) >= 3:
                titles = " → ".join(e[2].get("summary") or e[2].get("title", "") for e in run)
                conflicts.append({
                    "type": "back_to_back",
                    "key": f"b2b_{run[0][0].date()}_{len(run)}",
                    "event_count": len(run),
                    "date": str(run[0][0].date()),
                    "message": (
                        f"🔴 Back-to-back run on {run[0][0].strftime('%a %b %d')}: "
                        f"{len(run)} meetings with no breaks ({titles}). "
                        f"Want to add buffer time?"
                    ),
                })
            run = [timed[i]]

    if len(run) >= 3:
        titles = " → ".join(e[2].get("summary") or e[2].get("title", "") for e in run)
        conflicts.append({
            "type": "back_to_back",
            "key": f"b2b_{run[0][0].date()}_{len(run)}",
            "event_count": len(run),
            "date": str(run[0][0].date()),
            "message": (
                f"🔴 Back-to-back run on {run[0][0].strftime('%a %b %d')}: "
                f"{len(run)} meetings with no breaks. Want to add buffer time?"
            ),
        })

    return conflicts


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", help="JSON file from scan_calendar.py (default: read stdin)")
    parser.add_argument("--overlap-threshold", type=int, default=1, help="Min overlap minutes to flag")
    parser.add_argument("--overload-threshold", type=int, default=4, help="Events per day to flag")
    parser.add_argument("--b2b-gap", type=int, default=10, help="Minutes gap for back-to-back detection")
    args = parser.parse_args()

    if args.file:
        data = json.loads(Path(args.file).read_text())
    else:
        data = json.loads(sys.stdin.read())

    events = data.get("events", [])
    # Filter to only events in the future
    now = datetime.now(timezone.utc)
    future_events = []
    for e in events:
        start_raw = e.get("start", "")
        try:
            if "T" in start_raw:
                s = parse_dt(start_raw)
                if s > now:
                    future_events.append(e)
            else:
                future_events.append(e)
        except Exception:
            future_events.append(e)

    overlaps = detect_overlaps(future_events)
    overloaded = detect_overloaded_days(future_events, args.overload_threshold)
    b2b = detect_back_to_back(future_events, args.b2b_gap)

    all_conflicts = overlaps + overloaded + b2b

    print(json.dumps({
        "total_conflicts": len(all_conflicts),
        "overlaps": len(overlaps),
        "overloaded_days": len(overloaded),
        "back_to_back_runs": len(b2b),
        "conflicts": all_conflicts,
    }, indent=2))


if __name__ == "__main__":
    main()
