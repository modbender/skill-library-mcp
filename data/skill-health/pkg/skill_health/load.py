"""
Load and normalize health data from a directory of CSVs or a ZIP archive.

Performs deduplication by source: multiple devices (Samsung Health, Google Fit, etc.)
may report the same event; we group by time window and keep a single value to avoid
double-counting.
"""

from __future__ import annotations

import logging
import zipfile
from datetime import datetime
from pathlib import Path

import pandas as pd

from skill_health.models import HealthDataBundle

logger = logging.getLogger(__name__)

HEALTH_DATA_PREFIX = "health_data_"


def _parse_datetime(date_str: str, time_str: str) -> datetime:
    """Parse 'YYYY-MM-DD' and 'HH:MM:SS' strings into a single datetime."""
    combined = f"{date_str} {time_str}"
    try:
        return datetime.strptime(combined, "%Y-%m-%d %H:%M:%S")
    except ValueError as e:
        raise ValueError(f"Invalid date/time: {combined}") from e


def _load_csv(path: Path) -> pd.DataFrame | None:
    """Read a CSV file from disk. Returns None if missing or empty."""
    if not path.exists():
        return None
    try:
        raw_df = pd.read_csv(path)
    except Exception as e:
        logger.warning("Could not read %s: %s", path, e)
        return None
    if raw_df.empty:
        return None
    return raw_df


def _load_csv_from_zip(
    zip_file: zipfile.ZipFile, member_name: str
) -> pd.DataFrame | None:
    """Read a CSV member from an open ZIP. Returns None if missing or empty."""
    if member_name not in zip_file.namelist():
        return None
    try:
        with zip_file.open(member_name) as f:
            raw_df = pd.read_csv(f)
    except Exception as e:
        logger.warning("Could not read %s from ZIP: %s", member_name, e)
        return None
    if raw_df.empty:
        return None
    return raw_df


def _normalize_and_dedupe_steps(raw_df: pd.DataFrame | None) -> pd.DataFrame:
    """
    Normalize steps CSV to timestamp + steps; deduplicate by (Date, Time) taking max steps.
    Same reading is often reported by both android and Google Fit.
    """
    if raw_df is None or raw_df.empty:
        return pd.DataFrame(columns=["timestamp", "steps"])

    required_columns = {"Date", "Time", "Steps"}
    missing = required_columns - set(raw_df.columns)
    if missing:
        raise ValueError(f"steps.csv missing columns: {missing}")

    steps_df = raw_df.copy()
    steps_df["timestamp"] = [
        _parse_datetime(str(date_val), str(time_val))
        for date_val, time_val in zip(steps_df["Date"], steps_df["Time"], strict=False)
    ]
    steps_df["steps"] = pd.to_numeric(steps_df["Steps"], errors="coerce")
    steps_df = steps_df.dropna(subset=["timestamp", "steps"])
    steps_df = steps_df[steps_df["steps"] >= 0]

    deduped = steps_df.groupby(["Date", "Time"], as_index=False)["steps"].max()
    deduped["timestamp"] = [
        _parse_datetime(str(date_val), str(time_val))
        for date_val, time_val in zip(deduped["Date"], deduped["Time"], strict=False)
    ]
    return (
        deduped[["timestamp", "steps"]].sort_values("timestamp").reset_index(drop=True)
    )


