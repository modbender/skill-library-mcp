from __future__ import annotations

import json
import pathlib
import sys
from types import SimpleNamespace
from urllib.error import URLError

import feedparser


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import search_feed_episodes as sfe  # noqa: E402


def _load_fixture_feed():
    fixture_path = ROOT / "tests" / "fixtures" / "sample_feed.xml"
    return feedparser.parse(fixture_path.read_bytes())


def test_search_schema_is_compact():
    parsed = _load_fixture_feed()
    episodes = sfe.entries_to_episodes(parsed.entries, "https://example.fm/feed.xml")
    payload = sfe.build_search_result(
        rss_url="https://example.fm/feed.xml",
        query="dark side sky",
        episodes=episodes,
        limit=3,
        use_semantic=False,
        include_snippet=False,
    )

    assert payload["ok"] is True
    assert set(payload.keys()) == {
        "ok",
        "mode",
        "rssUrl",
        "query",
        "semanticUsed",
        "candidateCount",
        "candidates",
    }
    assert payload["mode"] == "search"
    assert payload["candidateCount"] <= 3
    assert payload["candidates"]
    assert set(payload["candidates"][0].keys()) == {
        "guid",
        "title",
        "pubDate",
        "fallbackLink",
        "score",
    }


def test_newest_schema_and_ordering():
    parsed = _load_fixture_feed()
    episodes = sfe.entries_to_episodes(parsed.entries, "https://example.fm/feed.xml")
    payload = sfe.build_newest_result(
        rss_url="https://example.fm/feed.xml", episodes=episodes, limit=3
    )

    assert payload["ok"] is True
    assert payload["mode"] == "newest"
    assert set(payload.keys()) == {"ok", "mode", "rssUrl", "count", "items"}
    assert payload["count"] == 3
    assert payload["items"][0]["guid"] == "ep-orbital-logistics"
    assert payload["items"][1]["guid"] == "ep-econ-gravity"
    assert payload["items"][2]["guid"] == "ep-space-qa"


def test_overview_schema():
    parsed = _load_fixture_feed()
    episodes = sfe.entries_to_episodes(parsed.entries, "https://example.fm/feed.xml")
    payload = sfe.build_overview_result(
        rss_url="https://example.fm/feed.xml", parsed_feed=parsed, episodes=episodes
    )

    assert payload["ok"] is True
    assert payload["mode"] == "overview"
    assert set(payload.keys()) == {
        "ok",
        "mode",
        "rssUrl",
        "feedTitle",
        "feedDescriptionShort",
        "author",
        "language",
        "lastBuildDate",
        "itemCount",
    }
    assert payload["feedTitle"] == "Example Spacecast"
    assert payload["itemCount"] == 4


def test_ranking_prefers_strong_title_match():
    parsed = _load_fixture_feed()
    episodes = sfe.entries_to_episodes(parsed.entries, "https://example.fm/feed.xml")
    payload = sfe.build_search_result(
        rss_url="https://example.fm/feed.xml",
        query="dark side of the sky",
        episodes=episodes,
        limit=3,
        use_semantic=False,
        include_snippet=False,
    )
    assert payload["candidates"][0]["guid"] == "ep-dark-sky"
    assert payload["candidates"][0]["score"] >= payload["candidates"][1]["score"]


def test_fallback_resolution_precedence():
    parsed = _load_fixture_feed()
    episodes = sfe.entries_to_episodes(parsed.entries, "https://example.fm/feed.xml")
    by_guid = {episode.guid: episode for episode in episodes}

    # link preferred
    assert by_guid["ep-dark-sky"].fallback_link == "https://example.fm/episodes/dark-sky"
    # enclosure second
    assert (
        by_guid["ep-econ-gravity"].fallback_link
        == "https://cdn.example.fm/audio/econ-gravity.mp3"
    )
    # feed url fallback
    assert by_guid["ep-orbital-logistics"].fallback_link == "https://example.fm/feed.xml"


def test_run_fails_when_search_missing_query(capsys):
    exit_code = sfe.run(["--mode", "search", "--rss-url", "https://example.fm/feed.xml"])
    out = json.loads(capsys.readouterr().out)
    assert exit_code == 2
    assert out["ok"] is False
    assert out["error"]["type"] == "invalid_input"


def test_run_network_error(monkeypatch, capsys):
    def _raise(_rss_url):
        raise URLError("network down")

    monkeypatch.setattr(sfe, "fetch_feed", _raise)
    exit_code = sfe.run(["--mode", "newest", "--rss-url", "https://example.fm/feed.xml"])
    out = json.loads(capsys.readouterr().out)
    assert exit_code == 1
    assert out["ok"] is False
    assert out["error"]["type"] == "network_error"


def test_run_parse_error(monkeypatch, capsys):
    fake = SimpleNamespace(bozo=True, bozo_exception=Exception("bad xml"), entries=[], feed={})
    monkeypatch.setattr(sfe, "fetch_feed", lambda _rss_url: fake)
    exit_code = sfe.run(["--mode", "overview", "--rss-url", "https://example.fm/feed.xml"])
    out = json.loads(capsys.readouterr().out)
    assert exit_code == 1
    assert out["ok"] is False
    assert out["error"]["type"] == "parse_error"


def test_run_empty_feed(monkeypatch, capsys):
    fake = SimpleNamespace(bozo=False, entries=[], feed={"title": "t"})
    monkeypatch.setattr(sfe, "fetch_feed", lambda _rss_url: fake)
    exit_code = sfe.run(["--mode", "newest", "--rss-url", "https://example.fm/feed.xml"])
    out = json.loads(capsys.readouterr().out)
    assert exit_code == 1
    assert out["ok"] is False
    assert out["error"]["type"] == "empty_feed"
