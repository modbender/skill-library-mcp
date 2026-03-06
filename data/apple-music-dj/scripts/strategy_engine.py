#!/usr/bin/env python3
"""
strategy_engine.py — Playlist Strategy Engine.

Implements the 5 core playlist strategies from references/playlist-strategies.md
and orchestrates candidate sourcing, scoring, sequencing, and playlist creation.

Strategies:
  deep-cuts       Hidden gems from artists you love
  mood            Mood/Activity-matched playlist (requires --mood)
  trend           Trending tracks filtered through your taste
  constellation   Gradual discovery from familiar to frontier
  refresh         Refresh an existing playlist (requires --playlist-id)

Usage:
  python3 strategy_engine.py --strategy deep-cuts --profile <path> --storefront <sf>
  python3 strategy_engine.py --strategy mood --mood workout --profile <path> --storefront <sf>
  python3 strategy_engine.py --strategy trend --profile <path> --storefront <sf>
  python3 strategy_engine.py --strategy constellation --profile <path> --storefront <sf>
  python3 strategy_engine.py --strategy refresh --playlist-id <id> --profile <path> --storefront <sf>

Common options:
  --name NAME         Custom playlist name (auto-generated if omitted)
  --size N            Target track count (default: from config or 30)
  --create            Actually create the playlist in Apple Music
  --output PATH       Write playlist JSON to file

Requires: APPLE_MUSIC_DEV_TOKEN and APPLE_MUSIC_USER_TOKEN env vars.
"""

import sys

# Python version guard
if sys.version_info < (3, 9):
    sys.exit(
        f"ERROR: Python 3.9+ is required (you have "
        f"{sys.version_info.major}.{sys.version_info.minor}). Please upgrade."
    )

import argparse
import json
import random
import subprocess
import tempfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Union

from _common import (
    call_api,
    filter_generic_genres,
    get_album_tracks,
    get_storefront,
    load_config,
    load_profile,
    require_env_tokens,
    search_artist,
)

SCRIPT_DIR = Path(__file__).parent


# ── Mood/Activity Mapping ────────────────────────────────────────

MOOD_MAP = {
    "workout": {
        "energy": "high", "genres": ["Electronic", "Hip-Hop/Rap", "Pop", "Rock", "Dance"],
        "description": "High-energy tracks to keep you moving.",
    },
    "focus": {
        "energy": "low-med", "genres": ["Ambient", "Classical", "Electronic", "Jazz"],
        "description": "Steady, minimal tracks for deep focus.",
    },
    "chill": {
        "energy": "low", "genres": ["Folk", "Jazz", "Ambient", "Indie Pop", "Singer/Songwriter"],
        "description": "Warm, relaxed vibes for unwinding.",
    },
    "party": {
        "energy": "high", "genres": ["Pop", "Dance", "Hip-Hop/Rap", "Funk", "R&B/Soul"],
        "description": "Singalongs and crowd-pleasers.",
    },
    "drive": {
        "energy": "med-high", "genres": ["Rock", "Indie", "Alternative", "Pop"],
        "description": "Confident, road-trip anthems.",
    },
    "sleep": {
        "energy": "very-low", "genres": ["Ambient", "Classical", "New Age"],
        "description": "Progressively quieter and slower.",
    },
    "cooking": {
        "energy": "medium", "genres": ["Jazz", "R&B/Soul", "Bossa Nova", "Indie Pop"],
        "description": "Warm, soulful backdrop for the kitchen.",
    },
    "morning": {
        "energy": "medium", "genres": ["Indie Pop", "Folk", "Acoustic"],
        "description": "Gentle and uplifting to start your day.",
    },
    "sad": {
        "energy": "low", "genres": ["Singer/Songwriter", "Indie", "Classical", "Folk"],
        "description": "Emotional, raw tracks for reflective moments.",
    },
    "anger": {
        "energy": "very-high", "genres": ["Metal", "Punk", "Rock"],
        "description": "Aggressive catharsis.",
    },
}


# ── Genre Adjacency (imported concept from compatibility.py) ─────

