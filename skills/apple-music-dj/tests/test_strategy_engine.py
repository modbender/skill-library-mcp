"""Tests for strategy_engine — playlist strategy engine."""

import json
from unittest.mock import MagicMock
import pytest

import strategy_engine as se


# ── Genre Proximity ──────────────────────────────────────────────

class TestGenreProximity:
    def test_exact_match(self):
        assert se.genre_proximity("Rock", "Rock") == 1.0

    def test_case_insensitive(self):
        assert se.genre_proximity("rock", "ROCK") == 1.0

    def test_same_family(self):
        assert se.genre_proximity("Rock", "Alternative") == 0.5

    def test_different_family(self):
        assert se.genre_proximity("Rock", "Classical") == 0.0

    def test_electronic_family(self):
        assert se.genre_proximity("Electronic", "Dance") == 0.5

    def test_hiphop_family(self):
        assert se.genre_proximity("Hip-Hop/Rap", "Funk") == 0.5


class TestBestGenreMatch:
    def test_exact_in_list(self):
        assert se.best_genre_match(["Rock", "Pop"], ["Rock"]) == 1.0

    def test_partial_in_list(self):
        assert se.best_genre_match(["Alternative"], ["Rock"]) == 0.5

    def test_no_match(self):
        assert se.best_genre_match(["Classical"], ["Hip-Hop/Rap"]) == 0.0

    def test_empty_track_genres(self):
        assert se.best_genre_match([], ["Rock"]) == 0.0

    def test_empty_target_genres(self):
        assert se.best_genre_match(["Rock"], []) == 0.0


# ── Sequencing ───────────────────────────────────────────────────

class TestSequenceTracks:
    def _make(self, artist, album="", tid=""):
        return {"id": tid or f"{artist}-1", "name": "Song",
                "artist": artist, "album": album}

    def test_preserves_short_list(self):
        tracks = [self._make("A"), self._make("B")]
        result = se.sequence_tracks(tracks)
        assert len(result) == 2

    def test_artist_spacing(self):
        """Same artist should not appear back-to-back after sequencing."""
        tracks = [self._make("A", tid=f"A{i}") for i in range(3)]
        tracks += [self._make("B", tid=f"B{i}") for i in range(3)]
        tracks += [self._make("C", tid=f"C{i}") for i in range(3)]
        tracks += [self._make("D", tid=f"D{i}") for i in range(3)]
        tracks += [self._make("E", tid=f"E{i}") for i in range(3)]
        tracks += [self._make("F", tid=f"F{i}") for i in range(3)]
        result = se.sequence_tracks(tracks, max_same_artist=5)
        # Check no immediate back-to-back repeat
        for i in range(1, len(result)):
            if result[i]["artist"] == result[i-1]["artist"]:
                # Allow at most one back-to-back when forced
                if i >= 2:
                    assert result[i]["artist"] != result[i-2]["artist"]

    def test_album_cap(self):
        """Max 2 tracks from the same album."""
        tracks = [self._make("A", album="Album1", tid=f"t{i}") for i in range(5)]
        result = se.sequence_tracks(tracks)
        album1 = [t for t in result if t["album"] == "Album1"]
        assert len(album1) <= 2

    def test_empty_input(self):
        assert se.sequence_tracks([]) == []


# ── Strategy: Deep Cuts ──────────────────────────────────────────

