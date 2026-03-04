#!/usr/bin/env python3
"""
taste_profiler.py — Builds a structured taste profile from Apple Music API data.

Pulls from: recently played, heavy rotation, library, ratings, recommendations,
and Apple Music Replay / Music Summaries when available.

Usage:
  python3 taste_profiler.py [options]

Options:
  --storefront SF       Storefront code (default: auto-detect via API)
  --output PATH         Write JSON to file (default: stdout)
  --cache PATH          Cache file path for reuse
  --max-age HOURS       Re-generate if cache is older than N hours (default: 168 = 7 days)
  --skip-replay         Skip Replay/Music Summaries endpoints
  --verbose             Print progress to stderr

Requires: APPLE_MUSIC_DEV_TOKEN and APPLE_MUSIC_USER_TOKEN env vars.
"""

import sys

# Python version guard (also checked in _common, but be explicit for entry points)
if sys.version_info < (3, 9):
    sys.exit(
        f"ERROR: Python 3.9+ is required (you have "
        f"{sys.version_info.major}.{sys.version_info.minor}). Please upgrade."
    )

import argparse
import json
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from _common import call_api, check_token_expiry, get_storefront, require_env_tokens
from typing import Optional, Union

SCRIPT_DIR = Path(__file__).parent


def log(msg: str, verbose: bool = True):
    if verbose:
        print(f"  → {msg}", file=sys.stderr)


def load_cache(path: str, max_age_hours: int) -> Optional[dict]:
    """Load cached profile if it exists and is fresh enough."""
    try:
        p = Path(path)
        if not p.exists():
            return None
        age_hours = (time.time() - p.stat().st_mtime) / 3600
        if age_hours > max_age_hours:
            return None
        with open(p) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def save_cache(profile: dict, path: str):
    """Write profile to cache file with restrictive permissions."""
    import os as _os
    try:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        fd = _os.open(str(p), _os.O_WRONLY | _os.O_CREAT | _os.O_TRUNC, 0o600)
        with _os.fdopen(fd, "w") as f:
            json.dump(profile, f, indent=2)
    except OSError as e:
        print(f"WARN: Could not save cache: {e}", file=sys.stderr)


def detect_storefront() -> str:
    """Auto-detect user's storefront via API (with caching)."""
    return get_storefront()


def extract_genres(tracks: list[dict]) -> list[dict]:
    """Extract genre distribution from track data."""
    genre_counts: Counter = Counter()
    for track in tracks:
        attrs = track.get("attributes", {})
        for genre in attrs.get("genreNames", []):
            if genre.lower() != "music":  # filter out the generic "Music" genre
                genre_counts[genre] += 1
    total = sum(genre_counts.values()) or 1
    return [
        {"genre": g, "count": c, "weight": round(c / total, 3)}
        for g, c in genre_counts.most_common(20)
    ]


def extract_artists(tracks: list[dict]) -> list[dict]:
    """Extract artist frequency from tracks."""
    artist_data: dict[str, dict] = {}
    for track in tracks:
        attrs = track.get("attributes", {})
        name = attrs.get("artistName", "Unknown")
        if name not in artist_data:
            artist_data[name] = {"name": name, "count": 0, "ids": set()}
        artist_data[name]["count"] += 1
        # Try to get catalog artist ID from relationships
        rels = track.get("relationships", {})
        artists_rel = rels.get("artists", {}).get("data", [])
        for a in artists_rel:
            artist_data[name]["ids"].add(a.get("id", ""))

    total = sum(a["count"] for a in artist_data.values()) or 1
    result = []
    for a in sorted(artist_data.values(), key=lambda x: -x["count"]):
        ids = list(a["ids"] - {""})
        result.append({
            "name": a["name"],
            "id": ids[0] if ids else None,
            "play_weight": round(a["count"] / total, 3),
            "count": a["count"],
        })
    return result[:30]


