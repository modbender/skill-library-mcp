#!/usr/bin/env python3
"""
energy_predictor.py — Predictive scheduling from sentiment + time-of-day patterns.

Analyses outcome history to detect when the user performs best/worst.
Suggests optimal focus time blocks and warns about scheduling high-stakes
events at low-energy times.

Usage:
  python3 energy_predictor.py --analyse              # run full energy analysis
  python3 energy_predictor.py --suggest-focus-time   # suggest focus blocks for this week
  python3 energy_predictor.py --check "2025-03-15T09:00:00" "one_off_high_stakes"
  python3 energy_predictor.py --block-focus-week     # actually create focus blocks in calendar
"""

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

if sys.version_info < (3, 8):
    print(json.dumps({"error": "python_version_too_old", "detail": f"Python 3.8+ required."}))
    sys.exit(1)

SKILL_DIR = Path.home() / ".openclaw/workspace/skills/proactive-claw"
CONFIG_FILE = SKILL_DIR / "config.json"
sys.path.insert(0, str(SKILL_DIR / "scripts"))

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
SLOTS = ["early_morning", "morning", "midday", "afternoon", "late_afternoon", "evening"]
SLOT_HOURS = {
    "early_morning": (5, 8),
    "morning": (8, 11),
    "midday": (11, 13),
    "afternoon": (13, 16),
    "late_afternoon": (16, 18),
    "evening": (18, 22),
}
SENTIMENT_SCORE = {"positive": 1, "neutral": 0, "negative": -1}
MIN_OUTCOMES = 5  # minimum outcomes needed before making predictions


def load_config() -> dict:
    with open(CONFIG_FILE) as f:
        return json.load(f)


def hour_to_slot(hour: int) -> str:
    for slot, (start, end) in SLOT_HOURS.items():
        if start <= hour < end:
            return slot
    return "evening"


