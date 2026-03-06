#!/usr/bin/env python3
"""Normalize garmin_tracking.json to the Garmin tracker skill contract."""

import argparse
import json
import re
from datetime import date, datetime, timezone
from pathlib import Path

CONTROL_START_DATE = "2026-02-01"


def parse_distance_km(value):
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().lower().replace("km", "").replace(" ", "").replace(",", ".")
    try:
        return float(text)
    except ValueError:
        return None


def parse_hms_to_seconds(value):
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return int(value)
    text = str(value).strip()
    parts = text.split(":")
    if len(parts) == 2:
        mins, secs = parts
        if mins.isdigit() and secs.isdigit():
            return int(mins) * 60 + int(secs)
        return None
    if len(parts) == 3:
        hrs, mins, secs = parts
        if hrs.isdigit() and mins.isdigit() and secs.isdigit():
            return int(hrs) * 3600 + int(mins) * 60 + int(secs)
        return None
    return None


def parse_pace_to_seconds_per_km(value):
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return int(value)
    text = str(value).strip().lower().replace("/km", "").strip()
    parts = text.split(":")
    if len(parts) != 2:
        return None
    mins, secs = parts
    if not mins.isdigit() or not secs.isdigit():
        return None
    return int(mins) * 60 + int(secs)


def parse_hr_bpm(value):
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return int(value)
    match = re.search(r"\d+", str(value))
    return int(match.group(0)) if match else None


def parse_calories(value):
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().replace(",", ".")
    try:
        return float(text)
    except ValueError:
        return None


def normalize_activity(activity, fallback_source_id):
    source_id = activity.get("sourceId") or activity.get("id") or fallback_source_id
    normalized = {
        "type": activity.get("type") or "Unknown",
        "distanceKm": parse_distance_km(activity.get("distanceKm", activity.get("distance"))),
        "durationSec": parse_hms_to_seconds(activity.get("durationSec", activity.get("time"))),
        "avgPaceSecPerKm": parse_pace_to_seconds_per_km(
            activity.get("avgPaceSecPerKm", activity.get("avg_pace"))
        ),
        "avgHrBpm": parse_hr_bpm(activity.get("avgHrBpm", activity.get("avg_hr"))),
        "calories": parse_calories(activity.get("calories")),
        "sourceId": str(source_id),
    }
    return normalized


def normalize_history(data):
    by_date_nutrition = {}
    for row in data.get("history", []):
        if isinstance(row, dict) and row.get("date") and row.get("nutrition") is not None:
            by_date_nutrition[row["date"]] = row["nutrition"]

    normalized_history = []
    for row in data.get("history", []):
        if not isinstance(row, dict):
            continue
        day = row.get("date")
        if not day or day < CONTROL_START_DATE:
            continue

        out = {"date": day}
        if "scheduled" in row:
            out["scheduled"] = row["scheduled"]

        activities = row.get("activities") or []
        if activities:
            normalized = []
            for idx, activity in enumerate(activities):
                if not isinstance(activity, dict):
                    continue
                fallback_source_id = f"garmin:{day}:{idx}"
                normalized.append(normalize_activity(activity, fallback_source_id))
            if normalized:
                out["activities"] = normalized

        nutrition = by_date_nutrition.get(day)
        if nutrition is not None:
            out["nutrition"] = nutrition

        normalized_history.append(out)

    normalized_history.sort(key=lambda entry: entry["date"])
    return normalized_history


def recompute_summary(history):
    activities_count = 0
    total_distance_km = 0.0
    total_duration_sec = 0
    total_calories = 0.0

    for day in history:
        for activity in day.get("activities", []):
            activities_count += 1
            if isinstance(activity.get("distanceKm"), (int, float)):
                total_distance_km += float(activity["distanceKm"])
            if isinstance(activity.get("durationSec"), (int, float)):
                total_duration_sec += int(activity["durationSec"])
            if isinstance(activity.get("calories"), (int, float)):
                total_calories += float(activity["calories"])

    return {
        "from": CONTROL_START_DATE,
        "to": date.today().isoformat(),
        "activitiesCount": activities_count,
        "totalDistanceKm": round(total_distance_km, 2),
        "totalDurationSec": total_duration_sec,
        "totalCalories": round(total_calories, 2),
    }


def reconcile(data):
    output = {
        "lastUpdate": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "planName": data.get("planName", "Garmin Training Plan"),
        "currentWeek": data.get("currentWeek", ""),
        "history": normalize_history(data),
        "upcoming": data.get("upcoming", []),
        "recurring_activities": data.get("recurring_activities", []),
    }
    output["summary"] = recompute_summary(output["history"])
    return output


def main():
    parser = argparse.ArgumentParser(description="Reconcile Garmin tracking JSON to canonical schema")
    parser.add_argument("--file", default="garmin_tracking.json", help="Path to tracking JSON file")
    parser.add_argument("--write", action="store_true", help="Write normalized data back to file")
    args = parser.parse_args()

    path = Path(args.file)
    if not path.exists() and args.file.startswith("persona/"):
        legacy_path = Path(args.file.removeprefix("persona/"))
        if legacy_path.exists():
            path = legacy_path
    if not path.exists():
        raise SystemExit(f"File not found: {path}")

    with path.open("r", encoding="utf-8") as handle:
        raw = json.load(handle)

    reconciled = reconcile(raw)

    if args.write:
        with path.open("w", encoding="utf-8") as handle:
            json.dump(reconciled, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        print(f"Reconciled and wrote: {path}")
    else:
        print(json.dumps(reconciled, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
