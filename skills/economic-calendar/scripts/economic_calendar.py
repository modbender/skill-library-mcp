"""
US Economic Calendar Scraper – Investing.com
=============================================
Fetches economic calendar events from Investing.com.

Requirements:
    pip install requests beautifulsoup4 lxml

Usage:
    python us_economic_calendar.py                                        # today, US, high only
    python us_economic_calendar.py --date tomorrow                        # tomorrow
    python us_economic_calendar.py --date 2026-03-01                      # specific date
    python us_economic_calendar.py --days 7                               # next 7 days
    python us_economic_calendar.py --importance high medium               # multiple importance levels
    python us_economic_calendar.py --countries "united states" germany    # multiple countries
    python us_economic_calendar.py --timezone "GMT -5:00"                 # New York time
"""

import argparse
import json
import random
import sys
import time
from datetime import date, timedelta

import requests
from bs4 import BeautifulSoup

# ══════════════════════════════════════════════════════════════════════════════
# INTERNAL MAPPINGS
# ══════════════════════════════════════════════════════════════════════════════

COUNTRY_IDS = {
    "united states":  5,
    "germany":        17,
    "united kingdom": 4,
    "france":         22,
    "japan":          35,
    "china":          37,
    "canada":         6,
    "australia":      25,
    "switzerland":    12,
    "eurozone":       72,
}

IMPORTANCE_IDS = {"low": 1, "medium": 2, "high": 3}

TIMEZONE_IDS = {
    "GMT -5:00": 8,   # New York (EST)
    "GMT -4:00": 9,   # New York (EDT)
    "GMT":       19,
    "GMT +1:00": 55,  # Berlin/Vienna (CET)
    "GMT +2:00": 56,  # Berlin/Vienna (CEST)
}

# Language support for Investing.com
# Maps language codes to domain prefixes
LANGUAGE_DOMAINS = {
    "en": "www",
    "de": "de",
    "es": "es",
    "fr": "fr",
    "it": "it",
    "pt": "pt",
}

def get_calendar_url(lang: str = "en") -> str:
    """Get the calendar API URL for the specified language."""
    domain = LANGUAGE_DOMAINS.get(lang, "www")
    return f"https://{domain}.investing.com/economic-calendar/Service/getCalendarFilteredData"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_3) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:124.0) Gecko/20100101 Firefox/124.0",
]


# ══════════════════════════════════════════════════════════════════════════════
# ARGUMENTS
# ══════════════════════════════════════════════════════════════════════════════

VALID_COUNTRIES  = sorted(COUNTRY_IDS.keys())
VALID_TIMEZONES  = sorted(TIMEZONE_IDS.keys())

def parse_args():
    parser = argparse.ArgumentParser(
        description="Fetch economic calendar events from Investing.com",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--date",
        default="today",
        help=(
            "Date to fetch. Possible values:\n"
            "  today        – today (default)\n"
            "  tomorrow     – tomorrow\n"
            "  yesterday    – yesterday\n"
            "  YYYY-MM-DD   – specific date, e.g. 2026-03-01"
        ),
    )
    parser.add_argument(
        "--days",
        type=int,
        default=None,
        help=(
            "Fetch a range of days starting from today instead of a single date.\n"
            "Overrides --date. Example: --days 5"
        ),
    )
    parser.add_argument(
        "--importance",
        nargs="+",
        choices=["low", "medium", "high"],
        default=["high"],
        help=(
            "Importance levels (space-separated). Default: high\n"
            "Example: --importance high medium"
        ),
    )
    parser.add_argument(
        "--countries",
        nargs="+",
        default=["united states"],
        metavar="COUNTRY",
        help=(
            "Countries to include (space-separated, use quotes for multi-word names).\n"
            f"Available: {', '.join(VALID_COUNTRIES)}\n"
            'Default: "united states"\n'
            'Example: --countries "united states" germany japan'
        ),
    )
    parser.add_argument(
        "--timezone",
        default="GMT +1:00",
        choices=VALID_TIMEZONES,
        metavar="TIMEZONE",
        help=(
            "Timezone for event times.\n"
            f"Available: {', '.join(VALID_TIMEZONES)}\n"
            'Default: "GMT +1:00" (Berlin/Vienna CET)\n'
            'Example: --timezone "GMT -5:00"'
        ),
    )
    parser.add_argument(
        "--json",
        choices=["file", "stdout", "none"],
        default="file",
        help=(
            "JSON output mode. Default: file\n"
            "  file    – save to calendar_YYYYMMDD.json\n"
            "  stdout  – print JSON to stdout (status messages go to stderr)\n"
            "  none    – no JSON output"
        ),
    )
    parser.add_argument(
        "--language",
        default="en",
        choices=["en", "de", "es", "fr", "it", "pt"],
        metavar="LANG",
        help=(
            "Language for event names and output.\n"
            "Available: en, de, es, fr, it, pt\n"
            'Default: "en"'
        ),
    )
    return parser.parse_args()


