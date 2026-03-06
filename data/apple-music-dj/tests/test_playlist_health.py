"""Tests for playlist_health.py — playlist health checking and maintenance."""

import json
import sys
from unittest.mock import patch, MagicMock

import pytest

import playlist_health as phealth


# ── check_playlist ───────────────────────────────────────────────

class TestCheckPlaylist:
    def test_returns_error_when_no_tracks(self, monkeypatch):
        monkeypatch.setattr("playlist_health.call_api", lambda *a, **kw: None)
        result = phealth.check_playlist("pl1", "us")
        assert result["error"] == "Could not fetch playlist tracks"
        assert result["total_tracks"] == 0

    def test_returns_error_when_no_data_key(self, monkeypatch):
        monkeypatch.setattr("playlist_health.call_api", lambda *a, **kw: {"no": "data"})
        result = phealth.check_playlist("pl1", "us")
        assert "error" in result

    def test_healthy_playlist(self, monkeypatch):
        tracks = [
            {
                "id": "t1",
                "attributes": {"name": "Song A", "artistName": "Artist A"},
                "relationships": {"catalog": {"data": [{"id": "cat1"}]}},
            },
        ]

        def mock_api(command, *args, **kwargs):
            if command == "playlist-tracks":
                return {"data": tracks}
            elif command == "song-detail":
                return {"data": [{"id": "cat1"}]}
            return None

        monkeypatch.setattr("playlist_health.call_api", mock_api)
        result = phealth.check_playlist("pl1", "us")
        assert result["healthy"] is True
        assert result["removed_count"] == 0
        assert result["duplicate_count"] == 0
        assert result["total_tracks"] == 1

    def test_detects_removed_tracks(self, monkeypatch):
        tracks = [
            {
                "id": "t1",
                "attributes": {"name": "Gone Song", "artistName": "Artist A"},
                "relationships": {"catalog": {"data": [{"id": "cat1"}]}},
            },
        ]

        def mock_api(command, *args, **kwargs):
            if command == "playlist-tracks":
                return {"data": tracks}
            elif command == "song-detail":
                return {"data": []}  # track not found
            return None

        monkeypatch.setattr("playlist_health.call_api", mock_api)
        result = phealth.check_playlist("pl1", "us")
        assert result["removed_count"] == 1
        assert result["removed"][0]["name"] == "Gone Song"
        assert result["healthy"] is False

    def test_detects_duplicates(self, monkeypatch):
        tracks = [
            {
                "id": "t1",
                "attributes": {"name": "Song A", "artistName": "A"},
                "relationships": {"catalog": {"data": [{"id": "cat1"}]}},
            },
            {
                "id": "t2",
                "attributes": {"name": "Song A", "artistName": "A"},
                "relationships": {"catalog": {"data": [{"id": "cat1"}]}},
            },
        ]

        def mock_api(command, *args, **kwargs):
            if command == "playlist-tracks":
                return {"data": tracks}
            elif command == "song-detail":
                return {"data": [{"id": "cat1"}]}
            return None

        monkeypatch.setattr("playlist_health.call_api", mock_api)
        result = phealth.check_playlist("pl1", "us")
        assert result["duplicate_count"] == 1
        assert result["duplicates"][0]["count"] == 2

    def test_fallback_to_track_id_when_no_catalog(self, monkeypatch):
        tracks = [
            {
                "id": "t1",
                "attributes": {"name": "Song A", "artistName": "A"},
                "relationships": {},
            },
        ]

        def mock_api(command, *args, **kwargs):
            if command == "playlist-tracks":
                return {"data": tracks}
            elif command == "song-detail":
                return {"data": [{"id": "t1"}]}
            return None

        monkeypatch.setattr("playlist_health.call_api", mock_api)
        result = phealth.check_playlist("pl1", "us")
        assert result["total_tracks"] == 1
        assert result["healthy"] is True


