"""Tests for listening_insights.py — timeline, streaks, year-review."""

import pytest

from listening_insights import cmd_streaks, cmd_timeline, cmd_year_review


# ── cmd_timeline ─────────────────────────────────────────────────

class TestCmdTimeline:
    def test_returns_expected_keys(self, monkeypatch, sample_profile):
        # Mock call_api to return year-specific replay data
        def mock_api(command, *args, **kw):
            year = args[0] if args else "2024"
            return {
                "data": [{
                    "attributes": {
                        "year": int(year),
                        "topArtists": [{"name": "Radiohead"}],
                        "topGenres": [{"name": "Alternative"}],
                        "listenTimeInMinutes": 30000,
                        "topSongs": [{"name": "Everything In Its Right Place"}],
                    }
                }]
            }

        monkeypatch.setattr("listening_insights.call_api", mock_api)
        result = cmd_timeline(sample_profile)

        assert "timeline" in result
        assert "narrative" in result
        assert "current_top_genres" in result
        assert "current_top_artists" in result
        assert "replay_available" in result
        assert "years_covered" in result

    def test_timeline_entries_have_year(self, monkeypatch, sample_profile):
        def mock_api(command, *args, **kw):
            return {
                "data": [{
                    "attributes": {
                        "year": 2023,
                        "topArtists": [{"name": "Radiohead"}],
                        "topGenres": [{"name": "Rock"}],
                        "listenTimeInMinutes": 5000,
                    }
                }]
            }

        monkeypatch.setattr("listening_insights.call_api", mock_api)
        result = cmd_timeline(sample_profile)
        for entry in result["timeline"]:
            assert "year" in entry

    def test_narrative_contains_year(self, monkeypatch, sample_profile):
        def mock_api(command, *args, **kw):
            return {
                "data": [{
                    "attributes": {
                        "year": 2023,
                        "topArtists": [{"name": "Radiohead"}],
                        "topGenres": [{"name": "Rock"}],
                        "listenTimeInMinutes": 12000,
                    }
                }]
            }

        monkeypatch.setattr("listening_insights.call_api", mock_api)
        result = cmd_timeline(sample_profile)
        assert any("2023" in n for n in result["narrative"])

    def test_empty_replay(self, monkeypatch, sample_profile):
        monkeypatch.setattr("listening_insights.call_api", lambda *a, **kw: None)
        result = cmd_timeline(sample_profile)
        assert result["years_covered"] == 0
        assert result["timeline"] == []

    def test_current_profile_genres_included(self, monkeypatch, sample_profile):
        monkeypatch.setattr("listening_insights.call_api", lambda *a, **kw: None)
        result = cmd_timeline(sample_profile)
        assert "Alternative" in result["current_top_genres"]

    def test_current_profile_artists_included(self, monkeypatch, sample_profile):
        monkeypatch.setattr("listening_insights.call_api", lambda *a, **kw: None)
        result = cmd_timeline(sample_profile)
        assert "Radiohead" in result["current_top_artists"]


# ── cmd_streaks ──────────────────────────────────────────────────

class TestCmdStreaks:
    def test_returns_expected_keys(self, monkeypatch, sample_profile):
        monkeypatch.setattr("listening_insights.call_api", lambda *a, **kw: None)
        result = cmd_streaks(sample_profile)
        assert "milestones" in result
        assert "insights" in result
        assert "listening_velocity" in result
        assert "data_summary" in result

    def test_artist_loyalty_insight(self, monkeypatch):
        profile = {
            "top_artists": [{"name": "Radiohead", "count": 25}],
            "genre_distribution": [{"genre": "Alternative", "weight": 0.3}],
            "listening_velocity": "moderate",
            "data_summary": {"recent_tracks": 50, "library_songs": 200},
        }
        monkeypatch.setattr("listening_insights.call_api", lambda *a, **kw: None)
        result = cmd_streaks(profile)
        types = [i["type"] for i in result["insights"]]
        assert "artist_loyalty" in types

    def test_genre_dominance_insight(self, monkeypatch):
        profile = {
            "top_artists": [{"name": "X", "count": 5}],
            "genre_distribution": [{"genre": "Rock", "weight": 0.6}],
            "listening_velocity": "moderate",
            "data_summary": {"recent_tracks": 50, "library_songs": 100},
        }
        monkeypatch.setattr("listening_insights.call_api", lambda *a, **kw: None)
        result = cmd_streaks(profile)
        types = [i["type"] for i in result["insights"]]
        assert "genre_dominance" in types

    def test_no_insights_for_small_data(self, monkeypatch, empty_profile):
        monkeypatch.setattr("listening_insights.call_api", lambda *a, **kw: None)
        result = cmd_streaks(empty_profile)
        assert result["insights"] == []

    def test_milestones_from_api(self, monkeypatch, sample_profile):
        mock_milestones = {
            "data": [{
                "attributes": {
                    "kind": "listenCount",
                    "value": 10000,
                    "description": "You listened to 10,000 songs!",
                }
            }]
        }
        monkeypatch.setattr("listening_insights.call_api", lambda *a, **kw: mock_milestones)
        result = cmd_streaks(sample_profile)
        assert len(result["milestones"]) == 1
        assert result["milestones"][0]["type"] == "listenCount"

    def test_library_size_insight(self, monkeypatch):
        profile = {
            "top_artists": [{"name": "X", "count": 2}],
            "genre_distribution": [{"genre": "Rock", "weight": 0.3}],
            "listening_velocity": "moderate",
            "data_summary": {"recent_tracks": 10, "library_songs": 600},
        }
        monkeypatch.setattr("listening_insights.call_api", lambda *a, **kw: None)
        result = cmd_streaks(profile)
        types = [i["type"] for i in result["insights"]]
        assert "library_size" in types

    def test_active_rater_insight(self, monkeypatch):
        profile = {
            "top_artists": [{"name": "X", "count": 2}],
            "genre_distribution": [{"genre": "Rock", "weight": 0.3}],
            "listening_velocity": "moderate",
            "data_summary": {"recent_tracks": 10, "library_songs": 50, "loved_count": 75},
        }
        monkeypatch.setattr("listening_insights.call_api", lambda *a, **kw: None)
        result = cmd_streaks(profile)
        types = [i["type"] for i in result["insights"]]
        assert "active_rater" in types


