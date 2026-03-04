"""Tests for taste_profiler.py — core data extraction and scoring functions."""

import json
import sys
import time
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from taste_profiler import (
    build_profile,
    compute_mainstream_score,
    compute_variety_score,
    extract_artists,
    extract_eras,
    extract_genres,
    extract_ratings,
    extract_replay_highlights,
    infer_energy_profile,
    load_cache,
    save_cache,
    log,
)
import taste_profiler as tp


# ── extract_genres ───────────────────────────────────────────────

class TestExtractGenres:
    def test_counts_genres_from_tracks(self, sample_tracks):
        genres = extract_genres(sample_tracks)
        genre_names = [g["genre"] for g in genres]
        assert "Alternative" in genre_names
        assert "Rock" in genre_names

    def test_filters_generic_music_tag(self, sample_tracks):
        genres = extract_genres(sample_tracks)
        assert "Music" not in [g["genre"] for g in genres]

    def test_weights_sum_to_approximately_one(self, sample_tracks):
        genres = extract_genres(sample_tracks)
        total = sum(g["weight"] for g in genres)
        assert 0.99 <= total <= 1.01

    def test_sorted_by_frequency(self, sample_tracks):
        genres = extract_genres(sample_tracks)
        counts = [g["count"] for g in genres]
        assert counts == sorted(counts, reverse=True)

    def test_empty_tracks(self):
        genres = extract_genres([])
        assert genres == []

    def test_tracks_without_genres(self):
        tracks = [{"attributes": {"name": "Song"}}]
        genres = extract_genres(tracks)
        assert genres == []


# ── extract_artists ──────────────────────────────────────────────

class TestExtractArtists:
    def test_counts_artist_appearances(self, sample_tracks):
        artists = extract_artists(sample_tracks)
        radiohead = next(a for a in artists if a["name"] == "Radiohead")
        assert radiohead["count"] == 2

    def test_extracts_artist_ids(self, sample_tracks):
        artists = extract_artists(sample_tracks)
        radiohead = next(a for a in artists if a["name"] == "Radiohead")
        assert radiohead["id"] == "a1"

    def test_sorted_by_count_descending(self, sample_tracks):
        artists = extract_artists(sample_tracks)
        counts = [a["count"] for a in artists]
        assert counts == sorted(counts, reverse=True)

    def test_capped_at_30(self):
        tracks = [
            {"attributes": {"artistName": f"Artist{i}", "genreNames": []}}
            for i in range(50)
        ]
        artists = extract_artists(tracks)
        assert len(artists) <= 30

    def test_play_weight_calculated(self, sample_tracks):
        artists = extract_artists(sample_tracks)
        for a in artists:
            assert 0 < a["play_weight"] <= 1.0

    def test_empty_tracks(self):
        artists = extract_artists([])
        assert artists == []


# ── extract_eras ─────────────────────────────────────────────────

class TestExtractEras:
    def test_decade_bucketing(self, sample_tracks):
        eras = extract_eras(sample_tracks)
        decades = {e["decade"] for e in eras}
        assert "2000s" in decades  # releaseDate "2000-10-02"
        assert "1970s" in decades  # releaseDate "1975-10-31"
        assert "2010s" in decades  # releaseDate "2017-03-30" and "2019-11-29"

    def test_year_only_date(self):
        tracks = [{"attributes": {"releaseDate": "2023"}}]
        eras = extract_eras(tracks)
        assert eras[0]["decade"] == "2020s"

    def test_1999_goes_to_1990s(self):
        tracks = [{"attributes": {"releaseDate": "1999-12-31"}}]
        eras = extract_eras(tracks)
        assert eras[0]["decade"] == "1990s"

    def test_2000_goes_to_2000s(self):
        tracks = [{"attributes": {"releaseDate": "2000-01-01"}}]
        eras = extract_eras(tracks)
        assert eras[0]["decade"] == "2000s"

    def test_malformed_date_skipped(self):
        tracks = [{"attributes": {"releaseDate": "not-a-date"}}]
        eras = extract_eras(tracks)
        assert eras == []

    def test_missing_date_skipped(self):
        tracks = [{"attributes": {"name": "Song"}}]
        eras = extract_eras(tracks)
        assert eras == []

    def test_empty_tracks(self):
        assert extract_eras([]) == []