# ── find_replacement ─────────────────────────────────────────────

class TestFindReplacement:
    def test_exact_artist_match(self, monkeypatch):
        search_result = {
            "results": {
                "songs": {
                    "data": [
                        {"id": "new1", "attributes": {"name": "Song A", "artistName": "Artist X"}},
                    ]
                }
            }
        }
        monkeypatch.setattr("playlist_health.call_api", lambda *a, **kw: search_result)
        result = phealth.find_replacement("us", "Song A", "Artist X")
        assert result is not None
        assert result["id"] == "new1"
        assert "approximate" not in result

    def test_approximate_match_when_no_exact(self, monkeypatch):
        search_result = {
            "results": {
                "songs": {
                    "data": [
                        {"id": "new1", "attributes": {"name": "Song A (Live)", "artistName": "Different Artist"}},
                    ]
                }
            }
        }
        monkeypatch.setattr("playlist_health.call_api", lambda *a, **kw: search_result)
        result = phealth.find_replacement("us", "Song A", "Artist X")
        assert result is not None
        assert result["approximate"] is True

    def test_returns_none_when_no_results(self, monkeypatch):
        monkeypatch.setattr("playlist_health.call_api", lambda *a, **kw: {"results": {"songs": {"data": []}}})
        result = phealth.find_replacement("us", "Song A", "Artist X")
        assert result is None

    def test_returns_none_when_api_fails(self, monkeypatch):
        monkeypatch.setattr("playlist_health.call_api", lambda *a, **kw: None)
        result = phealth.find_replacement("us", "Song A", "Artist X")
        assert result is None


# ── cmd_check ────────────────────────────────────────────────────

class TestCmdCheck:
    def test_check_single_playlist(self, monkeypatch):
        def mock_api(command, *args, **kwargs):
            if command == "playlist-tracks":
                return {"data": []}
            return None

        monkeypatch.setattr("playlist_health.call_api", mock_api)
        monkeypatch.setattr("playlist_health.require_env_tokens", lambda: None)
        monkeypatch.setattr("playlist_health.load_config", lambda: {"default_storefront": "us"})

        args = MagicMock()
        args.playlist_id = "pl1"
        args.storefront = None
        result = phealth.cmd_check(args)
        assert result["playlist_id"] == "pl1"

    def test_check_all_playlists(self, monkeypatch):
        def mock_api(command, *args, **kwargs):
            if command == "library-playlists":
                return {"data": [
                    {"id": "pl1", "attributes": {"name": "Mix 1"}},
                    {"id": "pl2", "attributes": {"name": "Mix 2"}},
                ]}
            elif command == "playlist-tracks":
                return {"data": []}
            return None

        monkeypatch.setattr("playlist_health.call_api", mock_api)
        monkeypatch.setattr("playlist_health.require_env_tokens", lambda: None)
        monkeypatch.setattr("playlist_health.load_config", lambda: {"default_storefront": "us"})

        args = MagicMock()
        args.playlist_id = "all"
        args.storefront = None
        result = phealth.cmd_check(args)
        assert result["playlists_checked"] == 2

    def test_check_all_api_failure(self, monkeypatch):
        monkeypatch.setattr("playlist_health.call_api", lambda *a, **kw: None)
        monkeypatch.setattr("playlist_health.require_env_tokens", lambda: None)
        monkeypatch.setattr("playlist_health.load_config", lambda: {})

        args = MagicMock()
        args.playlist_id = "all"
        args.storefront = "us"
        result = phealth.cmd_check(args)
        assert "error" in result

    def test_check_uses_storefront_override(self, monkeypatch):
        captured_sf = {}

        def mock_check(pid, sf):
            captured_sf["sf"] = sf
            return {"playlist_id": pid, "total_tracks": 0, "removed": [],
                    "removed_count": 0, "duplicates": [], "duplicate_count": 0, "healthy": True}

        monkeypatch.setattr("playlist_health.check_playlist", mock_check)
        monkeypatch.setattr("playlist_health.require_env_tokens", lambda: None)
        monkeypatch.setattr("playlist_health.load_config", lambda: {})

        args = MagicMock()
        args.playlist_id = "pl1"
        args.storefront = "gb"
        phealth.cmd_check(args)
        assert captured_sf["sf"] == "gb"


