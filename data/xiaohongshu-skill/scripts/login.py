"""
小红书登录模块

基于 xiaohongshu-mcp/login.go 翻译
支持生成微信登录二维码，保存供主模型发送
"""

import json
import sys
import time
import base64
import os
from typing import Optional, Tuple, Dict, Any

from .client import XiaohongshuClient, DEFAULT_COOKIE_PATH


# QRCode 图片保存目录 - 放在 skill 文件夹内
SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QRCODE_DIR = os.path.join(SKILL_DIR, "data")
QRCODE_PATH = os.path.join(QRCODE_DIR, "qrcode.png")


class LoginAction:
    """登录动作"""

    def __init__(self, client: XiaohongshuClient):
        self.client = client

    def check_login_status(self, navigate: bool = True) -> Tuple[bool, Optional[str]]:
        """
        检查登录状态

        Args:
            navigate: 是否先导航到首页。
                      如果已经在首页上，设 False 避免刷新页面。

        Returns:
            (是否已登录, 用户名)
        """
        page = self.client.page

        if navigate:
            self.client.navigate("https://www.xiaohongshu.com/explore")
            time.sleep(3)

        # ---- 方式 1：检测页面上是否弹出了登录弹窗 ----
        # 如果弹窗的二维码区域可见 → 未登录
        try:
            qr = page.locator('img.qrcode-img[src^="data:image"]')
            if qr.count() > 0 and qr.first.is_visible():
                return False, None
        except Exception:
            pass

        # ---- 方式 2：检查 cookie 里是否包含 web_session ----
        try:
            cookies = self.client.context.cookies()
            has_session = any(c['name'] == 'web_session' for c in cookies)
            if has_session:
                # 尝试获取用户名
                username = self._try_get_username()
                return True, username or "已登录用户"
        except Exception:
            pass

        # ---- 方式 3：检查 HTML 里有没有用户头像链接（登录后才有） ----
        try:
            # 侧边栏会有 /user/profile/xxx 的链接
            profile_link = page.locator('a[href*="/user/profile/"]')
            if profile_link.count() > 0:
                username = self._try_get_username()
                return True, username or "已登录用户"
        except Exception:
            pass

        return False, None

    def _try_get_username(self) -> Optional[str]:
        """尝试从页面提取用户昵称"""
        try:
            name = self.client.page.evaluate("""() => {
                const el = document.querySelector('.user .name, .sidebar .user-name, [class*="nickname"]');
                return el ? el.textContent.trim() : '';
            }""")
            return name if name else None
        except Exception:
            return None

    def get_wechat_qrcode(self) -> Tuple[Optional[str], bool]:
        """
        获取微信登录二维码

        流程：
        1. 访问小红书首页触发登录弹窗
        2. 获取弹窗中的微信二维码图片
        3. 保存到文件

        Returns:
            (二维码文件路径, 是否已登录)
        """
        client = self.client
        page = client.page

        # 访问首页触发登录弹窗
        client.navigate("https://www.xiaohongshu.com/explore")
        time.sleep(4)  # 给弹窗足够时间渲染

        # 先检查是否已登录（不要重新 navigate）
        is_logged_in, _ = self.check_login_status(navigate=False)
        if is_logged_in:
            return None, True

        # 尝试获取二维码 base64 图片
        qrcode_src = None
        for attempt in range(5):
            try:
                qr = page.locator('img.qrcode-img[src^="data:image"]')
                if qr.count() > 0:
                    src = qr.first.get_attribute('src')
                    if src and len(src) > 200:  # 有效 base64 至少上百字符
                        qrcode_src = src
                        break
            except Exception:
                pass
            time.sleep(1)

        if qrcode_src:
            # 去掉 data:image/png;base64, 前缀
            if ',' in qrcode_src:
                qrcode_src = qrcode_src.split(',', 1)[1]

            # 保存二维码图片
            img_data = base64.b64decode(qrcode_src)
            os.makedirs(QRCODE_DIR, exist_ok=True)
            with open(QRCODE_PATH, 'wb') as f:
                f.write(img_data)

            print(f"二维码已保存到: {QRCODE_PATH}", file=sys.stderr)
            return QRCODE_PATH, False

        # 后备：整页截屏
        print("未找到有效的二维码图片，截屏保存...", file=sys.stderr)
        os.makedirs(QRCODE_DIR, exist_ok=True)
        page.screenshot(path=QRCODE_PATH)
        return QRCODE_PATH, False

    def wait_for_login(self, timeout: int = 120, min_wait: int = 30) -> bool:
        """
        在 **当前页面** 上等待用户扫码登录。
        不会重新 navigate，以免刷新掉二维码弹窗。

        会强制等待至少 min_wait 秒再开始检测，
        给用户足够时间在手机上确认登录。

        Args:
            timeout: 总超时时间（秒）
            min_wait: 最少等待秒数（默认 30）

        Returns:
            是否登录成功
        """
        start = time.time()

        # ---- 阶段 1: 强制等待 min_wait 秒 ----
        print(f"请在手机上扫码并确认登录（至少等待 {min_wait} 秒）...", file=sys.stderr)
        while time.time() - start < min_wait:
            elapsed = int(time.time() - start)
            remaining = min_wait - elapsed
            if remaining > 0 and remaining % 10 == 0:
                print(f"  等待中... 还剩 {remaining} 秒", file=sys.stderr)
            time.sleep(2)

        # ---- 阶段 2: 开始轮询检测 web_session cookie ----
        print("开始检测登录状态...", file=sys.stderr)
        while time.time() - start < timeout:
            try:
                cookies = self.client.context.cookies()
                has_session = any(c['name'] == 'web_session' for c in cookies)
                if has_session:
                    print("检测到 web_session cookie，登录成功！", file=sys.stderr)
                    self.client._save_cookies()
                    return True
            except Exception:
                pass

            elapsed = int(time.time() - start)
            remaining = timeout - elapsed
            if remaining > 0 and remaining % 15 == 0:
                print(f"  仍在等待登录... 剩余 {remaining} 秒", file=sys.stderr)
            time.sleep(3)

        print("登录超时", file=sys.stderr)
        return False