def extract_eras(tracks: list[dict]) -> list[dict]:
    """Extract decade distribution from release dates."""
    decade_counts: Counter = Counter()
    for track in tracks:
        date_str = track.get("attributes", {}).get("releaseDate", "")
        if date_str and len(date_str) >= 4:
            try:
                year = int(date_str[:4])
                decade = f"{(year // 10) * 10}s"
                decade_counts[decade] += 1
            except ValueError:
                pass
    total = sum(decade_counts.values()) or 1
    return [
        {"decade": d, "count": c, "weight": round(c / total, 3)}
        for d, c in decade_counts.most_common(10)
    ]


def infer_energy_profile(genres: list[dict]) -> str:
    """Infer overall energy from genre distribution."""
    high_energy = {"Electronic", "Dance", "Hip-Hop/Rap", "Metal", "Punk", "Rock", "Pop"}
    low_energy = {"Ambient", "Classical", "Jazz", "Singer/Songwriter", "Folk", "New Age"}
    high_score = sum(g["weight"] for g in genres if g["genre"] in high_energy)
    low_score = sum(g["weight"] for g in genres if g["genre"] in low_energy)
    if high_score > low_score + 0.2:
        return "high-energy"
    elif low_score > high_score + 0.2:
        return "chill"
    return "balanced"


def compute_variety_score(artists: list[dict], tracks: list[dict]) -> float:
    """How diverse is the listening? 0=repetitive, 1=very varied."""
    if not tracks:
        return 0.5
    unique_artists = len(set(t.get("attributes", {}).get("artistName", "") for t in tracks))
    # Ratio of unique artists to total tracks
    ratio = unique_artists / len(tracks) if tracks else 0.5
    return round(min(ratio * 1.5, 1.0), 2)  # scale up slightly, cap at 1


def compute_mainstream_score(top_artists: list[dict], chart_data: Optional[dict]) -> float:
    """How mainstream is the taste? Compare artists against charts."""
    if not chart_data or not top_artists:
        return 0.5  # unknown
    chart_artist_names = set()
    for section in chart_data.get("results", {}).values():
        if isinstance(section, list):
            for chart in section:
                for item in chart.get("data", []):
                    name = item.get("attributes", {}).get("artistName", "")
                    if name:
                        chart_artist_names.add(name.lower())
    if not chart_artist_names:
        return 0.5
    user_names = {a["name"].lower() for a in top_artists[:15]}
    overlap = len(user_names & chart_artist_names)
    return round(overlap / len(user_names), 2) if user_names else 0.5


def extract_ratings(ratings_data: Optional[dict]) -> tuple[list[str], list[str]]:
    """Extract loved and disliked song IDs from ratings."""
    loved_ids = []
    disliked_song_ids = []
    if not ratings_data or "data" not in ratings_data:
        return loved_ids, disliked_song_ids
    for item in ratings_data.get("data", []):
        attrs = item.get("attributes", {})
        value = attrs.get("value", 0)
        rid = item.get("id", "")
        if value == 1 and rid:
            loved_ids.append(rid)
        elif value == -1 and rid:
            disliked_song_ids.append(rid)
    return loved_ids, disliked_song_ids


def extract_replay_highlights(summary_data: Optional[dict], milestones_data: Optional[dict]) -> dict:
    """Extract Replay / Music Summaries highlights."""
    highlights = {
        "available": False,
        "top_artist_all_time": None,
        "total_minutes_latest_year": None,
        "genre_evolution": [],
    }
    if not summary_data or "data" not in summary_data:
        return highlights

    highlights["available"] = True
    summaries = summary_data.get("data", [])
    for s in summaries:
        attrs = s.get("attributes", {})
        year = attrs.get("year", "")
        # Extract top genre from summary
        top_genres_list = attrs.get("topGenres", [])
        top_genre = top_genres_list[0].get("name") if top_genres_list else None
        # Fall back to genreNames if topGenres not available
        if not top_genre:
            genre_names = attrs.get("genreNames", [])
            top_genre = genre_names[0] if genre_names else None
        top_artists = attrs.get("topArtists", [])
        if top_artists:
            highlights["top_artist_all_time"] = top_artists[0].get("name")
        listen_time = attrs.get("listenTimeInMinutes")
        if listen_time:
            highlights["total_minutes_latest_year"] = listen_time
        if year and top_genre:
            highlights["genre_evolution"].append({"year": str(year), "top_genre": top_genre})

    if milestones_data and "data" in milestones_data:
        for m in milestones_data["data"]:
            attrs = m.get("attributes", {})
            listen_time = attrs.get("listenTimeInMinutes")
            if listen_time and listen_time > (highlights.get("total_minutes_latest_year") or 0):
                highlights["total_minutes_latest_year"] = listen_time

    return highlights


