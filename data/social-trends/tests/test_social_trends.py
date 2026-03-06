"""Tests for social-trends skill."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

_RUN_PATH = Path(__file__).resolve().parent.parent / "run.py"
_spec = importlib.util.spec_from_file_location("social_trends_run", _RUN_PATH)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

fetch_douyin_hot = _mod.fetch_douyin_hot
run = _mod.run


class TestFetchDouyinHot:
    def test_successful_fetch(self):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({
            "word_list": [
                {"position": 1, "word": "热搜话题1", "hot_value": 9999},
                {"position": 2, "word": "热搜话题2", "hot_value": 8888},
            ]
        }).encode()
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)

        with patch("urllib.request.urlopen", return_value=mock_resp):
            items = fetch_douyin_hot(limit=5)
            assert len(items) == 2
            assert items[0]["rank"] == 1
            assert items[0]["title"] == "热搜话题1"
            assert "douyin.com" in items[0]["url"]

    def test_api_failure_returns_empty(self):
        import urllib.error

        with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("fail")):
            items = fetch_douyin_hot()
            assert items == []

    def test_limit_parameter(self):
        mock_resp = MagicMock()
        many_items = [{"position": i, "word": f"topic{i}", "hot_value": 1000 - i} for i in range(50)]
        mock_resp.read.return_value = json.dumps({"word_list": many_items}).encode()
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)

        with patch("urllib.request.urlopen", return_value=mock_resp):
            items = fetch_douyin_hot(limit=3)
            assert len(items) == 3


class TestRun:
    def test_default_platform_all(self):
        with patch.object(_mod, "fetch_douyin_hot", return_value=[{"rank": 1, "title": "test"}]):
            result = run({})
            assert result["success"] is True
            assert "douyin" in result["platforms"]

    def test_filter_by_query(self):
        items = [
            {"rank": 1, "title": "Python 3.12 发布"},
            {"rank": 2, "title": "Java 新版本"},
        ]
        with patch.object(_mod, "fetch_douyin_hot", return_value=items):
            result = run({"query": "python"})
            assert len(result["platforms"]["douyin"]) == 1
            assert "Python" in result["platforms"]["douyin"][0]["title"]

    def test_total_count(self):
        with patch.object(_mod, "fetch_douyin_hot", return_value=[{"rank": 1, "title": "a"}, {"rank": 2, "title": "b"}]):
            result = run({})
            assert result["total"] == 2
