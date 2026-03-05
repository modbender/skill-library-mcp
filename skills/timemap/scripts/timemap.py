#!/usr/bin/env python3
"""Timemap.co.il - Historical Tel Aviv/Haifa entertainment & culture venue database."""

import argparse
import json
import math
import os
import random
import sys
import tempfile
import time
import urllib.request
import urllib.error
from collections import defaultdict

API_URL = "https://timemap.co.il/api/venue"
SITE_URL = "https://timemap.co.il"
CACHE_TTL = 86400  # 24 hours
CACHE_FILE = os.path.join(tempfile.gettempdir(), "timemap-venues-cache.json")

_use_color = False

# --- Color support ---


def _init_color(no_color_flag):
    global _use_color
    if no_color_flag or os.environ.get("NO_COLOR"):
        _use_color = False
    elif not sys.stdout.isatty():
        _use_color = False
    else:
        _use_color = True


def c(text, code):
    if not _use_color:
        return text
    return f"\033[{code}m{text}\033[0m"


def green(text):
    return c(text, "32")


def red(text):
    return c(text, "31")


def yellow(text):
    return c(text, "33")


def blue(text):
    return c(text, "34")


def magenta(text):
    return c(text, "35")


def cyan(text):
    return c(text, "36")


def bold(text):
    return c(text, "1")


def dim(text):
    return c(text, "2")


# --- Cache ---

_force_fresh = False


def _read_cache():
    """Return cached venues array or None if stale/missing."""
    if _force_fresh:
        return None
    try:
        if not os.path.exists(CACHE_FILE):
            return None
        age = time.time() - os.path.getmtime(CACHE_FILE)
        if age > CACHE_TTL:
            return None
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Handle both list (old cache) and dict (new cache with {"result": [...]})
            if isinstance(data, dict):
                return data.get("result", [])
            return data
    except (json.JSONDecodeError, OSError):
        return None


def _write_cache(venues):
    """Write venues to cache file."""
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(venues, f, ensure_ascii=False)
    except OSError:
        pass  # best effort


def get_all_venues():
    """Get all venues, from cache if fresh, otherwise from API."""
    cached = _read_cache()
    if cached is not None:
        # Filter out deleted venues
        return [v for v in cached if not v.get("isDeleted", False)]
    
    try:
        req = urllib.request.Request(API_URL)
        req.add_header("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")
        with urllib.request.urlopen(req, timeout=15) as resp:
            response = json.loads(resp.read().decode())
            # API returns {"result": [...]} structure
            data = response.get("result", [])
            _write_cache(data)
            # Filter out deleted venues
            return [v for v in data if not v.get("isDeleted", False)]
    except urllib.error.HTTPError as e:
        print(f"Error: HTTP {e.code} - {e.reason}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Error: Could not fetch venues - {e.reason}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON response - {e}", file=sys.stderr)
        sys.exit(1)


# --- Haversine distance calculation ---


def haversine(lat1, lon1, lat2, lon2):
    """Calculate distance in km between two coordinates."""
    R = 6371  # Earth radius in km
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c


# --- Helper functions ---


def normalize_city(city):
    """Normalize city codes."""
    city_names = {
        "tlv": "Tel Aviv",
        "haifa": "Haifa",
    }
    return city_names.get(city, city)


def contains(query, text):
    """Case-insensitive substring match."""
    if not query or not text:
        return False
    return query.lower() in text.lower()


def search_venues(venues, query):
    """Search venues by name or address (Hebrew or English)."""
    matches = []
    for v in venues:
        name = v.get("name", "")
        name_en = v.get("nameEn", "")
        address = v.get("address", "")
        if contains(query, name) or contains(query, name_en) or contains(query, address):
            matches.append(v)
    return matches


def was_active_in_year(venue, year):
    """Check if venue was active in a given year."""
    opened = venue.get("yearOpened")
    closed = venue.get("yearClosed")
    
    if opened is None:
        return False
    
    if closed is None:
        # Still open
        return year >= opened
    
    return opened <= year <= closed


# --- Formatting ---


