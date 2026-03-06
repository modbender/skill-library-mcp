#!/usr/bin/env python3
"""
stats.fm CLI - Query stats.fm API for Spotify listening statistics
Usage: statsfm.py <command> [args...]
"""

import sys
import json
import argparse
import os
import time
from typing import Optional, Dict, Any
from urllib.parse import quote
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError
from datetime import datetime


def get_local_timezone() -> str:
    """Detect the system's IANA timezone name (e.g. Europe/Amsterdam).
    Falls back to UTC if detection fails."""
    tz = os.environ.get("TZ", "").strip()
    if tz:
        return tz
    try:
        with open("/etc/timezone") as f:
            tz = f.read().strip()
            if tz:
                return tz
    except OSError:
        pass
    try:
        link = os.path.realpath("/etc/localtime")
        marker = "/zoneinfo/"
        idx = link.find(marker)
        if idx != -1:
            return link[idx + len(marker):]
    except OSError:
        pass
    return "UTC"


BASE_URL = "https://api.stats.fm/api/v1"
DEFAULT_USER = os.environ.get("STATSFM_USER", "")
DEFAULT_RANGE = "weeks"
DEFAULT_LIMIT = 15


class StatsAPI:
    """stats.fm API client"""

    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url

    def request(self, endpoint: str) -> Dict[str, Any]:
        """Make a GET request to the API"""
        url = f"{self.base_url}{endpoint}"

        try:
            req = Request(url)
            req.add_header('User-Agent', 'statsfm-cli/1.0')
            req.add_header('Accept', 'application/json')

            with urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
                return data
        except HTTPError as e:
            error_body = e.read().decode() if e.fp else ""
            try:
                error_data = json.loads(error_body)
                message = error_data.get("message", str(e))
            except json.JSONDecodeError:
                message = str(e)

            print(f"API Error ({e.code}): {message}", file=sys.stderr)
            if e.code == 404 and "private" in message.lower():
                print("Please check your stats.fm privacy settings (Settings > Privacy)", file=sys.stderr)
            sys.exit(1)
        except URLError as e:
            print(f"Connection Error: {e.reason}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)


def format_duration(ms: int) -> str:
    """Format milliseconds as MM:SS"""
    seconds = ms // 1000
    return f"{seconds // 60}:{seconds % 60:02d}"


def format_time(ms: int) -> str:
    """Format milliseconds as minutes or hours"""
    mins = ms // 60000
    if mins >= 60:
        hours = mins // 60
        remaining_mins = mins % 60
        return f"{hours:,}h {remaining_mins}m"
    return f"{mins:,} min"


def get_user_or_exit(args) -> str:
    """Get user from args or env, exit if not found"""
    user = args.user or DEFAULT_USER
    if not user:
        print("Error: No user specified. Set STATSFM_USER or pass --user", file=sys.stderr)
        sys.exit(1)
    return quote(user, safe='')


def get_per_day_stats_with_totals(api: StatsAPI, endpoint: str) -> tuple[Dict[str, Any], int, int]:
    """Get per-day stats and calculate totals"""
    data = api.request(endpoint)
    days = data.get("items", {}).get("days", {})

    total_count = sum(day.get('count', 0) for day in days.values())
    total_ms = sum(day.get('durationMs', 0) for day in days.values())

    return days, total_count, total_ms


def show_monthly_breakdown(days_data: Dict[str, Any], limit: Optional[int] = None):
    """Display monthly breakdown from per-day stats"""
    from collections import defaultdict

    # Group by month
    monthly = defaultdict(lambda: {'count': 0, 'durationMs': 0})

    for date_str, stats in days_data.items():
        try:
            dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            month_key = dt.strftime("%Y-%m")
            monthly[month_key]['count'] += stats['count']
            monthly[month_key]['durationMs'] += stats['durationMs']
        except:
            continue

    # Sort by month and get only months with plays
    months_with_plays = [(month, stats) for month, stats in sorted(monthly.items()) if stats['count'] > 0]

    # Apply limit (most recent months)
    if limit and limit > 0:
        months_with_plays = months_with_plays[-limit:]

    # Display
    print("Monthly breakdown:")
    for month, stats in months_with_plays:
        print(f"  {month}: {stats['count']:>4} plays  ({format_time(stats['durationMs'])})")


def show_daily_breakdown(days_data: Dict[str, Any], limit: Optional[int] = None):
    """Display daily breakdown from per-day stats"""
    daily = []
    for date_str, stats in days_data.items():
        if stats.get('count', 0) > 0:
            try:
                dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                daily.append((dt, stats))
            except:
                continue

    daily.sort(key=lambda x: x[0])
    if limit and limit > 0:
        daily = daily[-limit:]

    print("Daily breakdown:")
    for dt, stats in daily:
        day_name = dt.strftime("%a")
        date_label = dt.strftime("%Y-%m-%d")
        print(f"  {date_label} ({day_name}): {stats['count']:>4} plays  ({format_time(stats['durationMs'])})")


def show_weekly_breakdown(days_data: Dict[str, Any], limit: Optional[int] = None):
    """Display weekly breakdown from per-day stats"""
    from collections import defaultdict
    import datetime as dt_module

    weekly = defaultdict(lambda: {'count': 0, 'durationMs': 0})

    for date_str, stats in days_data.items():
        if stats.get('count', 0) > 0:
            try:
                dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                week_key = dt.strftime("%G-W%V")
                week_start = dt - dt_module.timedelta(days=dt.weekday())
                weekly[week_key]['count'] += stats['count']
                weekly[week_key]['durationMs'] += stats['durationMs']
                weekly[week_key]['start'] = min(weekly[week_key].get('start', week_start), week_start)
            except:
                continue

    weeks_with_plays = [(wk, stats) for wk, stats in sorted(weekly.items()) if stats['count'] > 0]
    if limit and limit > 0:
        weeks_with_plays = weeks_with_plays[-limit:]

    print("Weekly breakdown:")
    for wk, stats in weeks_with_plays:
        start = stats.get('start')
        start_str = start.strftime("%b %d") if start else ""
        print(f"  {wk} ({start_str}): {stats['count']:>4} plays  ({format_time(stats['durationMs'])})")


def show_yearly_breakdown(days_data: Dict[str, Any], limit: Optional[int] = None):
    """Display yearly breakdown from per-day stats"""
    from collections import defaultdict

    yearly = defaultdict(lambda: {'count': 0, 'durationMs': 0})

    for date_str, stats in days_data.items():
        if stats.get('count', 0) > 0:
            try:
                dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                year_key = dt.strftime("%Y")
                yearly[year_key]['count'] += stats['count']
                yearly[year_key]['durationMs'] += stats['durationMs']
            except:
                continue

    years_with_plays = [(yr, stats) for yr, stats in sorted(yearly.items()) if stats['count'] > 0]
    if limit and limit > 0:
        years_with_plays = years_with_plays[-limit:]

    print("Yearly breakdown:")
    for yr, stats in years_with_plays:
        print(f"  {yr}: {stats['count']:>6} plays ({format_time(stats['durationMs'])})")


def parse_date(date_str: str) -> int:
    """Parse date string to Unix timestamp in milliseconds

    Supports formats:
    - YYYY (e.g., "2025" -> Jan 1, 2025 00:00:00)
    - YYYY-MM (e.g., "2025-06" -> Jun 1, 2025 00:00:00)
    - YYYY-MM-DD (e.g., "2025-06-15" -> Jun 15, 2025 00:00:00)
    """
    parts = date_str.split("-")
    if len(parts) == 1:  # YYYY
        dt = datetime(int(parts[0]), 1, 1)
    elif len(parts) == 2:  # YYYY-MM
        dt = datetime(int(parts[0]), int(parts[1]), 1)
    elif len(parts) == 3:  # YYYY-MM-DD
        dt = datetime(int(parts[0]), int(parts[1]), int(parts[2]))
    else:
        raise ValueError(f"Invalid date format: {date_str}")

    return int(dt.timestamp() * 1000)


def get_album_name(track: dict) -> str:
    """Extract album name from track object"""
    albums = track.get("albums", [])
    if albums:
        return albums[0]["name"]
    return "?"


def format_artists(artists: list) -> str:
    """Format artist list as comma-separated string"""
    if not artists:
        return "?"
    return ", ".join(a.get("name", "?") for a in artists)


def print_table(rows, max_width=40):
    """Print rows with dynamically computed column widths, capped at max_width."""
    if not rows:
        return
    widths = [min(max(len(row[i]) for row in rows), max_width) for i in range(len(rows[0]))]
    for row in rows:
        parts = []
        for i, cell in enumerate(row):
            cell = cell[:widths[i]] if len(cell) > widths[i] else cell
            if i == len(row) - 1:
                parts.append(cell)
            else:
                parts.append(f"{cell:<{widths[i]}}")
        print("  ".join(parts))


def build_date_params(args, default_range: str = "weeks") -> str:
    """Build date query parameters from args (range or start/end)

    Returns query string like "range=weeks" or "after=123&before=456"
    """
    if hasattr(args, 'start') and args.start:
        # Use custom date range
        after = parse_date(args.start)
        params = f"after={after}"
        if hasattr(args, 'end') and args.end:
            before = parse_date(args.end)
            params += f"&before={before}"
        return params
    else:
        # Use predefined range
        range_val = args.range if hasattr(args, 'range') and args.range else default_range
        return f"range={range_val}"


def cmd_profile(api: StatsAPI, args):
    """Show user profile"""
    user = get_user_or_exit(args)
    data = api.request(f"/users/{user}")
    u = data.get("item", {})

    name = u.get("displayName", "?")
    custom_id = u.get("customId", "")
    pronouns = u.get("profile", {}).get("pronouns", "")
    bio = u.get("profile", {}).get("bio", "")
    created = u.get("createdAt", "")[:10]
    timezone = u.get("timezone", "")
    recently_active = u.get("recentlyActive", False)

    badges = []
    if u.get("isPlus"):
        badges.append("Plus")
        plus_since = u.get("plusSinceAt", "")[:10]
        if plus_since:
            badges[-1] += f" since {plus_since}"
    if u.get("isPro"):
        badges.append("Pro")
    badge_str = "  [" + " | ".join(badges) + "]" if badges else ""

    handle = f" / {custom_id}" if custom_id and custom_id != name else ""
    pronoun_str = f" ({pronouns})" if pronouns else ""
    print(f"{name}{handle}{pronoun_str}{badge_str}")

    if bio:
        print(f"Bio: {bio}")

    active_str = "yes" if recently_active else "no"
    tz_str = f"  •  {timezone}" if timezone else ""
    print(f"Member since: {created}{tz_str}  •  Recently active: {active_str}")

    spotify = u.get("spotifyAuth")
    if spotify:
        sp_name = spotify.get("displayName", "")
        sp_product = spotify.get("product", "")
        sp_sync = "yes" if spotify.get("sync") else "no"
        sp_imported = "yes" if spotify.get("imported") else "no"
        name_str = f"{sp_name}  " if sp_name else ""
        product_str = f"({sp_product})  " if sp_product else ""
        print(f"Spotify: {name_str}{product_str}sync={sp_sync}  imported={sp_imported}")


def cmd_top_artists(api: StatsAPI, args):
    """Show top artists"""
    user = args.user or DEFAULT_USER
    if not user:
        print("Error: No user specified. Set STATSFM_USER or pass --user", file=sys.stderr)
        sys.exit(1)
    user = quote(user, safe='')

    date_params = build_date_params(args)
    limit = args.limit or DEFAULT_LIMIT

    data = api.request(f"/users/{user}/top/artists?{date_params}&limit={limit}")
    items = data.get("items", [])

    if not items:
        print("No data found.")
        return

    has_stats = items[0].get("playedMs", 0) and (items[0].get("streams") or "?") != "?"
    rows = []
    for item in items:
        artist = item["artist"]
        genres = f"[{', '.join(artist.get('genres', [])[:2])}]"
        row = [f"{item['position']:>3}.", artist["name"]]
        if has_stats:
            row += [f"{item['streams']} plays", f"({format_time(item['playedMs'])})"]
        row += [genres, f"#{artist.get('id', '?')}"]
        rows.append(row)
    print_table(rows)


def cmd_top_tracks(api: StatsAPI, args):
    """Show top tracks"""
    user = args.user or DEFAULT_USER
    if not user:
        print("Error: No user specified. Set STATSFM_USER or pass --user", file=sys.stderr)
        sys.exit(1)
    user = quote(user, safe='')

    date_params = build_date_params(args)
    limit = args.limit or DEFAULT_LIMIT

    data = api.request(f"/users/{user}/top/tracks?{date_params}&limit={limit}")
    items = data.get("items", [])

    if not items:
        print("No data found.")
        return

    has_stats = items[0].get("playedMs", 0) and (items[0].get("streams") or "?") != "?"
    rows = []
    for item in items:
        track = item["track"]
        row = [f"{item['position']:>3}.", track["name"], track["artists"][0]["name"]]
        if args.album:
            row.append(get_album_name(track))
        if has_stats:
            row += [f"{item['streams']} plays", f"({format_time(item['playedMs'])})"]
        row.append(f"#{track.get('id', '?')}")
        rows.append(row)
    print_table(rows)


def cmd_top_albums(api: StatsAPI, args):
    """Show top albums"""
    user = args.user or DEFAULT_USER
    if not user:
        print("Error: No user specified. Set STATSFM_USER or pass --user", file=sys.stderr)
        sys.exit(1)
    user = quote(user, safe='')

    date_params = build_date_params(args)
    limit = args.limit or DEFAULT_LIMIT

    data = api.request(f"/users/{user}/top/albums?{date_params}&limit={limit}")
    items = data.get("items", [])

    if not items:
        print("No data found.")
        return

    has_stats = items[0].get("playedMs", 0) and (items[0].get("streams") or "?") != "?"
    rows = []
    for item in items:
        album = item["album"]
        artists = album.get("artists", [])
        artist = artists[0]["name"] if artists else "?"
        row = [f"{item['position']:>3}.", album["name"], artist]
        if has_stats:
            row += [f"{item['streams']} plays", f"({format_time(item['playedMs'])})"]
        row.append(f"#{album.get('id', '?')}")
        rows.append(row)
    print_table(rows)


def cmd_top_genres(api: StatsAPI, args):
    """Show top genres"""
    user = args.user or DEFAULT_USER
    if not user:
        print("Error: No user specified. Set STATSFM_USER or pass --user", file=sys.stderr)
        sys.exit(1)
    user = quote(user, safe='')

    date_params = build_date_params(args)
    limit = args.limit or DEFAULT_LIMIT

    data = api.request(f"/users/{user}/top/genres?{date_params}&limit={limit}")
    items = data.get("items", [])

    if not items:
        print("No data found.")
        return

    has_stats = items[0].get("playedMs", 0) and (items[0].get("streams") or "?") != "?"
    rows = []
    for item in items:
        row = [f"{item['position']:>3}.", item["genre"]["tag"]]
        if has_stats:
            row += [f"{item['streams']} plays", f"({format_time(item['playedMs'])})"]
        rows.append(row)
    print_table(rows)


def cmd_now_playing(api: StatsAPI, args):
    """Show currently playing track"""
    user = args.user or DEFAULT_USER
    if not user:
        print("Error: No user specified. Set STATSFM_USER or pass --user", file=sys.stderr)
        sys.exit(1)
    user = quote(user, safe='')

    data = api.request(f"/users/{user}/streams/current")
    item = data.get("item")

    if not item:
        print("Nothing playing.")
        return

    track = item["track"]
    artists = format_artists(track["artists"])
    name = track["name"]
    album = track["albums"][0]["name"] if track.get("albums") else "?"
    progress = item["progressMs"] // 1000
    duration = track["durationMs"] // 1000
    device = item.get("deviceName", "?")
    icon = "▶" if item.get("isPlaying") else "⏸"
    track_id = track.get("id", "?")
    artist_id = track["artists"][0].get("id", "?") if track.get("artists") else "?"

    print(f"{icon} {name}")
    print(f"   by {artists}  •  {album}")
    print(f"   {progress//60}:{progress%60:02d} / {duration//60}:{duration%60:02d}  •  {device}")
    print(f"   IDs: track={track_id}, artist={artist_id}")


def cmd_recent(api: StatsAPI, args):
    """Show recently played tracks"""
    user = args.user or DEFAULT_USER
    if not user:
        print("Error: No user specified. Set STATSFM_USER or pass --user", file=sys.stderr)
        sys.exit(1)
    user = quote(user, safe='')

    limit = args.limit or DEFAULT_LIMIT

    data = api.request(f"/users/{user}/streams/recent?limit={limit}")
    items = data.get("items", [])

    if not items:
        print("No recent streams found.")
        return

    rows = []
    for stream in items:
        track = stream.get("track", {})
        end_time = stream.get("endTime", "")
        if end_time:
            try:
                dt = datetime.fromisoformat(end_time.replace("Z", "+00:00")).astimezone()
                time_str = dt.strftime("%H:%M")
            except:
                time_str = "??:??"
        else:
            time_str = "??:??"

        row = [time_str, track.get("name", "?"), track.get("artists", [{}])[0].get("name", "?")]
        if args.album:
            row.append(get_album_name(track))
        rows.append(row)
    print_table(rows)


def cmd_artist_stats(api: StatsAPI, args):
    """Show stats for a specific artist"""
    user = get_user_or_exit(args)

    artist_data = api.request(f"/artists/{args.artist_id}")
    artist = artist_data.get("item", {})
    genres = ", ".join(artist.get("genres", []))
    followers = artist.get("followers", 0)
    follower_str = f"{followers:,}" if followers else "?"
    print(f"{artist.get('name', '?')}  [{genres}]  {follower_str} followers")
    print()

    date_params = build_date_params(args, "lifetime")
    days, total_count, total_ms = get_per_day_stats_with_totals(
        api, f"/users/{user}/streams/artists/{args.artist_id}/stats/per-day?timeZone={quote(get_local_timezone(), safe='')}&{date_params}"
    )

    print(f"Total: {total_count} plays  ({format_time(total_ms)})")
    print()
    granularity = getattr(args, 'granularity', 'monthly') or 'monthly'
    if granularity == 'daily':
        show_daily_breakdown(days, getattr(args, 'limit', None))
    elif granularity == 'weekly':
        show_weekly_breakdown(days, getattr(args, 'limit', None))
    elif granularity == 'yearly':
        show_yearly_breakdown(days, getattr(args, 'limit', None))
    else:
        show_monthly_breakdown(days, getattr(args, 'limit', None))


def cmd_track_stats(api: StatsAPI, args):
    """Show stats for a specific track"""
    user = get_user_or_exit(args)

    if not args.track_id:
        print("Error: Track ID required", file=sys.stderr)
        sys.exit(1)

    # Fetch track info
    track_data = api.request(f"/tracks/{args.track_id}")
    track = track_data.get("item", {})
    track_name = track.get("name", "?")
    artists = format_artists(track.get("artists", []))
    album = get_album_name(track) if track.get("albums") else "?"

    print(f"{track_name} by {artists}")
    print(f"Album: {album}")
    print()

    date_params = build_date_params(args, "lifetime")
    days, total_count, total_ms = get_per_day_stats_with_totals(
        api, f"/users/{user}/streams/tracks/{args.track_id}/stats/per-day?timeZone={quote(get_local_timezone(), safe='')}&{date_params}"
    )

    print(f"Total: {total_count} plays  ({format_time(total_ms)})")
    print()
    granularity = getattr(args, 'granularity', 'monthly') or 'monthly'
    if granularity == 'daily':
        show_daily_breakdown(days, getattr(args, 'limit', None))
    elif granularity == 'weekly':
        show_weekly_breakdown(days, getattr(args, 'limit', None))
    elif granularity == 'yearly':
        show_yearly_breakdown(days, getattr(args, 'limit', None))
    else:
        show_monthly_breakdown(days, getattr(args, 'limit', None))


def cmd_album_stats(api: StatsAPI, args):
    """Show stats for a specific album"""
    user = get_user_or_exit(args)

    if not args.album_id:
        print("Error: Album ID required", file=sys.stderr)
        sys.exit(1)

    date_params = build_date_params(args, "lifetime")
    days, total_count, total_ms = get_per_day_stats_with_totals(
        api, f"/users/{user}/streams/albums/{args.album_id}/stats/per-day?timeZone={quote(get_local_timezone(), safe='')}&{date_params}"
    )

    print(f"Total: {total_count} plays  ({format_time(total_ms)})")
    print()
    granularity = getattr(args, 'granularity', 'monthly') or 'monthly'
    if granularity == 'daily':
        show_daily_breakdown(days, getattr(args, 'limit', None))
    elif granularity == 'weekly':
        show_weekly_breakdown(days, getattr(args, 'limit', None))
    elif granularity == 'yearly':
        show_yearly_breakdown(days, getattr(args, 'limit', None))
    else:
        show_monthly_breakdown(days, getattr(args, 'limit', None))


def cmd_stream_stats(api: StatsAPI, args):
    """Show overall stream statistics"""
    user = get_user_or_exit(args)

    date_params = build_date_params(args)

    data = api.request(f"/users/{user}/streams/stats?{date_params}")
    items = data.get("items", data.get("item", {}))

    count = items.get("count", "?")
    ms = items.get("durationMs", 0)

    print(f"Streams: {count:,}" if isinstance(count, int) else f"Streams: {count}")
    print(f"Total time: {format_time(ms)}")

    played = items.get("playedMs", {})
    if isinstance(played, dict) and played.get("avg"):
        print(f"Avg track: {format_duration(int(played['avg']))}")
        print(f"Shortest: {format_duration(int(played['min']))}  |  Longest: {format_duration(int(played['max']))}")

    card = items.get("cardinality", {})
    if card:
        parts = []
        if card.get("tracks"):
            parts.append(f"{card['tracks']:,} tracks")
        if card.get("artists"):
            parts.append(f"{card['artists']:,} artists")
        if card.get("albums"):
            parts.append(f"{card['albums']:,} albums")
        if parts:
            print(f"Unique: {', '.join(parts)}")


def show_top_items(api: StatsAPI, endpoint: str, item_key: str, limit: int, show_album=False):
    """Shared logic for top-tracks-from-artist, top-tracks-from-album, top-albums-from-artist"""
    data = api.request(endpoint)
    items = data.get("items", [])

    if not items:
        print("No data found.")
        return

    total = len(items)
    items = items[:limit]
    has_stats = items[0].get("playedMs", 0) and (items[0].get("streams") or "?") != "?"
    rows = []
    for item in items:
        entry = item[item_key]
        row = [f"{item['position']:>3}.", entry["name"]]
        if show_album:
            row.append(get_album_name(entry))
        if has_stats:
            row += [f"{item['streams']} plays", f"({format_time(item['playedMs'])})"]
        rows.append(row)
    print_table(rows)
    remaining = total - limit
    if remaining > 0:
        print(f"  ({remaining} more)")


def cmd_top_tracks_from_artist(api: StatsAPI, args):
    """Show top tracks from a specific artist"""
    user = get_user_or_exit(args)
    if not args.artist_id:
        print("Error: Artist ID required", file=sys.stderr)
        sys.exit(1)
    date_params = build_date_params(args)
    limit = args.limit or DEFAULT_LIMIT
    show_top_items(api, f"/users/{user}/top/artists/{args.artist_id}/tracks?{date_params}", "track", limit, show_album=args.album)


def cmd_top_tracks_from_album(api: StatsAPI, args):
    """Show top tracks from a specific album"""
    user = get_user_or_exit(args)
    if not args.album_id:
        print("Error: Album ID required", file=sys.stderr)
        sys.exit(1)
    date_params = build_date_params(args)
    limit = args.limit or 100
    show_top_items(api, f"/users/{user}/top/albums/{args.album_id}/tracks?{date_params}", "track", limit)


def cmd_top_albums_from_artist(api: StatsAPI, args):
    """Show top albums from a specific artist"""
    user = get_user_or_exit(args)
    if not args.artist_id:
        print("Error: Artist ID required", file=sys.stderr)
        sys.exit(1)
    date_params = build_date_params(args)
    limit = args.limit or DEFAULT_LIMIT
    show_top_items(api, f"/users/{user}/top/artists/{args.artist_id}/albums?{date_params}", "album", limit)


def cmd_charts_top_tracks(api: StatsAPI, args):
    """Show global top tracks chart"""
    range_val = args.range or "today"
    limit = args.limit or DEFAULT_LIMIT

    data = api.request(f"/charts/top/tracks?range={range_val}")
    items = data.get("items", [])[:limit]  # Apply limit in software

    if not items:
        print("No chart data found.")
        return

    print(f"Global Top Tracks ({range_val}):")
    rows = []
    for item in items:
        track = item.get("track", {})
        artists = track.get("artists", [])
        artist = artists[0].get("name", "?") if artists else "?"
        row = [f"{item.get('position', '?'):>3}.", track.get("name", "?"), artist]
        if args.album:
            row.append(get_album_name(track))
        row.append(f"{item.get('streams', 0)} streams")
        rows.append(row)
    print_table(rows)


def cmd_charts_top_artists(api: StatsAPI, args):
    """Show global top artists chart"""
    range_val = args.range or "today"
    limit = args.limit or DEFAULT_LIMIT

    data = api.request(f"/charts/top/artists?range={range_val}")
    items = data.get("items", [])[:limit]

    if not items:
        print("No chart data found.")
        return

    print(f"Global Top Artists ({range_val}):")
    rows = []
    for item in items:
        artist = item.get("artist", {})
        genres = f"[{', '.join(artist.get('genres', [])[:2])}]"
        rows.append([f"{item.get('position', '?'):>3}.", artist.get("name", "?"), f"{item.get('streams', 0)} streams", genres])
    print_table(rows)


def cmd_charts_top_albums(api: StatsAPI, args):
    """Show global top albums chart"""
    range_val = args.range or "today"
    limit = args.limit or DEFAULT_LIMIT

    data = api.request(f"/charts/top/albums?range={range_val}")
    items = data.get("items", [])[:limit]

    if not items:
        print("No chart data found.")
        return

    print(f"Global Top Albums ({range_val}):")
    rows = []
    for item in items:
        album = item.get("album", {})
        artists = album.get("artists", [])
        artist = artists[0].get("name", "?") if artists else "?"
        rows.append([f"{item.get('position', '?'):>3}.", album.get("name", "?"), artist, f"{item.get('streams', 0)} streams"])
    print_table(rows)


def cmd_artist_albums(api: StatsAPI, args):
    """Show albums by a specific artist"""
    data = api.request(f"/artists/{args.artist_id}/albums?limit=500")
    items = data.get("items", [])

    if not items:
        print("No albums found.")
        return

    seen = set()
    unique = []
    for a in items:
        if a["id"] not in seen:
            seen.add(a["id"])
            unique.append(a)
    unique.sort(key=lambda a: a.get("releaseDate", 0), reverse=True)

    groups = {}
    for a in unique:
        groups.setdefault(a.get("type", "other"), []).append(a)

    type_order = [("album", "Albums"), ("single", "Singles & EPs"), ("compilation", "Compilations")]
    show_types = type_order if args.type == "all" else [(args.type, dict(type_order)[args.type])]
    limit = args.limit or DEFAULT_LIMIT

    first = True
    for key, label in show_types:
        section = groups.get(key, [])
        if not section:
            continue
        if not first:
            print()
        first = False
        print(f"{label}:")
        rows = []
        for album in section[:limit]:
            release_ms = album.get("releaseDate", 0)
            year = datetime.fromtimestamp(release_ms / 1000).strftime("%Y") if release_ms else "?"
            rows.append([year, album["name"], f"{album.get('totalTracks', '?')} tracks", f"#{album['id']}"])
        print_table(rows)
        remaining = len(section) - limit
        if remaining > 0:
            print(f"  ({remaining} more)")


def cmd_album(api: StatsAPI, args):
    """Show album info and tracklist"""
    data = api.request(f"/albums/{args.album_id}")
    album = data.get("item", {})

    name = album.get("name", "?")
    artists = format_artists(album.get("artists", []))
    release_ms = album.get("releaseDate", 0)
    release_date = datetime.fromtimestamp(release_ms / 1000).strftime("%Y-%m-%d") if release_ms else "?"
    label = album.get("label", "")
    genres = ", ".join(album.get("genres", []))

    print(f"{name} by {artists}  #{args.album_id}")
    info_parts = [release_date, f"{album.get('totalTracks', '?')} tracks"]
    if label:
        info_parts.append(label)
    if genres:
        info_parts.append(genres)
    print("  " + "  |  ".join(info_parts))
    print()

    tracks_data = api.request(f"/albums/{args.album_id}/tracks")
    tracks = tracks_data.get("items", [])

    if not tracks:
        print("No tracks found.")
        return

    rows = []
    for i, track in enumerate(tracks, 1):
        tag = " [E]" if track.get("explicit") else ""
        rows.append([
            f"{i:>2}.",
            track.get("name", "?") + tag,
            format_duration(track.get("durationMs", 0)),
            f"#{track.get('id', '?')}",
        ])
    print_table(rows)


def cmd_search(api: StatsAPI, args):
    """Search for artists, tracks, or albums"""
    if not args.query:
        print("Error: Search query required", file=sys.stderr)
        sys.exit(1)

    search_type = args.type
    limit = args.limit or 5
    encoded_query = quote(args.query)

    # Build URL: omit type param for broad search across all categories
    if search_type:
        url = f"/search?query={encoded_query}&type={search_type}&limit={limit}"
    else:
        url = f"/search?query={encoded_query}&limit={limit}"

    data = api.request(url)
    items = data.get("items", {})

    found_any = False

    # Show artists if type is artist or broad search
    if search_type in ("artist", None):
        artists = items.get("artists", [])
        if artists:
            found_any = True
            print("\nARTISTS:")
            for artist in artists[:limit]:
                aid = artist.get("id", "?")
                name = artist.get("name", "?")
                genres = ", ".join(artist.get("genres", [])[:2])
                extra = f"  [{genres}]" if genres else ""
                print(f"  [{aid}] {name}{extra}")

    # Show tracks if type is track or broad search
    if search_type in ("track", None):
        tracks = items.get("tracks", [])
        if tracks:
            found_any = True
            print("\nTRACKS:")
            for track in tracks[:limit]:
                tid = track.get("id", "?")
                name = track.get("name", "?")
                artists = format_artists(track.get("artists", []))
                print(f"  [{tid}] {name} by {artists}")

    # Show albums if type is album or broad search
    if search_type in ("album", None):
        albums = items.get("albums", [])
        if albums:
            found_any = True
            print("\nALBUMS:")
            for album in albums[:limit]:
                alb_id = album.get("id", "?")
                name = album.get("name", "?")
                artists = format_artists(album.get("artists", []))
                print(f"  [{alb_id}] {name} by {artists}")

    if not found_any:
        print("No results found.")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="stats.fm CLI - Query Spotify listening statistics",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s top-artists
  %(prog)s top-tracks --range lifetime --limit 20
  %(prog)s now-playing --user <username>
  %(prog)s search "madison beer"
  %(prog)s search "madison beer" --type artist
  %(prog)s track-stats 70714270 --range lifetime
  %(prog)s album-stats 16211936
  %(prog)s stream-stats --range weeks

Ranges: today, weeks (4 weeks), months (6 months), lifetime
Set STATSFM_USER environment variable for default user
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Profile command
    profile_parser = subparsers.add_parser("profile", help="Show user profile")
    profile_parser.add_argument("--user", "-u", help="stats.fm username")

    # Top artists command
    artists_parser = subparsers.add_parser("top-artists", help="Show top artists")
    artists_parser.add_argument("--range", "-r", help="Time range (default: weeks)")
    artists_parser.add_argument("--start", help="Start date (YYYY, YYYY-MM, or YYYY-MM-DD)")
    artists_parser.add_argument("--end", help="End date (YYYY, YYYY-MM, or YYYY-MM-DD)")
    artists_parser.add_argument("--limit", "-l", type=int, help="Number of results (default: 10)")
    artists_parser.add_argument("--user", "-u", help="stats.fm username")

    # Top tracks command
    tracks_parser = subparsers.add_parser("top-tracks", help="Show top tracks")
    tracks_parser.add_argument("--range", "-r", help="Time range (default: weeks)")
    tracks_parser.add_argument("--start", help="Start date (YYYY, YYYY-MM, or YYYY-MM-DD)")
    tracks_parser.add_argument("--end", help="End date (YYYY, YYYY-MM, or YYYY-MM-DD)")
    tracks_parser.add_argument("--limit", "-l", type=int, help="Number of results (default: 10)")
    tracks_parser.add_argument("--user", "-u", help="stats.fm username")
    tracks_parser.add_argument("--no-album", dest="album", action="store_false", help="Hide album name")

    # Top albums command
    albums_parser = subparsers.add_parser("top-albums", help="Show top albums")
    albums_parser.add_argument("--range", "-r", help="Time range (default: weeks)")
    albums_parser.add_argument("--start", help="Start date (YYYY, YYYY-MM, or YYYY-MM-DD)")
    albums_parser.add_argument("--end", help="End date (YYYY, YYYY-MM, or YYYY-MM-DD)")
    albums_parser.add_argument("--limit", "-l", type=int, help="Number of results (default: 10)")
    albums_parser.add_argument("--user", "-u", help="stats.fm username")

    # Top genres command
    genres_parser = subparsers.add_parser("top-genres", help="Show top genres")
    genres_parser.add_argument("--range", "-r", help="Time range (default: weeks)")
    genres_parser.add_argument("--start", help="Start date (YYYY, YYYY-MM, or YYYY-MM-DD)")
    genres_parser.add_argument("--end", help="End date (YYYY, YYYY-MM, or YYYY-MM-DD)")
    genres_parser.add_argument("--limit", "-l", type=int, help="Number of results (default: 10)")
    genres_parser.add_argument("--user", "-u", help="stats.fm username")

    # Now playing command
    now_parser = subparsers.add_parser("now-playing", aliases=["now", "np"], help="Show currently playing")
    now_parser.add_argument("--user", "-u", help="stats.fm username")

    # Recent command
    recent_parser = subparsers.add_parser("recent", help="Show recently played tracks")
    recent_parser.add_argument("--limit", "-l", type=int, help="Number of results (default: 10)")
    recent_parser.add_argument("--user", "-u", help="stats.fm username")
    recent_parser.add_argument("--no-album", dest="album", action="store_false", help="Hide album name")

    # Artist stats command
    artist_stats_parser = subparsers.add_parser("artist-stats", help="Show stats for a specific artist")
    artist_stats_parser.add_argument("artist_id", type=int, help="Artist ID")
    artist_stats_parser.add_argument("--range", "-r", help="Time range (weeks/months/lifetime)")
    artist_stats_parser.add_argument("--start", help="Start date (YYYY, YYYY-MM, or YYYY-MM-DD)")
    artist_stats_parser.add_argument("--end", help="End date (YYYY, YYYY-MM, or YYYY-MM-DD)")
    artist_stats_parser.add_argument("--limit", "-l", type=int, help="Limit to most recent N periods")
    artist_stats_parser.add_argument("--granularity", "-g", choices=["daily", "weekly", "monthly", "yearly"], default="monthly", help="Breakdown granularity (default: monthly)")
    artist_stats_parser.add_argument("--user", "-u", help="stats.fm username")

    # Track stats command
    track_stats_parser = subparsers.add_parser("track-stats", help="Show stats for a specific track")
    track_stats_parser.add_argument("track_id", type=int, help="Track ID")
    track_stats_parser.add_argument("--range", "-r", help="Time range (weeks/months/lifetime)")
    track_stats_parser.add_argument("--start", help="Start date (YYYY, YYYY-MM, or YYYY-MM-DD)")
    track_stats_parser.add_argument("--end", help="End date (YYYY, YYYY-MM, or YYYY-MM-DD)")
    track_stats_parser.add_argument("--limit", "-l", type=int, help="Limit to most recent N periods")
    track_stats_parser.add_argument("--granularity", "-g", choices=["daily", "weekly", "monthly", "yearly"], default="monthly", help="Breakdown granularity (default: monthly)")
    track_stats_parser.add_argument("--user", "-u", help="stats.fm username")

    # Album stats command
    album_stats_parser = subparsers.add_parser("album-stats", help="Show stats for a specific album")
    album_stats_parser.add_argument("album_id", type=int, help="Album ID")
    album_stats_parser.add_argument("--range", "-r", help="Time range (weeks/months/lifetime)")
    album_stats_parser.add_argument("--start", help="Start date (YYYY, YYYY-MM, or YYYY-MM-DD)")
    album_stats_parser.add_argument("--end", help="End date (YYYY, YYYY-MM, or YYYY-MM-DD)")
    album_stats_parser.add_argument("--limit", "-l", type=int, help="Limit to most recent N periods")
    album_stats_parser.add_argument("--granularity", "-g", choices=["daily", "weekly", "monthly", "yearly"], default="monthly", help="Breakdown granularity (default: monthly)")
    album_stats_parser.add_argument("--user", "-u", help="stats.fm username")

    # Stream stats command
    stream_stats_parser = subparsers.add_parser("stream-stats", help="Show overall stream statistics")
    stream_stats_parser.add_argument("--range", "-r", help="Time range (default: weeks)")
    stream_stats_parser.add_argument("--start", help="Start date (YYYY, YYYY-MM, or YYYY-MM-DD)")
    stream_stats_parser.add_argument("--end", help="End date (YYYY, YYYY-MM, or YYYY-MM-DD)")
    stream_stats_parser.add_argument("--user", "-u", help="stats.fm username")

    # Top tracks from artist command
    top_tracks_artist_parser = subparsers.add_parser("top-tracks-from-artist", help="Show top tracks from a specific artist")
    top_tracks_artist_parser.add_argument("artist_id", type=int, help="Artist ID")
    top_tracks_artist_parser.add_argument("--range", "-r", help="Time range (default: weeks)")
    top_tracks_artist_parser.add_argument("--start", help="Start date (YYYY, YYYY-MM, or YYYY-MM-DD)")
    top_tracks_artist_parser.add_argument("--end", help="End date (YYYY, YYYY-MM, or YYYY-MM-DD)")
    top_tracks_artist_parser.add_argument("--limit", "-l", type=int, help="Number of results (default: 15)")
    top_tracks_artist_parser.add_argument("--user", "-u", help="stats.fm username")
    top_tracks_artist_parser.add_argument("--no-album", dest="album", action="store_false", help="Hide album name")

    # Top tracks from album command
    top_tracks_album_parser = subparsers.add_parser("top-tracks-from-album", help="Show top tracks from a specific album")
    top_tracks_album_parser.add_argument("album_id", type=int, help="Album ID")
    top_tracks_album_parser.add_argument("--range", "-r", help="Time range (default: weeks)")
    top_tracks_album_parser.add_argument("--start", help="Start date (YYYY, YYYY-MM, or YYYY-MM-DD)")
    top_tracks_album_parser.add_argument("--end", help="End date (YYYY, YYYY-MM, or YYYY-MM-DD)")
    top_tracks_album_parser.add_argument("--limit", "-l", type=int, help="Number of results (default: 15)")
    top_tracks_album_parser.add_argument("--user", "-u", help="stats.fm username")

    # Top albums from artist command
    top_albums_artist_parser = subparsers.add_parser("top-albums-from-artist", help="Show top albums from a specific artist")
    top_albums_artist_parser.add_argument("artist_id", type=int, help="Artist ID")
    top_albums_artist_parser.add_argument("--range", "-r", help="Time range (default: weeks)")
    top_albums_artist_parser.add_argument("--start", help="Start date (YYYY, YYYY-MM, or YYYY-MM-DD)")
    top_albums_artist_parser.add_argument("--end", help="End date (YYYY, YYYY-MM, or YYYY-MM-DD)")
    top_albums_artist_parser.add_argument("--limit", "-l", type=int, help="Number of results (default: 15)")
    top_albums_artist_parser.add_argument("--user", "-u", help="stats.fm username")

    # Artist albums command
    artist_albums_parser = subparsers.add_parser("artist-albums", help="Show albums by a specific artist")
    artist_albums_parser.add_argument("artist_id", type=int, help="Artist ID")
    artist_albums_parser.add_argument("--type", "-t", choices=["album", "single", "all"], default="all", help="Filter by type (default: all)")
    artist_albums_parser.add_argument("--limit", "-l", type=int, help="Items per section (default: 15)")

    # Charts commands
    charts_tracks_parser = subparsers.add_parser("charts-top-tracks", help="Show global top tracks chart")
    charts_tracks_parser.add_argument("--limit", "-l", type=int, help="Number of results (default: 15)")
    charts_tracks_parser.add_argument("--range", "-r", help="Time range (default: today)")
    charts_tracks_parser.add_argument("--no-album", dest="album", action="store_false", help="Hide album name")

    charts_artists_parser = subparsers.add_parser("charts-top-artists", help="Show global top artists chart")
    charts_artists_parser.add_argument("--limit", "-l", type=int, help="Number of results (default: 15)")
    charts_artists_parser.add_argument("--range", "-r", help="Time range (default: today)")

    charts_albums_parser = subparsers.add_parser("charts-top-albums", help="Show global top albums chart")
    charts_albums_parser.add_argument("--limit", "-l", type=int, help="Number of results (default: 15)")
    charts_albums_parser.add_argument("--range", "-r", help="Time range (default: today)")

    # Album lookup command
    album_parser = subparsers.add_parser("album", help="Show album info and tracklist")
    album_parser.add_argument("album_id", type=int, help="Album ID")

    # Search command
    search_parser = subparsers.add_parser("search", help="Search for artists, tracks, or albums")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--type", "-t", choices=["artist", "track", "album"], help="Filter by type (omit to search all)")
    search_parser.add_argument("--limit", "-l", type=int, help="Results per category (default: 5)")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    api = StatsAPI()

    # Route to appropriate command
    commands = {
        "profile": cmd_profile,
        "top-artists": cmd_top_artists,
        "top-tracks": cmd_top_tracks,
        "top-albums": cmd_top_albums,
        "top-genres": cmd_top_genres,
        "now-playing": cmd_now_playing,
        "now": cmd_now_playing,
        "np": cmd_now_playing,
        "recent": cmd_recent,
        "artist-stats": cmd_artist_stats,
        "track-stats": cmd_track_stats,
        "album-stats": cmd_album_stats,
        "stream-stats": cmd_stream_stats,
        "top-tracks-from-artist": cmd_top_tracks_from_artist,
        "top-tracks-from-album": cmd_top_tracks_from_album,
        "top-albums-from-artist": cmd_top_albums_from_artist,
        "charts-top-tracks": cmd_charts_top_tracks,
        "charts-top-artists": cmd_charts_top_artists,
        "charts-top-albums": cmd_charts_top_albums,
        "album": cmd_album,
        "artist-albums": cmd_artist_albums,
        "search": cmd_search,
    }

    cmd_func = commands.get(args.command)
    if cmd_func:
        cmd_func(api, args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