GENRE_ADJACENCY = {
    "rock_family": {"Rock", "Alternative", "Indie", "Punk", "Metal", "Grunge"},
    "electronic_family": {"Electronic", "Dance", "House", "Techno", "Ambient", "IDM"},
    "hiphop_family": {"Hip-Hop/Rap", "R&B/Soul", "Funk"},
    "folk_family": {"Folk", "Singer/Songwriter", "Country", "Americana", "Bluegrass"},
    "jazz_family": {"Jazz", "Blues", "Bossa Nova", "Soul"},
    "classical_family": {"Classical", "Soundtrack", "New Age"},
    "pop_family": {"Pop", "Synth Pop", "Indie Pop", "K-Pop", "J-Pop"},
}


def genre_proximity(genre_a: str, genre_b: str) -> float:
    """Score genre proximity: 1.0 exact, 0.5 same family, 0.0 different."""
    if genre_a.lower() == genre_b.lower():
        return 1.0
    for family in GENRE_ADJACENCY.values():
        lower = {g.lower() for g in family}
        if genre_a.lower() in lower and genre_b.lower() in lower:
            return 0.5
    return 0.0


def best_genre_match(track_genres: list[str], target_genres: list[str]) -> float:
    """Best proximity score between any track genre and any target genre."""
    best = 0.0
    for tg in track_genres:
        for target in target_genres:
            best = max(best, genre_proximity(tg, target))
    return best


# ── Sequencing ───────────────────────────────────────────────────

def sequence_tracks(tracks: list[dict], max_same_artist: int = 5) -> list[dict]:
    """Reorder tracks to follow the arc pattern and enforce spacing rules.

    Rules:
    - No artist repeat within max_same_artist tracks
    - Max 2 songs from same album
    - Builds a gentle arc: familiar opener → build → core → wind down
    """
    if len(tracks) <= 3:
        return tracks

    # Enforce album cap: max 2 per album
    album_counts: Counter = Counter()
    filtered = []
    for t in tracks:
        album = t.get("album", "")
        if album and album_counts[album] >= 2:
            continue
        album_counts[album] += 1
        filtered.append(t)

    # Greedy scheduling with artist spacing
    result = []
    remaining = list(filtered)
    recent_artists: list[str] = []

    while remaining:
        placed = False
        for i, track in enumerate(remaining):
            artist = track.get("artist", "")
            if artist not in recent_artists[-max_same_artist:]:
                result.append(remaining.pop(i))
                recent_artists.append(artist)
                placed = True
                break
        if not placed:
            # Can't satisfy spacing — just append next
            result.append(remaining.pop(0))
            recent_artists.append(result[-1].get("artist", ""))

    return result


# ── Strategy: Deep Cuts ──────────────────────────────────────────

def strategy_deep_cuts(profile: dict, sf: str, target_size: int = 30) -> list[dict]:
    """Hidden gems from artists the user already loves."""
    top_artists = profile.get("top_artists", [])[:15]
    library_ids = set(profile.get("library_song_ids", []))
    disliked = set(profile.get("disliked_song_ids", []))
    candidates = []

    for i, artist in enumerate(top_artists):
        artist_id = artist.get("id")
        artist_name = artist.get("name", "")
        if not artist_id:
            continue
        print(f"  [{i+1}/{len(top_artists)}] Scanning {artist_name}...", file=sys.stderr)

        # Get top songs to identify hits to exclude
        top_data = call_api("artist-top", sf, artist_id)
        top_song_names = set()
        if top_data and "data" in top_data:
            for ad in top_data["data"]:
                views = ad.get("views", {})
                for ts in views.get("top-songs", {}).get("data", []):
                    name = ts.get("attributes", {}).get("name", "")
                    if name:
                        top_song_names.add(name.lower())

        # Fetch discography
        albums_data = call_api("artist-albums", sf, artist_id)
        if not albums_data or "data" not in albums_data:
            continue

        for album in albums_data["data"]:
            album_attrs = album.get("attributes", {})
            if album_attrs.get("isSingle", False):
                continue

            album_tracks = get_album_tracks(sf, album["id"])
            for track in album_tracks:
                tid = track.get("id", "")
                attrs = track.get("attributes", {})
                name = attrs.get("name", "")

                # Exclude: in library, disliked, top songs
                if tid in library_ids or tid in disliked:
                    continue
                if name.lower() in top_song_names:
                    continue

                track_num = attrs.get("trackNumber", 1)
                candidates.append({
                    "id": tid,
                    "name": name,
                    "artist": attrs.get("artistName", artist_name),
                    "album": album_attrs.get("name", ""),
                    "genre": filter_generic_genres(attrs.get("genreNames", [])),
                    "source": "deep_cut",
                    "reason": f"A deep cut from {artist_name} — album track you haven't heard.",
                    "_score": 0.5 + (track_num / 30),  # later tracks score slightly higher
                })

        if len(candidates) >= target_size * 3:
            break  # enough candidates

    # Score and sort
    rng = random.Random()
    for c in candidates:
        c["_score"] += rng.random() * 0.2

    candidates.sort(key=lambda c: c["_score"], reverse=True)
    selected = candidates[:target_size]

    # Clean up internal fields
    for c in selected:
        c.pop("_score", None)

    return sequence_tracks(selected)


