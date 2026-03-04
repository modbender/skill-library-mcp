"""Shared fixtures for apple-music-dj tests."""

import pytest


# ── Sample Tracks ────────────────────────────────────────────────

@pytest.fixture
def sample_tracks():
    """Diverse track list for extraction function tests."""
    return [
        {
            "id": "t1",
            "attributes": {
                "name": "Everything In Its Right Place",
                "artistName": "Radiohead",
                "genreNames": ["Alternative", "Rock"],
                "releaseDate": "2000-10-02",
            },
            "relationships": {
                "artists": {"data": [{"id": "a1"}]},
            },
        },
        {
            "id": "t2",
            "attributes": {
                "name": "Idioteque",
                "artistName": "Radiohead",
                "genreNames": ["Alternative", "Electronic"],
                "releaseDate": "2000-10-02",
            },
            "relationships": {
                "artists": {"data": [{"id": "a1"}]},
            },
        },
        {
            "id": "t3",
            "attributes": {
                "name": "Blinding Lights",
                "artistName": "The Weeknd",
                "genreNames": ["Pop", "R&B/Soul"],
                "releaseDate": "2019-11-29",
            },
            "relationships": {
                "artists": {"data": [{"id": "a2"}]},
            },
        },
        {
            "id": "t4",
            "attributes": {
                "name": "Bohemian Rhapsody",
                "artistName": "Queen",
                "genreNames": ["Rock", "Music"],  # includes generic "Music"
                "releaseDate": "1975-10-31",
            },
        },
        {
            "id": "t5",
            "attributes": {
                "name": "Clair de Lune",
                "artistName": "Claude Debussy",
                "genreNames": ["Classical"],
                "releaseDate": "1905",
            },
        },
        {
            "id": "t6",
            "attributes": {
                "name": "HUMBLE.",
                "artistName": "Kendrick Lamar",
                "genreNames": ["Hip-Hop/Rap"],
                "releaseDate": "2017-03-30",
            },
        },
    ]


@pytest.fixture
def sample_profile():
    """Full taste profile dict for compatibility/card tests."""
    return {
        "top_artists": [
            {"name": "Radiohead", "id": "a1", "count": 25, "play_weight": 0.2},
            {"name": "The Weeknd", "id": "a2", "count": 15, "play_weight": 0.12},
            {"name": "Kendrick Lamar", "id": "a3", "count": 10, "play_weight": 0.08},
            {"name": "Queen", "id": "a4", "count": 8, "play_weight": 0.06},
            {"name": "Debussy", "id": "a5", "count": 5, "play_weight": 0.04},
        ],
        "genre_distribution": [
            {"genre": "Alternative", "count": 30, "weight": 0.3},
            {"genre": "Rock", "count": 20, "weight": 0.2},
            {"genre": "Pop", "count": 15, "weight": 0.15},
            {"genre": "Electronic", "count": 10, "weight": 0.1},
            {"genre": "Hip-Hop/Rap", "count": 8, "weight": 0.08},
            {"genre": "Classical", "count": 5, "weight": 0.05},
            {"genre": "R&B/Soul", "count": 5, "weight": 0.05},
        ],
        "era_distribution": [
            {"decade": "2000s", "count": 30, "weight": 0.4},
            {"decade": "2010s", "count": 25, "weight": 0.33},
            {"decade": "1970s", "count": 10, "weight": 0.13},
            {"decade": "1900s", "count": 5, "weight": 0.07},
        ],
        "energy_profile": "balanced",
        "variety_score": 0.65,
        "mainstream_score": 0.35,
        "listening_velocity": "moderate",
        "library_song_ids": ["t3", "t4"],
        "data_summary": {
            "recent_tracks": 50,
            "library_songs": 200,
            "heavy_rotation_items": 10,
            "loved_count": 30,
            "disliked_count": 2,
        },
        "replay_highlights": {
            "available": True,
            "genre_evolution": [
                {"year": "2022", "top_genre": "Alternative"},
                {"year": "2023", "top_genre": "Electronic"},
            ],
        },
    }


@pytest.fixture
def empty_profile():
    """Minimal/empty profile for edge case testing."""
    return {
        "top_artists": [],
        "genre_distribution": [],
        "era_distribution": [],
        "energy_profile": "balanced",
        "variety_score": 0.5,
        "mainstream_score": 0.5,
        "listening_velocity": "steady",
        "library_song_ids": [],
        "data_summary": {},
        "replay_highlights": {"available": False},
    }


@pytest.fixture
def sample_chart_data():
    """Chart data for mainstream score testing."""
    return {
        "results": {
            "songs": [{
                "data": [
                    {"attributes": {"name": "Blinding Lights", "artistName": "The Weeknd"}},
                    {"attributes": {"name": "Bad Guy", "artistName": "Billie Eilish"}},
                    {"attributes": {"name": "Heat Waves", "artistName": "Glass Animals"}},
                ],
            }],
            "albums": [{
                "data": [
                    {"attributes": {"name": "Midnights", "artistName": "Taylor Swift"}},
                ],
            }],
        },
    }


@pytest.fixture
def sample_replay_summary():
    """Replay summary data for highlight extraction tests."""
    return {
        "data": [
            {
                "attributes": {
                    "year": 2023,
                    "topGenres": [{"name": "Alternative"}, {"name": "Rock"}],
                    "topArtists": [{"name": "Radiohead"}],
                    "listenTimeInMinutes": 52000,
                },
            },
            {
                "attributes": {
                    "year": 2024,
                    "topGenres": [{"name": "Electronic"}],
                    "topArtists": [{"name": "Aphex Twin"}],
                    "listenTimeInMinutes": 48000,
                },
            },
        ],
    }


@pytest.fixture
def sample_ratings_data():
    """Ratings for extract_ratings tests."""
    return {
        "data": [
            {"id": "r1", "attributes": {"value": 1}},
            {"id": "r2", "attributes": {"value": 1}},
            {"id": "r3", "attributes": {"value": -1}},
            {"id": "r4", "attributes": {"value": 0}},   # neutral — ignored
            {"id": "",   "attributes": {"value": 1}},    # empty ID — skipped
        ],
    }
