#!/usr/bin/env python3
"""
Radarr-Sonarr CLI

Command-line interface for Radarr and Sonarr operations.
"""

import sys
import os
import argparse

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.radarr import RadarrClient
from scripts.sonarr import SonarrClient
from scripts.parser import NLParser


def create_radarr_client() -> RadarrClient:
    """Create Radarr client with environment config."""
    try:
        return RadarrClient()
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)


def create_sonarr_client() -> SonarrClient:
    """Create Sonarr client with environment config."""
    try:
        return SonarrClient()
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)


def cmd_radarr_search(args):
    """Search for movies."""
    client = create_radarr_client()
    results = client.search(args.query)
    if not results:
        print(f"No results found for: {args.query}")
        return
    print(f"\nSearch results for: {args.query}\n")
    for i, movie in enumerate(results[:5], 1):
        print(f"{i}. {movie.get('title', 'Unknown')} ({movie.get('year', 'N/A')})")
        print(f"   TMDB ID: {movie.get('tmdbId')}")
        if movie.get('imdbId'):
            print(f"   IMDb: tt{movie.get('imdbId')}")
        print()


def cmd_radarr_download(args):
    """Download a movie."""
    client = create_radarr_client()
    result = client.add(int(args.tmdb_id))
    if "error" in result:
        print(f"Error: {result['error']}")
    else:
        title = result.get('title', 'Movie')
        print(f"✅ Added to download queue: {title}")
        print("   Radarr will search and download the best available quality.")


def cmd_radarr_queue(args):
    """Show Radarr download queue."""
    client = create_radarr_client()
    queue = client.get_queue()
    if "error" in queue:
        print(f"Error: {queue['error']}")
        return
    records = queue.get("records", [])
    if not records:
        print("Queue is empty. 🎉")
        return
    print("\nDownload Queue:\n")
    for item in records[:10]:
        print(f"📥 {item.get('title', 'Unknown')}")
        print(f"   Status: {item.get('status', 'N/A')}")
        print(f"   Progress: {item.get('progress', 0):.0f}%")
        print()


def cmd_radarr_wanted(args):
    """Show wanted/missing movies."""
    client = create_radarr_client()
    wanted = client.get_wanted()
    if "error" in wanted:
        print(f"Error: {wanted['error']}")
        return
    records = wanted.get("records", [])
    if not records:
        print("No wanted movies! 🎉")
        return
    print("\nWanted Movies:\n")
    for movie in records[:10]:
        print(f"🎬 {movie.get('title', 'Unknown')} ({movie.get('year', 'N/A')})")
        print(f"   ID: {movie.get('id')}")
        print()


def cmd_radarr_status(args):
    """Show Radarr system status."""
    client = create_radarr_client()
    status = client.test_connection()
    if "error" in status:
        print(f"Connection Error: {status['error']}")
    else:
        version = status.get('version', 'Unknown')
        print(f"✅ Radarr connected")
        print(f"   Version: {version}")


def cmd_sonarr_search(args):
    """Search for TV series."""
    client = create_sonarr_client()
    results = client.search(args.query)
    if not results:
        print(f"No results found for: {args.query}")
        return
    print(f"\nSearch results for: {args.query}\n")
    for i, series in enumerate(results[:5], 1):
        print(f"{i}. {series.get('title', 'Unknown')} ({series.get('year', 'N/A')})")
        print(f"   TVDB ID: {series.get('tvdbId')}")
        print()


def cmd_sonarr_download(args):
    """Download/add a TV series."""
    client = create_sonarr_client()
    result = client.add(int(args.tvdb_id))
    if "error" in result:
        print(f"Error: {result['error']}")
    else:
        title = result.get('title', 'Series')
        print(f"✅ Added to download queue: {title}")


def cmd_sonarr_season(args):
    """Add a specific season."""
    client = create_sonarr_client()
    # First get the series ID
    series_info = client.get_series(int(args.tvdb_id))
    if isinstance(series_info, list) and series_info:
        series = series_info[0]
        series_id = series.get('id')
    else:
        print(f"Error: Series not found")
        return

    result = client.add_season(series_id, int(args.season))
    if "error" in result:
        print(f"Error: {result['error']}")
    else:
        title = series.get('title', 'Series')
        print(f"✅ Added season {args.season} for: {title}")


def cmd_sonarr_queue(args):
    """Show Sonarr download queue."""
    client = create_sonarr_client()
    queue = client.get_queue()
    if "error" in queue:
        print(f"Error: {queue['error']}")
        return
    records = queue.get("records", [])
    if not records:
        print("Queue is empty. 🎉")
        return
    print("\nDownload Queue:\n")
    for item in records[:10]:
        print(f"📥 {item.get('title', 'Unknown')}")
        print(f"   Status: {item.get('status', 'N/A')}")
        print(f"   Progress: {item.get('progress', 0):.0f}%")
        print()


def cmd_sonarr_wanted(args):
    """Show wanted/missing episodes."""
    client = create_sonarr_client()
    wanted = client.get_wanted()
    if "error" in wanted:
        print(f"Error: {wanted['error']}")
        return
    records = wanted.get("records", [])
    if not records:
        print("No wanted episodes! 🎉")
        return
    print("\nWanted Episodes:\n")
    for ep in records[:10]:
        print(f"📺 {ep.get('title', 'Unknown')}")
        print(f"   Episode: S{ep.get('seasonNumber', 0):02d}E{ep.get('episodeNumber', 0):02d}")
        print()