# ── Strategy: Mood/Activity ──────────────────────────────────────

def strategy_mood(profile: dict, sf: str, mood: str, target_size: int = 30) -> list[dict]:
    """Mood/Activity-matched playlist filtered through user taste."""
    mood_config = MOOD_MAP.get(mood)
    if not mood_config:
        print(f"ERROR: Unknown mood '{mood}'. Available: {', '.join(MOOD_MAP)}", file=sys.stderr)
        sys.exit(1)

    target_genres = mood_config["genres"]
    user_genres = [g["genre"] for g in profile.get("genre_distribution", [])[:10]]
    library_ids = set(profile.get("library_song_ids", []))
    disliked = set(profile.get("disliked_song_ids", []))

    # Cross-reference mood genres with user preferences
    personalized_genres = []
    for mg in target_genres:
        if mg in user_genres:
            personalized_genres.append(mg)
    # Add mood genres even if not in user taste (that's the point)
    for mg in target_genres:
        if mg not in personalized_genres:
            personalized_genres.append(mg)

    candidates = []

    # Source 1: Charts for mood-relevant genres
    print("  Fetching charts for mood-relevant genres...", file=sys.stderr)
    charts = call_api("charts", sf)
    if charts:
        for section in charts.get("results", {}).values():
            if isinstance(section, list):
                for chart in section:
                    for item in chart.get("data", []):
                        attrs = item.get("attributes", {})
                        item_genres = filter_generic_genres(attrs.get("genreNames", []))
                        tid = item.get("id", "")
                        if tid in library_ids or tid in disliked:
                            continue
                        match = best_genre_match(item_genres, personalized_genres)
                        if match > 0:
                            candidates.append({
                                "id": tid,
                                "name": attrs.get("name", ""),
                                "artist": attrs.get("artistName", ""),
                                "album": "",
                                "genre": item_genres,
                                "source": "trending",
                                "reason": f"Matches your {mood} vibe.",
                                "_score": match,
                            })

    # Source 2: Deep cuts from user's artists in mood-relevant genres
    top_artists = profile.get("top_artists", [])[:10]
    for i, artist in enumerate(top_artists[:5]):
        artist_id = artist.get("id")
        if not artist_id:
            continue
        print(f"  Scanning {artist['name']} for {mood} tracks...", file=sys.stderr)
        albums_data = call_api("artist-albums", sf, artist_id)
        if not albums_data or "data" not in albums_data:
            continue
        for album in albums_data["data"][:3]:
            album_tracks = get_album_tracks(sf, album["id"])
            for track in album_tracks:
                tid = track.get("id", "")
                attrs = track.get("attributes", {})
                if tid in library_ids or tid in disliked:
                    continue
                item_genres = filter_generic_genres(attrs.get("genreNames", []))
                match = best_genre_match(item_genres, personalized_genres)
                if match > 0:
                    candidates.append({
                        "id": tid,
                        "name": attrs.get("name", ""),
                        "artist": attrs.get("artistName", artist["name"]),
                        "album": album.get("attributes", {}).get("name", ""),
                        "genre": item_genres,
                        "source": "deep_cut",
                        "reason": f"From {artist['name']} — fits your {mood} mood.",
                        "_score": match + 0.1,  # slight boost for familiar artists
                    })

    # Add randomness and sort
    rng = random.Random()
    for c in candidates:
        c["_score"] += rng.random() * 0.2

    candidates.sort(key=lambda c: c["_score"], reverse=True)
    selected = candidates[:target_size]
    for c in selected:
        c.pop("_score", None)

    return sequence_tracks(selected)


# ── Strategy: Trend Radar ────────────────────────────────────────

