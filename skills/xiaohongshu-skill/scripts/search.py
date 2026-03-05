"""
小红书搜索模块

基于 xiaohongshu-mcp/search.go 翻译
"""

import json
import sys
import time
import urllib.parse
from typing import Optional, List, Dict, Any

from .client import XiaohongshuClient, DEFAULT_COOKIE_PATH


# 筛选选项映射表（来自 Go 源码）
FILTER_OPTIONS_MAP = {
    1: [  # 排序依据
        {"index": 1, "text": "综合"},
        {"index": 2, "text": "最新"},
        {"index": 3, "text": "最多点赞"},
        {"index": 4, "text": "最多评论"},
        {"index": 5, "text": "最多收藏"},
    ],
    2: [  # 笔记类型
        {"index": 1, "text": "不限"},
        {"index": 2, "text": "视频"},
        {"index": 3, "text": "图文"},
    ],
    3: [  # 发布时间
        {"index": 1, "text": "不限"},
        {"index": 2, "text": "一天内"},
        {"index": 3, "text": "一周内"},
        {"index": 4, "text": "半年内"},
    ],
    4: [  # 搜索范围
        {"index": 1, "text": "不限"},
        {"index": 2, "text": "已看过"},
        {"index": 3, "text": "未看过"},
        {"index": 4, "text": "已关注"},
    ],
    5: [  # 位置距离
        {"index": 1, "text": "不限"},
        {"index": 2, "text": "同城"},
        {"index": 3, "text": "附近"},
    ],
}