def resolve_date(date_str: str) -> date:
    today = date.today()
    if date_str == "today":
        return today
    elif date_str == "tomorrow":
        return today + timedelta(days=1)
    elif date_str == "yesterday":
        return today - timedelta(days=1)
    else:
        try:
            return date.fromisoformat(date_str)
        except ValueError:
            raise ValueError(f"Invalid date '{date_str}'. Use YYYY-MM-DD or today/tomorrow/yesterday.")


def validate_countries(countries: list) -> list:
    """Check all requested countries are supported and return normalised names."""
    validated = []
    for c in countries:
        c_lower = c.lower()
        if c_lower not in COUNTRY_IDS:
            raise ValueError(
                f"Unknown country '{c}'.\n"
                f"Available: {', '.join(VALID_COUNTRIES)}"
            )
        validated.append(c_lower)
    return validated


# ══════════════════════════════════════════════════════════════════════════════
# REQUEST
# ══════════════════════════════════════════════════════════════════════════════

def build_payload(from_date: date, to_date: date, importances: list,
                  countries: list, timezone: str) -> list:
    tz_id = TIMEZONE_IDS.get(timezone, 55)
    payload = [
        ("timeZone",      str(tz_id)),
        ("timeFilter",    "timeOnly"),
        ("currentTab",    "custom"),
        ("submitFilters", "1"),
        ("limit_from",    "0"),
        ("dateFrom",      from_date.strftime("%Y-%m-%d")),
        ("dateTo",        to_date.strftime("%Y-%m-%d")),
    ]
    for country in countries:
        cid = COUNTRY_IDS.get(country)
        if cid:
            payload.append(("country[]", str(cid)))
    for imp in importances:
        iid = IMPORTANCE_IDS.get(imp.lower())
        if iid:
            payload.append(("importance[]", str(iid)))
    return payload


def fetch_calendar(from_date: date, to_date: date, importances: list,
                   countries: list, timezone: str, language: str = "en") -> str:
    ua = random.choice(USER_AGENTS)
    session = requests.Session()

    # Get the domain for the specified language
    domain = LANGUAGE_DOMAINS.get(language, "www")
    base_url = f"https://{domain}.investing.com"
    calendar_url = f"{base_url}/economic-calendar/"
    api_url = f"{base_url}/economic-calendar/Service/getCalendarFilteredData"

    # Load the main page first to initialise cookies and session
    session.get(
        calendar_url,
        headers={"User-Agent": ua},
        timeout=15,
    )
    time.sleep(1)

    # NOTE: Do NOT set Accept-Encoding manually.
    # requests sets it automatically and handles decompression itself.
    # Setting it manually returns raw compressed bytes that cannot be parsed as JSON.
    headers = {
        "User-Agent":       ua,
        "X-Requested-With": "XMLHttpRequest",
        "Accept":           "application/json, text/javascript, */*; q=0.01",
        "Referer":          calendar_url,
        "Content-Type":     "application/x-www-form-urlencoded",
    }

    payload = build_payload(from_date, to_date, importances, countries, timezone)
    resp = session.post(api_url, headers=headers, data=payload, timeout=15)
    resp.raise_for_status()

    data = resp.json()
    if not data.get("data"):
        raise ValueError(f"Empty response from server: {str(data)[:300]}")
    return data["data"]