def cmd_sonarr_status(args):
    """Show Sonarr system status."""
    client = create_sonarr_client()
    status = client.test_connection()
    if "error" in status:
        print(f"Connection Error: {status['error']}")
    else:
        version = status.get('version', 'Unknown')
        print(f"✅ Sonarr connected")
        print(f"   Version: {version}")


def cmd_auto(args):
    """Auto-parse and execute natural language request."""
    parser = NLParser()
    movie_req, series_req, req_type = parser.parse(args.query)

    if req_type == "movie":
        client = create_radarr_client()
        print(f"\n🎬 Movie: {movie_req.title}")
        print(f"   Quality: {movie_req.quality}")
        print(f"   Language: {movie_req.language}")
        print()

        # Search for the movie
        results = client.search(movie_req.title)
        if not results:
            print(f"❌ Movie not found: {movie_req.title}")
            return

        movie = results[0]
        tmdb_id = movie.get('tmdbId')
        print(f"🎬 Found: {movie.get('title')} ({movie.get('year')})")
        print(f"   TMDB ID: {tmdb_id}")
        print()

        # Add to Radarr
        result = client.add(tmdb_id)
        if "error" in result:
            print(f"Error: {result['error']}")
        else:
            print(f"✅ Added to download queue!")

    else:
        client = create_sonarr_client()
        print(f"\n📺 Series: {series_req.title}")
        if series_req.season:
            print(f"   Season: {series_req.season}")
        if series_req.episode:
            print(f"   Episode: {series_req.episode}")
        print(f"   Quality: {series_req.quality}")
        print(f"   Language: {series_req.language}")
        print()

        # Search for the series
        results = client.search(series_req.title)
        if not results:
            print(f"❌ Series not found: {series_req.title}")
            return

        series = results[0]
        tvdb_id = series.get('tvdbId')
        print(f"📺 Found: {series.get('title')} ({series.get('year')})")
        print(f"   TVDB ID: {tvdb_id}")
        print()

        # Add to Sonarr
        result = client.add(tvdb_id)
        if "error" in result:
            print(f"Error: {result['error']}")
        else:
            print(f"✅ Added to download queue!")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Radarr and Sonarr CLI for OpenClaw",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Auto command
    auto_parser = subparsers.add_parser("auto", help="Auto-parse natural language")
    auto_parser.add_argument("query", help="Natural language query")
    auto_parser.set_defaults(func=cmd_auto)

    # Radarr commands
    radarr_parser = subparsers.add_parser("radarr", help="Radarr operations")
    radarr_sub = radarr_parser.add_subparsers(dest="radarr_command")

    radarr_search = radarr_sub.add_parser("search", help="Search for movies")
    radarr_search.add_argument("query", help="Search query")
    radarr_search.set_defaults(func=cmd_radarr_search)

    radarr_download = radarr_sub.add_parser("download", help="Download a movie")
    radarr_download.add_argument("tmdb_id", help="TMDB ID")
    radarr_download.set_defaults(func=cmd_radarr_download)

    radarr_queue = radarr_sub.add_parser("queue", help="Show download queue")
    radarr_queue.set_defaults(func=cmd_radarr_queue)

    radarr_wanted = radarr_sub.add_parser("wanted", help="Show wanted movies")
    radarr_wanted.set_defaults(func=cmd_radarr_wanted)

    radarr_status = radarr_sub.add_parser("status", help="Show Radarr status")
    radarr_status.set_defaults(func=cmd_radarr_status)

    # Sonarr commands
    sonarr_parser = subparsers.add_parser("sonarr", help="Sonarr operations")
    sonarr_sub = sonarr_parser.add_subparsers(dest="sonarr_command")

    sonarr_search = sonarr_sub.add_parser("search", help="Search for series")
    sonarr_search.add_argument("query", help="Search query")
    sonarr_search.set_defaults(func=cmd_sonarr_search)

    sonarr_download = sonarr_sub.add_parser("download", help="Download a series")
    sonarr_download.add_argument("tvdb_id", help="TVDB ID")
    sonarr_download.set_defaults(func=cmd_sonarr_download)

    sonarr_season = sonarr_sub.add_parser("season", help="Add a specific season")
    sonarr_season.add_argument("tvdb_id", help="TVDB ID")
    sonarr_season.add_argument("season", help="Season number")
    sonarr_season.set_defaults(func=cmd_sonarr_season)

    sonarr_queue = sonarr_sub.add_parser("queue", help="Show download queue")
    sonarr_queue.set_defaults(func=cmd_sonarr_queue)

    sonarr_wanted = sonarr_sub.add_parser("wanted", help="Show wanted episodes")
    sonarr_wanted.set_defaults(func=cmd_sonarr_wanted)

    sonarr_status = sonarr_sub.add_parser("status", help="Show Sonarr status")
    sonarr_status.set_defaults(func=cmd_sonarr_status)

    # Parse arguments
    args = parser.parse_args()

    # Execute command
    if hasattr(args, "func"):
        if args.command == "radarr":
            if args.radarr_command is None:
                radarr_parser.print_help()
            else:
                args.func(args)
        elif args.command == "sonarr":
            if args.sonarr_command is None:
                sonarr_parser.print_help()
            else:
                args.func(args)
        else:
            args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
