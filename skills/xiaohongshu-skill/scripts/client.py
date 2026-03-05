"""
小红书浏览器客户端封装

基于 xiaohongshu-mcp Go 源码翻译为 Python Playwright
"""

import json
import os
import random
import sys
import time
from pathlib import Path
from typing import Optional, Any, Dict

try:
    from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page, Playwright
except ImportError:
    print("请先安装 playwright: pip install playwright && playwright install chromium")
    raise


# Cookie 文件路径
DEFAULT_COOKIE_PATH = os.path.expanduser("~/.xiaohongshu/cookies.json")

# 验证码/安全拦截页面的 URL 特征
CAPTCHA_URL_PATTERNS = [
    'captcha',
    'security-verification',
    'website-login/captcha',
    'verifyType',
    'verifyBiz',
]

# 验证码页面的标题特征
CAPTCHA_TITLE_PATTERNS = [
    '安全验证',
    '验证码',
    'captcha',
    'Security Verification',
]


class CaptchaError(Exception):
    """触发验证码异常"""
    def __init__(self, url: str, message: str = ""):
        self.captcha_url = url
        super().__init__(message or f"触发安全验证: {url}")


class XiaohongshuClient:
    """小红书浏览器客户端"""

    # 频率控制参数
    MIN_INTERVAL = 3.0       # 两次导航最小间隔（秒）
    MAX_INTERVAL = 6.0       # 两次导航最大间隔（秒）
    BURST_THRESHOLD = 5      # 连续请求阈值，超过后增加额外冷却
    BURST_COOLDOWN = 10.0    # 连续请求冷却时间（秒）

    def __init__(
        self,
        headless: bool = True,
        cookie_path: str = DEFAULT_COOKIE_PATH,
        timeout: int = 60,
    ):
        self.headless = headless
        self.cookie_path = cookie_path
        self.timeout = timeout * 1000  # 转换为毫秒

        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

        # 请求计时器（实例变量，避免跨实例干扰）
        self._last_navigate_time: float = 0.0
        self._navigate_count: int = 0
        self._session_start: float = 0.0

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def start(self):
        """启动浏览器"""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=self.headless,
            args=['--disable-blink-features=AutomationControlled'],
        )

        # 创建上下文
        self.context = self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        )

        # 加载 Cookie
        self._load_cookies()

        # 创建页面
        self.page = self.context.new_page()
        self.page.set_default_timeout(self.timeout)

    def close(self):
        """关闭浏览器"""
        # 保存 Cookie
        self._save_cookies()

        if self.page:
            self.page.close()
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def _load_cookies(self):
        """从文件加载 Cookie"""
        if not os.path.exists(self.cookie_path):
            return

        try:
            with open(self.cookie_path, 'r', encoding='utf-8') as f:
                cookies = json.load(f)
            if cookies:
                self.context.add_cookies(cookies)
                print(f"已加载 {len(cookies)} 个 Cookie", file=sys.stderr)
        except Exception as e:
            print(f"加载 Cookie 失败: {e}", file=sys.stderr)

    def _save_cookies(self):
        """保存 Cookie 到文件"""
        if not self.context:
            return

        try:
            cookies = self.context.cookies()
            os.makedirs(os.path.dirname(self.cookie_path), exist_ok=True)
            with open(self.cookie_path, 'w', encoding='utf-8') as f:
                json.dump(cookies, f, ensure_ascii=False, indent=2)
            print(f"已保存 {len(cookies)} 个 Cookie 到 {self.cookie_path}", file=sys.stderr)
        except Exception as e:
            print(f"保存 Cookie 失败: {e}", file=sys.stderr)

    def _throttle(self):
        """请求频率控制：模拟人类浏览节奏"""
        now = time.time()

        # 初始化会话起点
        if self._session_start == 0:
            self._session_start = now

        # 计算距上次导航的间隔
        elapsed = now - self._last_navigate_time if self._last_navigate_time > 0 else 999

        # 连续请求达到阈值 → 额外冷却
        if self._navigate_count > 0 and self._navigate_count % self.BURST_THRESHOLD == 0:
            cooldown = self.BURST_COOLDOWN + random.uniform(0, 3)
            if elapsed < cooldown:
                wait = cooldown - elapsed
                print(f"反爬保护: 连续请求 {self._navigate_count} 次，冷却 {wait:.1f}s...", file=sys.stderr)
                time.sleep(wait)
        elif elapsed < self.MIN_INTERVAL:
            # 普通间隔控制
            wait = random.uniform(self.MIN_INTERVAL, self.MAX_INTERVAL) - elapsed
            if wait > 0:
                time.sleep(wait)

        self._last_navigate_time = time.time()
        self._navigate_count += 1

    def _check_captcha(self) -> bool:
        """
        检测当前页面是否被重定向到验证码页面

        Returns:
            True 表示触发了验证码
        """
        if not self.page:
            return False

        try:
            current_url = self.page.url.lower()
            for pattern in CAPTCHA_URL_PATTERNS:
                if pattern in current_url:
                    return True

            page_title = self.page.title().lower()
            for pattern in CAPTCHA_TITLE_PATTERNS:
                if pattern.lower() in page_title:
                    return True
        except Exception:
            pass

        return False

    def _handle_captcha(self):
        """
        处理验证码拦截：抛出异常通知调用方

        Raises:
            CaptchaError
        """
        url = self.page.url if self.page else "unknown"
        raise CaptchaError(
            url=url,
            message=(
                f"触发小红书安全验证！\n"
                f"  验证页面: {url}\n"
                f"  本次会话已请求 {self._navigate_count} 次\n"
                f"  建议: 1) 等待几分钟后重试  2) 用 --headless=false 手动过验证码  "
                f"3) 重新扫码登录"
            ),
        )

    def navigate(self, url: str, wait_until: str = "domcontentloaded"):
        """导航到指定 URL（含频率控制和验证码检测）"""
        if not self.page:
            raise RuntimeError("浏览器未启动")

        # 频率控制
        self._throttle()

        self.page.goto(url, wait_until=wait_until)
        # 等待页面稳定
        time.sleep(random.uniform(1.5, 3.0))
        # 尝试等待 networkidle，但不强制
        try:
            self.page.wait_for_load_state("networkidle", timeout=8000)
        except Exception:
            pass

        # 验证码检测
        if self._check_captcha():
            self._handle_captcha()

    def wait_for_initial_state(self, timeout: int = 30000, retries: int = 2):
        """等待 __INITIAL_STATE__ 加载完成，带重试和回退"""
        if not self.page:
            raise RuntimeError("浏览器未启动")

        for attempt in range(retries + 1):
            # 先检测验证码
            if self._check_captcha():
                self._handle_captcha()

            try:
                self.page.wait_for_function(
                    "() => window.__INITIAL_STATE__ !== undefined",
                    timeout=timeout,
                )
                return
            except Exception:
                if attempt < retries:
                    print(f"__INITIAL_STATE__ 等待超时，刷新重试 ({attempt + 1}/{retries})...", file=sys.stderr)
                    self.page.reload(wait_until="domcontentloaded")
                    time.sleep(random.uniform(2, 4))
                    # 刷新后再检测验证码
                    if self._check_captcha():
                        self._handle_captcha()
                else:
                    print("警告: __INITIAL_STATE__ 加载超时，尝试继续执行", file=sys.stderr)

    def get_initial_state(self) -> Dict[str, Any]:
        """获取 __INITIAL_STATE__ 数据"""
        if not self.page:
            raise RuntimeError("浏览器未启动")

        # 使用 structuredClone 或手动提取需要的部分，避免循环引用
        result = self.page.evaluate("""() => {
            if (!window.__INITIAL_STATE__) {
                return '';
            }
            // 只提取需要的顶层结构
            const state = window.__INITIAL_STATE__;
            const result = {};
            if (state.search) result.search = state.search;
            if (state.feed) result.feed = state.feed;
            if (state.note) result.note = state.note;
            if (state.user) result.user = state.user;
            return JSON.stringify(result);
        }""")

        if not result:
            return {}

        return json.loads(result)

    def get_data_by_path(self, path: str) -> Any:
        """
        根据路径获取 __INITIAL_STATE__ 中的数据

        例如: "search.feeds", "note.noteDetailMap", "user.userPageData"
        """
        state = self.get_initial_state()

        # 处理 value/_value
        def get_value(obj):
            if isinstance(obj, dict):
                if 'value' in obj:
                    return obj['value']
                if '_value' in obj:
                    return obj['_value']
            return obj

        keys = path.split('.')
        current = state

        for key in keys:
            if current is None:
                return None
            if isinstance(current, dict):
                current = current.get(key)
            else:
                return None
            current = get_value(current)

        return current

    # DEPRECATED: use login.LoginAction.check_login_status() instead
    def check_login_status(self) -> bool:
        """检查登录状态（已废弃，请使用 login.LoginAction）"""
        if not self.page:
            raise RuntimeError("浏览器未启动")

        # 访问首页
        self.navigate("https://www.xiaohongshu.com/explore")
        time.sleep(1)

        # 检查是否存在登录后的元素
        try:
            element = self.page.locator('.main-container .user .link-wrapper .channel')
            count = element.count()
            return count > 0
        except Exception:
            return False

    # DEPRECATED: use login.LoginAction.get_wechat_qrcode() instead
    def get_qrcode(self) -> Optional[str]:
        """获取登录二维码（已废弃，请使用 login.LoginAction）"""
        if not self.page:
            raise RuntimeError("浏览器未启动")

        # 访问首页触发二维码弹窗
        self.navigate("https://www.xiaohongshu.com/explore")
        time.sleep(2)

        # 检查是否已登录
        if self.check_login_status():
            return None

        # 获取二维码图片
        try:
            qrcode = self.page.locator('.login-container .qrcode-img')
            src = qrcode.get_attribute('src')
            return src
        except Exception:
            return None

    # DEPRECATED: use login.LoginAction.wait_for_login() instead
    def wait_for_login(self, timeout: int = 120) -> bool:
        """
        等待用户扫码登录

        Args:
            timeout: 超时时间（秒）

        Returns:
            是否登录成功
        """
        if not self.page:
            raise RuntimeError("浏览器未启动")

        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.check_login_status():
                # 保存登录后的 Cookie
                self._save_cookies()
                return True
            time.sleep(1)

        return False

    def scroll_to_bottom(self, distance: int = 500):
        """滚动页面"""
        if not self.page:
            raise RuntimeError("浏览器未启动")

        self.page.evaluate(f"window.scrollBy(0, {distance})")
        time.sleep(0.5)


def create_client(
    headless: bool = True,
    cookie_path: str = DEFAULT_COOKIE_PATH,
    timeout: int = 60,
) -> XiaohongshuClient:
    """创建小红书客户端的便捷函数"""
    return XiaohongshuClient(
        headless=headless,
        cookie_path=cookie_path,
        timeout=timeout,
    )
