#!/usr/bin/env python3
"""
playlist_health.py — Playlist Health Check & Maintenance.

Subcommands:
  check     Scan playlists for removed tracks, duplicates, and staleness
  fix       Remove duplicates and replaced removed tracks (with --auto or interactive)

Usage:
  python3 playlist_health.py check <playlist_id|all> --profile <profile.json>
  python3 playlist_health.py fix <playlist_id> --profile <profile.json> [--auto]

Requires: APPLE_MUSIC_DEV_TOKEN and APPLE_MUSIC_USER_TOKEN env vars.
"""

import sys
if sys.version_info < (3, 9):
    sys.exit(
        f"ERROR: Python 3.9+ is required (you have "
        f"{sys.version_info.major}.{sys.version_info.minor}). Please upgrade."
    )

import argparse
import json
from collections import Counter
from pathlib import Path

from _common import call_api, load_config, load_profile, require_env_tokens
from typing import Optional, Union

SCRIPT_DIR = Path(__file__).parent


def check_playlist(playlist_id: str, sf: str) -> dict:
    """Check a single playlist for health issues.

    Returns a report dict with removed, duplicates, and track count.
    """
    tracks_data = call_api("playlist-tracks", playlist_id)
    if not tracks_data or "data" not in tracks_data:
        return {
            "playlist_id": playlist_id,
            "error": "Could not fetch playlist tracks",
            "total_tracks": 0,
            "removed": [],
            "duplicates": [],
        }

    tracks = tracks_data["data"]
    total_tracks = len(tracks)

    # Track duplicates by catalog ID
    id_counts: Counter = Counter()
    track_ids = []
    for track in tracks:
        # Try catalog relationship first, fall back to track ID
        catalog_rel = track.get("relationships", {}).get("catalog", {}).get("data", [])
        if catalog_rel:
            tid = catalog_rel[0].get("id", "")
        else:
            tid = track.get("id", "")
        if tid:
            id_counts[tid] += 1
            track_ids.append(tid)

    duplicates = [
        {"id": tid, "count": count}
        for tid, count in id_counts.items()
        if count > 1
    ]

    # Check for removed tracks by verifying against catalog
    removed = []
    checked = set()
    for track in tracks:
        attrs = track.get("attributes", {})
        name = attrs.get("name", "Unknown")
        artist = attrs.get("artistName", "Unknown")

        # Get catalog ID
        catalog_rel = track.get("relationships", {}).get("catalog", {}).get("data", [])
        if catalog_rel:
            cat_id = catalog_rel[0].get("id", "")
        else:
            cat_id = track.get("id", "")

        if not cat_id or cat_id in checked:
            continue
        checked.add(cat_id)

        # Verify track exists in catalog
        detail = call_api("song-detail", sf, cat_id)
        if not detail or "data" not in detail or not detail["data"]:
            removed.append({
                "id": cat_id,
                "name": name,
                "artist": artist,
            })

    return {
        "playlist_id": playlist_id,
        "total_tracks": total_tracks,
        "removed": removed,
        "removed_count": len(removed),
        "duplicates": duplicates,
        "duplicate_count": len(duplicates),
        "healthy": len(removed) == 0 and len(duplicates) == 0,
    }


def find_replacement(sf: str, name: str, artist: str) -> Optional[dict]:
    """Search catalog for a replacement track (same song, different catalog ID)."""
    query = f"{name} {artist}"
    result = call_api("search", sf, query, "songs")
    if not result:
        return None
    songs = result.get("results", {}).get("songs", {}).get("data", [])
    for song in songs:
        attrs = song.get("attributes", {})
        # Match by artist name (case-insensitive)
        if attrs.get("artistName", "").lower() == artist.lower():
            return {
                "id": song.get("id", ""),
                "name": attrs.get("name", ""),
                "artist": attrs.get("artistName", ""),
            }
    # If exact artist match not found, return first result as suggestion
    if songs:
        attrs = songs[0].get("attributes", {})
        return {
            "id": songs[0].get("id", ""),
            "name": attrs.get("name", ""),
            "artist": attrs.get("artistName", ""),
            "approximate": True,
        }
    return None


