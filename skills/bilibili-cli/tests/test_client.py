"""Tests for client.py — mock bilibili-api internals."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from bili_cli import client


@pytest.mark.asyncio
async def test_get_video_info(mock_video_info):
    with patch("bili_cli.client.video.Video") as MockVideo:
        MockVideo.return_value.get_info = AsyncMock(return_value=mock_video_info)
        result = await client.get_video_info("BV1test123")
        assert result["title"] == "测试视频标题"
        assert result["stat"]["view"] == 15000
        MockVideo.assert_called_once_with(bvid="BV1test123", credential=None)


@pytest.mark.asyncio
async def test_get_user_info(mock_user_info):
    with patch("bili_cli.client.user.User") as MockUser:
        MockUser.return_value.get_user_info = AsyncMock(return_value=mock_user_info)
        result = await client.get_user_info(946974)
        assert result["name"] == "TestUP"
        assert result["level"] == 6


@pytest.mark.asyncio
async def test_get_user_relation_info(mock_relation_info):
    with patch("bili_cli.client.user.User") as MockUser:
        MockUser.return_value.get_relation_info = AsyncMock(return_value=mock_relation_info)
        result = await client.get_user_relation_info(946974)
        assert result["follower"] == 50000
        assert result["following"] == 100


@pytest.mark.asyncio
async def test_get_hot_videos():
    mock_data = {"list": [{"bvid": "BV1hot", "title": "Hot Video"}]}
    with patch("bili_cli.client.hot.get_hot_videos", new_callable=AsyncMock, return_value=mock_data):
        result = await client.get_hot_videos()
        assert len(result["list"]) == 1
        assert result["list"][0]["bvid"] == "BV1hot"


@pytest.mark.asyncio
async def test_get_rank_videos():
    mock_data = {"list": [{"bvid": "BV1rank", "title": "Rank Video", "score": 1000}]}
    with patch("bili_cli.client.rank.get_rank", new_callable=AsyncMock, return_value=mock_data):
        result = await client.get_rank_videos()
        assert result["list"][0]["score"] == 1000


@pytest.mark.asyncio
async def test_search_user():
    mock_data = {"result": [{"mid": 123, "uname": "TestUser", "fans": 100}]}
    with patch("bili_cli.client.search.search_by_type", new_callable=AsyncMock, return_value=mock_data):
        result = await client.search_user("test")
        assert len(result) == 1
        assert result[0]["uname"] == "TestUser"


@pytest.mark.asyncio
async def test_search_video():
    mock_data = {"result": [{"bvid": "BV1found", "title": "Found", "author": "UP"}]}
    with patch("bili_cli.client.search.search_by_type", new_callable=AsyncMock, return_value=mock_data):
        result = await client.search_video("test")
        assert len(result) == 1
        assert result[0]["bvid"] == "BV1found"


@pytest.mark.asyncio
async def test_search_user_empty():
    mock_data = {"result": []}
    with patch("bili_cli.client.search.search_by_type", new_callable=AsyncMock, return_value=mock_data):
        result = await client.search_user("nonexistent")
        assert result == []


@pytest.mark.asyncio
async def test_get_related_videos():
    mock_related = [{"bvid": "BV1rel", "title": "Related"}]
    with patch("bili_cli.client.video.Video") as MockVideo:
        MockVideo.return_value.get_related = AsyncMock(return_value=mock_related)
        result = await client.get_related_videos("BV1test")
        assert len(result) == 1


@pytest.mark.asyncio
async def test_like_video(mock_credential):
    with patch("bili_cli.client.video.Video") as MockVideo:
        MockVideo.return_value.like = AsyncMock(return_value={})
        await client.like_video("BV1test", credential=mock_credential)
        MockVideo.return_value.like.assert_called_once_with(status=True)


@pytest.mark.asyncio
async def test_like_video_undo(mock_credential):
    with patch("bili_cli.client.video.Video") as MockVideo:
        MockVideo.return_value.like = AsyncMock(return_value={})
        await client.like_video("BV1test", credential=mock_credential, undo=True)
        MockVideo.return_value.like.assert_called_once_with(status=False)


@pytest.mark.asyncio
async def test_triple_video(mock_credential):
    mock_result = {"like": True, "coin": True, "fav": True}
    with patch("bili_cli.client.video.Video") as MockVideo:
        MockVideo.return_value.triple = AsyncMock(return_value=mock_result)
        result = await client.triple_video("BV1test", credential=mock_credential)
        assert result["like"] is True
        assert result["coin"] is True
