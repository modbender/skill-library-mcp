"""ClawEvents CLI.

Usage:
  python -m clawevents search --city tel-aviv --type jazz --days 7
  python -m clawevents search --city barcelona new-york --type concert --age adults --evening
  python -m clawevents search --city new-york --type cinema --free --limit 10
"""

from __future__ import annotations
import argparse
import json
import logging
import sys
from datetime import datetime, timedelta

from .engine import ClawEventsEngine
from .models import AgeGroup, City, EventType, TimeOfDay

logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(name)s: %(message)s")


_CITY_ALIASES = {
    "tel-aviv": City.TEL_AVIV, "telaviv": City.TEL_AVIV, "tlv": City.TEL_AVIV,
    "barcelona": City.BARCELONA, "bcn": City.BARCELONA,
    "new-york": City.NEW_YORK, "nyc": City.NEW_YORK, "newyork": City.NEW_YORK,
}

_TYPE_ALIASES = {
    "concert":   EventType.CONCERT,   "music":      EventType.CONCERT,
    "jazz":      EventType.JAZZ,
    "cinema":    EventType.CINEMA,    "movie":      EventType.CINEMA, "film": EventType.CINEMA,
    "theatre":   EventType.THEATRE,   "theater":    EventType.THEATRE,
    "nightlife": EventType.NIGHTLIFE,
    "family":    EventType.FAMILY,    "kids":       EventType.FAMILY,
    "comedy":    EventType.COMEDY,    "stand-up":   EventType.COMEDY,
    "art":       EventType.ART,       "exhibition": EventType.ART,
    "sport":     EventType.SPORT,
    "festival":  EventType.FESTIVAL,
    "community": EventType.COMMUNITY,
}

_AGE_ALIASES = {
    "kids": AgeGroup.KIDS, "children": AgeGroup.KIDS,
    "family": AgeGroup.FAMILY, "all": AgeGroup.FAMILY,
    "adults": AgeGroup.ADULTS, "adult": AgeGroup.ADULTS,
}

_TIME_ALIASES = {
    "morning": TimeOfDay.MORNING,
    "afternoon": TimeOfDay.AFTERNOON,
    "evening": TimeOfDay.EVENING,
    "late-night": TimeOfDay.LATE_NIGHT, "night": TimeOfDay.LATE_NIGHT,
}


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="clawevents", description="ClawEvents — multi-city event search")
    sub = p.add_subparsers(dest="cmd")

    s = sub.add_parser("search", help="Search for events")
    s.add_argument("--city", "-c",  nargs="+", required=True,
                   help="Cities: tel-aviv, barcelona, new-york (multiple allowed)")
    s.add_argument("--type", "-t",  nargs="+", dest="event_types",
                   help="Event types: jazz, concert, cinema, theatre, family, comedy, art, sport, festival")
    s.add_argument("--age", "-a",   nargs="+", dest="age_groups",
                   help="Age groups: kids, family, adults")
    s.add_argument("--time",        nargs="+", dest="time_of_day",
                   help="Time of day: morning, afternoon, evening, late-night")
    s.add_argument("--from",        dest="date_from",
                   help="Start date YYYY-MM-DD (default: today)")
    s.add_argument("--to",          dest="date_to",
                   help="End date YYYY-MM-DD (default: +7 days)")
    s.add_argument("--days",        type=int, default=7,
                   help="Days from now (overridden by --to if both given)")
    s.add_argument("--free",        action="store_true",
                   help="Free events only")
    s.add_argument("--limit", "-n", type=int, default=20,
                   help="Max results per search (default 20)")
    s.add_argument("--format",      choices=["text", "json"], default="text")
    s.add_argument("--verbose", "-v", action="store_true")
    return p


def run():
    parser = build_parser()
    args = parser.parse_args()

    if args.cmd != "search":
        parser.print_help()
        sys.exit(0)

    if args.verbose:
        logging.getLogger().setLevel(logging.INFO)

    # Parse cities
    cities = []
    for c in args.city:
        city = _CITY_ALIASES.get(c.lower())
        if not city:
            print(f"Unknown city: {c}. Use: tel-aviv, barcelona, new-york", file=sys.stderr)
            sys.exit(1)
        cities.append(city)

    # Parse types
    event_types = None
    if args.event_types:
        event_types = []
        for t in args.event_types:
            et = _TYPE_ALIASES.get(t.lower())
            if et:
                event_types.append(et)

    # Parse age groups
    age_groups = None
    if args.age_groups:
        age_groups = [_AGE_ALIASES[a.lower()] for a in args.age_groups if a.lower() in _AGE_ALIASES]

    # Parse time of day
    time_of_day = None
    if args.time_of_day:
        time_of_day = [_TIME_ALIASES[t.lower()] for t in args.time_of_day if t.lower() in _TIME_ALIASES]

    # Parse dates
    now   = datetime.now().replace(hour=0, minute=0, second=0)
    start = datetime.strptime(args.date_from, "%Y-%m-%d") if args.date_from else now
    if args.date_to:
        end = datetime.strptime(args.date_to, "%Y-%m-%d").replace(hour=23, minute=59)
    else:
        end = now + timedelta(days=args.days, hours=23, minutes=59)

    engine = ClawEventsEngine()
    events = engine.search(
        cities      = cities,
        start       = start,
        end         = end,
        event_types = event_types,
        age_groups  = age_groups,
        time_of_day = time_of_day,
        free_only   = args.free,
        limit       = args.limit,
    )

    if args.format == "json":
        print(json.dumps([e.to_dict() for e in events], ensure_ascii=False, indent=2))
        return

    # Text output
    if not events:
        print("No events found matching your criteria.")
        return

    print(f"\n🎉 Found {len(events)} events\n")
    for i, e in enumerate(events, 1):
        city_emoji = {"tel-aviv": "🇮🇱", "barcelona": "🇪🇸", "new-york": "🗽"}.get(e.city.value, "📍")
        types_str  = ", ".join(t.value for t in e.event_types)
        time_str   = e.start.strftime("%-d %b %H:%M") if e.start else "TBA"
        price_str  = f" · {e.price_display}" if e.price_display else ""
        print(f"{i}. {city_emoji} [{types_str}] {e.title}")
        print(f"   📅 {time_str} · 📍 {e.venue_name or e.address}{price_str}")
        if e.url:
            print(f"   🔗 {e.url}")
        print()


if __name__ == "__main__":
    run()