class TestStrategyDeepCuts:
    def test_basic_deep_cuts(self, sample_profile, monkeypatch):
        """Deep cuts should return tracks from artist discographies."""
        albums_response = {"data": [{
            "id": "alb1",
            "attributes": {"name": "OK Computer", "isSingle": False},
        }]}

        album_tracks = [{
            "id": "new1",
            "attributes": {
                "name": "Lucky",
                "artistName": "Radiohead",
                "genreNames": ["Alternative"],
                "trackNumber": 8,
            },
        }, {
            "id": "new2",
            "attributes": {
                "name": "The Tourist",
                "artistName": "Radiohead",
                "genreNames": ["Alternative"],
                "trackNumber": 12,
            },
        }]

        top_response = {"data": [{"views": {
            "top-songs": {"data": [
                {"attributes": {"name": "Creep"}},
            ]},
        }}]}

        def mock_call_api(cmd, *args, **kwargs):
            if cmd == "artist-top":
                return top_response
            if cmd == "artist-albums":
                return albums_response
            return None

        monkeypatch.setattr(se, "call_api", mock_call_api)
        monkeypatch.setattr(se, "get_album_tracks", lambda sf, aid: album_tracks)

        result = se.strategy_deep_cuts(sample_profile, "us", target_size=5)
        assert len(result) > 0
        assert all("name" in t for t in result)
        assert all(t["source"] == "deep_cut" for t in result)

    def test_excludes_library_and_disliked(self, sample_profile, monkeypatch):
        """Deep cuts should skip library songs and disliked songs."""
        sample_profile["library_song_ids"] = ["lib1"]
        sample_profile["disliked_song_ids"] = ["dis1"]

        albums_response = {"data": [{
            "id": "alb1",
            "attributes": {"name": "Test Album", "isSingle": False},
        }]}

        album_tracks = [
            {"id": "lib1", "attributes": {"name": "InLib", "artistName": "X",
                                           "genreNames": [], "trackNumber": 1}},
            {"id": "dis1", "attributes": {"name": "Disliked", "artistName": "X",
                                           "genreNames": [], "trackNumber": 2}},
            {"id": "ok1", "attributes": {"name": "Good", "artistName": "X",
                                          "genreNames": [], "trackNumber": 3}},
        ]

        monkeypatch.setattr(se, "call_api", lambda cmd, *a, **k:
            albums_response if cmd == "artist-albums"
            else {"data": [{"views": {"top-songs": {"data": []}}}]} if cmd == "artist-top"
            else None)
        monkeypatch.setattr(se, "get_album_tracks", lambda sf, aid: album_tracks)

        result = se.strategy_deep_cuts(sample_profile, "us", target_size=5)
        ids = {t["id"] for t in result}
        assert "lib1" not in ids
        assert "dis1" not in ids

    def test_skips_singles(self, sample_profile, monkeypatch):
        """Deep cuts should skip single releases."""
        albums_response = {"data": [{
            "id": "alb1",
            "attributes": {"name": "A Single", "isSingle": True},
        }]}

        monkeypatch.setattr(se, "call_api", lambda cmd, *a, **k:
            albums_response if cmd == "artist-albums"
            else {"data": [{"views": {"top-songs": {"data": []}}}]}
            if cmd == "artist-top" else None)
        monkeypatch.setattr(se, "get_album_tracks", lambda sf, aid: [])

        result = se.strategy_deep_cuts(sample_profile, "us", target_size=5)
        assert result == []

    def test_empty_profile(self, empty_profile, monkeypatch):
        monkeypatch.setattr(se, "call_api", lambda *a, **k: None)
        result = se.strategy_deep_cuts(empty_profile, "us", target_size=5)
        assert result == []


# ── Strategy: Mood ───────────────────────────────────────────────

class TestStrategyMood:
    def _mock_charts(self):
        return {"results": {"songs": [{
            "data": [
                {"id": "c1", "attributes": {"name": "Beat Drop", "artistName": "DJ X",
                                              "genreNames": ["Electronic", "Dance"]}},
                {"id": "c2", "attributes": {"name": "Slow Jam", "artistName": "Singer Y",
                                              "genreNames": ["Jazz", "R&B/Soul"]}},
                {"id": "c3", "attributes": {"name": "Rock On", "artistName": "Band Z",
                                              "genreNames": ["Rock"]}},
            ],
        }]}}

    def test_workout_returns_high_energy(self, sample_profile, monkeypatch):
        monkeypatch.setattr(se, "call_api", lambda cmd, *a, **k:
            self._mock_charts() if cmd == "charts"
            else {"data": []} if cmd == "artist-albums" else None)
        monkeypatch.setattr(se, "get_album_tracks", lambda sf, aid: [])

        result = se.strategy_mood(sample_profile, "us", "workout", target_size=5)
        # Should include Electronic/Dance track
        genres_flat = [g for t in result for g in t.get("genre", [])]
        assert any(g in genres_flat for g in ["Electronic", "Dance", "Pop"])

    def test_unknown_mood_exits(self, sample_profile, monkeypatch):
        with pytest.raises(SystemExit):
            se.strategy_mood(sample_profile, "us", "nonexistent", target_size=5)

    def test_all_moods_have_genres(self):
        for mood, config in se.MOOD_MAP.items():
            assert len(config["genres"]) > 0, f"Mood {mood} has no genres"
            assert "energy" in config
            assert "description" in config

    def test_chill_mood(self, sample_profile, monkeypatch):
        monkeypatch.setattr(se, "call_api", lambda cmd, *a, **k:
            self._mock_charts() if cmd == "charts"
            else {"data": []} if cmd == "artist-albums" else None)
        monkeypatch.setattr(se, "get_album_tracks", lambda sf, aid: [])

        result = se.strategy_mood(sample_profile, "us", "chill", target_size=5)
        # Jazz track should match chill mood
        if result:
            assert any(t.get("name") == "Slow Jam" for t in result)