def format_venue_brief(venue):
    """Format venue as single line."""
    venue_id = venue.get("id", "?")
    name = venue.get("name", "?")
    name_en = venue.get("nameEn", "")
    
    # Show both names if different
    if name_en and name_en != name:
        display_name = f"{name} / {name_en}"
    else:
        display_name = name
    
    city = normalize_city(venue.get("city", ""))
    tags = [t for t in venue.get("tags", []) if t]
    tag_str = ", ".join(tags) if tags else "-"
    
    opened = venue.get("yearOpened", "?")
    closed = venue.get("yearClosed")
    
    if closed:
        years = f"{opened}-{closed}"
        status = red("closed")
    else:
        years = f"{opened}-present"
        status = green("open")
    
    return f"{bold(display_name)}  {cyan(city)}  {yellow(tag_str)}  {years}  {status}  {dim(f'id:{venue_id}')}"


def format_venue_detail(venue):
    """Format venue with full details."""
    lines = []
    venue_id = venue.get("id", "?")
    name = venue.get("name", "?")
    name_en = venue.get("nameEn", "")
    
    lines.append(f"{magenta('===')} {bold(name)} {magenta('===')}")
    
    if name_en and name_en != name:
        lines.append(f"  {dim('English name:')} {name_en}")
    
    lines.append(f"  {dim('ID:')} {venue_id}")
    
    city = normalize_city(venue.get("city", ""))
    lines.append(f"  {dim('City:')} {city}")
    
    address = venue.get("address", "")
    if address:
        lines.append(f"  {dim('Address:')} {address}")
    
    coords = venue.get("coordinates", [])
    if coords and len(coords) == 2:
        lat, lng = coords
        lines.append(f"  {dim('Coordinates:')} {lat}, {lng}")
        lines.append(f"  {dim('Google Maps:')} https://www.google.com/maps?q={lat},{lng}")
    
    tags = [t for t in venue.get("tags", []) if t]
    if tags:
        lines.append(f"  {dim('Tags:')} {', '.join(tags)}")
    
    opened = venue.get("yearOpened")
    closed = venue.get("yearClosed")
    if opened:
        opened_str = f"{opened}"
        if venue.get("isYearOpenedEstimate"):
            opened_str += " (est.)"
        lines.append(f"  {dim('Opened:')} {opened_str}")
    
    if closed:
        closed_str = f"{closed}"
        if venue.get("isYearClosedEstimate"):
            closed_str += " (est.)"
        lines.append(f"  {dim('Closed:')} {closed_str}")
        
        if opened:
            duration = closed - opened
            lines.append(f"  {dim('Duration:')} {duration} years")
    elif opened:
        lines.append(f"  {dim('Status:')} {green('Still open')}")
    
    desc = venue.get("description", "")
    if desc:
        lines.append(f"  {dim('Description:')} {desc}")
    
    owners = venue.get("owners", "")
    if owners:
        lines.append(f"  {dim('Owners:')} {owners}")
    
    refs = venue.get("references", "")
    if refs:
        lines.append(f"  {dim('References:')} {refs}")
    
    memories = venue.get("memories", [])
    if memories:
        lines.append(f"  {dim('Memories:')} {len(memories)} user memories")
    
    photos = venue.get("photos", [])
    if photos:
        lines.append(f"  {dim('Photos:')} {len(photos)} photos")
    
    related = venue.get("relatedVenues", [])
    if related:
        lines.append(f"  {dim('Related venues:')} {len(related)}")
    
    lines.append(f"  {dim('Web:')} {SITE_URL}/venue/{venue_id}")
    
    return "\n".join(lines)


def format_json(data):
    """Format as JSON."""
    return json.dumps(data, ensure_ascii=False, indent=2)


# --- Commands ---


def cmd_search(args):
    """Search venues by name or address."""
    if not args.query or not args.query.strip():
        if args.json:
            print(format_json({"ok": False, "error": "Search query cannot be empty"}))
        else:
            print("Error: Search query cannot be empty", file=sys.stderr)
        sys.exit(1)

    venues = get_all_venues()
    matches = search_venues(venues, args.query.strip())

    if args.json:
        limited = matches
        if args.limit:
            limited = matches[:args.limit]
        print(format_json({
            "ok": True,
            "command": "search",
            "query": args.query,
            "count": len(matches),
            "venues": limited
        }))
        return

    if not matches:
        print(f"No venues found matching '{args.query}'")
        return

    total = len(matches)
    limit = args.limit if args.limit else 25

    if total == 1:
        print(f"Found 1 match for '{args.query}':\n")
        print(format_venue_detail(matches[0]))
    else:
        display = matches[:limit] if total > limit else matches
        if total > limit:
            print(f"Found {total} match(es) for '{args.query}' (showing first {limit}, use --limit N to see more):\n")
        else:
            print(f"Found {total} match(es) for '{args.query}':\n")
        for venue in display:
            print(f"  {format_venue_brief(venue)}")


