#!/usr/bin/env python3
"""Generate a compact health block for OpenClaw morning briefings."""

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

DATA_DIR = Path.home() / "vitavault" / "data"
LATEST = DATA_DIR / "latest.json"


def load_data():
    if not LATEST.exists():
        return None
    with open(LATEST, encoding="utf-8") as f:
        return json.load(f)


def parse_date(s):
    s = s.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(s)
    except ValueError:
        return datetime.strptime(s[:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)


def get_latest_value(records, type_key, cutoff):
    """Get most recent value for a metric type within cutoff."""
    matches = []
    for r in records:
        if r.get("type") != type_key:
            continue
        try:
            d = parse_date(r.get("startDate", ""))
        except Exception:
            continue
        if d >= cutoff and r.get("value") is not None:
            matches.append((d, float(r["value"])))
    if not matches:
        return None, None
    matches.sort(key=lambda x: x[0])
    return matches[-1]  # most recent


def get_avg_value(records, type_key, cutoff):
    """Get average value for a metric type within cutoff."""
    values = []
    for r in records:
        if r.get("type") != type_key:
            continue
        try:
            d = parse_date(r.get("startDate", ""))
        except Exception:
            continue
        if d >= cutoff and r.get("value") is not None:
            values.append(float(r["value"]))
    if not values:
        return None
    return sum(values) / len(values)


def get_total_value(records, type_key, cutoff):
    """Get sum of values for a metric type within cutoff (steps, calories, etc.)."""
    total = 0
    for r in records:
        if r.get("type") != type_key:
            continue
        try:
            d = parse_date(r.get("startDate", ""))
        except Exception:
            continue
        if d >= cutoff and r.get("value") is not None:
            total += float(r["value"])
    return total if total > 0 else None


def get_sleep_hours(records, cutoff):
    """Calculate sleep hours from sleep analysis records."""
    total_sec = 0
    for r in records:
        if r.get("type") != "sleepAnalysis":
            continue
        if r.get("categoryValue") not in ("Asleep", "AsleepCore", "AsleepDeep", "AsleepREM"):
            continue
        try:
            start = parse_date(r["startDate"])
            end = parse_date(r["endDate"])
        except Exception:
            continue
        if start >= cutoff - timedelta(hours=12):  # Sleep spans midnight
            total_sec += (end - start).total_seconds()
    if total_sec <= 0:
        return None
    hours = total_sec / 3600
    h, m = int(hours), int((hours % 1) * 60)
    return f"{h}h {m:02d}m"


def week_trend(records, type_key):
    """Compare this week vs last week average."""
    now = datetime.now(timezone.utc)
    this_week = now - timedelta(days=7)
    last_week = now - timedelta(days=14)

    this_vals = []
    last_vals = []
    for r in records:
        if r.get("type") != type_key or r.get("value") is None:
            continue
        try:
            d = parse_date(r.get("startDate", ""))
        except Exception:
            continue
        v = float(r["value"])
        if d >= this_week:
            this_vals.append(v)
        elif d >= last_week:
            last_vals.append(v)

    if not this_vals or not last_vals:
        return None

    this_avg = sum(this_vals) / len(this_vals)
    last_avg = sum(last_vals) / len(last_vals)
    pct = ((this_avg - last_avg) / last_avg) * 100
    if abs(pct) < 2:
        return "→"
    return f"↑{pct:.0f}%" if pct > 0 else f"↓{abs(pct):.0f}%"


def generate_briefing(as_json=False):
    data = load_data()
    if not data:
        if as_json:
            print(json.dumps({"error": "No VitaVault data imported"}))
        else:
            print("No VitaVault data imported yet.")
        return

    records = data.get("records", [])
    now = datetime.now(timezone.utc)
    cutoff_24h = now - timedelta(hours=24)

    # Gather metrics
    steps = get_total_value(records, "stepCount", cutoff_24h)
    hr_avg = get_avg_value(records, "heartRate", cutoff_24h)
    hr_min = None
    hr_max = None
    hr_vals = [float(r["value"]) for r in records
               if r.get("type") == "heartRate" and r.get("value")
               and parse_date(r.get("startDate", "")) >= cutoff_24h]
    if hr_vals:
        hr_min, hr_max = min(hr_vals), max(hr_vals)

    sleep = get_sleep_hours(records, cutoff_24h)
    _, weight = get_latest_value(records, "bodyMass", now - timedelta(days=7))
    hrv = get_avg_value(records, "heartRateVariabilitySDNN", cutoff_24h)
    spo2 = get_avg_value(records, "oxygenSaturation", cutoff_24h)
    rhr = get_avg_value(records, "restingHeartRate", cutoff_24h)
    active_cal = get_total_value(records, "activeEnergyBurned", cutoff_24h)
    exercise = get_total_value(records, "appleExerciseTime", cutoff_24h)

    # Trends
    sleep_trend = week_trend(records, "sleepAnalysis")
    step_trend = week_trend(records, "stepCount")

    if as_json:
        result = {
            "period": "24h",
            "steps": int(steps) if steps else None,
            "heartRate": {"avg": round(hr_avg) if hr_avg else None,
                          "min": round(hr_min) if hr_min else None,
                          "max": round(hr_max) if hr_max else None},
            "sleep": sleep,
            "weight": round(weight, 1) if weight else None,
            "hrv": round(hrv) if hrv else None,
            "spo2": round(spo2, 1) if spo2 else None,
            "restingHR": round(rhr) if rhr else None,
            "activeCal": round(active_cal) if active_cal else None,
            "exercise": round(exercise) if exercise else None,
            "trends": {"sleep": sleep_trend, "steps": step_trend},
        }
        print(json.dumps(result, indent=2))
        return

    # Human-readable output
    lines = ["🏥 Health (last 24h)"]

    line1 = []
    if steps:
        line1.append(f"Steps: {steps:,.0f}")
    if hr_avg:
        hr_str = f"HR: {hr_avg:.0f} avg"
        if hr_min and hr_max:
            hr_str += f" ({hr_min:.0f}-{hr_max:.0f})"
        line1.append(hr_str)
    if sleep:
        line1.append(f"Sleep: {sleep}")
    if line1:
        lines.append(" | ".join(line1))

    line2 = []
    if weight:
        line2.append(f"Weight: {weight:.1f} lbs")
    if hrv:
        line2.append(f"HRV: {hrv:.0f}ms")
    if spo2:
        line2.append(f"SpO2: {spo2:.0f}%")
    if rhr:
        line2.append(f"RHR: {rhr:.0f} bpm")
    if line2:
        lines.append(" | ".join(line2))

    line3 = []
    if active_cal:
        line3.append(f"Active Cal: {active_cal:,.0f}")
    if exercise:
        line3.append(f"Exercise: {exercise:.0f} min")
    if line3:
        lines.append(" | ".join(line3))

    # Trends
    trends = []
    if sleep_trend and sleep_trend != "→":
        trends.append(f"Sleep {sleep_trend} vs last week")
    if step_trend and step_trend != "→":
        trends.append(f"Steps {step_trend} vs last week")
    if trends:
        lines.append(f"Trend: {', '.join(trends)}")

    print("\n".join(lines))


if __name__ == "__main__":
    as_json = "--json" in sys.argv
    generate_briefing(as_json=as_json)
