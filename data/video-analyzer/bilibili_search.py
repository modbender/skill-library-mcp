"""
Bilibili Search - Search and batch process videos
"""

import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


def search_bilibili_videos(
    keyword: str, count: int = 5, order: str = "totalrank"
) -> List[Dict[str, Any]]:
    """
    Search Bilibili videos by keyword.

    Args:
        keyword: Search keyword
        count: Number of results to return
        order: Sorting order (totalrank/pubdate/click/dm)

    Returns:
        List of video info dicts
    """
    try:
        from bilibili_api import search, sync
    except ImportError:
        logger.error("bilibili-api-python not installed")
        return []

    # Order mapping
    order_map = {
        "totalrank": search.OrderVideo.TOTALRANK,
        "pubdate": search.OrderVideo.PUBDATE,
        "click": search.OrderVideo.CLICK,
        "dm": search.OrderVideo.DM,
    }

    order_type = order_map.get(order, search.OrderVideo.TOTALRANK)

    # Execute search
    async def _search():
        return await search.search_by_type(
            keyword=keyword,
            search_type=search.SearchObjectType.VIDEO,
            order_type=order_type,
            page=1,
        )

    result = sync(_search())

    if not result or "result" not in result:
        return []

    videos = result["result"][:count]

    video_list = []
    for video in videos:
        bvid = video.get("bvid")
        if not bvid:
            continue

        video_list.append(
            {
                "url": f"https://www.bilibili.com/video/{bvid}",
                "title": video.get("title", "Unknown"),
                "bvid": bvid,
                "duration": _parse_duration(video.get("duration", "0:00")),
                "play": video.get("play", 0),
                "author": video.get("author", "Unknown"),
            }
        )

    return video_list


def _parse_duration(duration_str: str) -> int:
    """Parse duration string to seconds."""
    try:
        parts = duration_str.split(":")
        if len(parts) == 2:
            return int(parts[0]) * 60 + int(parts[1])
        elif len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        return 0
    except Exception:
        return 0


def format_duration(seconds: int) -> str:
    """Format seconds to duration string."""
    if seconds < 3600:
        return f"{seconds // 60}:{seconds % 60:02d}"
    return f"{seconds // 3600}:{(seconds % 3600) // 60:02d}:{seconds % 60:02d}"


def format_play_count(count: int) -> str:
    """Format play count."""
    if count >= 10000:
        return f"{count / 10000:.1f}万"
    return str(count)
