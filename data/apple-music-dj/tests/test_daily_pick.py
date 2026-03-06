"""Tests for daily_pick.py — scoring, seeding, and time context."""

import random
from datetime import datetime, timezone
from unittest.mock import patch

import pytest

from daily_pick import daily_seed, get_time_context, score_candidate, get_candidates, cmd_daily, cmd_now


# ── daily_seed ───────────────────────────────────────────────────

class TestDailySeed:
    def test_returns_int(self):
        assert isinstance(daily_seed(), int)

    def test_deterministic_same_day(self):
        assert daily_seed() == daily_seed()

    def test_different_days_differ(self):
        with patch("daily_pick.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2025, 1, 1, tzinfo=timezone.utc)
            mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
            seed_a = daily_seed()

        with patch("daily_pick.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2025, 1, 2, tzinfo=timezone.utc)
            mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
            seed_b = daily_seed()

        assert seed_a != seed_b


# ── get_time_context ─────────────────────────────────────────────

class TestGetTimeContext:
    @pytest.mark.parametrize("hour,expected_period", [
        (5, "morning"),
        (8, "morning"),
        (9, "mid-morning"),
        (11, "mid-morning"),
        (12, "midday"),
        (13, "midday"),
        (14, "afternoon"),
        (16, "afternoon"),
        (17, "evening"),
        (19, "evening"),
        (20, "night"),
        (22, "night"),
        (23, "late-night"),
        (0, "late-night"),
        (3, "late-night"),
        (4, "late-night"),
    ])
    def test_period_boundaries(self, hour, expected_period):
        with patch("daily_pick.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2025, 1, 1, hour, 0, 0)
            ctx = get_time_context()
            assert ctx["period"] == expected_period

    def test_context_has_required_keys(self):
        ctx = get_time_context()
        assert "period" in ctx
        assert "energy" in ctx
        assert "mood" in ctx
        assert "genres_boost" in ctx
        assert isinstance(ctx["genres_boost"], list)


# ── score_candidate ──────────────────────────────────────────────

class TestScoreCandidate:
    """These tests would have caught the rng keyword argument bug."""

    @pytest.fixture
    def base_candidate(self):
        return {
            "id": "t1",
            "name": "Test Song",
            "artist": "Test Artist",
            "genre": ["Rock"],
            "source": "charts",
        }

    @pytest.fixture
    def deep_cut(self):
        return {
            "id": "t2",
            "name": "Deep Cut",
            "artist": "Test Artist",
            "genre": ["Rock"],
            "source": "deep_cut",
        }

    def test_base_score(self, base_candidate, sample_profile):
        rng = random.Random(42)
        score = score_candidate(base_candidate, sample_profile, rng=rng)
        assert 0.5 <= score <= 0.8  # base 0.5 + random(0, 0.3)

    def test_deep_cut_bonus(self, deep_cut, sample_profile):
        rng = random.Random(42)
        score = score_candidate(deep_cut, sample_profile, rng=rng)
        assert score >= 0.7  # base 0.5 + 0.2 deep_cut + random

    def test_deep_cut_scores_higher(self, base_candidate, deep_cut, sample_profile):
        """Deep cuts should consistently score higher (same RNG seed)."""
        rng1 = random.Random(42)
        rng2 = random.Random(42)
        normal = score_candidate(base_candidate, sample_profile, rng=rng1)
        deep = score_candidate(deep_cut, sample_profile, rng=rng2)
        assert deep > normal

    def test_genre_context_boost(self, base_candidate, sample_profile):
        context = {"genres_boost": ["Rock"]}
        rng = random.Random(42)
        score_with = score_candidate(base_candidate, sample_profile, context, rng=rng)

        rng = random.Random(42)  # reset
        score_without = score_candidate(base_candidate, sample_profile, rng=rng)

        assert score_with > score_without

    def test_genre_boost_case_insensitive(self, sample_profile):
        candidate = {"genre": ["rock"], "source": "charts"}
        context = {"genres_boost": ["Rock"]}
        rng = random.Random(42)
        score = score_candidate(candidate, sample_profile, context, rng=rng)
        assert score > 0.5 + 0.3  # base + genre boost (at minimum)

    def test_deterministic_with_seeded_rng(self, base_candidate, sample_profile):
        rng1 = random.Random(99)
        rng2 = random.Random(99)
        s1 = score_candidate(base_candidate, sample_profile, rng=rng1)
        s2 = score_candidate(base_candidate, sample_profile, rng=rng2)
        assert s1 == s2

    def test_no_context(self, base_candidate, sample_profile):
        """Passing context=None should work without error."""
        score = score_candidate(base_candidate, sample_profile, None)
        assert isinstance(score, float)

    def test_rng_keyword_argument(self, base_candidate, sample_profile):
        """Regression: score_candidate must accept rng as keyword arg."""
        rng = random.Random(42)
        # This call would have crashed before the fix
        score = score_candidate(base_candidate, sample_profile, context=None, rng=rng)
        assert isinstance(score, float)


# ── get_candidates ───────────────────────────────────────────────

class TestGetCandidates:
    def test_returns_list(self, monkeypatch, sample_profile):
        # Mock all API calls to return empty/minimal data
        def mock_api(cmd, *args, **kw):
            if cmd == "artist-albums":
                return {"data": []}
            if cmd == "album-tracks":
                return {"data": []}
            if cmd == "charts":
                return {"results": {}}
            return None

        monkeypatch.setattr("daily_pick.call_api", mock_api)
        result = get_candidates(sample_profile, "us")
        assert isinstance(result, list)

    def test_excludes_library_songs(self, monkeypatch):
        profile = {
            "top_artists": [{"name": "Artist", "id": "a1"}],
            "library_song_ids": ["t1"],
            "genre_distribution": [{"genre": "Rock", "weight": 1.0}],
        }

        def mock_api(cmd, *args, **kw):
            if cmd == "artist-albums":
                return {"data": [{"id": "alb1", "attributes": {"name": "Album"}}]}
            if cmd == "album-tracks":
                return {
                    "data": [{
                        "relationships": {
                            "tracks": {
                                "data": [
                                    {"id": "t1", "attributes": {"name": "In Library",
                                                                 "artistName": "Artist",
                                                                 "genreNames": ["Rock"]}},
                                    {"id": "t2", "attributes": {"name": "Not In Library",
                                                                 "artistName": "Artist",
                                                                 "genreNames": ["Rock"]}},
                                ]
                            }
                        }
                    }]
                }
            if cmd == "charts":
                return {"results": {}}
            return None

        monkeypatch.setattr("daily_pick.call_api", mock_api)
        candidates = get_candidates(profile, "us")
        ids = [c["id"] for c in candidates]
        assert "t1" not in ids
        assert "t2" in ids

    def test_chart_candidates_filtered_by_genre(self, monkeypatch):
        profile = {
            "top_artists": [],
            "library_song_ids": [],
            "genre_distribution": [{"genre": "Rock", "weight": 0.5}],
        }

        def mock_api(cmd, *args, **kw):
            if cmd == "charts":
                return {
                    "results": {
                        "songs": [{
                            "data": [
                                {"id": "s1", "attributes": {"name": "Rock Song",
                                                             "artistName": "A",
                                                             "genreNames": ["Rock"]}},
                                {"id": "s2", "attributes": {"name": "Jazz Song",
                                                             "artistName": "B",
                                                             "genreNames": ["Jazz"]}},
                            ]
                        }]
                    }
                }
            return {"data": []} if cmd == "artist-albums" else None

        monkeypatch.setattr("daily_pick.call_api", mock_api)
        candidates = get_candidates(profile, "us")
        ids = [c["id"] for c in candidates]
        assert "s1" in ids
        assert "s2" not in ids


# ── cmd_daily ────────────────────────────────────────────────────

class TestCmdDaily:
    def test_returns_daily_pick(self, monkeypatch, sample_profile):
        def mock_api(cmd, *args, **kw):
            if cmd == "artist-albums":
                return {"data": [{"id": "alb1", "attributes": {"name": "Album"}}]}
            if cmd == "album-tracks":
                return {
                    "data": [{
                        "relationships": {
                            "tracks": {
                                "data": [
                                    {"id": "t99", "attributes": {
                                        "name": "Song", "artistName": "Radiohead",
                                        "genreNames": ["Rock"]
                                    }}
                                ]
                            }
                        }
                    }]
                }
            if cmd == "charts":
                return {"results": {}}
            return None

        monkeypatch.setattr("daily_pick.call_api", mock_api)
        result = cmd_daily(sample_profile, "us")
        assert result["type"] == "daily_song_drop"
        assert "track" in result
        assert "date" in result
        assert "message" in result

    def test_error_on_no_candidates(self, monkeypatch, sample_profile):
        monkeypatch.setattr("daily_pick.call_api", lambda *a, **kw: {"data": []})
        # Override get_candidates to return empty
        monkeypatch.setattr("daily_pick.get_candidates", lambda *a, **kw: [])
        result = cmd_daily(sample_profile, "us")
        assert "error" in result


# ── cmd_now ──────────────────────────────────────────────────────

class TestCmdNow:
    def test_returns_instant_recommendation(self, monkeypatch, sample_profile):
        def mock_api(cmd, *args, **kw):
            if cmd == "artist-albums":
                return {"data": [{"id": "alb1", "attributes": {"name": "Album"}}]}
            if cmd == "album-tracks":
                return {
                    "data": [{
                        "relationships": {
                            "tracks": {
                                "data": [
                                    {"id": "t99", "attributes": {
                                        "name": "Song", "artistName": "Radiohead",
                                        "album": "Album",
                                        "genreNames": ["Rock"]
                                    }}
                                ]
                            }
                        }
                    }]
                }
            if cmd == "charts":
                return {"results": {}}
            return None

        monkeypatch.setattr("daily_pick.call_api", mock_api)
        result = cmd_now(sample_profile, "us")
        assert result["type"] == "instant_recommendation"
        assert "context" in result
        assert "track" in result
        assert "message" in result

    def test_error_on_no_candidates(self, monkeypatch, sample_profile):
        monkeypatch.setattr("daily_pick.get_candidates", lambda *a, **kw: [])
        result = cmd_now(sample_profile, "us")
        assert "error" in result