def cmd_filter(args):
    """Filter venues by various criteria."""
    has_filters = any([args.city, args.tags, args.year, args.active_in, args.opened, args.closed])
    if not has_filters:
        if args.json:
            print(format_json({"ok": False, "error": "No filter criteria provided. Use --city, --tags, --year, --active-in, --opened, or --closed."}))
        else:
            print("No filter criteria provided. Specify at least one of:")
            print("  --city <tlv|haifa>")
            print("  --tags <tag>")
            print("  --year <year>")
            print("  --active-in <year>")
            print("  --opened <year>")
            print("  --closed <year>")
            print("\nUse 'stats' for a database overview")
        sys.exit(1)

    venues = get_all_venues()

    # Apply filters
    if args.city:
        city_lower = args.city.lower()
        venues = [v for v in venues if v.get("city", "").lower() == city_lower]

    if args.tags:
        tag_lower = args.tags.lower()
        venues = [v for v in venues if any(tag_lower in t.lower() for t in v.get("tags", []))]

    if args.year:
        venues = [v for v in venues if v.get("yearOpened") == args.year or v.get("yearClosed") == args.year]

    if args.active_in:
        venues = [v for v in venues if was_active_in_year(v, args.active_in)]

    if args.opened:
        venues = [v for v in venues if v.get("yearOpened") == args.opened]

    if args.closed:
        venues = [v for v in venues if v.get("yearClosed") == args.closed]

    venues.sort(key=lambda v: v.get("name", ""))

    if args.json:
        limited = venues
        if args.limit:
            limited = venues[:args.limit]
        print(format_json({
            "ok": True,
            "command": "filter",
            "filters": {
                "city": args.city,
                "tags": args.tags,
                "year": args.year,
                "active_in": args.active_in,
                "opened": args.opened,
                "closed": args.closed
            },
            "count": len(venues),
            "venues": limited
        }))
        return

    if not venues:
        print("No venues match the filter criteria")
        return

    total = len(venues)
    limit = args.limit if args.limit else 25
    display = venues[:limit] if total > limit else venues

    if total > limit:
        print(f"Found {total} venue(s) (showing first {limit}, use --limit N to see more):\n")
    else:
        print(f"Found {total} venue(s):\n")
    for venue in display:
        print(f"  {format_venue_brief(venue)}")


def _find_venue(venues, id_or_name, command, json_mode):
    """Find a single venue by ID or name, with disambiguation."""
    venue = None

    # Try to find by ID
    try:
        venue_id = int(id_or_name)
        matches = [v for v in venues if v.get("id") == venue_id]
        if matches:
            return matches[0]
    except ValueError:
        pass

    # Fall back to name/address search
    matches = search_venues(venues, id_or_name)
    if len(matches) == 1:
        return matches[0]
    elif len(matches) > 1:
        if json_mode:
            print(format_json({
                "ok": False,
                "error": f"Multiple venues match '{id_or_name}'. Use a venue ID for exact lookup.",
                "matches": [{"id": v.get("id"), "name": v.get("name"), "nameEn": v.get("nameEn", ""), "city": v.get("city", "")} for v in matches[:10]]
            }))
        else:
            print(f"Multiple venues match '{id_or_name}'. Use a venue ID for exact lookup:\n")
            for v in matches[:10]:
                print(f"  {format_venue_brief(v)}")
            if len(matches) > 10:
                print(f"\n  ... and {len(matches) - 10} more")
        sys.exit(1)

    # No matches
    if json_mode:
        print(format_json({"ok": False, "error": f"No venue found matching '{id_or_name}'"}))
    else:
        print(f"No venue found matching '{id_or_name}'")
    sys.exit(1)


def cmd_venue(args):
    """Get full details for a specific venue."""
    venues = get_all_venues()
    venue = _find_venue(venues, args.id, "venue", args.json)

    if args.json:
        print(format_json({"ok": True, "command": "venue", "venue": venue}))
        return

    print(format_venue_detail(venue))


