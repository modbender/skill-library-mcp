#!/usr/bin/env python3
"""
catalog_explorer.py — Album Deep Dive, Artist Rabbit Hole, Catalog Gap Analysis.

Subcommands:
  gap-analysis     Find albums you're missing from artists you love
  album-dive       Deep dive into a specific album
  rabbit-hole      Interactive artist-to-artist exploration chain

Usage:
  python3 catalog_explorer.py gap-analysis <profile.json> <storefront>
  python3 catalog_explorer.py album-dive <storefront> <album_name_or_id> [--artist <name>]
  python3 catalog_explorer.py rabbit-hole <profile.json> <storefront> <start_artist>

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
from pathlib import Path

from _common import call_api, load_profile, search_artist, search_album, get_album_tracks
from typing import Optional, Union

SCRIPT_DIR = Path(__file__).parent


# ── Catalog Gap Analysis ─────────────────────────────────────────

def cmd_gap_analysis(profile: dict, sf: str) -> dict:
    """Find albums the user is missing from their favorite artists."""
    top_artists = profile.get("top_artists", [])[:10]
    library_song_ids = set(profile.get("library_song_ids", []))

    results = []
    for i, artist_entry in enumerate(top_artists):
        artist_name = artist_entry.get("name")
        if not artist_name:
            continue
        print(f"  Checking {artist_name} ({i+1}/{len(top_artists)})...", file=sys.stderr)
        artist_id = artist_entry.get("id")

        if not artist_id:
            found = search_artist(sf, artist_name)
            if found:
                artist_id = found.get("id")
            else:
                continue

        # Fetch all albums
        albums_data = call_api("artist-albums", sf, artist_id)
        if not albums_data or "data" not in albums_data:
            continue

        albums = albums_data["data"]
        artist_result = {
            "artist": artist_name,
            "artist_id": artist_id,
            "total_albums": len(albums),
            "albums_heard": [],
            "albums_missing": [],
        }

        for album in albums:
            album_attrs = album.get("attributes", {})
            album_name = album_attrs.get("name", "Unknown")
            album_id = album.get("id", "")
            track_count = album_attrs.get("trackCount", 0)
            release_date = album_attrs.get("releaseDate", "")
            is_single = album_attrs.get("isSingle", False)

            # Skip singles for gap analysis
            if is_single:
                continue

            # Check if user has any tracks from this album
            album_tracks = get_album_tracks(sf, album_id)

            owned_count = 0
            for track in album_tracks:
                if track.get("id", "") in library_song_ids:
                    owned_count += 1

            album_info = {
                "name": album_name,
                "id": album_id,
                "track_count": track_count,
                "release_date": release_date,
                "tracks_in_library": owned_count,
            }

            if owned_count > 0:
                album_info["coverage_pct"] = int((owned_count / max(track_count, 1)) * 100)
                artist_result["albums_heard"].append(album_info)
            else:
                artist_result["albums_missing"].append(album_info)

        # Sort missing by release date (newest first for recommendations)
        artist_result["albums_missing"].sort(
            key=lambda a: a.get("release_date", ""), reverse=True
        )
        artist_result["missing_count"] = len(artist_result["albums_missing"])
        artist_result["heard_count"] = len(artist_result["albums_heard"])

        results.append(artist_result)

    # Summary
    total_missing = sum(r["missing_count"] for r in results)
    return {
        "artists_analyzed": len(results),
        "total_albums_missing": total_missing,
        "results": results,
    }


# ── Album Deep Dive ──────────────────────────────────────────────

def cmd_album_dive(sf: str, album_query: str, artist_hint: Optional[str] = None) -> dict:
    """Deep dive into a specific album."""
    query = f"{album_query} {artist_hint}" if artist_hint else album_query
    album = search_album(sf, query)
    if not album:
        return {"error": f"Could not find album: {album_query}"}

    album_id = album.get("id", "")
    attrs = album.get("attributes", {})

    # Fetch full album with tracks
    track_data = get_album_tracks(sf, album_id)
    tracks = []
    for t in track_data:
        ta = t.get("attributes", {})
        tracks.append({
            "number": ta.get("trackNumber"),
            "name": ta.get("name", "Unknown"),
            "duration_ms": ta.get("durationInMillis"),
            "id": t.get("id"),
            "artist": ta.get("artistName", ""),
            "has_features": " feat" in ta.get("name", "").lower() or
                           "&" in ta.get("artistName", ""),
        })

    # Get artist's top songs to identify which are "hits" vs "deep cuts"
    artist_name = attrs.get("artistName", "")
    artist = search_artist(sf, artist_name) if artist_name else None
    top_song_names = set()
    if artist:
        top_data = call_api("artist-top", sf, artist["id"])
        if top_data and "data" in top_data:
            for ad in top_data["data"]:
                views = ad.get("views", {})
                top_songs = views.get("top-songs", {}).get("data", [])
                for ts in top_songs:
                    name = ts.get("attributes", {}).get("name", "")
                    if name:
                        top_song_names.add(name.lower())

    # Classify tracks
    for t in tracks:
        t["is_single"] = t["name"].lower() in top_song_names
        t["is_deep_cut"] = not t["is_single"]

    # Count albums by this artist to place this in discography
    discog_position = None
    if artist:
        albums_data = call_api("artist-albums", sf, artist["id"])
        if albums_data and "data" in albums_data:
            all_albums = sorted(
                albums_data["data"],
                key=lambda a: a.get("attributes", {}).get("releaseDate", "")
            )
            for i, a in enumerate(all_albums):
                if a.get("id") == album_id:
                    discog_position = {
                        "position": i + 1,
                        "total": len(all_albums),
                        "label": f"Album {i+1} of {len(all_albums)}",
                    }
                    break

    total_ms = sum(t.get("duration_ms", 0) for t in tracks)
    deep_cuts = [t for t in tracks if t.get("is_deep_cut")]

    return {
        "album": attrs.get("name", album_query),
        "artist": artist_name,
        "album_id": album_id,
        "release_date": attrs.get("releaseDate", ""),
        "genre": attrs.get("genreNames", []),
        "track_count": len(tracks),
        "total_duration_min": round(total_ms / 60000, 1) if total_ms else None,
        "tracks": tracks,
        "deep_cut_count": len(deep_cuts),
        "recommended_deep_cuts": [t["name"] for t in deep_cuts[:5]],
        "discography_position": discog_position,
    }


# ── Artist Rabbit Hole ───────────────────────────────────────────

def cmd_rabbit_hole(profile: dict, sf: str, start_artist: str, depth: int = 4) -> dict:
    """Map connections outward from a starting artist."""
    visited = set()
    chain = []
    current_query = start_artist
    user_genres = {g["genre"].lower() for g in profile.get("genre_distribution", [])[:10]}
    library_artists = {a["name"].lower() for a in profile.get("top_artists", [])}

    for step in range(depth):
        print(f"  Hop {step+1}/{depth}: searching '{current_query}'...", file=sys.stderr)
        artist = search_artist(sf, current_query)
        if not artist:
            break

        artist_name = artist.get("attributes", {}).get("name", current_query)
        artist_id = artist.get("id", "")

        if artist_id in visited:
            break
        visited.add(artist_id)

        # Get top songs for this artist
        top_data = call_api("artist-top", sf, artist_id)
        top_songs = []
        if top_data and "data" in top_data:
            for ad in top_data["data"]:
                views = ad.get("views", {})
                for ts in views.get("top-songs", {}).get("data", [])[:3]:
                    ta = ts.get("attributes", {})
                    top_songs.append({
                        "name": ta.get("name", ""),
                        "id": ts.get("id", ""),
                    })

        # Determine familiarity
        in_library = artist_name.lower() in library_artists
        artist_genres = [g for g in artist.get("attributes", {}).get("genreNames", [])
                         if g.lower() != "music"]
        genre_overlap = bool(set(g.lower() for g in artist_genres) & user_genres)

        if step == 0:
            zone = "origin"
        elif in_library:
            zone = "familiar"
        elif genre_overlap:
            zone = "adjacent"
        else:
            zone = "frontier"

        chain.append({
            "step": step + 1,
            "artist": artist_name,
            "artist_id": artist_id,
            "genres": artist_genres,
            "zone": zone,
            "in_library": in_library,
            "sample_tracks": top_songs,
        })

        # Find the next artist by searching related terms
        if artist_genres:
            next_query = f"{artist_name} {artist_genres[0]}"
        else:
            next_query = artist_name

        search_results = call_api("search", sf, next_query, "artists")
        if search_results:
            candidates = search_results.get("results", {}).get("artists", {}).get("data", [])
            next_artist = None
            for c in candidates:
                cid = c.get("id", "")
                if cid not in visited:
                    next_artist = c
                    break
            if next_artist:
                current_query = next_artist.get("attributes", {}).get("name", "")
            else:
                break
        else:
            break

    # Collect all sample tracks for a potential playlist
    all_tracks = []
    for node in chain:
        for t in node.get("sample_tracks", []):
            if t.get("id"):
                all_tracks.append({
                    "id": t["id"],
                    "name": t["name"],
                    "artist": node["artist"],
                    "zone": node["zone"],
                })

    return {
        "start_artist": start_artist,
        "chain_length": len(chain),
        "chain": chain,
        "playlist_tracks": all_tracks,
        "zones_reached": list(set(n["zone"] for n in chain)),
    }


# ── Main ─────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Catalog Explorer")
    sub = parser.add_subparsers(dest="command", required=True)

    p_gap = sub.add_parser("gap-analysis", help="Find missing albums from favorite artists")
    p_gap.add_argument("profile", help="Path to taste profile JSON")
    p_gap.add_argument("storefront", help="Storefront code (e.g., us)")

    p_album = sub.add_parser("album-dive", help="Deep dive into an album")
    p_album.add_argument("storefront", help="Storefront code")
    p_album.add_argument("album", nargs="+", help="Album name or search query")
    p_album.add_argument("--artist", default=None, help="Artist name hint")

    p_rh = sub.add_parser("rabbit-hole", help="Artist-to-artist discovery chain")
    p_rh.add_argument("profile", help="Path to taste profile JSON")
    p_rh.add_argument("storefront", help="Storefront code")
    p_rh.add_argument("artist", nargs="+", help="Starting artist name")
    p_rh.add_argument("--depth", type=int, default=4, help="Chain depth (default: 4)")

    args = parser.parse_args()

    if args.command == "gap-analysis":
        profile = load_profile(args.profile)
        result = cmd_gap_analysis(profile, args.storefront)
    elif args.command == "album-dive":
        query = " ".join(args.album)
        result = cmd_album_dive(args.storefront, query, args.artist)
    elif args.command == "rabbit-hole":
        profile = load_profile(args.profile)
        artist = " ".join(args.artist)
        result = cmd_rabbit_hole(profile, args.storefront, artist, args.depth)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