def analyse_energy(conn) -> dict:
    """Compute energy scores by day-of-week and time slot from outcome history."""
    rows = conn.execute("""
        SELECT event_datetime, sentiment, follow_up_needed, prep_done
        FROM outcomes
        WHERE event_datetime != ''
        ORDER BY event_datetime
    """).fetchall()

    if len(rows) < MIN_OUTCOMES:
        return {
            "status": "insufficient_data",
            "outcomes_analysed": len(rows),
            "needed": MIN_OUTCOMES,
            "message": f"Need at least {MIN_OUTCOMES} outcomes to detect patterns. Have {len(rows)}.",
        }

    # Accumulate scores per (day, slot) with dates for decay weighting
    scores = defaultdict(list)
    scores_dates = defaultdict(list)
    for row in rows:
        try:
            dt = datetime.fromisoformat(row["event_datetime"].replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            day = DAYS[dt.weekday()]
            slot = hour_to_slot(dt.hour)
            score = SENTIMENT_SCORE.get(row["sentiment"], 0)
            # Bonus for prep + no follow-up needed
            if row["prep_done"]:
                score += 0.3
            if not row["follow_up_needed"]:
                score += 0.2
            scores[(day, slot)].append(score)
            scores_dates[(day, slot)].append(row["event_datetime"])
        except Exception:
            continue

    # Compute decay-weighted averages
    try:
        from decay import weighted_average
        half_life = load_config().get("memory_decay_half_life_days", 90)
    except Exception:
        weighted_average = None
        half_life = 90

    avg_scores = {}
    for (day, slot), vals in scores.items():
        if len(vals) >= 2:  # need at least 2 data points
            if weighted_average and scores_dates.get((day, slot)):
                pairs = list(zip(vals, scores_dates[(day, slot)]))
                avg = round(weighted_average(pairs, half_life), 2)
            else:
                avg = round(sum(vals) / len(vals), 2)
            avg_scores[f"{day}_{slot}"] = {
                "day": day,
                "slot": slot,
                "avg_score": avg,
                "sample_size": len(vals),
            }

    if not avg_scores:
        return {"status": "insufficient_data", "message": "Not enough per-slot data yet."}

    sorted_slots = sorted(avg_scores.values(), key=lambda x: -x["avg_score"])
    best = sorted_slots[:3]
    worst = sorted_slots[-3:]

    # Build human insights
    insights = []
    for entry in best[:2]:
        insights.append(f"✅ {entry['day']} {entry['slot'].replace('_', ' ')} "
                        f"→ high performance (score {entry['avg_score']:+.1f})")
    for entry in worst[:2]:
        if entry["avg_score"] < 0:
            insights.append(f"⚠️ {entry['day']} {entry['slot'].replace('_', ' ')} "
                            f"→ low performance (score {entry['avg_score']:+.1f})")

    return {
        "status": "ok",
        "outcomes_analysed": len(rows),
        "best_times": best,
        "worst_times": worst,
        "all_slots": list(avg_scores.values()),
        "insights": insights,
    }


def check_event_timing(conn, event_datetime: str, event_type: str) -> dict:
    """Check if an event is scheduled at a good/bad time and warn if needed."""
    analysis = analyse_energy(conn)
    if analysis.get("status") != "ok":
        return {"status": "no_data", "warning": None}

    try:
        dt = datetime.fromisoformat(event_datetime.replace("Z", "+00:00"))
        day = DAYS[dt.weekday()]
        slot = hour_to_slot(dt.hour)
        key = f"{day}_{slot}"
    except Exception:
        return {"status": "parse_error"}

    all_slots = {s["day"] + "_" + s["slot"]: s for s in analysis.get("all_slots", [])}
    slot_data = all_slots.get(key)

    if not slot_data:
        return {"status": "no_data_for_slot", "slot": key}

    score = slot_data["avg_score"]
    warning = None
    tip = None  # initialise before branching so it is always defined
    if event_type in ("one_off_high_stakes", "routine_high_stakes") and score < -0.3:
        warning = (f"⚠️ Heads up: your {day} {slot.replace('_', ' ')} historically has "
                   f"lower energy (score {score:+.1f}). Consider rescheduling this high-stakes event "
                   f"to {analysis['best_times'][0]['day']} {analysis['best_times'][0]['slot'].replace('_', ' ')} "
                   f"(your best time).")
    elif score > 0.5:
        tip = f"✅ Good timing — {day} {slot.replace('_', ' ')} is one of your best windows."

    return {
        "status": "ok",
        "slot": key,
        "energy_score": score,
        "warning": warning,
        "tip": tip if not warning else None,
    }


def suggest_focus_blocks(conn, days_ahead: int = 5) -> dict:
    """Suggest focus time blocks for the coming week based on energy patterns."""
    analysis = analyse_energy(conn)
    if analysis.get("status") != "ok":
        return {"status": "no_data",
                "message": "Not enough history yet. Default: Monday and Tuesday mornings."}

    best = analysis.get("best_times", [])[:3]
    now = datetime.now(timezone.utc)
    suggestions = []

    for entry in best:
        target_day = entry["day"]
        slot_start_hour = SLOT_HOURS[entry["slot"]][0]
        # Find next occurrence of this day
        for delta in range(1, days_ahead + 1):
            candidate = now + timedelta(days=delta)
            if DAYS[candidate.weekday()] == target_day:
                block_start = candidate.replace(
                    hour=slot_start_hour, minute=0, second=0, microsecond=0)
                block_end = block_start + timedelta(hours=2)
                suggestions.append({
                    "day": target_day,
                    "slot": entry["slot"],
                    "energy_score": entry["avg_score"],
                    "start": block_start.isoformat(),
                    "end": block_end.isoformat(),
                    "title": f"🦞 Focus time ({target_day} {entry['slot'].replace('_', ' ')})",
                })
                break

    return {
        "status": "ok",
        "suggestions": suggestions,
        "based_on_outcomes": analysis["outcomes_analysed"],
    }


def create_focus_blocks(conn) -> dict:
    """Actually create suggested focus blocks in the OpenClaw calendar."""
    from cal_backend import CalendarBackend
    suggestions = suggest_focus_blocks(conn)
    if suggestions.get("status") != "ok":
        return suggestions

    backend = CalendarBackend()
    openclaw_cal_id = backend.get_openclaw_cal_id()
    created = []

    for s in suggestions.get("suggestions", []):
        try:
            start = datetime.fromisoformat(s["start"])
            end = datetime.fromisoformat(s["end"])
            if start.tzinfo is None:
                start = start.replace(tzinfo=timezone.utc)
            if end.tzinfo is None:
                end = end.replace(tzinfo=timezone.utc)
            event = backend.create_event(
                openclaw_cal_id, s["title"], start, end,
                f"Auto-scheduled focus block based on your energy patterns "
                f"(score {s['energy_score']:+.1f})"
            )
            created.append({"title": s["title"], "start": s["start"],
                             "event_id": event.get("id")})
        except Exception as e:
            created.append({"title": s["title"], "error": str(e)})

    return {"status": "ok", "created": created, "count": len(created)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--analyse", action="store_true")
    parser.add_argument("--suggest-focus-time", action="store_true")
    parser.add_argument("--check", nargs=2, metavar=("DATETIME", "EVENT_TYPE"))
    parser.add_argument("--block-focus-week", action="store_true")
    args = parser.parse_args()

    from memory import get_db
    conn = get_db()

    if args.analyse:
        print(json.dumps(analyse_energy(conn), indent=2))
    elif args.suggest_focus_time:
        print(json.dumps(suggest_focus_blocks(conn), indent=2))
    elif args.check:
        print(json.dumps(check_event_timing(conn, args.check[0], args.check[1]), indent=2))
    elif args.block_focus_week:
        print(json.dumps(create_focus_blocks(conn), indent=2))
    else:
        parser.print_help()

    conn.close()


if __name__ == "__main__":
    main()