def cmd_timeline(args):
    """Show all venues active in a given year."""
    venues = get_all_venues()
    active = [v for v in venues if was_active_in_year(v, args.year)]
    active.sort(key=lambda v: v.get("name", ""))

    if args.json:
        limited = active
        if args.limit:
            limited = active[:args.limit]
        print(format_json({
            "ok": True,
            "command": "timeline",
            "year": args.year,
            "count": len(active),
            "venues": limited
        }))
        return

    if not active:
        print(f"No venues were active in {args.year}")
        return

    total = len(active)
    limit = args.limit if args.limit else 25
    display = active[:limit] if total > limit else active

    if total > limit:
        print(f"{bold('Timeline:')} {total} venue(s) active in {yellow(str(args.year))} (showing first {limit}, use --limit N to see more)\n")
    else:
        print(f"{bold('Timeline:')} {total} venue(s) active in {yellow(str(args.year))}\n")
    for venue in display:
        print(f"  {format_venue_brief(venue)}")


def cmd_nearby(args):
    """Find venues near coordinates."""
    venues = get_all_venues()
    nearby = []
    
    for venue in venues:
        coords = venue.get("coordinates", [])
        if coords and len(coords) == 2:
            lat, lng = coords
            distance = haversine(args.lat, args.lng, lat, lng)
            if distance <= args.radius:
                nearby.append((distance, venue))
    
    # Sort by distance
    nearby.sort(key=lambda x: x[0])
    
    if args.json:
        result_venues = []
        for distance, venue in nearby:
            v = venue.copy()
            v["distance_km"] = round(distance, 2)
            result_venues.append(v)
        limited = result_venues
        if args.limit:
            limited = result_venues[:args.limit]
        print(format_json({
            "ok": True,
            "command": "nearby",
            "lat": args.lat,
            "lng": args.lng,
            "radius": args.radius,
            "count": len(nearby),
            "venues": limited
        }))
        return

    if not nearby:
        print(f"No venues found within {args.radius}km of ({args.lat}, {args.lng})")
        return

    total = len(nearby)
    limit = args.limit if args.limit else 25
    display = nearby[:limit] if total > limit else nearby

    if total > limit:
        print(f"Found {total} venue(s) within {args.radius}km (showing first {limit}, use --limit N to see more):\n")
    else:
        print(f"Found {total} venue(s) within {args.radius}km:\n")
    for distance, venue in display:
        dist_str = f"{distance:.2f}km"
        print(f"  {green(dist_str)}  {format_venue_brief(venue)}")


def cmd_tags(args):
    """List all tags or venues with a specific tag."""
    venues = get_all_venues()

    if args.tag:
        # Filter by tag
        tag_lower = args.tag.lower()
        matches = [v for v in venues if any(tag_lower in t.lower() for t in v.get("tags", []) if t)]
        matches.sort(key=lambda v: v.get("name", ""))

        if args.json:
            limited = matches
            if args.limit:
                limited = matches[:args.limit]
            print(format_json({
                "ok": True,
                "command": "tags",
                "tag": args.tag,
                "count": len(matches),
                "venues": limited
            }))
            return

        if not matches:
            print(f"No venues found with tag '{args.tag}'")
            return

        total = len(matches)
        limit = args.limit if args.limit else 25
        display = matches[:limit] if total > limit else matches

        if total > limit:
            print(f"Found {total} venue(s) with tag '{args.tag}' (showing first {limit}, use --limit N to see more):\n")
        else:
            print(f"Found {total} venue(s) with tag '{args.tag}':\n")
        for venue in display:
            print(f"  {format_venue_brief(venue)}")
    else:
        # List all tags with counts
        tag_counts = defaultdict(int)
        for venue in venues:
            for tag in venue.get("tags", []):
                if tag:  # skip empty tags
                    tag_counts[tag] += 1

        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)

        if args.json:
            tag_list = [{"tag": tag, "count": count} for tag, count in sorted_tags]
            print(format_json({
                "ok": True,
                "command": "tags",
                "total_tags": len(sorted_tags),
                "tags": tag_list
            }))
            return

        print(f"{bold('All tags')} ({len(sorted_tags)} unique):\n")
        for tag, count in sorted_tags:
            print(f"  {yellow(f'{tag:20s}')} {dim(f'({count} venues)')}")


