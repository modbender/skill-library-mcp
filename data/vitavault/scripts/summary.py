#!/usr/bin/env python3
"""Generate a health summary from VitaVault data."""

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

DATA_DIR = Path.home() / "vitavault" / "data"
LATEST = DATA_DIR / "latest.json"

# Priority metrics for summary (order matters)
SUMMARY_METRICS = [
    ("stepCount", "Steps", "count", "{:,.0f}"),
    ("heartRate", "Heart Rate", "bpm", "{:.0f}"),
    ("restingHeartRate", "Resting HR", "bpm", "{:.0f}"),
    ("heartRateVariabilitySDNN", "HRV", "ms", "{:.0f}"),
    ("oxygenSaturation", "SpO2", "%", "{:.1f}"),
    ("bodyMass", "Weight", "lbs", "{:.1f}"),
    ("activeEnergyBurned", "Active Cal", "kcal", "{:,.0f}"),
    ("appleExerciseTime", "Exercise", "min", "{:.0f}"),
    ("flightsClimbed", "Flights", "", "{:.0f}"),
    ("distanceWalkingRunning", "Distance", "mi", "{:.1f}"),
    ("vo2Max", "VO2 Max", "mL/kg/min", "{:.1f}"),
    ("bloodGlucose", "Glucose", "mg/dL", "{:.0f}"),
    ("bloodPressureSystolic", "BP Systolic", "mmHg", "{:.0f}"),
    ("bloodPressureDiastolic", "BP Diastolic", "mmHg", "{:.0f}"),
    ("respiratoryRate", "Resp Rate", "br/min", "{:.1f}"),
    ("bodyTemperature", "Temp", "F", "{:.1f}"),
]


def load_data():
    if not LATEST.exists():
        print("No data imported yet. Run: python3 scripts/import.py <export-file>", file=sys.stderr)
        sys.exit(1)
    with open(LATEST, encoding="utf-8") as f:
        return json.load(f)


def parse_date(s):
    s = s.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(s)
    except ValueError:
        return datetime.strptime(s[:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)


def summarize_sleep(records, cutoff):
    """Compute sleep duration from sleep analysis records."""
    sleep_records = [
        r for r in records
        if r.get("type") == "sleepAnalysis"
        and r.get("categoryValue") in ("Asleep", "AsleepCore", "AsleepDeep", "AsleepREM")
    ]
    # Filter by date
    sleep_records = [
        r for r in sleep_records
        if parse_date(r.get("startDate", "")) >= cutoff
    ]
    if not sleep_records:
        return None

    total_ms = 0
    for r in sleep_records:
        try:
            start = parse_date(r["startDate"])
            end = parse_date(r["endDate"])
            total_ms += (end - start).total_seconds()
        except Exception:
            pass

    if total_ms <= 0:
        return None

    hours = total_ms / 3600
    h = int(hours)
    m = int((hours - h) * 60)
    return {"hours": round(hours, 1), "display": f"{h}h {m:02d}m"}


def generate_summary(records, days=1):
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=days)

    result = {"period": f"last {days} day(s)", "metrics": {}, "sleep": None}

    # Numeric metrics
    for type_key, label, unit, fmt in SUMMARY_METRICS:
        values = []
        for rec in records:
            if rec.get("type") != type_key:
                continue
            try:
                rec_date = parse_date(rec.get("startDate", ""))
            except Exception:
                continue
            if rec_date < cutoff:
                continue
            v = rec.get("value")
            if v is not None:
                values.append(float(v))

        if not values:
            continue

        avg = sum(values) / len(values)
        result["metrics"][type_key] = {
            "label": label,
            "avg": round(avg, 2),
            "min": round(min(values), 2),
            "max": round(max(values), 2),
            "count": len(values),
            "unit": unit,
            "display": f"{fmt.format(avg)} {unit}".strip(),
        }

    # Sleep
    sleep = summarize_sleep(records, cutoff)
    if sleep:
        result["sleep"] = sleep

    return result


def format_human(summary):
    print(f"\n🏥 Health Summary ({summary['period']})")
    print("-" * 40)

    metrics = summary["metrics"]

    # Top line: key vitals
    parts = []
    for key in ["stepCount", "heartRate", "restingHeartRate"]:
        if key in metrics:
            m = metrics[key]
            parts.append(f"{m['label']}: {m['display']}")
    if summary.get("sleep"):
        parts.append(f"Sleep: {summary['sleep']['display']}")
    if parts:
        print(" | ".join(parts))

    # Second line: body + HRV + SpO2
    parts = []
    for key in ["bodyMass", "heartRateVariabilitySDNN", "oxygenSaturation"]:
        if key in metrics:
            m = metrics[key]
            parts.append(f"{m['label']}: {m['display']}")
    if parts:
        print(" | ".join(parts))

    # Additional metrics
    shown = {"stepCount", "heartRate", "restingHeartRate", "bodyMass",
             "heartRateVariabilitySDNN", "oxygenSaturation"}
    extras = [(k, v) for k, v in metrics.items() if k not in shown]
    if extras:
        print()
        for key, m in extras:
            range_str = f"({m['min']}-{m['max']})" if m["count"] > 1 else ""
            print(f"  {m['label']}: {m['display']} {range_str}  [{m['count']} samples]")

    if not metrics and not summary.get("sleep"):
        print("  No data available for this period.")

    print()


def main():
    parser = argparse.ArgumentParser(description="VitaVault health summary")
    parser.add_argument("--days", "-d", type=int, default=1, help="Number of days (default: 1)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    data = load_data()
    records = data.get("records", [])
    summary = generate_summary(records, days=args.days)

    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        format_human(summary)


if __name__ == "__main__":
    main()