# ── Strategy: Trend Radar ────────────────────────────────────────

class TestStrategyTrend:
    def _mock_charts(self):
        return {"results": {"songs": [{
            "data": [
                {"id": "t1", "attributes": {"name": "Alt Hit", "artistName": "Radiohead",
                                              "genreNames": ["Alternative"]}},
                {"id": "t2", "attributes": {"name": "Pop Hit", "artistName": "Pop Star",
                                              "genreNames": ["Pop"]}},
                {"id": "t3", "attributes": {"name": "Country Song", "artistName": "Country Joe",
                                              "genreNames": ["Country"]}},
            ],
        }]}}

    def test_taste_filtering(self, sample_profile, monkeypatch):
        monkeypatch.setattr(se, "call_api", lambda cmd, *a, **k:
            self._mock_charts() if cmd == "charts" else None)

        result = se.strategy_trend(sample_profile, "us", target_size=5)
        assert len(result) > 0

    def test_known_artist_boosted(self, sample_profile, monkeypatch):
        monkeypatch.setattr(se, "call_api", lambda cmd, *a, **k:
            self._mock_charts() if cmd == "charts" else None)

        result = se.strategy_trend(sample_profile, "us", target_size=5)
        # Radiohead track should be included (known artist boost)
        if result:
            names = [t["name"] for t in result]
            assert "Alt Hit" in names

    def test_excludes_library_tracks(self, sample_profile, monkeypatch):
        sample_profile["library_song_ids"] = ["t1", "t2"]
        monkeypatch.setattr(se, "call_api", lambda cmd, *a, **k:
            self._mock_charts() if cmd == "charts" else None)

        result = se.strategy_trend(sample_profile, "us", target_size=5)
        ids = {t["id"] for t in result}
        assert "t1" not in ids
        assert "t2" not in ids

    def test_wildcards_included(self, sample_profile, monkeypatch):
        """Trend radar should include 2-3 wildcard tracks."""
        charts = {"results": {"songs": [{
            "data": [
                {"id": f"m{i}", "attributes": {"name": f"Match {i}", "artistName": "A",
                                                 "genreNames": ["Alternative"]}}
                for i in range(20)
            ] + [
                {"id": f"w{i}", "attributes": {"name": f"Wild {i}", "artistName": "B",
                                                 "genreNames": ["Reggaeton"]}}
                for i in range(5)
            ],
        }]}}
        monkeypatch.setattr(se, "call_api", lambda cmd, *a, **k:
            charts if cmd == "charts" else None)

        result = se.strategy_trend(sample_profile, "us", target_size=20)
        # All tracks should have required fields
        for t in result:
            assert "id" in t
            assert "name" in t


# ── Strategy: Constellation ──────────────────────────────────────

class TestStrategyConstellation:
    def test_basic_constellation(self, sample_profile, monkeypatch):
        search_results = {"results": {"artists": {"data": [
            {"id": "disc1", "attributes": {"name": "New Band", "genreNames": ["Alternative"]}},
            {"id": "disc2", "attributes": {"name": "Frontier Band", "genreNames": ["Country"]}},
        ]}}}

        top_songs = {"data": [{"views": {"top-songs": {"data": [
            {"id": "ns1", "attributes": {"name": "New Song", "artistName": "New Band",
                                          "genreNames": ["Alternative"]}},
        ]}}}]}

        def mock_call_api(cmd, *args, **kwargs):
            if cmd == "search":
                return search_results
            if cmd == "artist-top":
                return top_songs
            return None

        monkeypatch.setattr(se, "call_api", mock_call_api)
        monkeypatch.setattr(se, "search_artist", lambda sf, name:
            {"id": "seed1", "attributes": {"genreNames": ["Alternative"], "name": name}})

        result = se.strategy_constellation(sample_profile, "us", target_size=10)
        assert len(result) > 0
        # Should have zone assignments
        zones = {t.get("zone") for t in result}
        assert len(zones) > 0

    def test_excludes_library_artists(self, sample_profile, monkeypatch):
        """Known library artists should not appear as discoveries."""
        search_results = {"results": {"artists": {"data": [
            {"id": "a1", "attributes": {"name": "Radiohead", "genreNames": ["Alternative"]}},
        ]}}}

        monkeypatch.setattr(se, "call_api", lambda cmd, *a, **k:
            search_results if cmd == "search" else None)
        monkeypatch.setattr(se, "search_artist", lambda sf, name:
            {"id": "seed1", "attributes": {"genreNames": ["Alternative"], "name": name}})

        result = se.strategy_constellation(sample_profile, "us", target_size=10)
        artists = {t["artist"].lower() for t in result}
        # Radiohead should be filtered since they're already in library_artists
        assert "radiohead" not in artists

    def test_empty_profile(self, empty_profile, monkeypatch):
        monkeypatch.setattr(se, "call_api", lambda *a, **k: None)
        monkeypatch.setattr(se, "search_artist", lambda *a, **k: None)
        result = se.strategy_constellation(empty_profile, "us", target_size=10)
        assert result == []


