"""
小红书用户主页模块

基于 xiaohongshu-mcp/user_profile.go 翻译
"""

import json
import sys
import time
from typing import Optional, Dict, Any

from .client import XiaohongshuClient, DEFAULT_COOKIE_PATH


class UserProfileAction:
    """用户主页动作"""

    def __init__(self, client: XiaohongshuClient):
        self.client = client

    def _make_user_profile_url(self, user_id: str, xsec_token: str = "") -> str:
        """构建用户主页 URL"""
        if xsec_token:
            return f"https://www.xiaohongshu.com/user/profile/{user_id}?xsec_token={xsec_token}&xsec_source=pc_note"
        return f"https://www.xiaohongshu.com/user/profile/{user_id}"

    def _extract_user_profile_data(self) -> Optional[Dict[str, Any]]:
        """提取用户主页数据"""
        page = self.client.page

        # 获取用户信息
        user_data_result = page.evaluate("""() => {
            if (window.__INITIAL_STATE__ &&
                window.__INITIAL_STATE__.user &&
                window.__INITIAL_STATE__.user.userPageData) {
                const userPageData = window.__INITIAL_STATE__.user.userPageData;
                const data = userPageData.value !== undefined ? userPageData.value : userPageData._value;
                if (data) {
                    return JSON.stringify(data);
                }
            }
            return '';
        }""")

        if not user_data_result:
            return None

        # 获取用户笔记列表（含置顶标记和时间信息）
        notes_result = page.evaluate("""() => {
            if (!window.__INITIAL_STATE__ ||
                !window.__INITIAL_STATE__.user ||
                !window.__INITIAL_STATE__.user.notes) return '';

            var notes = window.__INITIAL_STATE__.user.notes;
            var data = notes.value !== undefined ? notes.value : (notes._value !== undefined ? notes._value : notes);
            if (!data) return '';

            // 展平二维数组
            var flat = [];
            for (var i = 0; i < data.length; i++) {
                if (Array.isArray(data[i])) {
                    for (var j = 0; j < data[i].length; j++) flat.push(data[i][j]);
                } else {
                    flat.push(data[i]);
                }
            }

            // 提取每条笔记的关键信息，包含置顶标记和排序所需字段
            return JSON.stringify(flat.map(function(item) {
                var nc = item.noteCard || {};
                var info = nc.interactInfo || {};
                var user = nc.user || {};
                var cover = nc.cover || {};
                var result = {
                    id: item.id || '',
                    xsecToken: item.xsecToken || '',
                    noteCard: {
                        displayTitle: nc.displayTitle || '',
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
                // 置顶标记（小红书用多种字段名）
                if (item.isTop) result.isTop = true;
                if (item.stickyTop) result.isTop = true;
                if (item.topFlag) result.isTop = true;
                if (nc.isTop) result.isTop = true;
                // 检查 showTags 中是否有置顶标签
                var tags = item.showTags || nc.showTags || [];
                for (var k = 0; k < tags.length; k++) {
                    if (tags[k] === 'top' || tags[k] === 'is_top' || tags[k] === 'sticky') {
                        result.isTop = true;
                    }
                }
                // 时间信息
                if (nc.time) result.time = nc.time;
                if (nc.createTime) result.time = nc.createTime;
                if (nc.lastUpdateTime) result.lastUpdateTime = nc.lastUpdateTime;
                if (item.timestamp) result.time = item.timestamp;
                return result;
            }));
        }""")

        try:
            user_page_data = json.loads(user_data_result)
        except json.JSONDecodeError:
            return None

        # 解析笔记数据
        feeds = []
        if notes_result:
            try:
                feeds = json.loads(notes_result)
            except json.JSONDecodeError:
                pass

        # 组装响应
        response = {
            "userBasicInfo": user_page_data.get("basicInfo", {}),
            "interactions": user_page_data.get("interactions", []),
            "feeds": feeds,
        }

        return response

    def get_user_profile(
        self,
        user_id: str,
        xsec_token: str = "",
    ) -> Optional[Dict[str, Any]]:
        """
        获取用户主页信息

        Args:
            user_id: 用户 ID
            xsec_token: xsec_token 参数（可选）

        Returns:
            用户主页数据
        """
        client = self.client

        # 构建 URL 并导航
        url = self._make_user_profile_url(user_id, xsec_token)
        print(f"打开用户主页: {url}", file=sys.stderr)
        client.navigate(url)

        # 等待页面加载
        client.wait_for_initial_state()
        time.sleep(1)

        # 提取数据
        profile = self._extract_user_profile_data()

        if not profile:
            print("未获取到用户主页数据", file=sys.stderr)
            return None

        return profile


    def get_my_profile(self) -> Optional[Dict[str, Any]]:
        """
        获取自己的个人主页（通过侧边栏导航）

        Returns:
            自己的用户主页数据
        """
        client = self.client

        # 先导航到首页
        print("导航到首页获取个人信息...", file=sys.stderr)
        client.navigate("https://www.xiaohongshu.com/explore")
        time.sleep(2)

        page = client.page

        # 尝试从侧边栏获取自己的用户 ID
        my_user_id = page.evaluate("""() => {
            // 方法 1: 从侧边栏用户链接提取
            var links = document.querySelectorAll('a[href*="/user/profile/"]');
            for (var i = 0; i < links.length; i++) {
                var href = links[i].getAttribute('href');
                var match = href.match(/\\/user\\/profile\\/([a-f0-9]+)/);
                if (match) return match[1];
            }
            // 方法 2: 从 __INITIAL_STATE__ 提取
            if (window.__INITIAL_STATE__ && window.__INITIAL_STATE__.user) {
                var user = window.__INITIAL_STATE__.user;
                if (user.userPageData) {
                    var data = user.userPageData.value || user.userPageData._value || user.userPageData;
                    if (data && data.basicInfo && data.basicInfo.userId) {
                        return data.basicInfo.userId;
                    }
                }
            }
            return '';
        }""")

        if not my_user_id:
            # 回退：点击侧边栏的个人头像/链接
            try:
                avatar = page.locator('.sidebar-nav .user-avatar, .side-bar .user-wrap a, a.user-link')
                if avatar.count() > 0:
                    avatar.first.click()
                    time.sleep(2)
                    # 从跳转后的 URL 提取用户 ID
                    import re
                    match = re.search(r'/user/profile/([a-f0-9]+)', page.url)
                    if match:
                        my_user_id = match.group(1)
            except Exception as e:
                print(f"通过侧边栏获取用户ID失败: {e}", file=sys.stderr)

        if not my_user_id:
            print("无法获取当前登录用户的 ID", file=sys.stderr)
            return None

        print(f"获取到用户 ID: {my_user_id}", file=sys.stderr)
        return self.get_user_profile(my_user_id)


def user_profile(
    user_id: str,
    xsec_token: str = "",
    headless: bool = True,
    cookie_path: str = DEFAULT_COOKIE_PATH,
) -> Optional[Dict[str, Any]]:
    """
    获取用户主页信息

    Args:
        user_id: 用户 ID
        xsec_token: xsec_token 参数
        headless: 是否无头模式
        cookie_path: Cookie 路径

    Returns:
        用户主页数据
    """
    client = XiaohongshuClient(
        headless=headless,
        cookie_path=cookie_path,
    )

    try:
        client.start()
        action = UserProfileAction(client)
        return action.get_user_profile(
            user_id=user_id,
            xsec_token=xsec_token,
        )
    finally:
        client.close()


def my_profile(
    headless: bool = True,
    cookie_path: str = DEFAULT_COOKIE_PATH,
) -> Optional[Dict[str, Any]]:
    """
    获取自己的个人主页

    Args:
        headless: 是否无头模式
        cookie_path: Cookie 路径

    Returns:
        自己的用户主页数据
    """
    client = XiaohongshuClient(
        headless=headless,
        cookie_path=cookie_path,
    )

    try:
        client.start()
        action = UserProfileAction(client)
        return action.get_my_profile()
    finally:
        client.close()
