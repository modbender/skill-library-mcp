"""
小红书互动模块（点赞 / 取消点赞 / 收藏 / 取消收藏）

基于 xiaohongshu-mcp/like_favorite.go 翻译
"""

import json
import sys
import time
from typing import Optional, Dict, Any, Tuple

from .client import XiaohongshuClient, DEFAULT_COOKIE_PATH


class InteractAction:
    """互动动作（点赞、收藏）"""

    # CSS 选择器
    LIKE_SELECTOR = '.interact-container .left .like-wrapper'
    LIKE_ACTIVE_SELECTOR = '.interact-container .left .like-wrapper.active, .interact-container .left .like-wrapper.liked'
    COLLECT_SELECTOR = '.interact-container .left .collect-wrapper'
    COLLECT_ACTIVE_SELECTOR = '.interact-container .left .collect-wrapper.active, .interact-container .left .collect-wrapper.collected'

    def __init__(self, client: XiaohongshuClient):
        self.client = client

    def _make_feed_url(self, feed_id: str, xsec_token: str, xsec_source: str = "pc_feed") -> str:
        """构建笔记详情 URL"""
        return f"https://www.xiaohongshu.com/explore/{feed_id}?xsec_token={xsec_token}&xsec_source={xsec_source}"

    def _navigate_to_feed(self, feed_id: str, xsec_token: str):
        """导航到笔记详情页并等待加载"""
        url = self._make_feed_url(feed_id, xsec_token)
        print(f"打开笔记详情页: {url}", file=sys.stderr)
        self.client.navigate(url)
        self.client.wait_for_initial_state()
        time.sleep(2)

    def _get_interact_state(self, feed_id: str) -> Dict[str, bool]:
        """
        从 __INITIAL_STATE__ 获取当前互动状态

        Returns:
            {"liked": bool, "collected": bool}
        """
        page = self.client.page
        result = page.evaluate("""(fid) => {
            var s = window.__INITIAL_STATE__;
            if (!s || !s.note || !s.note.noteDetailMap) return '';

            var ndm = s.note.noteDetailMap;
            var map = ndm;
            if (ndm.value !== undefined) map = ndm.value;
            else if (ndm._value !== undefined) map = ndm._value;

            var detail = map[fid];
            if (!detail || !detail.note || !detail.note.interactInfo) return '';

            var info = detail.note.interactInfo;
            return JSON.stringify({
                liked: !!info.liked,
                collected: !!info.collected
            });
        }""", feed_id)

        if not result:
            return {"liked": False, "collected": False}

        try:
            return json.loads(result)
        except json.JSONDecodeError:
            return {"liked": False, "collected": False}

    def _click_button(self, selector: str, label: str) -> bool:
        """点击互动按钮"""
        page = self.client.page
        try:
            btn = page.locator(selector)
            if btn.count() > 0:
                btn.first.click()
                time.sleep(1.5)
                return True
            else:
                print(f"未找到{label}按钮: {selector}", file=sys.stderr)
                return False
        except Exception as e:
            print(f"点击{label}按钮失败: {e}", file=sys.stderr)
            return False

    def like(self, feed_id: str, xsec_token: str) -> Dict[str, Any]:
        """
        点赞笔记

        Returns:
            操作结果
        """
        self._navigate_to_feed(feed_id, xsec_token)

        state = self._get_interact_state(feed_id)
        if state.get("liked"):
            return {
                "status": "success",
                "action": "like",
                "feed_id": feed_id,
                "already_liked": True,
                "message": "已经点赞过了",
            }

        success = self._click_button(self.LIKE_SELECTOR, "点赞")
        return {
            "status": "success" if success else "error",
            "action": "like",
            "feed_id": feed_id,
            "message": "点赞成功" if success else "点赞失败",
        }

    def unlike(self, feed_id: str, xsec_token: str) -> Dict[str, Any]:
        """
        取消点赞

        Returns:
            操作结果
        """
        self._navigate_to_feed(feed_id, xsec_token)

        state = self._get_interact_state(feed_id)
        if not state.get("liked"):
            return {
                "status": "success",
                "action": "unlike",
                "feed_id": feed_id,
                "already_unliked": True,
                "message": "尚未点赞，无需取消",
            }

        success = self._click_button(self.LIKE_SELECTOR, "取消点赞")
        return {
            "status": "success" if success else "error",
            "action": "unlike",
            "feed_id": feed_id,
            "message": "取消点赞成功" if success else "取消点赞失败",
        }

    def collect(self, feed_id: str, xsec_token: str) -> Dict[str, Any]:
        """
        收藏笔记

        Returns:
            操作结果
        """
        self._navigate_to_feed(feed_id, xsec_token)

        state = self._get_interact_state(feed_id)
        if state.get("collected"):
            return {
                "status": "success",
                "action": "collect",
                "feed_id": feed_id,
                "already_collected": True,
                "message": "已经收藏过了",
            }

        success = self._click_button(self.COLLECT_SELECTOR, "收藏")
        return {
            "status": "success" if success else "error",
            "action": "collect",
            "feed_id": feed_id,
            "message": "收藏成功" if success else "收藏失败",
        }

    def uncollect(self, feed_id: str, xsec_token: str) -> Dict[str, Any]:
        """
        取消收藏

        Returns:
            操作结果
        """
        self._navigate_to_feed(feed_id, xsec_token)

        state = self._get_interact_state(feed_id)
        if not state.get("collected"):
            return {
                "status": "success",
                "action": "uncollect",
                "feed_id": feed_id,
                "already_uncollected": True,
                "message": "尚未收藏，无需取消",
            }

        success = self._click_button(self.COLLECT_SELECTOR, "取消收藏")
        return {
            "status": "success" if success else "error",
            "action": "uncollect",
            "feed_id": feed_id,
            "message": "取消收藏成功" if success else "取消收藏失败",
        }


# ============================================================
# 便捷函数
# ============================================================

def _run_interact(action_name: str, feed_id: str, xsec_token: str,
                  headless: bool = True, cookie_path: str = DEFAULT_COOKIE_PATH) -> Dict[str, Any]:
    """通用互动操作执行器"""
    client = XiaohongshuClient(headless=headless, cookie_path=cookie_path)
    try:
        client.start()
        action = InteractAction(client)
        method = getattr(action, action_name)
        return method(feed_id, xsec_token)
    finally:
        client.close()


def like(feed_id: str, xsec_token: str, headless: bool = True,
         cookie_path: str = DEFAULT_COOKIE_PATH) -> Dict[str, Any]:
    """点赞笔记"""
    return _run_interact("like", feed_id, xsec_token, headless, cookie_path)


def unlike(feed_id: str, xsec_token: str, headless: bool = True,
           cookie_path: str = DEFAULT_COOKIE_PATH) -> Dict[str, Any]:
    """取消点赞"""
    return _run_interact("unlike", feed_id, xsec_token, headless, cookie_path)


def collect(feed_id: str, xsec_token: str, headless: bool = True,
            cookie_path: str = DEFAULT_COOKIE_PATH) -> Dict[str, Any]:
    """收藏笔记"""
    return _run_interact("collect", feed_id, xsec_token, headless, cookie_path)


def uncollect(feed_id: str, xsec_token: str, headless: bool = True,
              cookie_path: str = DEFAULT_COOKIE_PATH) -> Dict[str, Any]:
    """取消收藏"""
    return _run_interact("uncollect", feed_id, xsec_token, headless, cookie_path)