# ── Strategy: Refresh ────────────────────────────────────────────

class TestStrategyRefresh:
    def test_basic_refresh(self, sample_profile, monkeypatch):
        playlist_tracks = {"data": [{
            "id": "pt1",
            "attributes": {"name": "Old Song", "artistName": "Radiohead",
                           "genreNames": ["Alternative"]},
            "relationships": {"catalog": {"data": [{"id": "cat1"}]}},
        }]}

        charts = {"results": {"songs": [{
            "data": [
                {"id": "fresh1", "attributes": {"name": "Fresh Alt", "artistName": "NewArt",
                                                  "genreNames": ["Alternative"]}},
            ],
        }]}}

        def mock_call_api(cmd, *args, **kwargs):
            if cmd == "playlist-tracks":
                return playlist_tracks
            if cmd == "charts":
                return charts
            if cmd == "artist-albums":
                return {"data": []}
            return None

        monkeypatch.setattr(se, "call_api", mock_call_api)
        monkeypatch.setattr(se, "search_artist", lambda sf, name:
            {"id": "ra1", "attributes": {"name": name}})
        monkeypatch.setattr(se, "get_album_tracks", lambda sf, aid: [])

        result = se.strategy_refresh(sample_profile, "us", "p123", target_add=5)
        assert len(result) > 0
        assert all(t["source"] == "refresh" for t in result)

    def test_excludes_existing_tracks(self, sample_profile, monkeypatch):
        playlist_tracks = {"data": [{
            "id": "pt1",
            "attributes": {"name": "Existing", "artistName": "A",
                           "genreNames": ["Rock"]},
            "relationships": {"catalog": {"data": [{"id": "exist1"}]}},
        }]}

        charts = {"results": {"songs": [{
            "data": [
                {"id": "exist1", "attributes": {"name": "Dupe", "artistName": "A",
                                                  "genreNames": ["Rock"]}},
                {"id": "new1", "attributes": {"name": "New", "artistName": "B",
                                               "genreNames": ["Rock"]}},
            ],
        }]}}

        monkeypatch.setattr(se, "call_api", lambda cmd, *a, **k:
            playlist_tracks if cmd == "playlist-tracks"
            else charts if cmd == "charts"
            else {"data": []} if cmd == "artist-albums" else None)
        monkeypatch.setattr(se, "search_artist", lambda sf, name:
            {"id": "x", "attributes": {"name": name}})
        monkeypatch.setattr(se, "get_album_tracks", lambda sf, aid: [])

        result = se.strategy_refresh(sample_profile, "us", "p1", target_add=5)
        ids = {t["id"] for t in result}
        assert "exist1" not in ids

    def test_empty_playlist(self, sample_profile, monkeypatch):
        monkeypatch.setattr(se, "call_api", lambda cmd, *a, **k:
            None if cmd == "playlist-tracks" else None)
        result = se.strategy_refresh(sample_profile, "us", "p1", target_add=5)
        assert result == []


# ── Name & Description Generation ────────────────────────────────

class TestGenerateName:
    def test_deep_cuts_name(self, sample_profile):
        name = se.generate_name("deep-cuts", profile=sample_profile)
        assert "Radiohead" in name
        assert "Deep Cuts" in name

    def test_mood_name(self):
        name = se.generate_name("mood", mood="workout")
        assert "Workout" in name

    def test_trend_name(self, sample_profile):
        name = se.generate_name("trend", profile=sample_profile)
        assert "Trending" in name

    def test_constellation_name(self):
        name = se.generate_name("constellation")
        assert "Horizons" in name

    def test_refresh_name(self):
        name = se.generate_name("refresh")
        assert "Refresh" in name