def strategy_trend(profile: dict, sf: str, target_size: int = 20) -> list[dict]:
    """Trending tracks filtered through user's taste, with wildcards."""
    user_genres = [g["genre"] for g in profile.get("genre_distribution", [])[:5]]
    user_artist_names = {a["name"].lower() for a in profile.get("top_artists", [])[:15]}
    library_ids = set(profile.get("library_song_ids", []))
    disliked = set(profile.get("disliked_song_ids", []))

    candidates = []
    seen_ids = set()

    # Fetch overall charts
    print("  Fetching overall charts...", file=sys.stderr)
    charts = call_api("charts", sf)
    if charts:
        for section in charts.get("results", {}).values():
            if isinstance(section, list):
                for chart in section:
                    for rank, item in enumerate(chart.get("data", [])):
                        attrs = item.get("attributes", {})
                        tid = item.get("id", "")
                        if not tid or tid in library_ids or tid in disliked or tid in seen_ids:
                            continue
                        seen_ids.add(tid)
                        item_genres = filter_generic_genres(attrs.get("genreNames", []))
                        artist_name = attrs.get("artistName", "")

                        taste_match = best_genre_match(item_genres, user_genres)
                        if artist_name.lower() in user_artist_names:
                            taste_match = max(taste_match, 0.8)

                        rank_weight = 1.0 - (rank / 25) * 0.3  # top-ranked gets slight bonus
                        score = taste_match * rank_weight

                        candidates.append({
                            "id": tid,
                            "name": attrs.get("name", ""),
                            "artist": artist_name,
                            "album": "",
                            "genre": item_genres,
                            "source": "trending",
                            "reason": "Trending and matches your taste.",
                            "_score": score,
                            "_is_wildcard": taste_match == 0,
                        })

    # Separate wildcards (zero taste match) and matched
    matched = [c for c in candidates if not c.get("_is_wildcard")]
    wildcards = [c for c in candidates if c.get("_is_wildcard")]

    # Sort matched by score
    matched.sort(key=lambda c: c["_score"], reverse=True)

    # Pick main tracks + 2-3 wildcards
    wildcard_count = min(3, len(wildcards))
    main_count = target_size - wildcard_count
    selected = matched[:main_count]

    if wildcards:
        rng = random.Random()
        rng.shuffle(wildcards)
        selected.extend(wildcards[:wildcard_count])

    for c in selected:
        c.pop("_score", None)
        c.pop("_is_wildcard", None)
        if c in wildcards[:wildcard_count]:
            c["reason"] = "A wildcard pick — something outside your usual taste."

    return sequence_tracks(selected)


# ── Strategy: Constellation Discovery ────────────────────────────