# ══════════════════════════════════════════════════════════════════════════════
# PARSING
# ══════════════════════════════════════════════════════════════════════════════

IMPORTANCE_LABEL = {1: "low", 2: "medium", 3: "high"}


def parse_events(html: str) -> list:
    from datetime import datetime as dt
    soup = BeautifulSoup(html, "lxml")
    events = []
    current_time = ""
    current_date = ""

    for row in soup.select("tr"):
        # Detect date separator rows (id starts with "theDay")
        row_id = row.get("id", "")
        if row_id.startswith("theDay"):
            date_cell = row.select_one("td")
            if date_cell:
                current_date = date_cell.get_text(strip=True)
            continue

        if "js-event-item" not in row.get("class", []):
            continue

        # Fallback: parse date from data-event-datetime attribute (format: YYYY/MM/DD HH:MM:SS)
        if not current_date:
            raw_dt = row.get("data-event-datetime", "")
            if raw_dt:
                try:
                    current_date = dt.strptime(raw_dt, "%Y/%m/%d %H:%M:%S").strftime("%A, %B %d, %Y")
                except ValueError:
                    pass

        # Also update current_date when it changes between rows using data-event-datetime
        raw_dt = row.get("data-event-datetime", "")
        if raw_dt:
            try:
                row_date = dt.strptime(raw_dt, "%Y/%m/%d %H:%M:%S").strftime("%A, %B %d, %Y")
                if row_date != current_date:
                    current_date = row_date
            except ValueError:
                pass

        # Update current time if the cell is not empty
        time_cell = row.select_one("td.time")
        if time_cell and time_cell.get_text(strip=True):
            current_time = time_cell.get_text(strip=True)

        # Count filled bull icons to determine importance level (1–3)
        importance = len(row.select("i.grayFullBullishIcon"))

        name_cell = row.select_one("td.event a") or row.select_one("td.event")
        name = name_cell.get_text(strip=True) if name_cell else "-"

        curr_cell = row.select_one("td.flagCur")
        currency  = curr_cell.get_text(strip=True) if curr_cell else ""

        def cell_text(selector):
            el = row.select_one(selector)
            return el.get_text(strip=True) if el else ""

        events.append({
            "date":       current_date,
            "time":       current_time,
            "currency":   currency,
            "importance": importance,
            "event":      name,
            "actual":     cell_text("td.act"),
            "forecast":   cell_text("td.fore"),
            "previous":   cell_text("td.prev"),
        })

    return events


# ══════════════════════════════════════════════════════════════════════════════
# OUTPUT
# ══════════════════════════════════════════════════════════════════════════════

def print_table(events: list, from_date: date, to_date: date,
                importances: list, countries: list, timezone: str):
    W = 80
    date_label = (
        from_date.strftime("%d.%m.%Y")
        if from_date == to_date
        else f"{from_date.strftime('%d.%m.%Y')} - {to_date.strftime('%d.%m.%Y')}"
    )
    country_label = ", ".join(c.title() for c in countries)
    print(f"\n{'='*W}")
    print(f"  Economic Calendar  |  {date_label}")
    print(f"  Countries: {country_label}  |  Timezone: {timezone}  |  Importance: {', '.join(importances)}")
    print(f"{'='*W}")

    if not events:
        print("  No events found for the selected filters.")
        print(f"{'='*W}\n")
        return

    print(f"  {'Time':<7} {'Imp.':<8} {'Curr.':<6} {'Event':<30} {'Forecast':>9} {'Previous':>9} {'Actual':>8}")
    print(f"  {'-'*7} {'-'*8} {'-'*6} {'-'*30} {'-'*9} {'-'*9} {'-'*8}")

    current_date = None
    for e in events:
        # Print date separator when fetching multiple days
        if from_date != to_date and e["date"] != current_date:
            current_date = e["date"]
            print(f"\n  ┌─ {current_date} ─────────────────────────────────────────────────────┐")

        label = IMPORTANCE_LABEL.get(e["importance"], str(e["importance"]))
        print(
            f"  {e['time']:<7} {label:<8} {e['currency']:<6} {e['event'][:30]:<30} "
            f"{e['forecast']:>9} {e['previous']:>9} {e['actual']:>8}"
        )

    print(f"\n{'='*W}")
    print(f"  {len(events)} event(s) found.\n")