def _normalize_and_dedupe_heart_rate(raw_df: pd.DataFrame | None) -> pd.DataFrame:
    """
    Normalize heart_rate CSV to timestamp + bpm; deduplicate by (Date, Time) taking mean.
    Filters to physiologically plausible range 30–250 bpm.
    """
    if raw_df is None or raw_df.empty:
        return pd.DataFrame(columns=["timestamp", "bpm"])

    heart_rate_column = next(
        (c for c in raw_df.columns if "heart rate" in c.lower()), None
    )
    if not heart_rate_column or {"Date", "Time"} - set(raw_df.columns):
        raise ValueError("heart_rate.csv missing Date, Time or heart rate column")

    hr_df = raw_df.copy()
    hr_df["timestamp"] = [
        _parse_datetime(str(date_val), str(time_val))
        for date_val, time_val in zip(hr_df["Date"], hr_df["Time"], strict=False)
    ]
    hr_df["bpm"] = pd.to_numeric(hr_df[heart_rate_column], errors="coerce")
    hr_df = hr_df.dropna(subset=["timestamp", "bpm"])
    hr_df = hr_df[(hr_df["bpm"] >= 30) & (hr_df["bpm"] <= 250)]

    deduped = hr_df.groupby(["Date", "Time"], as_index=False)["bpm"].mean()
    deduped["timestamp"] = [
        _parse_datetime(str(date_val), str(time_val))
        for date_val, time_val in zip(deduped["Date"], deduped["Time"], strict=False)
    ]
    return deduped[["timestamp", "bpm"]].sort_values("timestamp").reset_index(drop=True)


def _normalize_and_dedupe_calories(raw_df: pd.DataFrame | None) -> pd.DataFrame:
    """
    Normalize calories CSV to start_time, end_time, active_kcal, total_kcal.
    Deduplicate by (Date, Start Time, End Time); fill missing Active with 0.
    """
    if raw_df is None or raw_df.empty:
        return pd.DataFrame(
            columns=[
                "start_time",
                "end_time",
                "active_kcal",
                "total_kcal",
                "active_kcal_measured",
            ]
        )

    required_columns = {"Date", "Start Time", "End Time", "Total Calories (kcal)"}
    missing = required_columns - set(raw_df.columns)
    if missing:
        raise ValueError(f"calories.csv missing columns: {missing}")

    cal_df = raw_df.copy()
    cal_df["start_time"] = [
        _parse_datetime(str(date_val), str(time_val))
        for date_val, time_val in zip(
            cal_df["Date"], cal_df["Start Time"], strict=False
        )
    ]
    cal_df["end_time"] = [
        _parse_datetime(str(date_val), str(time_val))
        for date_val, time_val in zip(cal_df["Date"], cal_df["End Time"], strict=False)
    ]
    cal_df["total_kcal"] = pd.to_numeric(
        cal_df["Total Calories (kcal)"], errors="coerce"
    )
    active_calories_column = "Active Calories (kcal)"
    if active_calories_column in cal_df.columns:
        cal_df["active_kcal"] = pd.to_numeric(
            cal_df[active_calories_column], errors="coerce"
        )
    else:
        cal_df["active_kcal"] = float("nan")
    cal_df = cal_df.dropna(subset=["start_time", "end_time", "total_kcal"])

    # Drop windows where end_time <= start_time (export bug: midnight parsed as same day)
    cal_df = cal_df[cal_df["end_time"] > cal_df["start_time"]]

    # Track whether active_kcal was actually measured in the source data
    cal_df["active_kcal_measured"] = cal_df["active_kcal"].notna()
    # Export often has empty Active; total remains valid
    cal_df["active_kcal"] = cal_df["active_kcal"].fillna(0.0)

    deduped = (
        cal_df.groupby(["Date", "Start Time", "End Time"], as_index=False)
        .agg(
            {
                "start_time": "first",
                "end_time": "first",
                "active_kcal": "max",
                "total_kcal": "max",
                "active_kcal_measured": "any",
            }
        )
        .reset_index(drop=True)
    )
    return (
        deduped[
            [
                "start_time",
                "end_time",
                "active_kcal",
                "total_kcal",
                "active_kcal_measured",
            ]
        ]
        .sort_values("start_time")
        .reset_index(drop=True)
    )