def cmd_check(args) -> dict:
    """Run health check on one or all playlists."""
    require_env_tokens()
    config = load_config()
    sf = args.storefront or config.get("default_storefront", "us")

    if args.playlist_id == "all":
        # Fetch all library playlists
        playlists_data = call_api("library-playlists", "100")
        if not playlists_data or "data" not in playlists_data:
            return {"error": "Could not fetch library playlists", "results": []}

        results = []
        playlists = playlists_data["data"]
        for i, pl in enumerate(playlists):
            pid = pl.get("id", "")
            name = pl.get("attributes", {}).get("name", "Unknown")
            print(f"  Checking '{name}' ({i+1}/{len(playlists)})...", file=sys.stderr)
            report = check_playlist(pid, sf)
            report["name"] = name
            results.append(report)

        total_issues = sum(r["removed_count"] + r["duplicate_count"] for r in results)
        return {
            "playlists_checked": len(results),
            "total_issues": total_issues,
            "results": results,
        }
    else:
        print(f"  Checking playlist {args.playlist_id}...", file=sys.stderr)
        return check_playlist(args.playlist_id, sf)


def cmd_fix(args) -> dict:
    """Fix health issues in a playlist."""
    require_env_tokens()
    config = load_config()
    sf = args.storefront or config.get("default_storefront", "us")

    # First run a check
    print(f"  Analyzing playlist {args.playlist_id}...", file=sys.stderr)
    report = check_playlist(args.playlist_id, sf)

    if report.get("error"):
        return report

    actions_taken = []

    # Handle duplicates — remove extra copies
    if report["duplicates"]:
        for dup in report["duplicates"]:
            extras = dup["count"] - 1
            if args.auto:
                print(f"  Removing {extras} duplicate(s) of {dup['id']}...", file=sys.stderr)
                # Write IDs to remove
                import tempfile
                import subprocess
                ids_to_remove = [dup["id"]] * extras
                with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
                    f.write("\n".join(ids_to_remove))
                    ids_file = f.name
                try:
                    subprocess.run(
                        [str(SCRIPT_DIR / "build_playlist.sh"), "remove",
                         args.playlist_id, ids_file],
                        capture_output=True, text=True, timeout=30,
                    )
                    actions_taken.append(f"Removed {extras} duplicate(s) of {dup['id']}")
                finally:
                    Path(ids_file).unlink(missing_ok=True)
            else:
                actions_taken.append(
                    f"WOULD remove {extras} duplicate(s) of {dup['id']} (use --auto to apply)"
                )

    # Handle removed tracks — find replacements
    replacements = []
    if report["removed"]:
        for track in report["removed"]:
            replacement = find_replacement(sf, track["name"], track["artist"])
            entry = {
                "original": track,
                "replacement": replacement,
            }
            replacements.append(entry)

            if replacement and args.auto:
                print(
                    f"  Replacing '{track['name']}' with '{replacement['name']}'...",
                    file=sys.stderr,
                )
                # Remove old, add new
                import tempfile
                import subprocess

                # Add replacement
                with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
                    f.write(replacement["id"])
                    ids_file = f.name
                try:
                    subprocess.run(
                        [str(SCRIPT_DIR / "build_playlist.sh"), "refresh",
                         args.playlist_id, ids_file],
                        capture_output=True, text=True, timeout=30,
                    )
                    actions_taken.append(
                        f"Added replacement: '{replacement['name']}' by {replacement['artist']}"
                    )
                finally:
                    Path(ids_file).unlink(missing_ok=True)
            elif replacement:
                actions_taken.append(
                    f"WOULD replace '{track['name']}' with '{replacement['name']}' "
                    f"by {replacement['artist']} (use --auto)"
                )
            else:
                actions_taken.append(
                    f"No replacement found for '{track['name']}' by {track['artist']}"
                )

    return {
        "playlist_id": args.playlist_id,
        "issues_found": report["removed_count"] + report["duplicate_count"],
        "actions_taken": actions_taken,
        "replacements": replacements,
        "auto_applied": args.auto,
    }


def main():
    parser = argparse.ArgumentParser(description="Playlist Health Check")
    sub = parser.add_subparsers(dest="command", required=True)

    p_check = sub.add_parser("check", help="Scan for playlist issues")
    p_check.add_argument("playlist_id", help="Playlist library ID, or 'all'")
    p_check.add_argument("--profile", default=None, help="Path to taste profile JSON")
    p_check.add_argument("--storefront", default=None, help="Storefront code")

    p_fix = sub.add_parser("fix", help="Fix playlist issues")
    p_fix.add_argument("playlist_id", help="Playlist library ID")
    p_fix.add_argument("--profile", default=None, help="Path to taste profile JSON")
    p_fix.add_argument("--storefront", default=None, help="Storefront code")
    p_fix.add_argument("--auto", action="store_true",
                       help="Automatically apply fixes without confirmation")

    args = parser.parse_args()

    if args.command == "check":
        result = cmd_check(args)
    elif args.command == "fix":
        result = cmd_fix(args)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