def cmd_cities(args):
    """List cities with venue counts."""
    venues = get_all_venues()
    city_counts = defaultdict(int)
    
    for venue in venues:
        city = venue.get("city", "unknown")
        city_counts[city] += 1
    
    sorted_cities = sorted(city_counts.items(), key=lambda x: x[1], reverse=True)
    
    if args.json:
        city_list = [{"city": city, "display": normalize_city(city), "count": count} 
                     for city, count in sorted_cities]
        print(format_json({
            "ok": True,
            "command": "cities",
            "total_cities": len(sorted_cities),
            "cities": city_list
        }))
        return
    
    print(f"{bold('Cities')} ({len(sorted_cities)} total):\n")
    for city, count in sorted_cities:
        display = normalize_city(city)
        print(f"  {cyan(f'{display:15s}')} {dim(f'({count} venues)')}")


def cmd_stats(args):
    """Show database statistics."""
    venues = get_all_venues()
    
    # Basic counts
    total = len(venues)
    
    # City breakdown
    city_counts = defaultdict(int)
    for v in venues:
        city_counts[v.get("city", "unknown")] += 1
    
    # Tag breakdown
    tag_counts = defaultdict(int)
    for v in venues:
        for tag in v.get("tags", []):
            if tag:  # skip empty tags
                tag_counts[tag] += 1

    # Decade breakdown
    decade_counts = defaultdict(int)
    for v in venues:
        opened = v.get("yearOpened")
        if opened:
            decade = (opened // 10) * 10
            decade_counts[decade] += 1
    
    # Status counts
    still_open = len([v for v in venues if v.get("yearClosed") is None])
    closed = total - still_open
    
    # Venues with memories/photos
    with_memories = len([v for v in venues if v.get("memories")])
    with_photos = len([v for v in venues if v.get("photos")])
    
    if args.json:
        print(format_json({
            "ok": True,
            "command": "stats",
            "total_venues": total,
            "still_open": still_open,
            "closed": closed,
            "with_memories": with_memories,
            "with_photos": with_photos,
            "cities": dict(city_counts),
            "top_tags": dict(sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]),
            "decades": dict(sorted(decade_counts.items()))
        }))
        return
    
    print(f"{bold('Timemap Database Statistics')}\n")
    print(f"  {dim('Total venues:')} {total}")
    print(f"  {dim('Still open:')} {green(str(still_open))}")
    print(f"  {dim('Closed:')} {red(str(closed))}")
    print(f"  {dim('With memories:')} {with_memories}")
    print(f"  {dim('With photos:')} {with_photos}")
    
    print(f"\n{bold('Cities:')}")
    for city, count in sorted(city_counts.items(), key=lambda x: x[1], reverse=True):
        display = normalize_city(city)
        print(f"  {cyan(f'{display:15s}')} {count}")
    
    print(f"\n{bold('Top 10 Tags:')}")
    for tag, count in sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {yellow(f'{tag:20s}')} {count}")
    
    print(f"\n{bold('Venues by Decade (opened):')}")
    for decade in sorted(decade_counts.keys()):
        count = decade_counts[decade]
        print(f"  {dim(f'{decade}s:')} {count}")


def cmd_memories(args):
    """Show user memories for a venue."""
    venues = get_all_venues()
    venue = _find_venue(venues, args.id, "memories", args.json)

    memories = venue.get("memories", [])
    
    if args.json:
        print(format_json({
            "ok": True,
            "command": "memories",
            "venue": venue,
            "count": len(memories),
            "memories": memories
        }))
        return
    
    name = venue.get("name", "?")
    print(f"{magenta('===')} Memories: {bold(name)} {magenta('===')}\n")
    
    if not memories:
        print("  No user memories for this venue")
        return
    
    for i, memory in enumerate(memories, 1):
        print(f"  {dim(f'Memory #{i}:')}")
        if isinstance(memory, dict):
            for key, value in memory.items():
                print(f"    {dim(f'{key}:')} {value}")
        else:
            print(f"    {memory}")
        print()


def cmd_random(args):
    """Pick a random venue."""
    venues = get_all_venues()
    
    # Prefer venues with memories or photos
    interesting = [v for v in venues if v.get("memories") or v.get("photos")]
    
    if interesting:
        pick = random.choice(interesting)
        source = "venues with memories/photos"
    else:
        pick = random.choice(venues)
        source = "all venues"
    
    if args.json:
        print(format_json({
            "ok": True,
            "command": "random",
            "source": source,
            "venue": pick
        }))
        return
    
    print(f"{yellow('🎲')} {bold('Random pick')} {dim(f'(from {source})')}\n")
    print(format_venue_detail(pick))


# --- Main ---


