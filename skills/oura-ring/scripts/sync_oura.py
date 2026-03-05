# /// script
# requires-python = ">=3.10"
# dependencies = ["oura-ring"]
# ///
"""Sync daily health data from Oura Ring into markdown files."""

import argparse
import os
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

from oura_ring import OuraClient


BASE_DIR = Path(__file__).resolve().parent.parent


def fmt_duration(seconds: float | int | None) -> str:
    """Format seconds into 'Xh Ym' string."""
    if seconds is None:
        return "—"
    total_minutes = int(seconds) // 60
    hours = total_minutes // 60
    minutes = total_minutes % 60
    return f"{hours}h {minutes:02d}m"


def fmt_duration_mmss(seconds: float | int | None) -> str:
    """Format seconds into 'MM:SS' string."""
    if seconds is None:
        return "—"
    total_seconds = int(seconds)
    minutes = total_seconds // 60
    secs = total_seconds % 60
    return f"{minutes}:{secs:02d}"


def find_day(items: list[dict], day_str: str) -> dict | None:
    """Find the entry matching a specific day from a list of API results."""
    for item in items:
        if item.get("day") == day_str:
            return item
    return None


def fetch_sleep(client: OuraClient, day_str: str) -> str | None:
    """Fetch and format sleep data from daily_sleep and sleep_periods."""
    # Get sleep score from daily_sleep
    daily = None
    try:
        data = client.get_daily_sleep(start_date=day_str, end_date=day_str)
        if data:
            daily = find_day(data, day_str)
    except Exception:
        pass

    # Get detailed sleep periods
    period = None
    try:
        periods = client.get_sleep_periods(start_date=day_str, end_date=day_str)
        if periods:
            # Use the "long_sleep" period if available, otherwise first
            for p in periods:
                if p.get("type") == "long_sleep":
                    period = p
                    break
            if not period:
                period = periods[0]
    except Exception:
        pass

    if not daily and not period:
        return None

    lines = []

    # Header: total sleep duration
    total_duration = period.get("total_sleep_duration") if period else None
    header = "## Sleep"
    if total_duration is not None:
        header += f": {fmt_duration(total_duration)}"
    lines.append(header)

    # Sleep stages
    if period:
        stages = []
        deep = period.get("deep_sleep_duration")
        if deep is not None:
            stages.append(f"Deep: {fmt_duration(deep)}")
        rem = period.get("rem_sleep_duration")
        if rem is not None:
            stages.append(f"REM: {fmt_duration(rem)}")
        light = period.get("light_sleep_duration")
        if light is not None:
            stages.append(f"Light: {fmt_duration(light)}")
        awake = period.get("awake_time")
        if awake is not None:
            stages.append(f"Awake: {fmt_duration(awake)}")
        if stages:
            lines.append(" | ".join(stages))

    # Sleep score
    score = daily.get("score") if daily else None
    if score is not None:
        lines.append(f"Sleep Score: {score}")

    # Bedtime and wake time
    if period:
        time_parts = []
        bedtime = period.get("bedtime_start")
        if bedtime:
            try:
                bt = datetime.fromisoformat(bedtime)
                time_parts.append(f"Bedtime: {bt.strftime('%H:%M')}")
            except (ValueError, TypeError):
                pass
        wake = period.get("bedtime_end")
        if wake:
            try:
                wt = datetime.fromisoformat(wake)
                time_parts.append(f"Wake: {wt.strftime('%H:%M')}")
            except (ValueError, TypeError):
                pass
        if time_parts:
            lines.append(" | ".join(time_parts))

    # Sleep contributors
    if daily:
        contributors = daily.get("contributors", {})
        if contributors:
            contrib_parts = []
            for key, label in [
                ("efficiency", "Efficiency"),
                ("restfulness", "Restfulness"),
                ("timing", "Timing"),
            ]:
                val = contributors.get(key)
                if val is not None:
                    contrib_parts.append(f"{label}: {val}")
            if contrib_parts:
                lines.append(" | ".join(contrib_parts))

    return "\n".join(lines) if len(lines) > 1 else None