def build_profile(args) -> dict:
    """Main profile builder. Fetches all data and assembles the taste DNA."""
    require_env_tokens()
    verbose = args.verbose

    # Check token expiry on startup
    token_status = check_token_expiry()
    if token_status and token_status["warning"]:
        print(token_status["message"], file=sys.stderr)
        if token_status["expired"]:
            sys.exit(1)

    print("🎧 Building your Taste DNA profile...", file=sys.stderr)

    # Detect storefront (with caching)
    log("Detecting storefront...", verbose)
    sf = get_storefront(args.storefront)
    log(f"Storefront: {sf}", verbose)

    # ── Fetch all data sources ────────────────────────────────────
    log("Fetching recently played tracks...", verbose)
    recent_tracks = call_api("recent-tracks") or []
    log(f"Got {len(recent_tracks)} recent tracks", verbose)

    log("Fetching heavy rotation...", verbose)
    heavy_rotation = call_api("heavy-rotation")
    hr_count = len((heavy_rotation or {}).get("data", []))
    log(f"Got {hr_count} heavy rotation items", verbose)

    log("Fetching library artists...", verbose)
    lib_artists = call_api("library-artists", "100")
    la_count = len((lib_artists or {}).get("data", []))
    log(f"Got {la_count} library artists", verbose)

    log("Fetching library songs (sample)...", verbose)
    lib_songs = call_api("library-songs", "100")
    ls_count = len((lib_songs or {}).get("data", []))
    log(f"Got {ls_count} library songs", verbose)

    log("Fetching ratings...", verbose)
    ratings = call_api("ratings", "songs")

    log("Fetching recommendations...", verbose)
    recs = call_api("recommendations")
    rec_count = len((recs or {}).get("data", []))
    log(f"Got {rec_count} recommendation groups", verbose)

    # Replay data
    replay_summary = None
    replay_milestones = None
    if not args.skip_replay:
        log("Fetching Replay / Music Summaries...", verbose)
        replay_summary = call_api("replay-summary")
        replay_milestones = call_api("replay-milestones")
        if replay_summary and "data" in replay_summary:
            log("Replay data available!", verbose)
        else:
            log("Replay data not available (may not be supported)", verbose)

    # Chart data for mainstream scoring
    log("Fetching charts for mainstream scoring...", verbose)
    chart_data = call_api("charts", sf)

    # ── Analyze ───────────────────────────────────────────────────
    log("Analyzing patterns...", verbose)

    # Combine all available track data for analysis
    all_tracks = list(recent_tracks)
    if lib_songs and "data" in lib_songs:
        all_tracks.extend(lib_songs["data"])

    # Extract tracks from heavy rotation (albums/playlists contain nested tracks)
    if heavy_rotation and "data" in heavy_rotation:
        for item in heavy_rotation["data"]:
            rels = item.get("relationships", {})
            for rel_key in ("tracks", "songs"):
                rel_tracks = rels.get(rel_key, {}).get("data", [])
                all_tracks.extend(rel_tracks)
            # If no nested tracks, use the item itself (it has artistName, genreNames, etc.)
            if not any(rels.get(k, {}).get("data") for k in ("tracks", "songs")):
                all_tracks.append(item)

    # Extract tracks from recommendation groups
    if recs and "data" in recs:
        for group in recs["data"]:
            rels = group.get("relationships", {})
            for rel_key in ("contents", "recommendations"):
                for container in rels.get(rel_key, {}).get("data", []):
                    container_rels = container.get("relationships", {})
                    for track_key in ("tracks", "songs"):
                        rec_tracks = container_rels.get(track_key, {}).get("data", [])
                        all_tracks.extend(rec_tracks)

    # Extract library song IDs (catalog IDs where available)
    library_song_ids = []
    if lib_songs and "data" in lib_songs:
        for song in lib_songs["data"]:
            # Prefer catalog ID from the include=catalog relationship
            catalog_rel = song.get("relationships", {}).get("catalog", {}).get("data", [])
            if catalog_rel:
                cat_id = catalog_rel[0].get("id")
                if cat_id:
                    library_song_ids.append(cat_id)
                    continue
            # Fall back to the song's own ID
            sid = song.get("id", "")
            if sid:
                library_song_ids.append(sid)

    genres = extract_genres(all_tracks)

    if not all_tracks:
        print("ERROR: No track data retrieved from API. Check your tokens and network.", file=sys.stderr)
        print("  Run: scripts/verify_setup.sh  to diagnose issues.", file=sys.stderr)
        sys.exit(1)
    artists = extract_artists(all_tracks)
    eras = extract_eras(all_tracks)
    energy = infer_energy_profile(genres)
    variety = compute_variety_score(artists, all_tracks)
    mainstream = compute_mainstream_score(artists, chart_data)
    loved, disliked_songs = extract_ratings(ratings)
    replay = extract_replay_highlights(replay_summary, replay_milestones)

    # Listening velocity — compare library size to recent diversity
    velocity = "moderate"
    if len(recent_tracks) > 0:
        recent_unique = len(set(
            t.get("attributes", {}).get("name", "") for t in recent_tracks
        ))
        if recent_unique > 40:
            velocity = "high"
        elif recent_unique < 15:
            velocity = "low"

    # ── Assemble profile ──────────────────────────────────────────
    profile = {
        "top_artists": artists[:20],
        "genre_distribution": genres,
        "era_distribution": eras,
        "energy_profile": energy,
        "variety_score": variety,
        "mainstream_score": mainstream,
        "listening_velocity": velocity,
        "loved_track_ids": loved,
        "disliked_song_ids": disliked_songs,
        "library_song_ids": library_song_ids,
        "replay_highlights": replay,
        "data_summary": {
            "recent_tracks": len(recent_tracks),
            "library_artists": la_count,
            "library_songs": ls_count,
            "library_song_ids_extracted": len(library_song_ids),
            "heavy_rotation_items": hr_count,
            "recommendation_groups": rec_count,
            "loved_count": len(loved),
            "disliked_count": len(disliked_songs),
        },
        "storefront": sf,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }

    print("\n✅ Taste DNA profile complete.", file=sys.stderr)
    return profile