def build_json_output(events: list, from_date: date, to_date: date,
                      importances: list, countries: list, timezone: str) -> dict:
    """Build the JSON-serialisable output dictionary."""
    return {
        "from":        from_date.isoformat(),
        "to":          to_date.isoformat(),
        "timezone":    timezone,
        "importances": importances,
        "countries":   countries,
        "events":      events,
    }


def save_json(events: list, from_date: date, to_date: date,
              importances: list, countries: list, timezone: str):
    """Write JSON output to a file."""
    suffix = (
        from_date.strftime("%Y%m%d")
        if from_date == to_date
        else f"{from_date.strftime('%Y%m%d')}-{to_date.strftime('%Y%m%d')}"
    )
    filename = f"calendar_{suffix}.json"
    output = build_json_output(events, from_date, to_date, importances, countries, timezone)
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"  JSON saved: {filename}", file=sys.stderr)


def print_json_stdout(events: list, from_date: date, to_date: date,
                      importances: list, countries: list, timezone: str):
    """Write JSON output to stdout (clean, pipe-friendly)."""
    output = build_json_output(events, from_date, to_date, importances, countries, timezone)
    print(json.dumps(output, ensure_ascii=False, indent=2))


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    args = parse_args()

    # Resolve date range
    if args.days:
        from_date = date.today()
        to_date   = date.today() + timedelta(days=args.days - 1)
    else:
        from_date = resolve_date(args.date)
        to_date   = from_date

    importances = args.importance
    timezone    = args.timezone
    language    = args.language
    json_mode = args.json

    try:
        countries = validate_countries(args.countries)
    except ValueError as e:
        print(f"Error: {e}")
        exit(1)

    status_file = sys.stderr if json_mode == "stdout" else sys.stdout
    print(
        f"Fetching calendar ({from_date} to {to_date}) | "
        f"Countries: {', '.join(countries)} | "
        f"Timezone: {timezone} | "
        f"Language: {language} | "
        f"Importance: {', '.join(importances)} ...",
        file=status_file,
    )
    try:
        html   = fetch_calendar(from_date, to_date, importances, countries, timezone, language)
        events = parse_events(html)
        
        # Convert US times to Berlin time if fetching US events
        is_us = any('united states' in c.lower() for c in countries)
        if is_us and timezone in ['GMT +1:00', 'GMT +2:00']:
            # User wants Berlin time for US events - convert from EST (+6 hours)
            import re
            for e in events:
                if e.get('time') and e['time'] != '-':
                    time_match = re.match(r'(\d{1,2}):(\d{2})', e['time'])
                    if time_match:
                        h = int(time_match.group(1)) + 6
                        if h >= 24:
                            h -= 24
                        e['time'] = f"{h:02d}:{time_match.group(2)}"
        
        # In stdout mode suppress the table so stdout contains only JSON
        if json_mode != "stdout":
            print_table(events, from_date, to_date, importances, countries, timezone)

        if json_mode == "file":
            save_json(events, from_date, to_date, importances, countries, timezone)
        elif json_mode == "stdout":
            print_json_stdout(events, from_date, to_date, importances, countries, timezone)

    except requests.exceptions.HTTPError as e:
        print(f"HTTP error {e.response.status_code}: {e}", file=sys.stderr)
    except requests.exceptions.ConnectionError:
        print("Connection error - could not reach investing.com.", file=sys.stderr)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
    except Exception as e:
        print(f"Unexpected error: {type(e).__name__}: {e}", file=sys.stderr)