def fetch_readiness(client: OuraClient, day_str: str) -> str | None:
    """Fetch and format readiness data."""
    try:
        data = client.get_daily_readiness(start_date=day_str, end_date=day_str)
    except Exception:
        return None

    if not data:
        return None

    entry = find_day(data, day_str)
    if not entry:
        return None

    score = entry.get("score")
    if score is None:
        return None

    lines = [f"## Readiness: {score}"]

    temp_dev = entry.get("temperature_deviation")
    if temp_dev is not None:
        sign = "+" if temp_dev >= 0 else ""
        lines.append(f"Temp Deviation: {sign}{temp_dev:.1f}\u00b0C")

    contributors = entry.get("contributors", {})
    if contributors:
        row1 = []
        for key, label in [
            ("hrv_balance", "HRV Balance"),
            ("resting_heart_rate", "Resting HR"),
            ("recovery_index", "Recovery Index"),
        ]:
            val = contributors.get(key)
            if val is not None:
                row1.append(f"{label}: {val}")
        if row1:
            lines.append(" | ".join(row1))

        row2 = []
        for key, label in [
            ("sleep_balance", "Sleep Balance"),
            ("activity_balance", "Activity Balance"),
        ]:
            val = contributors.get(key)
            if val is not None:
                row2.append(f"{label}: {val}")
        if row2:
            lines.append(" | ".join(row2))

    return "\n".join(lines) if len(lines) > 1 else lines[0]


def fetch_activity(client: OuraClient, day_str: str) -> str | None:
    """Fetch and format activity data."""
    try:
        data = client.get_daily_activity(start_date=day_str, end_date=day_str)
    except Exception:
        return None

    if not data:
        return None

    entry = find_day(data, day_str)
    if not entry:
        return None

    steps = entry.get("steps")
    total_cal = entry.get("total_calories")
    if steps is None and total_cal is None:
        return None

    header_parts = []
    if steps is not None:
        header_parts.append(f"{steps:,} steps")
    if total_cal is not None:
        header_parts.append(f"{int(total_cal):,} cal")

    header = "## Activity"
    if header_parts:
        header += ": " + " | ".join(header_parts)

    lines = [header]

    detail_parts = []
    distance = entry.get("equivalent_walking_distance")
    if distance is not None and distance > 0:
        detail_parts.append(f"Distance: {distance / 1000:.1f} km")

    # Sum active time (high + medium activity)
    high_time = entry.get("high_activity_time") or 0
    medium_time = entry.get("medium_activity_time") or 0
    active_time = high_time + medium_time
    if active_time > 0:
        detail_parts.append(f"Active: {active_time // 60} min")

    if detail_parts:
        lines.append(" | ".join(detail_parts))

    return "\n".join(lines)


def fetch_stress(client: OuraClient, day_str: str) -> str | None:
    """Fetch and format stress data."""
    try:
        data = client.get_daily_stress(start_date=day_str, end_date=day_str)
    except Exception:
        return None

    if not data:
        return None

    entry = find_day(data, day_str)
    if not entry:
        return None

    stress_high = entry.get("stress_high")
    recovery_high = entry.get("recovery_high")

    if stress_high is None and recovery_high is None:
        return None

    lines = ["## Stress"]
    parts = []
    if stress_high is not None:
        parts.append(f"High Stress: {stress_high // 60} min")
    if recovery_high is not None:
        parts.append(f"Recovery: {recovery_high // 60} min")
    if parts:
        lines.append(" | ".join(parts))

    return "\n".join(lines)