# ── infer_energy_profile ─────────────────────────────────────────

class TestInferEnergyProfile:
    def test_high_energy_genres(self):
        genres = [
            {"genre": "Electronic", "weight": 0.5},
            {"genre": "Rock", "weight": 0.3},
            {"genre": "Jazz", "weight": 0.1},
        ]
        assert infer_energy_profile(genres) == "high-energy"

    def test_chill_genres(self):
        genres = [
            {"genre": "Ambient", "weight": 0.4},
            {"genre": "Classical", "weight": 0.3},
            {"genre": "Jazz", "weight": 0.2},
        ]
        assert infer_energy_profile(genres) == "chill"

    def test_balanced_when_close(self):
        genres = [
            {"genre": "Rock", "weight": 0.3},
            {"genre": "Jazz", "weight": 0.25},
            {"genre": "Indie", "weight": 0.2},
        ]
        assert infer_energy_profile(genres) == "balanced"

    def test_empty_genres(self):
        assert infer_energy_profile([]) == "balanced"


# ── compute_variety_score ────────────────────────────────────────

class TestComputeVarietyScore:
    def test_empty_tracks_returns_default(self):
        assert compute_variety_score([], []) == 0.5

    def test_all_same_artist_is_low(self):
        tracks = [{"attributes": {"artistName": "Same"}} for _ in range(20)]
        score = compute_variety_score([], tracks)
        assert score < 0.2

    def test_all_different_artists_is_high(self):
        tracks = [{"attributes": {"artistName": f"Artist{i}"}} for i in range(20)]
        score = compute_variety_score([], tracks)
        assert score >= 0.9

    def test_capped_at_one(self):
        tracks = [{"attributes": {"artistName": f"A{i}"}} for i in range(5)]
        score = compute_variety_score([], tracks)
        assert score <= 1.0

    def test_score_is_float(self):
        tracks = [{"attributes": {"artistName": f"A{i}"}} for i in range(10)]
        score = compute_variety_score([], tracks)
        assert isinstance(score, float)


# ── compute_mainstream_score ─────────────────────────────────────

class TestComputeMainstreamScore:
    def test_no_chart_data_returns_default(self):
        artists = [{"name": "Any"}]
        assert compute_mainstream_score(artists, None) == 0.5

    def test_no_artists_returns_default(self):
        assert compute_mainstream_score([], {"results": {}}) == 0.5

    def test_full_overlap(self, sample_chart_data):
        artists = [
            {"name": "The Weeknd"},
            {"name": "Billie Eilish"},
            {"name": "Glass Animals"},
            {"name": "Taylor Swift"},
        ]
        score = compute_mainstream_score(artists, sample_chart_data)
        assert score == 1.0

    def test_no_overlap(self, sample_chart_data):
        artists = [{"name": "Radiohead"}, {"name": "Aphex Twin"}]
        score = compute_mainstream_score(artists, sample_chart_data)
        assert score == 0.0

    def test_partial_overlap(self, sample_chart_data):
        artists = [{"name": "The Weeknd"}, {"name": "Radiohead"}]
        score = compute_mainstream_score(artists, sample_chart_data)
        assert score == 0.5


# ── extract_ratings ──────────────────────────────────────────────

class TestExtractRatings:
    def test_loved_and_disliked(self, sample_ratings_data):
        loved, disliked = extract_ratings(sample_ratings_data)
        assert loved == ["r1", "r2"]
        assert disliked == ["r3"]

    def test_empty_id_skipped(self, sample_ratings_data):
        loved, _ = extract_ratings(sample_ratings_data)
        assert "" not in loved

    def test_neutral_value_ignored(self, sample_ratings_data):
        loved, disliked = extract_ratings(sample_ratings_data)
        assert "r4" not in loved and "r4" not in disliked

    def test_none_input(self):
        loved, disliked = extract_ratings(None)
        assert loved == [] and disliked == []

    def test_empty_data(self):
        loved, disliked = extract_ratings({"data": []})
        assert loved == [] and disliked == []