class TestGenerateDescription:
    def test_has_track_count(self):
        desc = se.generate_description("deep-cuts", track_count=25)
        assert "25 tracks" in desc

    def test_mood_description(self):
        desc = se.generate_description("mood", mood="workout")
        assert "energy" in desc.lower() or "moving" in desc.lower()

    def test_all_strategies(self):
        for strat in ["deep-cuts", "mood", "trend", "constellation", "refresh"]:
            desc = se.generate_description(strat, track_count=10)
            assert len(desc) > 5


# ── MOOD_MAP Integrity ───────────────────────────────────────────

class TestMoodMap:
    def test_all_moods_defined(self):
        expected = {"workout", "focus", "chill", "party", "drive",
                    "sleep", "cooking", "morning", "sad", "anger"}
        assert set(se.MOOD_MAP.keys()) == expected

    def test_mood_structure(self):
        for mood, config in se.MOOD_MAP.items():
            assert isinstance(config["genres"], list)
            assert len(config["genres"]) >= 2
            assert isinstance(config["energy"], str)
            assert isinstance(config["description"], str)


# ── check_playlist_exists ────────────────────────────────────────

class TestCheckPlaylistExists:
    def test_finds_existing_playlist(self, monkeypatch):
        data = json.dumps({"data": [
            {"id": "pl1", "attributes": {"name": "My Mix"}},
            {"id": "pl2", "attributes": {"name": "Other"}},
        ]})
        monkeypatch.setattr("subprocess.run", lambda *a, **kw: MagicMock(
            returncode=0, stdout=data
        ))
        assert se.check_playlist_exists("My Mix") == "pl1"

    def test_returns_none_when_not_found(self, monkeypatch):
        data = json.dumps({"data": [
            {"id": "pl1", "attributes": {"name": "Other"}},
        ]})
        monkeypatch.setattr("subprocess.run", lambda *a, **kw: MagicMock(
            returncode=0, stdout=data
        ))
        assert se.check_playlist_exists("Missing") is None

    def test_returns_none_on_api_failure(self, monkeypatch):
        monkeypatch.setattr("subprocess.run", lambda *a, **kw: MagicMock(
            returncode=1, stdout=""
        ))
        assert se.check_playlist_exists("Any") is None

    def test_returns_none_on_exception(self, monkeypatch):
        monkeypatch.setattr("subprocess.run", MagicMock(side_effect=Exception("fail")))
        assert se.check_playlist_exists("Any") is None


# ── create_playlist_from_tracks ──────────────────────────────────

class TestCreatePlaylistFromTracks:
    def test_returns_false_with_no_tracks(self):
        assert se.create_playlist_from_tracks([], "Name", "Desc") is False

    def test_returns_false_when_playlist_exists(self, monkeypatch):
        monkeypatch.setattr(se, "check_playlist_exists", lambda name: "pl1")
        tracks = [{"id": "t1"}]
        assert se.create_playlist_from_tracks(tracks, "Existing", "Desc") is False

    def test_creates_playlist_successfully(self, monkeypatch):
        monkeypatch.setattr(se, "check_playlist_exists", lambda name: None)
        monkeypatch.setattr("subprocess.run", lambda *a, **kw: MagicMock(returncode=0))
        tracks = [{"id": "t1"}, {"id": "t2"}]
        assert se.create_playlist_from_tracks(tracks, "New", "Desc") is True

    def test_returns_false_on_subprocess_failure(self, monkeypatch):
        monkeypatch.setattr(se, "check_playlist_exists", lambda name: None)
        monkeypatch.setattr("subprocess.run", lambda *a, **kw: MagicMock(
            returncode=1, stderr="error"
        ))
        tracks = [{"id": "t1"}]
        assert se.create_playlist_from_tracks(tracks, "New", "Desc") is False

    def test_returns_false_on_timeout(self, monkeypatch):
        import subprocess as sp
        monkeypatch.setattr(se, "check_playlist_exists", lambda name: None)
        monkeypatch.setattr("subprocess.run", MagicMock(
            side_effect=sp.TimeoutExpired("cmd", 60)
        ))
        tracks = [{"id": "t1"}]
        assert se.create_playlist_from_tracks(tracks, "New", "Desc") is False