# ── cmd_year_review ──────────────────────────────────────────────

class TestCmdYearReview:
    def test_returns_expected_keys(self, monkeypatch, sample_profile):
        mock_summary = {
            "data": [{
                "attributes": {
                    "listenTimeInMinutes": 30000,
                    "topArtists": [{"name": "Radiohead"}, {"name": "The Weeknd"}],
                    "topSongs": [{"name": "Idioteque", "artistName": "Radiohead"}],
                    "topAlbums": [{"name": "Kid A"}],
                    "topGenres": [{"name": "Alternative"}, {"name": "Electronic"}],
                }
            }]
        }
        monkeypatch.setattr("listening_insights.call_api",
                            lambda cmd, *a, **kw: mock_summary)
        result = cmd_year_review(sample_profile, 2024)
        assert result["year"] == 2024
        assert "replay_data" in result
        assert "insights" in result
        assert "obscurity_score" in result
        assert "variety_score" in result

    def test_listen_time_insight(self, monkeypatch, sample_profile):
        mock_summary = {
            "data": [{
                "attributes": {
                    "listenTimeInMinutes": 60000,
                    "topArtists": [{"name": "Radiohead"}],
                    "topSongs": [],
                    "topAlbums": [],
                    "topGenres": [{"name": "Alternative"}],
                }
            }]
        }
        monkeypatch.setattr("listening_insights.call_api",
                            lambda cmd, *a, **kw: mock_summary)
        result = cmd_year_review(sample_profile, 2024)
        assert any("hours" in insight for insight in result["insights"])

    def test_obscurity_score_range(self, monkeypatch, sample_profile):
        monkeypatch.setattr("listening_insights.call_api", lambda *a, **kw: None)
        result = cmd_year_review(sample_profile, 2024)
        assert 0 <= result["obscurity_score"] <= 100

    def test_no_replay_data(self, monkeypatch, sample_profile):
        monkeypatch.setattr("listening_insights.call_api", lambda *a, **kw: None)
        result = cmd_year_review(sample_profile, 2024)
        assert result["replay_available"] is False
        assert result["replay_data"] == {}

    def test_milestones_extracted(self, monkeypatch, sample_profile):
        call_count = {"n": 0}

        def mock_api(cmd, *args, **kw):
            call_count["n"] += 1
            if cmd == "replay-milestones":
                return {
                    "data": [{
                        "attributes": {"description": "You hit 1000 songs!"}
                    }]
                }
            return None

        monkeypatch.setattr("listening_insights.call_api", mock_api)
        result = cmd_year_review(sample_profile, 2024)
        assert "You hit 1000 songs!" in result["milestones"]

    def test_high_variety_insight(self, monkeypatch):
        profile = {
            "genre_distribution": [],
            "top_artists": [],
            "variety_score": 0.8,
            "mainstream_score": 0.3,
        }
        monkeypatch.setattr("listening_insights.call_api", lambda *a, **kw: None)
        result = cmd_year_review(profile, 2024)
        assert any("adventurous" in i for i in result["insights"])

    def test_low_variety_insight(self, monkeypatch):
        profile = {
            "genre_distribution": [],
            "top_artists": [],
            "variety_score": 0.2,
            "mainstream_score": 0.3,
        }
        monkeypatch.setattr("listening_insights.call_api", lambda *a, **kw: None)
        result = cmd_year_review(profile, 2024)
        assert any("deep" in i.lower() for i in result["insights"])

    def test_mainstream_insight(self, monkeypatch):
        profile = {
            "genre_distribution": [],
            "top_artists": [],
            "variety_score": 0.5,
            "mainstream_score": 0.7,
        }
        monkeypatch.setattr("listening_insights.call_api", lambda *a, **kw: None)
        result = cmd_year_review(profile, 2024)
        assert any("mainstream" in i for i in result["insights"])
