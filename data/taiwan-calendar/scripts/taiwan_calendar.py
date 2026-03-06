#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "requests",
#   "python-dateutil",
# ]
# ///

"""
Taiwan Calendar - Query Taiwan government calendar for working days and holidays.

This script queries Taiwan's government open data platform to provide accurate
working day/holiday information, solving Claude's knowledge cutoff issues.
"""

import argparse
import json
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any
from zoneinfo import ZoneInfo

import requests
from dateutil import parser as dateparser

# Constants
TAIWAN_TZ = ZoneInfo("Asia/Taipei")
CACHE_FILE = Path(tempfile.gettempdir()) / "taiwan-calendar-cache.json"
CACHE_EXPIRY_HOURS = 1

# API Sources
API_SOURCES = [
    {
        "name": "data.gov.tw - Taiwan Calendar (GitHub CDN)",
        "url": "https://cdn.jsdelivr.net/gh/ruyut/TaiwanCalendar/data/{year}.json",
        "field_mapping": {
            "date": "date",
            "is_holiday": "isHoliday",
            "name": "description",
        },
    },
    {
        "name": "New Taipei City Open Data",
        "url": "https://data.ntpc.gov.tw/api/datasets/308DCD75-6434-45BC-A95F-584DA4FED251/json",
        "field_mapping": {
            "date": "date",
            "is_holiday": "isHoliday",
            "name": "holidayCategory",
        },
    },
]


def get_taiwan_now() -> datetime:
    """Get current datetime in Taiwan timezone (UTC+8)."""
    return datetime.now(TAIWAN_TZ)


def load_cache() -> Optional[Dict[str, Any]]:
    """Load calendar data from cache if valid (not expired)."""
    if not CACHE_FILE.exists():
        return None

    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            cache = json.load(f)

        cached_time = datetime.fromisoformat(cache["cached_at"])
        now = datetime.now()
        age_hours = (now - cached_time).total_seconds() / 3600

        if age_hours < CACHE_EXPIRY_HOURS:
            return cache
        else:
            return None  # Expired
    except (json.JSONDecodeError, KeyError, ValueError):
        return None


def save_cache(data: Dict[str, Any]) -> None:
    """Save calendar data to cache."""
    cache = {"cached_at": datetime.now().isoformat(), "data": data}

    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
    except IOError as e:
        print(f"Warning: Failed to save cache: {e}", file=sys.stderr)  # Non-fatal error


def fetch_calendar_data(year: Optional[int] = None) -> Dict[str, Any]:
    """
    Fetch calendar data from government API.

    Returns:
        Dict with date strings as keys and holiday info as values.
        Format: {"2025-01-01": {"is_holiday": True, "name": "元旦"}}
    """
    if year is None:
        year = get_taiwan_now().year

    # Try each API source in order
    last_error = None
    for source in API_SOURCES:
        try:
            url = source["url"]

            # Replace {year} placeholder if present
            if "{year}" in url:
                url = url.format(year=year)
            elif "?" in url:
                url += f"&year={year}"
            else:
                url += f"?year={year}"

            # Some government APIs have SSL certificate issues
            # Use verify=False for fallback sources
            verify_ssl = "jsdelivr" in url or "github" in url
            response = requests.get(url, timeout=10, verify=verify_ssl)
            response.raise_for_status()

            data = response.json()
            mapping = source["field_mapping"]

            # Parse response based on source format
            calendar = {}
            records = []

            # Handle different response structures
            if isinstance(data, dict):
                if "result" in data and "records" in data["result"]:
                    records = data["result"]["records"]
                elif "records" in data:
                    records = data["records"]
                elif isinstance(data.get("data"), list):
                    records = data["data"]
            elif isinstance(data, list):
                records = data

            for record in records:
                date_str = record.get(mapping["date"], "")
                is_holiday_val = record.get(mapping["is_holiday"], "")
                name = record.get(mapping["name"], "")

                # Normalize date format to YYYY-MM-DD
                try:
                    if len(date_str) == 8:  # YYYYMMDD
                        date_str = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
                    elif "/" in date_str:  # YYYY/MM/DD
                        date_str = date_str.replace("/", "-")
                except (ValueError, IndexError):
                    continue

                # Determine if holiday
                is_holiday = False
                if isinstance(is_holiday_val, bool):
                    is_holiday = is_holiday_val
                elif isinstance(is_holiday_val, str):
                    is_holiday = is_holiday_val in ["是", "放假", "2", "true", "True"]
                elif isinstance(is_holiday_val, int):
                    is_holiday = is_holiday_val == 2

                calendar[date_str] = {"is_holiday": is_holiday, "name": name or ""}

            if calendar:  # Successfully parsed data
                return calendar

        except requests.RequestException as e:
            last_error = e
            continue  # Try next source

    # All sources failed
    raise Exception(
        f"Failed to fetch calendar data from all sources. Last error: {last_error}"
    )