def main():
    # Handle global flags before argparse
    no_color = "--no-color" in sys.argv
    fresh = "--fresh" in sys.argv
    argv = [a for a in sys.argv[1:] if a not in ("--no-color", "--fresh")]
    
    parser = argparse.ArgumentParser(
        prog="timemap",
        description="Timemap.co.il - Historical Tel Aviv/Haifa entertainment & culture venues",
        epilog=f"Data from {SITE_URL} (by Reut Miryam Cohen & Amir Ozer) - community-curated venue history"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # search
    p_search = subparsers.add_parser("search", help="Search venues by name or address (Hebrew/English)")
    p_search.add_argument("query", help="Venue name or address to search")
    p_search.add_argument("--limit", type=int, help="Max results (default: 25 for terminal, unlimited for --json)")
    p_search.add_argument("--json", action="store_true", help="JSON output")
    p_search.set_defaults(func=cmd_search)

    # filter
    p_filter = subparsers.add_parser("filter", help="Filter venues by criteria")
    p_filter.add_argument("--city", help="Filter by city (tlv, haifa)")
    p_filter.add_argument("--tags", help="Filter by tag (substring match)")
    p_filter.add_argument("--year", type=int, help="Opened or closed in this year")
    p_filter.add_argument("--active-in", type=int, help="Active in this year")
    p_filter.add_argument("--opened", type=int, help="Opened in this year")
    p_filter.add_argument("--closed", type=int, help="Closed in this year")
    p_filter.add_argument("--limit", type=int, help="Max results (default: 25 for terminal, unlimited for --json)")
    p_filter.add_argument("--json", action="store_true", help="JSON output")
    p_filter.set_defaults(func=cmd_filter)

    # venue
    p_venue = subparsers.add_parser("venue", help="Get full details for a specific venue")
    p_venue.add_argument("id", help="Venue ID or name")
    p_venue.add_argument("--json", action="store_true", help="JSON output")
    p_venue.set_defaults(func=cmd_venue)

    # timeline
    p_timeline = subparsers.add_parser("timeline", help="Show all venues active in a year")
    p_timeline.add_argument("year", type=int, help="Year to query")
    p_timeline.add_argument("--limit", type=int, help="Max results (default: 25 for terminal, unlimited for --json)")
    p_timeline.add_argument("--json", action="store_true", help="JSON output")
    p_timeline.set_defaults(func=cmd_timeline)

    # nearby
    p_nearby = subparsers.add_parser("nearby", help="Find venues near coordinates")
    p_nearby.add_argument("lat", type=float, help="Latitude")
    p_nearby.add_argument("lng", type=float, help="Longitude")
    p_nearby.add_argument("--radius", type=float, default=0.5, help="Radius in km (default: 0.5)")
    p_nearby.add_argument("--limit", type=int, help="Max results (default: 25 for terminal, unlimited for --json)")
    p_nearby.add_argument("--json", action="store_true", help="JSON output")
    p_nearby.set_defaults(func=cmd_nearby)

    # tags
    p_tags = subparsers.add_parser("tags", help="List all tags or filter by tag")
    p_tags.add_argument("tag", nargs="?", help="Tag to filter by (optional)")
    p_tags.add_argument("--limit", type=int, help="Max results when filtering by tag")
    p_tags.add_argument("--json", action="store_true", help="JSON output")
    p_tags.set_defaults(func=cmd_tags)
    
    # cities
    p_cities = subparsers.add_parser("cities", help="List cities with venue counts")
    p_cities.add_argument("--json", action="store_true", help="JSON output")
    p_cities.set_defaults(func=cmd_cities)
    
    # stats
    p_stats = subparsers.add_parser("stats", help="Database statistics")
    p_stats.add_argument("--json", action="store_true", help="JSON output")
    p_stats.set_defaults(func=cmd_stats)
    
    # memories
    p_memories = subparsers.add_parser("memories", help="Show user memories for a venue")
    p_memories.add_argument("id", help="Venue ID or name")
    p_memories.add_argument("--json", action="store_true", help="JSON output")
    p_memories.set_defaults(func=cmd_memories)
    
    # random
    p_random = subparsers.add_parser("random", help="Pick a random venue")
    p_random.add_argument("--json", action="store_true", help="JSON output")
    p_random.set_defaults(func=cmd_random)
    
    args = parser.parse_args(argv)
    _init_color(no_color)
    global _force_fresh
    _force_fresh = fresh
    args.func(args)


if __name__ == "__main__":
    main()