def main():
    parser = argparse.ArgumentParser(description="Build Apple Music taste profile")
    parser.add_argument("--storefront", default="auto", help="Storefront code (default: auto-detect)")
    parser.add_argument("--output", default=None, help="Output file path (default: stdout)")
    parser.add_argument("--cache", default=None, help="Cache file path")
    parser.add_argument("--max-age", type=int, default=168, help="Max cache age in hours (default: 168)")
    parser.add_argument("--skip-replay", action="store_true", help="Skip Replay endpoints")
    parser.add_argument("--verbose", action="store_true", help="Verbose output to stderr")
    args = parser.parse_args()

    # Check cache first
    if args.cache:
        cached = load_cache(args.cache, args.max_age)
        if cached:
            print("Using cached taste profile.", file=sys.stderr)
            output = json.dumps(cached, indent=2)
            if args.output:
                Path(args.output).write_text(output)
            else:
                print(output)
            return

    # Build fresh profile
    profile = build_profile(args)
    output = json.dumps(profile, indent=2)

    # Save cache
    if args.cache:
        save_cache(profile, args.cache)
        print(f"Cached to {args.cache}", file=sys.stderr)

    # Output
    if args.output:
        import os as _os
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        fd = _os.open(str(args.output), _os.O_WRONLY | _os.O_CREAT | _os.O_TRUNC, 0o600)
        with _os.fdopen(fd, "w") as f:
            f.write(output)
        print(f"Profile written to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