def _normalize_sleep(raw_df: pd.DataFrame | None) -> pd.DataFrame:
    """
    Normalize sleep_sessions CSV; deduplicate by (Date, Start Time, End Time).
    Keeps sessions between 0.5 and 16 hours.
    """
    if raw_df is None or raw_df.empty:
        return pd.DataFrame(columns=["start_time", "end_time", "duration_hours"])

    required_columns = {"Date", "Start Time", "End Time", "Duration (hours)"}
    missing = required_columns - set(raw_df.columns)
    if missing:
        raise ValueError(f"sleep_sessions.csv missing columns: {missing}")

    sleep_df = raw_df.copy()
    sleep_df["start_time"] = [
        _parse_datetime(str(date_val), str(time_val))
        for date_val, time_val in zip(
            sleep_df["Date"], sleep_df["Start Time"], strict=False
        )
    ]
    sleep_df["end_time"] = [
        _parse_datetime(str(date_val), str(time_val))
        for date_val, time_val in zip(
            sleep_df["Date"], sleep_df["End Time"], strict=False
        )
    ]
    sleep_df["duration_hours"] = pd.to_numeric(
        sleep_df["Duration (hours)"], errors="coerce"
    )
    sleep_df = sleep_df.dropna(subset=["start_time", "end_time", "duration_hours"])
    sleep_df = sleep_df[
        (sleep_df["duration_hours"] > 0.5) & (sleep_df["duration_hours"] < 16)
    ]

    deduped = (
        sleep_df.groupby(["Date", "Start Time", "End Time"], as_index=False)
        .first()
        .reset_index(drop=True)
    )
    return (
        deduped[["start_time", "end_time", "duration_hours"]]
        .sort_values("start_time")
        .reset_index(drop=True)
    )


def _normalize_exercise(raw_df: pd.DataFrame | None) -> pd.DataFrame:
    """
    Normalize exercise_sessions CSV to start_time, end_time, duration_hours, type, title.
    Returns empty DataFrame if required columns are missing.
    """
    if raw_df is None or raw_df.empty:
        return pd.DataFrame(
            columns=[
                "start_time",
                "end_time",
                "duration_hours",
                "type",
                "title",
                "source",
            ]
        )

    required_columns = {"Date", "Start Time", "End Time", "Duration (hours)"}
    if required_columns - set(raw_df.columns):
        logger.warning("exercise_sessions missing required columns, returning empty")
        return pd.DataFrame(
            columns=[
                "start_time",
                "end_time",
                "duration_hours",
                "type",
                "title",
                "source",
            ]
        )

    ex_df = raw_df.copy()
    ex_df["start_time"] = [
        _parse_datetime(str(date_val), str(time_val))
        for date_val, time_val in zip(ex_df["Date"], ex_df["Start Time"], strict=False)
    ]
    ex_df["end_time"] = [
        _parse_datetime(str(date_val), str(time_val))
        for date_val, time_val in zip(ex_df["Date"], ex_df["End Time"], strict=False)
    ]
    ex_df["duration_hours"] = pd.to_numeric(ex_df["Duration (hours)"], errors="coerce")
    ex_df["type"] = ex_df["Type"].astype(str) if "Type" in ex_df.columns else ""
    ex_df["title"] = ex_df["Title"].astype(str) if "Title" in ex_df.columns else ""
    # Preserve source so downstream analysis can distinguish treadmill (Kingsmith/Xiaojin)
    # from free-movement sessions (Samsung Health, etc.)
    ex_df["source"] = ex_df["Source"].astype(str) if "Source" in ex_df.columns else ""
    ex_df = ex_df.dropna(subset=["start_time", "end_time", "duration_hours"])
    ex_df = ex_df[(ex_df["duration_hours"] > 0.05) & (ex_df["duration_hours"] < 24)]

    return (
        ex_df[["start_time", "end_time", "duration_hours", "type", "title", "source"]]
        .sort_values("start_time")
        .reset_index(drop=True)
    )