def get_calendar_data(
    use_cache: bool = True, year: Optional[int] = None
) -> Dict[str, Any]:
    """
    Get calendar data, using cache if available and valid.

    Args:
        use_cache: Whether to use cached data if available
        year: Specific year to fetch (defaults to current year)

    Returns:
        Calendar data dictionary (may contain multiple years)
    """
    if year is None:
        year = get_taiwan_now().year

    data = {}

    if use_cache:
        cached = load_cache()
        if cached:
            data = cached["data"]

    # Check if the requested year is in cache
    year_key = f"{year}-01-01"
    if year_key not in data:
        # Fetch this year's data and merge into cache
        year_data = fetch_calendar_data(year)
        data.update(year_data)
        save_cache(data)

    return data


def parse_date_input(date_str: str) -> datetime:
    """
    Parse flexible date input formats.

    Supports: YYYY-MM-DD, YYYY/MM/DD, MM/DD (assumes current year)
    """
    # Try to parse with dateutil
    try:
        dt = dateparser.parse(date_str, dayfirst=False)
        if dt is None:
            raise ValueError(f"Unable to parse date: {date_str}")

        # If only month/day provided, assume current year
        if "/" in date_str and date_str.count("/") == 1:
            dt = dt.replace(year=get_taiwan_now().year)

        return dt.replace(tzinfo=TAIWAN_TZ)
    except (ValueError, TypeError):
        raise ValueError(f"Invalid date format: {date_str}. Use YYYY-MM-DD or MM/DD")


def is_weekend(dt: datetime) -> bool:
    """Check if date is Saturday (5) or Sunday (6)."""
    return dt.weekday() >= 5


def is_working_day(dt: datetime, calendar_data: Dict[str, Any]) -> tuple[bool, str]:
    """
    Check if a date is a working day.

    Returns:
        (is_working, reason) tuple
    """
    date_str = dt.strftime("%Y-%m-%d")

    # Check calendar data
    if date_str in calendar_data:
        info = calendar_data[date_str]
        if info["is_holiday"]:
            # Explicitly marked as holiday
            reason = info["name"] or "Holiday"
            return False, reason
        elif info["name"]:
            # Has a name but not marked as holiday - likely a make-up workday
            return True, info["name"]

    # Check if weekend
    if is_weekend(dt):
        return False, "Weekend"

    # Regular working day
    return True, "Working day"


def get_weekday_name_zh(dt: datetime) -> str:
    """Get Chinese weekday name."""
    weekdays = ["一", "二", "三", "四", "五", "六", "日"]
    return f"週{weekdays[dt.weekday()]}"


def format_date_output(dt: datetime, is_working: bool, reason: str) -> str:
    """Format date information for output."""
    date_str = dt.strftime("%Y-%m-%d")
    weekday = get_weekday_name_zh(dt)
    status = "工作日" if is_working else "非工作日"

    if reason in ["Working day", "Weekend"]:
        return f"{date_str} ({weekday}) 是{status}。"
    else:
        return f"{date_str} ({weekday}) 是{status} - {reason}。"


# CLI Commands