# ── extract_replay_highlights ────────────────────────────────────

class TestExtractReplayHighlights:
    """These tests would have caught the genre_evolution bug."""

    def test_extracts_genre_evolution(self, sample_replay_summary):
        highlights = extract_replay_highlights(sample_replay_summary, None)
        assert highlights["available"] is True
        evolution = highlights["genre_evolution"]
        assert len(evolution) == 2
        assert evolution[0] == {"year": "2023", "top_genre": "Alternative"}
        assert evolution[1] == {"year": "2024", "top_genre": "Electronic"}

    def test_top_genre_from_topGenres_field(self):
        """Regression: the bug was reading the wrong field."""
        data = {"data": [{"attributes": {
            "year": 2024,
            "topGenres": [{"name": "Rock"}],
            "topArtists": [{"name": "Queen"}],
        }}]}
        h = extract_replay_highlights(data, None)
        assert h["genre_evolution"][0]["top_genre"] == "Rock"

    def test_fallback_to_genreNames(self):
        """When topGenres is empty, falls back to genreNames."""
        data = {"data": [{"attributes": {
            "year": 2024,
            "topGenres": [],
            "genreNames": ["Jazz"],
            "topArtists": [],
        }}]}
        h = extract_replay_highlights(data, None)
        assert h["genre_evolution"][0]["top_genre"] == "Jazz"

    def test_top_genre_none_when_no_genres(self):
        data = {"data": [{"attributes": {
            "year": 2024,
            "topGenres": [],
            "genreNames": [],
            "topArtists": [],
        }}]}
        h = extract_replay_highlights(data, None)
        assert h["genre_evolution"] == []  # no genre → no entry

    def test_top_artist_all_time(self, sample_replay_summary):
        h = extract_replay_highlights(sample_replay_summary, None)
        # Last entry wins (Aphex Twin from 2024)
        assert h["top_artist_all_time"] == "Aphex Twin"

    def test_milestones_update_listen_time(self, sample_replay_summary):
        milestones = {"data": [{"attributes": {"listenTimeInMinutes": 99000}}]}
        h = extract_replay_highlights(sample_replay_summary, milestones)
        assert h["total_minutes_latest_year"] == 99000

    def test_milestones_lower_doesnt_replace(self, sample_replay_summary):
        milestones = {"data": [{"attributes": {"listenTimeInMinutes": 100}}]}
        h = extract_replay_highlights(sample_replay_summary, milestones)
        # The function iterates summaries in order; last year (2024=48000) wins
        # Milestone value 100 < 48000, so milestones don't overwrite
        assert h["total_minutes_latest_year"] == 48000

    def test_none_inputs(self):
        h = extract_replay_highlights(None, None)
        assert h["available"] is False
        assert h["genre_evolution"] == []

    def test_empty_data(self):
        h = extract_replay_highlights({"data": []}, None)
        assert h["available"] is True
        assert h["genre_evolution"] == []


# ── log ──────────────────────────────────────────────────────────

class TestLog:
    def test_log_verbose(self, capsys):
        log("hello", verbose=True)
        assert "hello" in capsys.readouterr().err

    def test_log_silent(self, capsys):
        log("hello", verbose=False)
        assert capsys.readouterr().err == ""


# ── load_cache ───────────────────────────────────────────────────

class TestLoadCache:
    def test_returns_none_when_missing(self, tmp_path):
        result = load_cache(str(tmp_path / "nonexistent.json"), 168)
        assert result is None

    def test_returns_data_when_fresh(self, tmp_path):
        f = tmp_path / "cache.json"
        data = {"genre_distribution": []}
        f.write_text(json.dumps(data))
        result = load_cache(str(f), max_age_hours=168)
        assert result == data

    def test_returns_none_when_expired(self, tmp_path, monkeypatch):
        f = tmp_path / "cache.json"
        f.write_text(json.dumps({"old": True}))
        # Make the file appear old
        import os
        old_time = time.time() - (200 * 3600)
        os.utime(str(f), (old_time, old_time))
        result = load_cache(str(f), max_age_hours=168)
        assert result is None

    def test_returns_none_on_invalid_json(self, tmp_path):
        f = tmp_path / "cache.json"
        f.write_text("{bad json")
        assert load_cache(str(f), 168) is None

    def test_returns_none_on_os_error(self, tmp_path):
        f = tmp_path / "cache.json"
        f.write_text("{}")
        f.chmod(0o000)
        result = load_cache(str(f), 168)
        f.chmod(0o644)
        assert result is None


