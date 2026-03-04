#!/usr/bin/env python3
"""
compatibility.py — Taste compatibility scoring.

Modes:
  artist   Compare user's taste profile against an artist's catalog DNA.
  profile  Compare two taste profile JSONs against each other.

Usage:
  python3 compatibility.py artist <profile.json> <storefront> <artist_name_or_id>
  python3 compatibility.py profile <profile1.json> <profile2.json>

Requires: APPLE_MUSIC_DEV_TOKEN (for artist mode).
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

from _common import call_api, load_profile
from typing import Optional, Union

SCRIPT_DIR = Path(__file__).parent


# ── Genre Similarity ─────────────────────────────────────────────

# Adjacency groups — genres in the same group get partial credit
GENRE_ADJACENCY = {
    "rock_family": {"Rock", "Alternative", "Indie", "Punk", "Metal", "Grunge"},
    "electronic_family": {"Electronic", "Dance", "House", "Techno", "Ambient", "IDM"},
    "hiphop_family": {"Hip-Hop/Rap", "R&B/Soul", "Funk"},
    "folk_family": {"Folk", "Singer/Songwriter", "Country", "Americana", "Bluegrass"},
    "jazz_family": {"Jazz", "Blues", "Bossa Nova", "Soul"},
    "classical_family": {"Classical", "Soundtrack", "New Age"},
    "pop_family": {"Pop", "Synth Pop", "Indie Pop", "K-Pop", "J-Pop"},
}


def genre_similarity(genre_a: str, genre_b: str) -> float:
    if genre_a.lower() == genre_b.lower():
        return 1.0
    for family in GENRE_ADJACENCY.values():
        lower = {g.lower() for g in family}
        if genre_a.lower() in lower and genre_b.lower() in lower:
            return 0.5
    return 0.0


def genre_overlap_score(genres_a: list[dict], genres_b: list[dict]) -> float:
    """Compare two genre distributions. Returns 0-1."""
    if not genres_a or not genres_b:
        return 0.0
    score = 0.0
    total_weight = 0.0
    for ga in genres_a:
        best_match = 0.0
        for gb in genres_b:
            sim = genre_similarity(ga["genre"], gb["genre"])
            if sim > 0:
                best_match = max(best_match, sim * min(ga["weight"], gb["weight"]) * 2)
        score += best_match * ga["weight"]
        total_weight += ga["weight"]
    return min(score / total_weight, 1.0) if total_weight > 0 else 0.0


# ── Artist Compatibility ─────────────────────────────────────────

def resolve_artist(sf: str, query: str) -> Optional[dict]:
    """Search for an artist by name and return their catalog data."""
    from _common import search_artist
    found = search_artist(sf, query)
    if not found:
        return None
    artist_id = found.get("id", "")
    # Fetch full detail
    detail = call_api("artist-detail", sf, artist_id)
    if detail and "data" in detail:
        return detail["data"][0]
    return found


def get_artist_genre_profile(artist: dict) -> list[dict]:
    """Extract genre distribution from artist data."""
    attrs = artist.get("attributes", {})
    genres = attrs.get("genreNames", [])
    if not genres:
        return []
    weight = 1.0 / len(genres) if genres else 0
    return [{"genre": g, "weight": round(weight, 3)} for g in genres if g.lower() != "music"]


def artist_compatibility(profile: dict, sf: str, artist_query: str) -> dict:
    """Score compatibility between user profile and an artist."""
    artist = resolve_artist(sf, artist_query)
    if not artist:
        return {"error": f"Could not find artist: {artist_query}"}

    artist_name = artist.get("attributes", {}).get("name", artist_query)
    artist_genres = get_artist_genre_profile(artist)
    user_genres = profile.get("genre_distribution", [])
    user_artists = profile.get("top_artists", [])

    # Genre overlap
    g_score = genre_overlap_score(user_genres, artist_genres)

    # Direct artist match (is this artist in user's top artists?)
    artist_match = 0.0
    for ua in user_artists:
        if ua["name"].lower() == artist_name.lower():
            artist_match = 1.0
            break

    # Final score: weighted blend
    # If user already listens to the artist, high compatibility is obvious
    if artist_match > 0:
        final = 0.85 + (g_score * 0.15)
    else:
        final = g_score * 0.8 + 0.1  # Base 10% + genre similarity

    final = round(min(final, 1.0), 2)
    pct = int(final * 100)

    # Generate explanation
    if pct >= 85:
        verdict = "Deeply compatible — this artist is right in your wheelhouse."
    elif pct >= 65:
        verdict = "Strong overlap — you'd probably dig most of their catalog."
    elif pct >= 45:
        verdict = "Moderate match — some alignment, some new territory."
    elif pct >= 25:
        verdict = "Stretch pick — outside your comfort zone, but that's not a bad thing."
    else:
        verdict = "Wild card — musically distant from your usual taste."

    matching_genres = []
    for ag in artist_genres:
        for ug in user_genres:
            if genre_similarity(ag["genre"], ug["genre"]) > 0:
                matching_genres.append(ag["genre"])
                break

    return {
        "artist": artist_name,
        "artist_id": artist.get("id"),
        "compatibility_pct": pct,
        "verdict": verdict,
        "genre_overlap": round(g_score, 2),
        "already_in_library": artist_match > 0,
        "matching_genres": matching_genres,
        "artist_genres": [g["genre"] for g in artist_genres],
    }


# ── Profile vs Profile ───────────────────────────────────────────

def profile_compatibility(profile_a: dict, profile_b: dict) -> dict:
    """Compare two user taste profiles."""
    genres_a = profile_a.get("genre_distribution", [])
    genres_b = profile_b.get("genre_distribution", [])
    artists_a = {a["name"].lower() for a in profile_a.get("top_artists", [])[:20]}
    artists_b = {a["name"].lower() for a in profile_b.get("top_artists", [])[:20]}

    g_score = genre_overlap_score(genres_a, genres_b)

    # Artist overlap
    shared_artists = artists_a & artists_b
    artist_overlap = len(shared_artists) / max(len(artists_a | artists_b), 1)

    # Era overlap
    eras_a = {e["decade"] for e in profile_a.get("era_distribution", [])}
    eras_b = {e["decade"] for e in profile_b.get("era_distribution", [])}
    era_overlap = len(eras_a & eras_b) / max(len(eras_a | eras_b), 1)

    # Energy match
    energy_match = 1.0 if profile_a.get("energy_profile") == profile_b.get("energy_profile") else 0.3

    final = (g_score * 0.4 + artist_overlap * 0.3 + era_overlap * 0.15 + energy_match * 0.15)
    pct = int(round(min(final, 1.0), 2) * 100)

    if pct >= 80:
        verdict = "Musical soulmates — remarkably similar taste."
    elif pct >= 60:
        verdict = "Strong alignment — you'd enjoy each other's playlists."
    elif pct >= 40:
        verdict = "Some common ground, lots of room for mutual discovery."
    elif pct >= 20:
        verdict = "Different worlds — your collab playlist would be... interesting."
    else:
        verdict = "Opposites. One of you is going to learn something new."

    return {
        "compatibility_pct": pct,
        "verdict": verdict,
        "genre_overlap": round(g_score, 2),
        "shared_artists": sorted(shared_artists),
        "artist_overlap_pct": int(artist_overlap * 100),
        "shared_eras": sorted(eras_a & eras_b),
        "energy_match": profile_a.get("energy_profile") == profile_b.get("energy_profile"),
    }


# ── Main ─────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Taste Compatibility Scoring")
    sub = parser.add_subparsers(dest="mode", required=True)

    p_artist = sub.add_parser("artist", help="Compare taste vs. an artist")
    p_artist.add_argument("profile", help="Path to taste profile JSON")
    p_artist.add_argument("storefront", help="Storefront code (e.g., us)")
    p_artist.add_argument("artist", help="Artist name or catalog ID", nargs="+")

    p_profile = sub.add_parser("profile", help="Compare two profiles")
    p_profile.add_argument("profile_a", help="Path to first taste profile JSON")
    p_profile.add_argument("profile_b", help="Path to second taste profile JSON")

    args = parser.parse_args()

    if args.mode == "artist":
        profile = load_profile(args.profile)
        artist_query = " ".join(args.artist)
        result = artist_compatibility(profile, args.storefront, artist_query)
    elif args.mode == "profile":
        profile_a = load_profile(args.profile_a)
        profile_b = load_profile(args.profile_b)
        result = profile_compatibility(profile_a, profile_b)
    else:
        parser.print_help()
        sys.exit(1)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