def cmd_today(args):
    """Show today's date and working day status."""
    try:
        calendar_data = get_calendar_data()
        now = get_taiwan_now()
        is_working, reason = is_working_day(now, calendar_data)
        print(format_date_output(now, is_working, reason))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_check(args):
    """Check if a specific date is a working day."""
    try:
        dt = parse_date_input(args.date)
        # Fetch data for the year of the date being checked
        calendar_data = get_calendar_data(year=dt.year)
        is_working, reason = is_working_day(dt, calendar_data)
        print(format_date_output(dt, is_working, reason))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_range(args):
    """Count working days in a date range."""
    try:
        start = parse_date_input(args.start)
        end = parse_date_input(args.end)

        if start > end:
            print("Error: Start date must be before end date", file=sys.stderr)
            sys.exit(1)

        # Fetch data for starting year
        calendar_data = get_calendar_data(year=start.year)

        # If range spans multiple years, fetch all needed years
        if end.year != start.year:
            for year in range(start.year + 1, end.year + 1):
                year_data = fetch_calendar_data(year)
                calendar_data.update(year_data)

        working_days = 0
        holidays = []
        current = start

        while current <= end:
            is_working, reason = is_working_day(current, calendar_data)
            if is_working:
                working_days += 1
            else:
                # Only list national holidays (not weekends) in the holidays section
                if not is_weekend(current) and reason not in ["Weekend"]:
                    holidays.append(
                        f"{current.strftime('%Y-%m-%d')} ({get_weekday_name_zh(current)}) - {reason}"
                    )
            current += timedelta(days=1)

        print(
            f"{start.strftime('%Y-%m-%d')} 到 {end.strftime('%Y-%m-%d')} 共有 {working_days} 個工作日。"
        )
        if holidays:
            print("\n期間假日：")
            for h in holidays:
                print(f"  - {h}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_add_days(args):
    """Calculate the date N working days from a given date."""
    try:
        # Parse start date (default to today if not provided)
        if args.date:
            start = parse_date_input(args.date)
        else:
            start = get_taiwan_now()

        n = args.n
        if n < 0:
            print("Error: Number of working days must be positive", file=sys.stderr)
            sys.exit(1)

        # Fetch data for starting year (might need to fetch more if crosses year boundary)
        calendar_data = get_calendar_data(year=start.year)

        current = start
        days_counted = 0

        while days_counted < n:
            current += timedelta(days=1)

            # If we cross into a new year, fetch that year's data
            if (
                current.year not in [start.year]
                and current.strftime("%Y-01-01") not in calendar_data
            ):
                new_year_data = fetch_calendar_data(current.year)
                calendar_data.update(new_year_data)

            is_working, _ = is_working_day(current, calendar_data)
            if is_working:
                days_counted += 1

        print(
            f"從 {start.strftime('%Y-%m-%d')} 算起 {n} 個工作日後是 {current.strftime('%Y-%m-%d')} ({get_weekday_name_zh(current)})。"
        )
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_next_working(args):
    """Find the next working day from a given date."""
    try:
        # Parse start date (default to today)
        if args.date:
            start = parse_date_input(args.date)
        else:
            start = get_taiwan_now()

        calendar_data = get_calendar_data(year=start.year)

        current = start + timedelta(days=1)
        while True:
            # If we cross into a new year, fetch that year's data
            if (
                current.year != start.year
                and current.strftime("%Y-01-01") not in calendar_data
            ):
                new_year_data = fetch_calendar_data(current.year)
                calendar_data.update(new_year_data)

            is_working, _ = is_working_day(current, calendar_data)
            if is_working:
                print(
                    f"下一個工作日是 {current.strftime('%Y-%m-%d')} ({get_weekday_name_zh(current)})。"
                )
                return
            current += timedelta(days=1)

            # Safety limit
            if (current - start).days > 30:
                print("Error: No working day found within 30 days", file=sys.stderr)
                sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_next_holiday(args):
    """Find the next holiday from a given date."""
    try:
        # Parse start date (default to today)
        if args.date:
            start = parse_date_input(args.date)
        else:
            start = get_taiwan_now()

        calendar_data = get_calendar_data(year=start.year)

        current = start + timedelta(days=1)
        while True:
            # If we cross into a new year, fetch that year's data
            if (
                current.year != start.year
                and current.strftime("%Y-01-01") not in calendar_data
            ):
                new_year_data = fetch_calendar_data(current.year)
                calendar_data.update(new_year_data)

            is_working, reason = is_working_day(current, calendar_data)
            # Find national holidays only (not weekends or "Holiday" without name)
            if (
                not is_working
                and reason not in ["Weekend", "Holiday"]
                and not is_weekend(current)
            ):
                print(
                    f"下一個假日是 {current.strftime('%Y-%m-%d')} ({get_weekday_name_zh(current)}) - {reason}。"
                )
                return
            current += timedelta(days=1)

            # Safety limit
            if (current - start).days > 365:
                print("Error: No holiday found within 365 days", file=sys.stderr)
                sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Taiwan Calendar - Query working days and holidays"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # today command
    parser_today = subparsers.add_parser("today", help="Show today's date and status")
    parser_today.set_defaults(func=cmd_today)

    # check command
    parser_check = subparsers.add_parser(
        "check", help="Check if a specific date is a working day"
    )
    parser_check.add_argument("date", help="Date to check (YYYY-MM-DD or MM/DD)")
    parser_check.set_defaults(func=cmd_check)

    # range command
    parser_range = subparsers.add_parser(
        "range", help="Count working days in a date range"
    )
    parser_range.add_argument("start", help="Start date (YYYY-MM-DD)")
    parser_range.add_argument("end", help="End date (YYYY-MM-DD)")
    parser_range.set_defaults(func=cmd_range)

    # add-days command
    parser_add = subparsers.add_parser(
        "add-days", help="Calculate date N working days later"
    )
    parser_add.add_argument(
        "date", nargs="?", help="Start date (default: today, YYYY-MM-DD or MM/DD)"
    )
    parser_add.add_argument("n", type=int, help="Number of working days")
    parser_add.set_defaults(func=cmd_add_days)

    # next-working command
    parser_next_working = subparsers.add_parser(
        "next-working", help="Find next working day"
    )
    parser_next_working.add_argument(
        "date", nargs="?", help="Start date (default: today, YYYY-MM-DD or MM/DD)"
    )
    parser_next_working.set_defaults(func=cmd_next_working)

    # next-holiday command
    parser_next_holiday = subparsers.add_parser(
        "next-holiday", help="Find next holiday"
    )
    parser_next_holiday.add_argument(
        "date", nargs="?", help="Start date (default: today, YYYY-MM-DD or MM/DD)"
    )
    parser_next_holiday.set_defaults(func=cmd_next_holiday)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