def strategy_constellation(profile: dict, sf: str, target_size: int = 25) -> list[dict]:
    """Gradual discovery: familiar → expansion → frontier."""
    top_artists = profile.get("top_artists", [])[:5]
    user_genres = [g["genre"] for g in profile.get("genre_distribution", [])[:10]]
    library_ids = set(profile.get("library_song_ids", []))
    library_artists = {a["name"].lower() for a in profile.get("top_artists", [])}
    disliked = set(profile.get("disliked_song_ids", []))

    # Discover adjacent artists
    discovered = []
    visited_ids = set()

    for artist in top_artists:
        artist_name = artist.get("name", "")
        print(f"  Exploring from {artist_name}...", file=sys.stderr)

        # Search for adjacent artists using name + genre terms
        artist_obj = search_artist(sf, artist_name)
        if not artist_obj:
            continue
        artist_genres = [g for g in artist_obj.get("attributes", {}).get("genreNames", [])
                         if g.lower() != "music"]
        search_query = f"{artist_name} {' '.join(artist_genres[:2])}"

        results = call_api("search", sf, search_query, "artists")
        if not results:
            continue

        candidates = results.get("results", {}).get("artists", {}).get("data", [])
        for c in candidates:
            cid = c.get("id", "")
            cname = c.get("attributes", {}).get("name", "")
            if cid in visited_ids or cname.lower() in library_artists:
                continue
            visited_ids.add(cid)

            c_genres = [g for g in c.get("attributes", {}).get("genreNames", [])
                        if g.lower() != "music"]
            proximity = best_genre_match(c_genres, user_genres)

            # Classify zone
            if proximity >= 0.9:
                zone = "familiar"
            elif proximity >= 0.4:
                zone = "expansion"
            else:
                zone = "frontier"

            discovered.append({
                "artist_id": cid,
                "artist_name": cname,
                "genres": c_genres,
                "proximity": proximity,
                "zone": zone,
                "seed_artist": artist_name,
            })

    # Fetch top songs from discovered artists
    all_tracks = []
    for disc in discovered:
        top_data = call_api("artist-top", sf, disc["artist_id"])
        if not top_data or "data" not in top_data:
            continue
        for ad in top_data["data"]:
            views = ad.get("views", {})
            for ts in views.get("top-songs", {}).get("data", [])[:3]:
                tid = ts.get("id", "")
                if tid in library_ids or tid in disliked:
                    continue
                attrs = ts.get("attributes", {})
                all_tracks.append({
                    "id": tid,
                    "name": attrs.get("name", ""),
                    "artist": disc["artist_name"],
                    "album": "",
                    "genre": filter_generic_genres(attrs.get("genreNames", [])),
                    "source": "constellation",
                    "zone": disc["zone"],
                    "reason": f"Discovered via {disc['seed_artist']} — {disc['zone']} zone.",
                    "_proximity": disc["proximity"],
                })

    # Build gradient: familiar first, then expansion, then frontier
    familiar = [t for t in all_tracks if t.get("zone") == "familiar"]
    expansion = [t for t in all_tracks if t.get("zone") == "expansion"]
    frontier = [t for t in all_tracks if t.get("zone") == "frontier"]

    # Allocate proportionally to target:  ~30% familiar, ~45% expansion, ~25% frontier
    fam_count = max(1, int(target_size * 0.3))
    exp_count = max(1, int(target_size * 0.45))
    fro_count = target_size - fam_count - exp_count

    rng = random.Random()
    rng.shuffle(familiar)
    rng.shuffle(expansion)
    rng.shuffle(frontier)

    selected = familiar[:fam_count] + expansion[:exp_count] + frontier[:fro_count]

    # Clean internal fields
    for c in selected:
        c.pop("_proximity", None)

    # Don't re-sequence — the gradient order IS the sequence
    return selected


# ── Strategy: Refresh ────────────────────────────────────────────

def strategy_refresh(profile: dict, sf: str, playlist_id: str, target_add: int = 10) -> list[dict]:
    """Refresh an existing playlist with fresh matching tracks."""
    # Analyze the existing playlist's sonic signature
    tracks_data = call_api("playlist-tracks", playlist_id)
    if not tracks_data or "data" not in tracks_data:
        print("ERROR: Could not fetch playlist tracks.", file=sys.stderr)
        return []

    existing_tracks = tracks_data["data"]
    existing_ids = set()
    playlist_genres: Counter = Counter()
    playlist_artists: Counter = Counter()

    for track in existing_tracks:
        attrs = track.get("attributes", {})
        catalog_rel = track.get("relationships", {}).get("catalog", {}).get("data", [])
        if catalog_rel:
            existing_ids.add(catalog_rel[0].get("id", ""))
        else:
            existing_ids.add(track.get("id", ""))

        for g in attrs.get("genreNames", []):
            if g.lower() != "music":
                playlist_genres[g] += 1
        artist = attrs.get("artistName", "")
        if artist:
            playlist_artists[artist] += 1

    # Build a target genre profile from the existing playlist
    total_genre = sum(playlist_genres.values()) or 1
    target_genres = [g for g, _ in playlist_genres.most_common(5)]

    library_ids = set(profile.get("library_song_ids", []))
    disliked = set(profile.get("disliked_song_ids", []))

    candidates = []

    # Source 1: Charts matching playlist genres
    print("  Fetching fresh tracks matching playlist signature...", file=sys.stderr)
    charts = call_api("charts", sf)
    if charts:
        for section in charts.get("results", {}).values():
            if isinstance(section, list):
                for chart in section:
                    for item in chart.get("data", []):
                        tid = item.get("id", "")
                        if tid in existing_ids or tid in disliked:
                            continue
                        attrs = item.get("attributes", {})
                        item_genres = filter_generic_genres(attrs.get("genreNames", []))
                        match = best_genre_match(item_genres, target_genres)
                        if match > 0:
                            candidates.append({
                                "id": tid,
                                "name": attrs.get("name", ""),
                                "artist": attrs.get("artistName", ""),
                                "album": "",
                                "genre": item_genres,
                                "source": "refresh",
                                "reason": "Fresh track matching your playlist's vibe.",
                                "_score": match,
                            })

    # Source 2: New tracks from artists already in the playlist
    top_playlist_artists = [a for a, _ in playlist_artists.most_common(5)]
    for artist_name in top_playlist_artists:
        artist = search_artist(sf, artist_name)
        if not artist:
            continue
        albums_data = call_api("artist-albums", sf, artist["id"])
        if not albums_data or "data" not in albums_data:
            continue
        for album in albums_data["data"][:2]:
            album_tracks = get_album_tracks(sf, album["id"])
            for track in album_tracks:
                tid = track.get("id", "")
                if tid in existing_ids or tid in disliked:
                    continue
                attrs = track.get("attributes", {})
                candidates.append({
                    "id": tid,
                    "name": attrs.get("name", ""),
                    "artist": attrs.get("artistName", artist_name),
                    "album": album.get("attributes", {}).get("name", ""),
                    "genre": filter_generic_genres(attrs.get("genreNames", [])),
                    "source": "refresh",
                    "reason": f"New from {artist_name}, matching your playlist.",
                    "_score": 0.7,
                })

    rng = random.Random()
    for c in candidates:
        c["_score"] += rng.random() * 0.2

    candidates.sort(key=lambda c: c["_score"], reverse=True)
    selected = candidates[:target_add]
    for c in selected:
        c.pop("_score", None)

    return selected


