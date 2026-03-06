"""
小红书首页推荐流模块

基于 xiaohongshu-mcp/feeds.go 翻译
"""

import json
import sys
import time
from typing import Optional, Dict, Any, List

from .client import XiaohongshuClient, DEFAULT_COOKIE_PATH


class ExploreAction:
    """首页推荐流动作"""

    EXPLORE_URL = "https://www.xiaohongshu.com/explore"

    def __init__(self, client: XiaohongshuClient):
        self.client = client

    def _extract_feeds(self) -> List[Dict[str, Any]]:
        """从 __INITIAL_STATE__ 提取首页推荐笔记列表"""
        page = self.client.page

        result = page.evaluate("""() => {
            var s = window.__INITIAL_STATE__;
            if (!s || !s.feed || !s.feed.feeds) return '';

            var feeds = s.feed.feeds;
            var data = feeds;
            if (feeds.value !== undefined) data = feeds.value;
            else if (feeds._value !== undefined) data = feeds._value;

            if (!data || !Array.isArray(data)) return '';

            // 展平二维数组（如果有的话）
            var flat = [];
            for (var i = 0; i < data.length; i++) {
                if (Array.isArray(data[i])) {
                    for (var j = 0; j < data[i].length; j++) flat.push(data[i][j]);
                } else {
                    flat.push(data[i]);
                }
            }

            // 提取每条笔记的关键信息
            return JSON.stringify(flat.map(function(item) {
                var nc = item.noteCard || item.model_type === 'note' ? item : {};
                if (item.noteCard) nc = item.noteCard;
                var info = nc.interactInfo || {};
                var user = nc.user || {};
                var cover = nc.cover || {};
                return {
                    id: item.id || '',
                    xsecToken: item.xsecToken || '',
                    noteCard: {
                        displayTitle: nc.displayTitle || nc.title || '',
                        type: nc.type || '',
                        interactInfo: {
                            likedCount: info.likedCount || '0',
                            collectedCount: info.collectedCount || '0',
                            commentCount: info.commentCount || '0',
                            sharedCount: info.sharedCount || '0'
                        },
                        user: {
                            nickname: user.nickname || user.nickName || '',
                            userId: user.userId || ''
                        },
                        cover: {
                            urlDefault: cover.urlDefault || cover.urlPre || ''
                        }
                    }
                };
            }));
        }""")

        if not result:
            return []

        try:
            return json.loads(result)
        except json.JSONDecodeError:
            return []

    def get_feeds(self, limit: int = 20) -> Dict[str, Any]:
        """
        获取首页推荐流

        Args:
            limit: 最大返回数量

        Returns:
            推荐笔记列表
        """
        client = self.client

        print("打开首页推荐流...", file=sys.stderr)
        client.navigate(self.EXPLORE_URL)
        client.wait_for_initial_state()
        time.sleep(2)

        feeds = self._extract_feeds()

        # 如果首页数据较少，尝试滚动加载更多
        if len(feeds) < limit:
            for _ in range(3):
                client.scroll_to_bottom(800)
                time.sleep(1.5)
                new_feeds = self._extract_feeds()
                if len(new_feeds) > len(feeds):
                    feeds = new_feeds
                if len(feeds) >= limit:
                    break

        # 截取到 limit
        feeds = feeds[:limit]

        print(f"获取到 {len(feeds)} 条推荐笔记", file=sys.stderr)
        return {
            "count": len(feeds),
            "feeds": feeds,
        }


def explore(
    limit: int = 20,
    headless: bool = True,
    cookie_path: str = DEFAULT_COOKIE_PATH,
) -> Dict[str, Any]:
    """
    获取首页推荐流

    Args:
        limit: 最大返回数量
        headless: 是否无头模式
        cookie_path: Cookie 路径

    Returns:
        推荐笔记列表
    """
    client = XiaohongshuClient(
        headless=headless,
        cookie_path=cookie_path,
    )

    try:
        client.start()
        action = ExploreAction(client)
        return action.get_feeds(limit=limit)
    finally:
        client.close()