def fetch_heart_rate(client: OuraClient, day_str: str) -> str | None:
    """Fetch and format heart rate data."""
    try:
        start_dt = f"{day_str}T00:00:00"
        end_dt = f"{day_str}T23:59:59"
        data = client.get_heart_rate(start_datetime=start_dt, end_datetime=end_dt)
    except Exception:
        return None

    if not data:
        return None

    bpms = [entry.get("bpm") for entry in data if entry.get("bpm") is not None]
    if not bpms:
        return None

    # Find resting HR from "rest" or "sleep" sources
    rest_bpms = [
        entry.get("bpm")
        for entry in data
        if entry.get("bpm") is not None and entry.get("source") in ("rest", "sleep")
    ]

    parts = []
    if rest_bpms:
        # Approximate resting HR as the 5th percentile of rest/sleep readings
        rest_sorted = sorted(rest_bpms)
        idx = max(0, len(rest_sorted) * 5 // 100)
        resting = rest_sorted[idx]
        parts.append(f"Resting: {resting} bpm")

    parts.append(f"Min: {min(bpms)} bpm")
    parts.append(f"Max: {max(bpms)} bpm")

    return "## Heart Rate\n" + " | ".join(parts)


def fetch_spo2(client: OuraClient, day_str: str) -> str | None:
    """Fetch and format SpO2 data."""
    try:
        data = client.get_daily_spo2(start_date=day_str, end_date=day_str)
    except Exception:
        return None

    if not data:
        return None

    entry = find_day(data, day_str)
    if not entry:
        return None

    spo2_data = entry.get("spo2_percentage", {})
    avg = spo2_data.get("average") if spo2_data else None
    if avg is None:
        return None

    return f"## SpO2: {avg:.0f}%"


def fetch_workouts(client: OuraClient, day_str: str) -> str | None:
    """Fetch and format workout data."""
    try:
        data = client.get_workouts(start_date=day_str, end_date=day_str)
    except Exception:
        return None

    if not data:
        return None

    # Filter to the requested day
    workouts = [w for w in data if w.get("day") == day_str]
    if not workouts:
        return None

    lines = ["## Workouts"]
    for w in workouts:
        activity = w.get("activity", "workout").replace("_", " ").title()
        label = w.get("label")
        name = label if label else activity

        # Calculate duration from start/end datetimes
        duration_str = ""
        start = w.get("start_datetime")
        end = w.get("end_datetime")
        if start and end:
            try:
                start_dt = datetime.fromisoformat(start)
                end_dt = datetime.fromisoformat(end)
                dur_secs = (end_dt - start_dt).total_seconds()
                duration_str = fmt_duration_mmss(dur_secs)
            except (ValueError, TypeError):
                pass

        header_parts = [f"**{name}**"]
        if duration_str:
            header_parts[0] += f" — {duration_str}"

        distance = w.get("distance")
        if distance and distance > 0:
            header_parts.append(f"{distance / 1000:.1f} km")

        calories = w.get("calories")
        if calories and calories > 0:
            header_parts.append(f"{int(calories)} cal")

        lines.append("- " + ", ".join(header_parts))

    return "\n".join(lines)


def sync_day(client: OuraClient, day: date, output_dir: Path) -> None:
    """Sync a single day's data and write the markdown file."""
    day_str = day.isoformat()
    display_date = day.strftime("%B %-d, %Y")

    sections = [f"# Health — {display_date}"]

    sleep = fetch_sleep(client, day_str)
    if sleep:
        sections.append(sleep)

    readiness = fetch_readiness(client, day_str)
    if readiness:
        sections.append(readiness)

    activity = fetch_activity(client, day_str)
    if activity:
        sections.append(activity)

    stress = fetch_stress(client, day_str)
    if stress:
        sections.append(stress)

    hr = fetch_heart_rate(client, day_str)
    if hr:
        sections.append(hr)

    spo2 = fetch_spo2(client, day_str)
    if spo2:
        sections.append(spo2)

    workouts = fetch_workouts(client, day_str)
    if workouts:
        sections.append(workouts)

    if len(sections) == 1:
        print(f"  {day_str}: No data available, skipping.")
        return

    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{day_str}.md"
    output_file.write_text("\n\n".join(sections) + "\n")
    print(f"  {day_str}: Written to {output_file}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync Oura Ring health data to markdown.")
    parser.add_argument("--date", type=str, help="Specific date to sync (YYYY-MM-DD). Default: today.")
    parser.add_argument("--days", type=int, help="Sync the last N days.")
    parser.add_argument(
        "--output-dir",
        type=str,
        default="health",
        help="Output directory for markdown files (relative to skill base dir).",
    )
    args = parser.parse_args()

    # Always resolve output-dir relative to the skill's base directory, not CWD
    output_dir = Path(args.output_dir)
    if not output_dir.is_absolute():
        output_dir = BASE_DIR / output_dir

    # Determine which days to sync
    if args.days:
        today = date.today()
        days = [today - timedelta(days=i) for i in range(args.days)]
    elif args.date:
        try:
            days = [date.fromisoformat(args.date)]
        except ValueError:
            print(f"Error: Invalid date format '{args.date}'. Use YYYY-MM-DD.", file=sys.stderr)
            sys.exit(1)
    else:
        days = [date.today()]

    token = os.environ.get("OURA_TOKEN")
    if not token:
        print("Error: OURA_TOKEN env var is required.", file=sys.stderr)
        print("Get your token at https://cloud.ouraring.com/personal-access-tokens", file=sys.stderr)
        sys.exit(1)

    print(f"Syncing {len(days)} day(s)...")

    with OuraClient(token) as client:
        for day in sorted(days):
            sync_day(client, day, output_dir)

    print("Done.")


if __name__ == "__main__":
    main()