# ── Playlist Creation ────────────────────────────────────────────

def generate_name(strategy: str, mood: Optional[str] = None,
                  profile: Optional[dict] = None) -> str:
    """Auto-generate a playlist name."""
    date_str = datetime.now(timezone.utc).strftime("%b %Y")
    if strategy == "deep-cuts":
        artists = profile.get("top_artists", [])[:2] if profile else []
        artist_str = " & ".join(a["name"] for a in artists) if artists else "Your Favorites"
        return f"Deep Cuts · {artist_str} · {date_str}"
    elif strategy == "mood":
        mood_label = (mood or "vibes").capitalize()
        return f"{mood_label} Mix · {date_str}"
    elif strategy == "trend":
        genres = profile.get("genre_distribution", [])[:2] if profile else []
        genre_str = " & ".join(g["genre"] for g in genres) if genres else "All Genres"
        return f"Trending For You · {genre_str} · {date_str}"
    elif strategy == "constellation":
        return f"New Horizons · {date_str}"
    elif strategy == "refresh":
        return f"Refreshed · {date_str}"
    return f"Apple Music DJ · {date_str}"


def generate_description(strategy: str, mood: Optional[str] = None,
                         track_count: int = 0) -> str:
    """Auto-generate a playlist description."""
    descriptions = {
        "deep-cuts": "Tracks you probably haven't heard from the artists you love. "
                     "No singles, no greatest hits — just the good stuff.",
        "mood": MOOD_MAP.get(mood or "", {}).get("description",
                "Tracks matched to your mood, filtered through your taste."),
        "trend": "What's trending right now, filtered through your taste. "
                 "A few wildcards in there too.",
        "constellation": "Starting from the artists you love, this playlist gradually "
                         "pulls you into new territory. The best discoveries are toward the end.",
        "refresh": "Fresh additions to keep your playlist evolving.",
    }
    desc = descriptions.get(strategy, "Curated by Apple Music DJ.")
    return f"{desc} {track_count} tracks."