# ── cmd_fix ──────────────────────────────────────────────────────

class TestCmdFix:
    def test_fix_no_issues(self, monkeypatch):
        monkeypatch.setattr("playlist_health.require_env_tokens", lambda: None)
        monkeypatch.setattr("playlist_health.load_config", lambda: {"default_storefront": "us"})
        monkeypatch.setattr("playlist_health.check_playlist", lambda pid, sf: {
            "playlist_id": pid, "total_tracks": 5, "removed": [], "removed_count": 0,
            "duplicates": [], "duplicate_count": 0, "healthy": True,
        })

        args = MagicMock()
        args.playlist_id = "pl1"
        args.storefront = None
        args.auto = False
        result = phealth.cmd_fix(args)
        assert result["issues_found"] == 0

    def test_fix_dry_run_duplicates(self, monkeypatch):
        monkeypatch.setattr("playlist_health.require_env_tokens", lambda: None)
        monkeypatch.setattr("playlist_health.load_config", lambda: {"default_storefront": "us"})
        monkeypatch.setattr("playlist_health.check_playlist", lambda pid, sf: {
            "playlist_id": pid, "total_tracks": 5, "removed": [], "removed_count": 0,
            "duplicates": [{"id": "cat1", "count": 3}], "duplicate_count": 1, "healthy": False,
        })

        args = MagicMock()
        args.playlist_id = "pl1"
        args.storefront = None
        args.auto = False
        result = phealth.cmd_fix(args)
        assert len(result["actions_taken"]) == 1
        assert "WOULD remove" in result["actions_taken"][0]

    def test_fix_auto_duplicates(self, monkeypatch):
        monkeypatch.setattr("playlist_health.require_env_tokens", lambda: None)
        monkeypatch.setattr("playlist_health.load_config", lambda: {"default_storefront": "us"})
        monkeypatch.setattr("playlist_health.check_playlist", lambda pid, sf: {
            "playlist_id": pid, "total_tracks": 5, "removed": [], "removed_count": 0,
            "duplicates": [{"id": "cat1", "count": 2}], "duplicate_count": 1, "healthy": False,
        })
        monkeypatch.setattr("subprocess.run", lambda *a, **kw: MagicMock(returncode=0))

        args = MagicMock()
        args.playlist_id = "pl1"
        args.storefront = None
        args.auto = True
        result = phealth.cmd_fix(args)
        assert result["auto_applied"] is True
        assert any("Removed" in a for a in result["actions_taken"])

    def test_fix_removed_tracks_dry_run(self, monkeypatch):
        monkeypatch.setattr("playlist_health.require_env_tokens", lambda: None)
        monkeypatch.setattr("playlist_health.load_config", lambda: {"default_storefront": "us"})
        monkeypatch.setattr("playlist_health.check_playlist", lambda pid, sf: {
            "playlist_id": pid, "total_tracks": 5,
            "removed": [{"id": "cat1", "name": "Gone", "artist": "Artist"}],
            "removed_count": 1, "duplicates": [], "duplicate_count": 0, "healthy": False,
        })
        monkeypatch.setattr("playlist_health.find_replacement", lambda sf, n, a: {
            "id": "new1", "name": "Gone (Remaster)", "artist": "Artist",
        })

        args = MagicMock()
        args.playlist_id = "pl1"
        args.storefront = None
        args.auto = False
        result = phealth.cmd_fix(args)
        assert any("WOULD replace" in a for a in result["actions_taken"])

    def test_fix_removed_no_replacement(self, monkeypatch):
        monkeypatch.setattr("playlist_health.require_env_tokens", lambda: None)
        monkeypatch.setattr("playlist_health.load_config", lambda: {"default_storefront": "us"})
        monkeypatch.setattr("playlist_health.check_playlist", lambda pid, sf: {
            "playlist_id": pid, "total_tracks": 5,
            "removed": [{"id": "cat1", "name": "Gone", "artist": "Artist"}],
            "removed_count": 1, "duplicates": [], "duplicate_count": 0, "healthy": False,
        })
        monkeypatch.setattr("playlist_health.find_replacement", lambda sf, n, a: None)

        args = MagicMock()
        args.playlist_id = "pl1"
        args.storefront = None
        args.auto = False
        result = phealth.cmd_fix(args)
        assert any("No replacement" in a for a in result["actions_taken"])

    def test_fix_auto_removed_with_replacement(self, monkeypatch):
        monkeypatch.setattr("playlist_health.require_env_tokens", lambda: None)
        monkeypatch.setattr("playlist_health.load_config", lambda: {"default_storefront": "us"})
        monkeypatch.setattr("playlist_health.check_playlist", lambda pid, sf: {
            "playlist_id": pid, "total_tracks": 5,
            "removed": [{"id": "cat1", "name": "Gone", "artist": "Artist"}],
            "removed_count": 1, "duplicates": [], "duplicate_count": 0, "healthy": False,
        })
        monkeypatch.setattr("playlist_health.find_replacement", lambda sf, n, a: {
            "id": "new1", "name": "Gone (Remaster)", "artist": "Artist",
        })
        monkeypatch.setattr("subprocess.run", lambda *a, **kw: MagicMock(returncode=0))

        args = MagicMock()
        args.playlist_id = "pl1"
        args.storefront = None
        args.auto = True
        result = phealth.cmd_fix(args)
        assert any("Added replacement" in a for a in result["actions_taken"])

    def test_fix_returns_error_from_check(self, monkeypatch):
        monkeypatch.setattr("playlist_health.require_env_tokens", lambda: None)
        monkeypatch.setattr("playlist_health.load_config", lambda: {})
        monkeypatch.setattr("playlist_health.check_playlist", lambda pid, sf: {
            "error": "fail", "playlist_id": pid,
        })

        args = MagicMock()
        args.playlist_id = "pl1"
        args.storefront = "us"
        args.auto = False
        result = phealth.cmd_fix(args)
        assert result["error"] == "fail"