def _normalize_oxygen_saturation(raw_df: pd.DataFrame | None) -> pd.DataFrame:
    """
    Normalize oxygen_saturation CSV to timestamp + spo2_pct.
    Returns empty DataFrame if Date/Time or SpO2 column is missing.
    """
    if raw_df is None or raw_df.empty:
        return pd.DataFrame(columns=["timestamp", "spo2_pct"])

    if "Date" not in raw_df.columns or "Time" not in raw_df.columns:
        return pd.DataFrame(columns=["timestamp", "spo2_pct"])
    spo2_column = next(
        (c for c in raw_df.columns if "spo2" in c.lower() or "oxygen" in c.lower()),
        None,
    )
    if not spo2_column:
        return pd.DataFrame(columns=["timestamp", "spo2_pct"])

    spo2_df = raw_df.copy()
    spo2_df["timestamp"] = [
        _parse_datetime(str(date_val), str(time_val))
        for date_val, time_val in zip(spo2_df["Date"], spo2_df["Time"], strict=False)
    ]
    spo2_df["spo2_pct"] = pd.to_numeric(spo2_df[spo2_column], errors="coerce")
    spo2_df = spo2_df.dropna(subset=["timestamp", "spo2_pct"])
    return (
        spo2_df[["timestamp", "spo2_pct"]]
        .sort_values("timestamp")
        .reset_index(drop=True)
    )


def load_health_data_from_path(data_path: Path) -> HealthDataBundle:
    """
    Load health data from a directory of CSVs or a single ZIP file.

    If `data_path` is a directory, reads steps.csv, heart_rate.csv, etc. inside it.
    If it is a .zip file, reads the same filenames from the archive.
    Applies normalization and source deduplication to avoid double-counting.

    Args:
        data_path: Path to a health_data_* directory or health_data_*.zip file.

    Returns:
        HealthDataBundle with normalized DataFrames per data type.

    Raises:
        FileNotFoundError: If the path does not exist or is not a directory/ZIP.
    """
    data_path = Path(data_path)
    if not data_path.exists():
        raise FileNotFoundError(f"Data path not found: {data_path}")

    if data_path.suffix.lower() == ".zip":
        with zipfile.ZipFile(data_path, "r") as zip_file:
            steps_df = _normalize_and_dedupe_steps(
                _load_csv_from_zip(zip_file, "steps.csv")
            )
            heart_rate_df = _normalize_and_dedupe_heart_rate(
                _load_csv_from_zip(zip_file, "heart_rate.csv")
            )
            calories_df = _normalize_and_dedupe_calories(
                _load_csv_from_zip(zip_file, "calories.csv")
            )
            sleep_sessions_df = _normalize_sleep(
                _load_csv_from_zip(zip_file, "sleep_sessions.csv")
            )
            exercise_sessions_df = _normalize_exercise(
                _load_csv_from_zip(zip_file, "exercise_sessions.csv")
            )
            oxygen_saturation_df = _normalize_oxygen_saturation(
                _load_csv_from_zip(zip_file, "oxygen_saturation.csv")
            )
            distance_raw = _load_csv_from_zip(zip_file, "distance.csv")
    else:
        if not data_path.is_dir():
            raise FileNotFoundError(f"Expected directory or ZIP: {data_path}")
        steps_df = _normalize_and_dedupe_steps(_load_csv(data_path / "steps.csv"))
        heart_rate_df = _normalize_and_dedupe_heart_rate(
            _load_csv(data_path / "heart_rate.csv")
        )
        calories_df = _normalize_and_dedupe_calories(
            _load_csv(data_path / "calories.csv")
        )
        sleep_sessions_df = _normalize_sleep(
            _load_csv(data_path / "sleep_sessions.csv")
        )
        exercise_sessions_df = _normalize_exercise(
            _load_csv(data_path / "exercise_sessions.csv")
        )
        oxygen_saturation_df = _normalize_oxygen_saturation(
            _load_csv(data_path / "oxygen_saturation.csv")
        )
        distance_raw = _load_csv(data_path / "distance.csv")

    if oxygen_saturation_df is None or oxygen_saturation_df.empty:
        oxygen_saturation_df = pd.DataFrame(columns=["timestamp", "spo2_pct"])
    if (
        distance_raw is not None
        and not distance_raw.empty
        and "Distance (km)" in distance_raw.columns
    ):
        distance_df = _normalize_distance(distance_raw)
    else:
        distance_df = pd.DataFrame(
            columns=["start_time", "end_time", "distance_m", "distance_km"]
        )

    return HealthDataBundle(
        steps=steps_df,
        heart_rate=heart_rate_df,
        calories=calories_df,
        sleep_sessions=sleep_sessions_df,
        exercise_sessions=exercise_sessions_df,
        oxygen_saturation=oxygen_saturation_df,
        distance=distance_df,
    )