# ── save_cache ───────────────────────────────────────────────────

class TestSaveCache:
    def test_saves_profile(self, tmp_path):
        f = tmp_path / "cache.json"
        save_cache({"test": True}, str(f))
        assert json.loads(f.read_text()) == {"test": True}

    def test_creates_parent_dirs(self, tmp_path):
        f = tmp_path / "deep" / "cache.json"
        save_cache({}, str(f))
        assert f.exists()

    def test_handles_os_error(self, capsys):
        """Should warn on error, not crash."""
        save_cache({}, "/nonexistent/readonly/cache.json")
        captured = capsys.readouterr()
        assert "WARN" in captured.err


# ── build_profile ────────────────────────────────────────────────

class TestBuildProfile:
    def _mock_all_apis(self, monkeypatch):
        """Mock all API calls and env tokens for build_profile."""
        monkeypatch.setattr("taste_profiler.require_env_tokens", lambda: None)
        monkeypatch.setattr("taste_profiler.check_token_expiry", lambda: None)
        monkeypatch.setattr("taste_profiler.get_storefront", lambda sf=None: "us")

        sample_tracks = [
            {
                "id": "t1",
                "attributes": {
                    "name": "Song A",
                    "artistName": "Artist A",
                    "genreNames": ["Rock"],
                    "releaseDate": "2020-01-01",
                },
                "relationships": {"artists": {"data": [{"id": "a1"}]}},
            },
            {
                "id": "t2",
                "attributes": {
                    "name": "Song B",
                    "artistName": "Artist B",
                    "genreNames": ["Pop"],
                    "releaseDate": "2021-06-15",
                },
                "relationships": {"artists": {"data": [{"id": "a2"}]}},
            },
        ]

        def mock_call_api(command, *args, **kwargs):
            if command == "recent-tracks":
                return sample_tracks
            elif command == "heavy-rotation":
                return {"data": []}
            elif command == "library-artists":
                return {"data": [{"id": "a1"}, {"id": "a2"}]}
            elif command == "library-songs":
                return {"data": sample_tracks}
            elif command == "ratings":
                return {"data": []}
            elif command == "recommendations":
                return {"data": []}
            elif command == "replay-summary":
                return None
            elif command == "replay-milestones":
                return None
            elif command == "charts":
                return None
            return None

        monkeypatch.setattr("taste_profiler.call_api", mock_call_api)

    def test_builds_complete_profile(self, monkeypatch):
        self._mock_all_apis(monkeypatch)
        args = MagicMock()
        args.verbose = False
        args.storefront = "us"
        args.skip_replay = False
        profile = build_profile(args)
        assert "top_artists" in profile
        assert "genre_distribution" in profile
        assert "era_distribution" in profile
        assert "energy_profile" in profile
        assert "variety_score" in profile
        assert "storefront" in profile
        assert profile["storefront"] == "us"

    def test_exits_on_no_track_data(self, monkeypatch):
        monkeypatch.setattr("taste_profiler.require_env_tokens", lambda: None)
        monkeypatch.setattr("taste_profiler.check_token_expiry", lambda: None)
        monkeypatch.setattr("taste_profiler.get_storefront", lambda sf=None: "us")
        monkeypatch.setattr("taste_profiler.call_api", lambda *a, **kw: None)

        args = MagicMock()
        args.verbose = False
        args.storefront = "us"
        args.skip_replay = True
        with pytest.raises(SystemExit):
            build_profile(args)

    def test_skip_replay(self, monkeypatch):
        self._mock_all_apis(monkeypatch)
        call_log = []
        original_mock = MagicMock()

        def tracking_api(command, *args, **kwargs):
            call_log.append(command)
            if command == "recent-tracks":
                return [{"id": "t1", "attributes": {"name": "S", "artistName": "A", "genreNames": ["Rock"], "releaseDate": "2020-01-01"}, "relationships": {"artists": {"data": [{"id": "a1"}]}}}]
            elif command in ("library-artists", "library-songs"):
                return {"data": []}
            return None

        monkeypatch.setattr("taste_profiler.require_env_tokens", lambda: None)
        monkeypatch.setattr("taste_profiler.check_token_expiry", lambda: None)
        monkeypatch.setattr("taste_profiler.get_storefront", lambda sf=None: "us")
        monkeypatch.setattr("taste_profiler.call_api", tracking_api)

        args = MagicMock()
        args.verbose = False
        args.storefront = "us"
        args.skip_replay = True
        build_profile(args)
        assert "replay-summary" not in call_log

    def test_expired_token_exits(self, monkeypatch):
        monkeypatch.setattr("taste_profiler.require_env_tokens", lambda: None)
        monkeypatch.setattr("taste_profiler.check_token_expiry", lambda: {
            "expired": True, "warning": True, "message": "Token expired",
            "days_remaining": 0,
        })

        args = MagicMock()
        args.verbose = False
        args.storefront = "us"
        args.skip_replay = True
        with pytest.raises(SystemExit):
            build_profile(args)