# ── main ─────────────────────────────────────────────────────────

class TestMain:
    def test_main_check(self, monkeypatch, capsys):
        monkeypatch.setattr(sys, "argv", ["playlist_health.py", "check", "pl1"])
        monkeypatch.setattr("playlist_health.require_env_tokens", lambda: None)
        monkeypatch.setattr("playlist_health.load_config", lambda: {"default_storefront": "us"})
        monkeypatch.setattr("playlist_health.call_api", lambda *a, **kw: {"data": []})
        phealth.main()
        captured = capsys.readouterr()
        assert "playlist_id" in captured.out

    def test_main_fix(self, monkeypatch, capsys):
        monkeypatch.setattr(sys, "argv", ["playlist_health.py", "fix", "pl1"])
        monkeypatch.setattr("playlist_health.require_env_tokens", lambda: None)
        monkeypatch.setattr("playlist_health.load_config", lambda: {"default_storefront": "us"})
        monkeypatch.setattr("playlist_health.check_playlist", lambda pid, sf: {
            "playlist_id": pid, "total_tracks": 0, "removed": [], "removed_count": 0,
            "duplicates": [], "duplicate_count": 0, "healthy": True,
        })
        phealth.main()
        captured = capsys.readouterr()
        assert "issues_found" in captured.out

    def test_main_no_command_exits(self, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["playlist_health.py"])
        with pytest.raises(SystemExit):
            phealth.main()