class SearchAction:
    """搜索动作"""

    def __init__(self, client: XiaohongshuClient):
        self.client = client

    def _make_search_url(self, keyword: str) -> str:
        """构建搜索 URL"""
        params = urllib.parse.urlencode({
            "keyword": keyword,
            "source": "web_explore_feed",
        })
        return f"https://www.xiaohongshu.com/search_result?{params}"

    def _apply_filters(
        self,
        sort_by: Optional[str] = None,
        note_type: Optional[str] = None,
        publish_time: Optional[str] = None,
        search_scope: Optional[str] = None,
        location: Optional[str] = None,
    ):
        """应用筛选条件"""
        page = self.client.page

        # 检查是否有筛选条件
        has_filters = any([sort_by, note_type, publish_time, search_scope, location])
        if not has_filters:
            return

        # 悬停在筛选按钮上
        try:
            filter_btn = page.locator('div.filter')
            filter_btn.hover()
            time.sleep(0.5)

            # 等待筛选面板出现
            page.wait_for_selector('div.filter-panel', timeout=5000)
        except Exception as e:
            print(f"打开筛选面板失败: {e}", file=sys.stderr)
            return

        # 映射筛选选项到文本
        filter_texts = []

        if sort_by:
            text = self._find_filter_text(1, sort_by)
            if text:
                filter_texts.append(text)

        if note_type:
            text = self._find_filter_text(2, note_type)
            if text:
                filter_texts.append(text)

        if publish_time:
            text = self._find_filter_text(3, publish_time)
            if text:
                filter_texts.append(text)

        if search_scope:
            text = self._find_filter_text(4, search_scope)
            if text:
                filter_texts.append(text)

        if location:
            text = self._find_filter_text(5, location)
            if text:
                filter_texts.append(text)

        # 应用筛选：使用文本定位器，避免依赖 DOM 顺序
        filter_panel = page.locator('div.filter-panel')
        for tag_text in filter_texts:
            try:
                filter_panel.get_by_text(tag_text, exact=True).click()
                time.sleep(0.3)
            except Exception as e:
                print(f"点击筛选选项失败: {e}", file=sys.stderr)

        # 等待页面更新
        time.sleep(1)

    def _find_filter_text(self, filters_group: int, text: str) -> Optional[str]:
        """查找筛选选项的显示文本（用于文本定位器）"""
        options = FILTER_OPTIONS_MAP.get(filters_group, [])
        for opt in options:
            if opt["text"] == text:
                return opt["text"]
        return None

    def search(
        self,
        keyword: str,
        sort_by: Optional[str] = None,
        note_type: Optional[str] = None,
        publish_time: Optional[str] = None,
        search_scope: Optional[str] = None,
        location: Optional[str] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        搜索小红书内容

        Args:
            keyword: 搜索关键词
            sort_by: 排序方式：综合 最新 最多点赞 最多评论 最多收藏
            note_type: 笔记类型：不限 视频 图文
            publish_time: 发布时间：不限 一天内 一周内 半年内
            search_scope: 搜索范围：不限 已看过 未看过 已关注
            location: 位置距离：不限 同城 附近
            limit: 返回数量限制

        Returns:
            搜索结果列表
        """
        client = self.client
        page = client.page

        # 导航到搜索页面
        search_url = self._make_search_url(keyword)
        client.navigate(search_url)

        # 等待页面加载 - 增加等待时间确保搜索结果加载完成
        client.wait_for_initial_state()
        time.sleep(3)

        # 滚动页面触发加载更多内容
        for _ in range(3):
            page.evaluate("window.scrollBy(0, 500)")
            time.sleep(0.5)

        # 应用筛选条件
        self._apply_filters(
            sort_by=sort_by,
            note_type=note_type,
            publish_time=publish_time,
            search_scope=search_scope,
            location=location,
        )

        # 提取数据 - 使用实际验证过的字段路径
        result = page.evaluate("""() => {
            const feeds = window.__INITIAL_STATE__?.search?.feeds;
            const data = feeds?.value || feeds?._value;
            if (!data || !Array.isArray(data) || data.length === 0) return '';

            return JSON.stringify(data.slice(0, 50).map(item => {
                const nc = item.noteCard || {};
                const user = nc.user || {};
                const info = nc.interactInfo || {};
                const cover = nc.cover || {};
                return {
                    id: item.id || '',
                    xsec_token: item.xsecToken || '',
                    title: nc.displayTitle || '',
                    type: nc.type || '',
                    user: user.nickname || user.nickName || '',
                    user_id: user.userId || '',
                    user_avatar: user.avatar || '',
                    liked_count: info.likedCount || '0',
                    collected_count: info.collectedCount || '0',
                    comment_count: info.commentCount || '0',
                    shared_count: info.sharedCount || '0',
                    cover_url: cover.urlDefault || cover.urlPre || '',
                };
            }));
        }""")

        if not result:
            print("未获取到搜索结果", file=sys.stderr)
            return []

        # 解析 JSON
        try:
            feeds = json.loads(result)
        except json.JSONDecodeError as e:
            print(f"解析搜索结果失败: {e}", file=sys.stderr)
            return []

        # 限制数量
        if limit > 0:
            feeds = feeds[:limit]

        return feeds


def search(
    keyword: str,
    sort_by: Optional[str] = None,
    note_type: Optional[str] = None,
    publish_time: Optional[str] = None,
    search_scope: Optional[str] = None,
    location: Optional[str] = None,
    limit: int = 10,
    headless: bool = True,
    cookie_path: str = DEFAULT_COOKIE_PATH,
) -> List[Dict[str, Any]]:
    """
    搜索小红书内容

    Args:
        keyword: 搜索关键词
        sort_by: 排序方式
        note_type: 笔记类型
        publish_time: 发布时间
        search_scope: 搜索范围
        location: 位置距离
        limit: 返回数量限制
        headless: 是否无头模式
        cookie_path: Cookie 路径

    Returns:
        搜索结果列表
    """
    client = XiaohongshuClient(
        headless=headless,
        cookie_path=cookie_path,
    )

    try:
        client.start()
        action = SearchAction(client)
        return action.search(
            keyword=keyword,
            sort_by=sort_by,
            note_type=note_type,
            publish_time=publish_time,
            search_scope=search_scope,
            location=location,
            limit=limit,
        )
    finally:
        client.close()