# ── main ─────────────────────────────────────────────────────────

class TestTasteProfilerMain:
    def test_main_uses_cache(self, monkeypatch, tmp_path, capsys):
        cache_file = tmp_path / "cache.json"
        cache_data = {"cached": True, "top_artists": []}
        cache_file.write_text(json.dumps(cache_data))

        monkeypatch.setattr(sys, "argv", [
            "taste_profiler.py",
            "--cache", str(cache_file),
            "--max-age", "9999",
        ])
        tp.main()
        captured = capsys.readouterr()
        assert "cached" in captured.out

    def test_main_writes_output(self, monkeypatch, tmp_path):
        output_file = tmp_path / "out" / "profile.json"

        monkeypatch.setattr(sys, "argv", [
            "taste_profiler.py",
            "--output", str(output_file),
        ])
        monkeypatch.setattr("taste_profiler.require_env_tokens", lambda: None)
        monkeypatch.setattr("taste_profiler.check_token_expiry", lambda: None)
        monkeypatch.setattr("taste_profiler.get_storefront", lambda sf=None: "us")

        tracks = [{"id": "t1", "attributes": {"name": "S", "artistName": "A", "genreNames": ["Rock"], "releaseDate": "2020-01-01"}, "relationships": {"artists": {"data": [{"id": "a1"}]}}}]

        def mock_api(command, *args, **kwargs):
            if command == "recent-tracks":
                return tracks
            elif command in ("library-artists", "library-songs"):
                return {"data": []}
            return None

        monkeypatch.setattr("taste_profiler.call_api", mock_api)
        tp.main()
        assert output_file.exists()
        data = json.loads(output_file.read_text())
        assert "top_artists" in data

    def test_main_saves_cache(self, monkeypatch, tmp_path, capsys):
        cache_file = tmp_path / "new_cache.json"

        monkeypatch.setattr(sys, "argv", [
            "taste_profiler.py",
            "--cache", str(cache_file),
            "--max-age", "0",  # force rebuild
        ])
        monkeypatch.setattr("taste_profiler.require_env_tokens", lambda: None)
        monkeypatch.setattr("taste_profiler.check_token_expiry", lambda: None)
        monkeypatch.setattr("taste_profiler.get_storefront", lambda sf=None: "us")

        tracks = [{"id": "t1", "attributes": {"name": "S", "artistName": "A", "genreNames": ["Rock"], "releaseDate": "2020-01-01"}, "relationships": {"artists": {"data": [{"id": "a1"}]}}}]

        def mock_api(command, *args, **kwargs):
            if command == "recent-tracks":
                return tracks
            elif command in ("library-artists", "library-songs"):
                return {"data": []}
            return None

        monkeypatch.setattr("taste_profiler.call_api", mock_api)
        tp.main()
        assert cache_file.exists()
