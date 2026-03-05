"""
小红书评论模块

基于 xiaohongshu-mcp/comment_feed.go 翻译
整合 xiaohongshu-ops 的安全评论理念（长度校验、人性化延迟、频率检测）
"""

import json
import sys
import time
import random
from typing import Optional, Dict, Any

from .client import XiaohongshuClient, DEFAULT_COOKIE_PATH

# 评论安全常量（来自 xiaohongshu-ops）
MAX_COMMENT_LENGTH = 280
TYPING_DELAY_MIN = 30   # 每字符输入延迟下限（ms）
TYPING_DELAY_MAX = 80   # 每字符输入延迟上限（ms）
PRE_SUBMIT_DELAY_MIN = 1.5  # 提交前等待下限（秒）
PRE_SUBMIT_DELAY_MAX = 3.0  # 提交前等待上限（秒）
POST_SUBMIT_COOLDOWN_MIN = 8   # 提交后冷却下限（秒）
POST_SUBMIT_COOLDOWN_MAX = 15  # 提交后冷却上限（秒）


class CommentAction:
    """评论动作"""

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

    @staticmethod
    def validate_comment(content: str) -> Optional[str]:
        """
        评论内容校验（来自 ops 安全理念）

        Returns:
            None 表示校验通过，否则返回错误原因
        """
        if not content or not content.strip():
            return "评论内容不能为空"
        if len(content) > MAX_COMMENT_LENGTH:
            return f"评论内容超长（{len(content)}/{MAX_COMMENT_LENGTH}）"
        return None

    def _check_rate_limit(self) -> bool:
        """
        检测是否触发了评论频率限制（来自 ops 安全理念）

        Returns:
            True 表示被限流
        """
        page = self.client.page
        try:
            # 检查常见的频率限制提示
            rate_limit_selectors = [
                'div.d-toast:has-text("频繁")',
                'div.d-toast:has-text("操作太快")',
                'div.d-toast:has-text("稍后再试")',
                'div.d-toast:has-text("限制")',
            ]
            for sel in rate_limit_selectors:
                toast = page.locator(sel)
                if toast.count() > 0 and toast.first.is_visible():
                    toast_text = toast.first.text_content()
                    print(f"检测到频率限制: {toast_text}", file=sys.stderr)
                    return True
        except Exception:
            pass
        return False

    def _verify_input_placeholder(self, expected_hint: Optional[str] = None) -> bool:
        """
        验证输入框 placeholder 是否正确（来自 ops 安全理念）
        确保输入框已正确激活，防止误输入

        Args:
            expected_hint: 期望的 placeholder 文本片段（如 "回复 用户名"）

        Returns:
            True 表示输入框状态正确
        """
        if not expected_hint:
            return True

        page = self.client.page
        try:
            placeholder = page.locator('div.input-box div.content-edit p.content-input')
            if placeholder.count() > 0:
                attr = placeholder.first.get_attribute('data-placeholder') or ''
                text = placeholder.first.text_content() or ''
                if expected_hint in attr or expected_hint in text:
                    print(f"输入框验证通过: {attr or text}", file=sys.stderr)
                    return True
                else:
                    print(f"输入框 placeholder 不匹配: 期望含「{expected_hint}」, 实际「{attr or text}」", file=sys.stderr)
        except Exception:
            pass
        return True  # 获取失败时不阻断流程

    def _type_and_submit(self, content: str) -> bool:
        """在评论输入框中输入文字并提交（整合 ops 人性化延迟）"""
        page = self.client.page

        # 点击评论输入框激活（span 占位符）
        try:
            input_trigger = page.locator('div.input-box div.content-edit span')
            input_trigger.first.click()
            time.sleep(0.5)
        except Exception as e:
            print(f"点击评论输入框失败: {e}", file=sys.stderr)
            return False

        # 在 contenteditable 的 p 元素中输入文字（人性化随机延迟）
        try:
            input_el = page.locator('div.input-box div.content-edit p.content-input')
            input_el.first.click()
            time.sleep(0.3)
            typing_delay = random.randint(TYPING_DELAY_MIN, TYPING_DELAY_MAX)
            page.keyboard.type(content, delay=typing_delay)
            # 提交前随机等待，模拟人类检查
            pre_wait = random.uniform(PRE_SUBMIT_DELAY_MIN, PRE_SUBMIT_DELAY_MAX)
            time.sleep(pre_wait)
        except Exception as e:
            print(f"输入评论内容失败: {e}", file=sys.stderr)
            return False

        # 点击发送按钮
        try:
            submit_btn = page.locator('div.bottom button.submit')
            submit_btn.first.click()
            time.sleep(1.5)
        except Exception as e:
            print(f"点击发送按钮失败: {e}", file=sys.stderr)
            return False

        # 检查是否触发频率限制
        if self._check_rate_limit():
            return False

        return True

    def post_comment(
        self,
        feed_id: str,
        xsec_token: str,
        content: str,
    ) -> Dict[str, Any]:
        """
        发表评论

        Args:
            feed_id: 笔记 ID
            xsec_token: xsec_token
            content: 评论内容

        Returns:
            操作结果
        """
        # 评论内容校验
        error = self.validate_comment(content)
        if error:
            return {
                "status": "error",
                "feed_id": feed_id,
                "content": content,
                "message": error,
            }

        self._navigate_to_feed(feed_id, xsec_token)

        # 滚动到评论区域
        self.client.page.evaluate("""() => {
            const comments = document.querySelector('.comments-wrap') ||
                              document.querySelector('.comment-wrapper');
            if (comments) comments.scrollIntoView();
        }""")
        time.sleep(1)

        success = self._type_and_submit(content)

        if success:
            print("评论发送成功", file=sys.stderr)
            # 提交后冷却（one-send-per-turn 理念）
            cooldown = random.uniform(POST_SUBMIT_COOLDOWN_MIN, POST_SUBMIT_COOLDOWN_MAX)
            print(f"提交后冷却 {cooldown:.1f}s...", file=sys.stderr)
            time.sleep(cooldown)
            return {
                "status": "success",
                "feed_id": feed_id,
                "content": content,
                "message": "评论发送成功",
            }
        else:
            return {
                "status": "error",
                "feed_id": feed_id,
                "content": content,
                "message": "评论发送失败",
            }

    def reply_to_comment(
        self,
        feed_id: str,
        xsec_token: str,
        comment_id: str,
        reply_user_id: str,
        content: str,
    ) -> Dict[str, Any]:
        """
        回复评论

        Args:
            feed_id: 笔记 ID
            xsec_token: xsec_token
            comment_id: 目标评论 ID
            reply_user_id: 被回复用户 ID
            content: 回复内容

        Returns:
            操作结果
        """
        # 评论内容校验
        error = self.validate_comment(content)
        if error:
            return {
                "status": "error",
                "feed_id": feed_id,
                "comment_id": comment_id,
                "content": content,
                "message": error,
            }

        self._navigate_to_feed(feed_id, xsec_token)

        page = self.client.page

        # 滚动到评论区域
        page.evaluate("""() => {
            const comments = document.querySelector('.comments-wrap') ||
                              document.querySelector('.comment-wrapper');
            if (comments) comments.scrollIntoView();
        }""")
        time.sleep(1)

        # 找到目标评论并点击"回复"按钮
        try:
            # 尝试通过评论 ID 定位
            comment_el = page.locator(f'[data-comment-id="{comment_id}"]')
            if comment_el.count() == 0:
                # 回退：通过遍历评论列表查找
                comment_el = page.locator('.comment-item').filter(has_text=comment_id)

            if comment_el.count() > 0:
                # 悬停以显示回复按钮
                comment_el.first.hover()
                time.sleep(0.3)

                # 点击回复按钮
                reply_btn = comment_el.first.locator('.reply-btn, button:has-text("回复"), span:has-text("回复")')
                if reply_btn.count() > 0:
                    reply_btn.first.click()
                    time.sleep(0.5)
                    # 验证输入框 placeholder（ops 技巧）
                    self._verify_input_placeholder(f"回复")
                else:
                    print("未找到回复按钮，尝试直接在评论框回复", file=sys.stderr)
            else:
                print(f"未找到评论 {comment_id}，尝试直接在评论框回复", file=sys.stderr)
        except Exception as e:
            print(f"定位目标评论失败: {e}", file=sys.stderr)

        # 输入回复内容并发送
        success = self._type_and_submit(content)

        if success:
            print("回复发送成功", file=sys.stderr)
            # 提交后冷却
            cooldown = random.uniform(POST_SUBMIT_COOLDOWN_MIN, POST_SUBMIT_COOLDOWN_MAX)
            print(f"提交后冷却 {cooldown:.1f}s...", file=sys.stderr)
            time.sleep(cooldown)
            return {
                "status": "success",
                "feed_id": feed_id,
                "comment_id": comment_id,
                "reply_user_id": reply_user_id,
                "content": content,
                "message": "回复发送成功",
            }
        else:
            return {
                "status": "error",
                "feed_id": feed_id,
                "comment_id": comment_id,
                "content": content,
                "message": "回复发送失败",
            }