def check_playlist_exists(name: str) -> Optional[str]:
    """Check if a playlist with this name already exists. Returns playlist ID or None."""
    try:
        result = subprocess.run(
            [str(SCRIPT_DIR / "apple_music_api.sh"), "library-playlists", "100"],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode == 0 and result.stdout.strip():
            data = json.loads(result.stdout)
            for pl in data.get("data", []):
                if pl.get("attributes", {}).get("name") == name:
                    return pl.get("id")
    except Exception:
        pass
    return None


def create_playlist_from_tracks(tracks: list[dict], name: str,
                                description: str) -> bool:
    """Create a playlist in Apple Music using build_playlist.sh."""
    if not tracks:
        print("ERROR: No tracks to create playlist from.", file=sys.stderr)
        return False

    # Check for existing playlist with same name
    existing_id = check_playlist_exists(name)
    if existing_id:
        print(f"⚠️  A playlist named '{name}' already exists (ID: {existing_id}).", file=sys.stderr)
        print("   Skipping creation. Use --strategy refresh to update it.", file=sys.stderr)
        return False

    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        for t in tracks:
            f.write(t["id"] + "\n")
        ids_file = f.name

    try:
        result = subprocess.run(
            [str(SCRIPT_DIR / "build_playlist.sh"), "create", name, description, ids_file],
            capture_output=True, text=True, timeout=60,
        )
        if result.returncode != 0:
            print(f"ERROR: Playlist creation failed: {result.stderr}", file=sys.stderr)
            return False
        return True
    except subprocess.TimeoutExpired:
        print("ERROR: Playlist creation timed out.", file=sys.stderr)
        return False
    finally:
        Path(ids_file).unlink(missing_ok=True)


# ── Main ─────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Apple Music DJ — Playlist Strategy Engine"
    )
    parser.add_argument("--strategy", required=True,
                        choices=["deep-cuts", "mood", "trend", "constellation", "refresh"],
                        help="Playlist strategy to use")
    parser.add_argument("--profile", required=True, help="Path to taste profile JSON")
    parser.add_argument("--storefront", default=None, help="Storefront code")
    parser.add_argument("--mood", default=None,
                        help=f"Mood for mood strategy ({', '.join(MOOD_MAP)})")
    parser.add_argument("--playlist-id", default=None,
                        help="Playlist ID for refresh strategy")
    parser.add_argument("--name", default=None, help="Custom playlist name")
    parser.add_argument("--size", type=int, default=None,
                        help="Target track count")
    parser.add_argument("--create", action="store_true",
                        help="Create the playlist in Apple Music")
    parser.add_argument("--output", default=None, help="Write playlist JSON to file")

    args = parser.parse_args()

    require_env_tokens()
    profile = load_profile(args.profile)
    config = load_config()

    sf = get_storefront(args.storefront or config.get("default_storefront"))

    target_size = args.size or config.get("playlist_size", 30)

    print(f"🎧 Strategy: {args.strategy} | Target: {target_size} tracks", file=sys.stderr)

    # Run the selected strategy
    if args.strategy == "deep-cuts":
        tracks = strategy_deep_cuts(profile, sf, target_size)
    elif args.strategy == "mood":
        if not args.mood:
            print(f"ERROR: --mood required. Options: {', '.join(MOOD_MAP)}", file=sys.stderr)
            sys.exit(1)
        tracks = strategy_mood(profile, sf, args.mood, target_size)
    elif args.strategy == "trend":
        tracks = strategy_trend(profile, sf, target_size)
    elif args.strategy == "constellation":
        tracks = strategy_constellation(profile, sf, target_size)
    elif args.strategy == "refresh":
        if not args.playlist_id:
            print("ERROR: --playlist-id required for refresh strategy.", file=sys.stderr)
            sys.exit(1)
        tracks = strategy_refresh(profile, sf, args.playlist_id, target_size)

    if not tracks:
        print("No tracks found for this strategy. Try refreshing your profile.", file=sys.stderr)
        sys.exit(1)

    # Generate name & description
    name = args.name or generate_name(args.strategy, args.mood, profile)
    description = generate_description(args.strategy, args.mood, len(tracks))

    result = {
        "strategy": args.strategy,
        "name": name,
        "description": description,
        "track_count": len(tracks),
        "tracks": tracks,
    }

    print(f"\n✅ {len(tracks)} tracks selected.", file=sys.stderr)

    # Output
    output_json = json.dumps(result, indent=2)
    if args.output:
        import os as _os
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        fd = _os.open(str(args.output), _os.O_WRONLY | _os.O_CREAT | _os.O_TRUNC, 0o600)
        with _os.fdopen(fd, "w") as f:
            f.write(output_json)
        print(f"Playlist JSON written to {args.output}", file=sys.stderr)
    else:
        print(output_json)

    # Optionally create in Apple Music
    if args.create:
        print("Creating playlist in Apple Music...", file=sys.stderr)
        if create_playlist_from_tracks(tracks, name, description):
            print(f"✅ Playlist '{name}' created!", file=sys.stderr)
            # Log to playlist history
            try:
                from playlist_history import log_playlist
                track_ids = [t["id"] for t in tracks if t.get("id")]
                log_playlist(name, args.strategy, track_ids)
                print("📝 Logged to playlist history.", file=sys.stderr)
            except Exception as e:
                print(f"⚠️  Could not log to history: {e}", file=sys.stderr)
        else:
            print("❌ Failed to create playlist.", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
