"""Tests for CLI commands using Click CliRunner."""

import json
import pytest
from click.testing import CliRunner
from unittest.mock import patch, AsyncMock, MagicMock
from bili_cli.cli import cli


@pytest.fixture
def runner():
    return CliRunner()


# ===== Login/Status =====


def test_status_not_logged_in(runner):
    with patch("bili_cli.cli.get_credential", return_value=None):
        result = runner.invoke(cli, ["status"])
        assert "未登录" in result.output
        assert result.exit_code == 0


def test_status_logged_in(runner, mock_user_info):
    mock_cred = MagicMock()
    with patch("bili_cli.cli.get_credential", return_value=mock_cred), \
         patch("bili_cli.client.get_self_info", new_callable=AsyncMock, return_value=mock_user_info):
        result = runner.invoke(cli, ["status"])
        assert "TestUP" in result.output
        assert "✅" in result.output


def test_logout(runner):
    with patch("bili_cli.cli.clear_credential") as mock_clear:
        result = runner.invoke(cli, ["logout"])
        assert "已注销" in result.output
        mock_clear.assert_called_once()


# ===== Video =====


def test_video_json(runner, mock_video_info):
    with patch("bili_cli.cli.get_credential", return_value=None), \
         patch("bili_cli.client.extract_bvid", return_value="BV1test123"), \
         patch("bili_cli.client.get_video_info", new_callable=AsyncMock, return_value=mock_video_info):
        result = runner.invoke(cli, ["video", "BV1test123", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["title"] == "测试视频标题"


def test_video_display(runner, mock_video_info):
    with patch("bili_cli.cli.get_credential", return_value=None), \
         patch("bili_cli.client.extract_bvid", return_value="BV1test123"), \
         patch("bili_cli.client.get_video_info", new_callable=AsyncMock, return_value=mock_video_info):
        result = runner.invoke(cli, ["video", "BV1test123"])
        assert result.exit_code == 0
        assert "测试视频标题" in result.output
        assert "BV1test123" in result.output


def test_video_invalid_bvid(runner):
    with patch("bili_cli.cli.get_credential", return_value=None):
        result = runner.invoke(cli, ["video", "invalid"])
        assert result.exit_code != 0


# ===== Hot =====


def test_hot_command(runner):
    mock_data = {
        "list": [
            {
                "bvid": "BV1hot",
                "title": "热门视频",
                "owner": {"name": "HotUP"},
                "stat": {"view": 100000, "like": 5000},
            }
        ]
    }
    with patch("bili_cli.cli.get_credential", return_value=None), \
         patch("bili_cli.client.get_hot_videos", new_callable=AsyncMock, return_value=mock_data):
        result = runner.invoke(cli, ["hot", "--max", "1"])
        assert result.exit_code == 0
        assert "BV1hot" in result.output
        assert "热门" in result.output


def test_hot_json(runner):
    mock_data = {"list": [{"bvid": "BV1hot", "title": "Hot"}]}
    with patch("bili_cli.cli.get_credential", return_value=None), \
         patch("bili_cli.client.get_hot_videos", new_callable=AsyncMock, return_value=mock_data):
        result = runner.invoke(cli, ["hot", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["list"][0]["bvid"] == "BV1hot"


# ===== Search =====


def test_search_user(runner):
    mock_results = [{"mid": 123, "uname": "TestUser", "fans": 1000, "videos": 10, "usign": "Hi"}]
    with patch("bili_cli.cli.get_credential", return_value=None), \
         patch("bili_cli.client.search_user", new_callable=AsyncMock, return_value=mock_results):
        result = runner.invoke(cli, ["search", "test"])
        assert result.exit_code == 0
        assert "TestUser" in result.output


def test_search_video(runner):
    mock_results = [{"bvid": "BV1found", "title": "Found Video", "author": "UP", "play": 5000, "duration": "10:30"}]
    with patch("bili_cli.cli.get_credential", return_value=None), \
         patch("bili_cli.client.search_video", new_callable=AsyncMock, return_value=mock_results):
        result = runner.invoke(cli, ["search", "test", "--type", "video"])
        assert result.exit_code == 0
        assert "BV1found" in result.output


def test_search_empty(runner):
    with patch("bili_cli.cli.get_credential", return_value=None), \
         patch("bili_cli.client.search_user", new_callable=AsyncMock, return_value=[]):
        result = runner.invoke(cli, ["search", "nonexistent_xyz"])
        assert "未找到" in result.output


# ===== User =====


def test_user_by_uid(runner, mock_user_info, mock_relation_info):
    with patch("bili_cli.cli.get_credential", return_value=None), \
         patch("bili_cli.client.get_user_info", new_callable=AsyncMock, return_value=mock_user_info), \
         patch("bili_cli.client.get_user_relation_info", new_callable=AsyncMock, return_value=mock_relation_info):
        result = runner.invoke(cli, ["user", "946974"])
        assert result.exit_code == 0
        assert "TestUP" in result.output
        assert "5.0万" in result.output  # follower count


# ===== Interactions =====


def test_like_requires_login(runner):
    with patch("bili_cli.cli.get_credential", return_value=None):
        result = runner.invoke(cli, ["like", "BV1test"])
        assert "需要登录" in result.output


def test_triple_requires_login(runner):
    with patch("bili_cli.cli.get_credential", return_value=None):
        result = runner.invoke(cli, ["triple", "BV1test"])
        assert "需要登录" in result.output


# ===== Version =====


def test_version(runner):
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "bili" in result.output