def post_comment(
    feed_id: str,
    xsec_token: str,
    content: str,
    headless: bool = True,
    cookie_path: str = DEFAULT_COOKIE_PATH,
) -> Dict[str, Any]:
    """
    发表评论

    Args:
        feed_id: 笔记 ID
        xsec_token: xsec_token
        content: 评论内容
        headless: 是否无头模式
        cookie_path: Cookie 路径

    Returns:
        操作结果
    """
    client = XiaohongshuClient(
        headless=headless,
        cookie_path=cookie_path,
    )

    try:
        client.start()
        action = CommentAction(client)
        return action.post_comment(feed_id, xsec_token, content)
    finally:
        client.close()


def reply_to_comment(
    feed_id: str,
    xsec_token: str,
    comment_id: str,
    reply_user_id: str,
    content: str,
    headless: bool = True,
    cookie_path: str = DEFAULT_COOKIE_PATH,
) -> Dict[str, Any]:
    """
    回复评论

    Args:
        feed_id: 笔记 ID
        xsec_token: xsec_token
        comment_id: 目标评论 ID
        reply_user_id: 被回复用户 ID
        content: 回复内容
        headless: 是否无头模式
        cookie_path: Cookie 路径

    Returns:
        操作结果
    """
    client = XiaohongshuClient(
        headless=headless,
        cookie_path=cookie_path,
    )

    try:
        client.start()
        action = CommentAction(client)
        return action.reply_to_comment(
            feed_id, xsec_token, comment_id, reply_user_id, content
        )
    finally:
        client.close()