def _normalize_distance(raw_df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize distance CSV to start_time, end_time, distance_m, distance_km, source.
    Returns empty DataFrame if required columns are missing.
    """
    required_columns = {"Date", "Start Time", "End Time"}
    if required_columns - set(raw_df.columns):
        return pd.DataFrame(
            columns=["start_time", "end_time", "distance_m", "distance_km", "source"]
        )
    dist_df = raw_df.copy()
    dist_df["start_time"] = [
        _parse_datetime(str(date_val), str(time_val))
        for date_val, time_val in zip(
            dist_df["Date"], dist_df["Start Time"], strict=False
        )
    ]
    dist_df["end_time"] = [
        _parse_datetime(str(date_val), str(time_val))
        for date_val, time_val in zip(
            dist_df["Date"], dist_df["End Time"], strict=False
        )
    ]
    distance_km_column = "Distance (km)" if "Distance (km)" in dist_df.columns else None
    distance_m_column = (
        "Distance (meters)" if "Distance (meters)" in dist_df.columns else None
    )
    if distance_km_column:
        dist_df["distance_km"] = pd.to_numeric(
            dist_df[distance_km_column], errors="coerce"
        )
    else:
        dist_df["distance_km"] = float("nan")
    if distance_m_column:
        dist_df["distance_m"] = pd.to_numeric(
            dist_df[distance_m_column], errors="coerce"
        )
    else:
        dist_df["distance_m"] = (
            dist_df["distance_km"] * 1000 if distance_km_column else float("nan")
        )
    dist_df["source"] = (
        dist_df["Source"].astype(str) if "Source" in dist_df.columns else ""
    )
    return (
        dist_df[["start_time", "end_time", "distance_m", "distance_km", "source"]]
        .dropna(subset=["start_time", "end_time"])
        .reset_index(drop=True)
    )


def load_health_data_from_directory(directory: Path) -> HealthDataBundle:
    """
    Load health data from the most recent health_data_* folder or ZIP in a directory.

    Scans for folders or ZIPs whose name starts with `health_data_` and loads
    the lexicographically latest (typically the most recent export by date/time).

    Args:
        directory: Parent directory containing health_data_* subdirs or ZIPs.

    Returns:
        HealthDataBundle with normalized data from the latest source.

    Raises:
        FileNotFoundError: If directory does not exist or no health_data_* found.
    """
    directory = Path(directory)
    if not directory.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")

    zip_paths = sorted(directory.glob(f"{HEALTH_DATA_PREFIX}*.zip"))
    data_dirs = [
        p
        for p in directory.iterdir()
        if p.is_dir() and p.name.startswith(HEALTH_DATA_PREFIX)
    ]
    data_dirs.sort(key=lambda p: p.name)

    if zip_paths and (not data_dirs or zip_paths[-1].name >= data_dirs[-1].name):
        return load_health_data_from_path(zip_paths[-1])
    if data_dirs:
        return load_health_data_from_path(data_dirs[-1])
    raise FileNotFoundError(
        f"No {HEALTH_DATA_PREFIX}* directory or ZIP found in {directory}"
    )