# ====== 顶层便捷函数 ======

def check_login(
    cookie_path: str = DEFAULT_COOKIE_PATH,
) -> Tuple[bool, Optional[str]]:
    """检查登录状态"""
    client = XiaohongshuClient(headless=True, cookie_path=cookie_path)
    try:
        client.start()
        action = LoginAction(client)
        return action.check_login_status(navigate=True)
    finally:
        client.close()


def login(
    headless: bool = True,
    cookie_path: str = DEFAULT_COOKIE_PATH,
    timeout: int = 120,
) -> Dict[str, Any]:
    """
    登录小红书（生成二维码 + 等待扫码）

    Returns:
        登录结果字典
    """
    client = XiaohongshuClient(headless=headless, cookie_path=cookie_path)
    try:
        client.start()
        action = LoginAction(client)

        # 获取二维码
        qrcode_path, is_logged_in = action.get_wechat_qrcode()
        if is_logged_in:
            return {
                "status": "logged_in",
                "qrcode_path": None,
                "username": "已登录用户",
                "message": "已登录",
            }

        if qrcode_path:
            # 等待扫码
            success = action.wait_for_login(timeout=timeout)
            if success:
                return {
                    "status": "logged_in",
                    "qrcode_path": None,
                    "username": "已登录用户",
                    "message": "扫码登录成功",
                }
            return {
                "status": "timeout",
                "qrcode_path": qrcode_path,
                "username": None,
                "message": "扫码超时",
            }

        return {
            "status": "error",
            "qrcode_path": None,
            "username": None,
            "message": "获取二维码失败",
        }
    finally:
        client.close()
