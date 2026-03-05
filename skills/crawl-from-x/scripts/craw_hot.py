#!/usr/bin/env python3
"""
Crawl Hot - X/Twitter 帖子抓取工具（重构版）
管理关注用户列表并抓取当天最新帖子 URL

架构：
    - 模块化设计，职责清晰
    - DRY 原则，消除重复代码
    - 配置化，易于维护
    - 类型提示完整
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any, Callable, Tuple
from datetime import datetime
from pathlib import Path
import json
import os
import sys
import random
import time
import subprocess
import requests
import re
import threading
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse


# ============================================================================
# 配置模块
# ============================================================================

@dataclass
class Config:
    """全局配置"""
    # 路径配置
    base_dir: Path = Path(__file__).parent.parent
    log_file: Path = None
    users_file: Path = None
    results_dir: Path = None

    # 超时配置（秒）
    page_load_timeout: int = 10  # 增加页面加载超时：5s → 10s
    scroll_check_interval: float = 0.5
    scroll_max_attempts: int = 10
    scroll_no_new_threshold: int = 2  # 连续 2 次没新帖就停止（优化：从 3 次降为 2 次）
    scroll_max_consecutive_errors: int = 3
    scroll_early_stop_on_yesterday: bool = True  # 检测到昨天的帖子就立即停止
    user_crawl_timeout: int = 120  # 2 分钟

    # 重试配置
    max_retries: int = 5
    browser_action_max_attempts: int = 2

    # 并发配置
    content_fetch_workers: int = 10
    user_crawl_workers: int = 5  # 用户抓取并发数

    # 浏览器配置
    browser_max_restarts: int = 10
    browser_restart_backoff: int = 30

    # 请求头
    request_headers: Dict[str, str] = None

    def __post_init__(self):
        """初始化路径"""
        self.log_file = self.base_dir / "craw_hot.log"
        self.users_file = self.base_dir / "users.txt"
        self.results_dir = self.base_dir / "results"
        self.images_dir = self.results_dir / "images"
        self.request_headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }


# ============================================================================
# 异常模块
# ============================================================================

class NoPostsFoundError(Exception):
    """没有找到帖子的异常（用于区分真正的失败和正常情况）"""
    pass


class BrowserActionError(Exception):
    """浏览器操作异常"""
    pass


class CrawlTimeoutError(Exception):
    """抓取超时异常"""
    pass


# ============================================================================
# 日志模块
# ============================================================================

class Logger:
    """日志工具"""

    def __init__(self, log_file: Path):
        self.log_file = log_file
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

    def log(self, level: str, message: str) -> None:
        """写入日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] [{level}] {message}\n"
        print(log_line.strip())
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_line)

    def info(self, message: str) -> None:
        self.log("INFO", message)

    def warning(self, message: str) -> None:
        self.log("WARN", message)

    def error(self, message: str) -> None:
        self.log("ERROR", message)

    def debug(self, message: str) -> None:
        self.log("DEBUG", message)


# ============================================================================
# 进程锁模块
# ============================================================================

class ProcessLock:
    """进程锁，防止多个实例同时运行"""

    def __init__(self, lock_file: Path):
        self.lock_file = lock_file
        self.lock_fd = None

    def acquire(self) -> bool:
        """尝试获取锁"""
        try:
            import fcntl
            self.lock_fd = open(self.lock_file, 'w')
            fcntl.flock(self.lock_fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.lock_fd.write(str(os.getpid()))
            self.lock_fd.flush()
            return True
        except (IOError, BlockingIOError):
            return False

    def release(self) -> None:
        """释放锁"""
        if self.lock_fd:
            import fcntl
            fcntl.flock(self.lock_fd.fileno(), fcntl.LOCK_UN)
            self.lock_fd.close()
            self.lock_fd = None

        if self.lock_file.exists():
            try:
                self.lock_file.unlink()
            except:
                pass

    def __enter__(self):
        return self.acquire()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()


# ============================================================================
# 浏览器客户端模块
# ============================================================================

class BrowserClient:
    """浏览器操作客户端（封装 subprocess 调用）"""

    def __init__(self, config: Config, logger: Logger):
        self.config = config
        self.logger = logger
        self.restart_count = 0

    def _run_command(self, args: List[str], timeout: int = 30) -> subprocess.CompletedProcess:
        """运行命令"""
        return subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=timeout
        )

    def _parse_output(self, output: str) -> Optional[Dict]:
        """解析浏览器命令输出（支持 JSON、布尔值）"""
        lines = output.strip().split('\n')

        # 从前往后找 JSON 开始（{, [, "）
        json_start = None
        for i, line in enumerate(lines):
            line_stripped = line.strip()

            # 跳过调试信息（以 │, ├, ╯, ◇ 等开头的行）
            if line_stripped.startswith(('│', '├', '╯', '◇')):
                continue

            # 找到 JSON 开始
            if line_stripped and (line_stripped.startswith('{') or line_stripped.startswith('"') or line_stripped.startswith('[')):
                json_start = i
                break

            # 处理布尔值
            if line_stripped == "true":
                return {"ok": True, "result": True}
            if line_stripped == "false":
                return {"ok": True, "result": False}

            # 处理数字（新增）
            if line_stripped.lstrip('-').isdigit():
                return {"ok": True, "result": int(line_stripped)}

        if json_start is not None:
            # 从 JSON 开始行合并后续行直到找到完整的 JSON
            json_text = lines[json_start]

            for j in range(json_start + 1, len(lines)):
                json_text += '\n' + lines[j]
                try:
                    response = json.loads(json_text)
                    if isinstance(response, str):
                        return {"ok": True, "result": response}
                    elif isinstance(response, dict):
                        if response.get("ok"):
                            return response
                        else:
                            return {"ok": True, "result": response.get("result")}
                    else:
                        return {"ok": True, "result": response}
                except json.JSONDecodeError:
                    # JSON 还不完整，继续合并
                    continue

            # 循环结束后，再次尝试解析（处理单行 JSON 的情况）
            try:
                response = json.loads(json_text)
                if isinstance(response, str):
                    return {"ok": True, "result": response}
                elif isinstance(response, dict):
                    if response.get("ok"):
                        return response
                    else:
                        return {"ok": True, "result": response.get("result")}
                else:
                    return {"ok": True, "result": response}
            except json.JSONDecodeError:
                # 合并了所有行还是无法解析
                self.logger.warning(f"Failed to parse JSON: {json_text[:100]}")

        # 没有找到有效输出
        self.logger.debug(f"Cannot find valid output. Lines: {lines[:10]}")  # 显示前 10 行用于调试
        return None

    def _check_tab_not_found(self, result: subprocess.CompletedProcess) -> bool:
        """检查是否有 tab not found 错误"""
        output = result.stderr + result.stdout
        return "tab not found" in output.lower()

    def _execute_action(self, action: str, **kwargs) -> Optional[Dict]:
        """执行浏览器操作（带重试和自动恢复）"""
        for attempt in range(1, self.config.browser_action_max_attempts + 1):
            try:
                result = self._run_command(kwargs['cmd'], timeout=kwargs.get('timeout', 30))

                # 检查是否需要浏览器恢复
                if self._check_tab_not_found(result):
                    if attempt < self.config.browser_action_max_attempts:
                        self.logger.warning("Detected 'tab not found', attempting recovery...")
                        if self._restart_browser():
                            continue
                        else:
                            return None

                # 检查返回码
                if result.returncode == 0:
                    return self._parse_output(result.stdout)
                else:
                    self.logger.error(f"Command failed: {result.stderr}")
                    return None

            except subprocess.TimeoutExpired:
                self.logger.error(f"Command timed out")
                return None
            except Exception as e:
                self.logger.error(f"Browser action error: {str(e)}")
                return None

        return None

    def _restart_browser(self) -> bool:
        """重启浏览器服务"""
        if self.restart_count >= self.config.browser_max_restarts:
            self.logger.warning(f"Already restarted {self.restart_count} times, giving up")
            return False

        self.restart_count += 1
        self.logger.info(f"Attempting browser restart ({self.restart_count}/{self.config.browser_max_restarts})...")

        try:
            # 停止
            self.logger.info("Stopping browser...")
            self._run_command(["openclaw", "browser", "stop"])
            time.sleep(2)

            # 启动
            self.logger.info("Starting browser...")
            self._run_command(["openclaw", "browser", "start"])
            time.sleep(self.config.browser_restart_backoff)

            # 验证
            if self.check_status():
                self.logger.info("✅ Browser restarted successfully")
                return True
            else:
                self.logger.error("❌ Browser check failed")
                return False
        except Exception as e:
            self.logger.error(f"Browser restart failed: {str(e)}")
            return False

    def check_status(self) -> bool:
        """检查浏览器状态"""
        try:
            result = self._run_command(["openclaw", "browser", "status"], timeout=10)
            return result.returncode == 0 and "enabled: true" in result.stdout
        except Exception:
            return False

    def ensure_available(self) -> bool:
        """确保浏览器可用"""
        if self.check_status():
            return True

        self.logger.warning("Browser not available, attempting to fix...")
        try:
            self._run_command(["openclaw", "browser", "start"])
            time.sleep(3)
            return self.check_status()
        except Exception:
            return False

    def navigate(self, url: str) -> bool:
        """导航到 URL"""
        self.logger.info(f"Navigating to {url}")
        result = self._execute_action(
            action="navigate",
            cmd=["openclaw", "browser", "navigate", "--json", url]
        )
        if result:
            self.target_id = result.get("targetId")
            return True
        return False

    def evaluate(self, js_code: str) -> Optional[Any]:
        """执行 JavaScript"""
        if not self.target_id:
            self.logger.warning("No targetId available, cannot evaluate")
            return None

        result = self._execute_action(
            action="evaluate",
            cmd=["openclaw", "browser", "evaluate", "--target-id", self.target_id, "--fn", js_code]
        )

        if not result:
            return None

        result_value = result.get("result")
        self.logger.debug(f"Evaluate result type: {type(result_value)}")
        self.logger.debug(f"Evaluate result (repr): {repr(result_value)[:200]}")

        # 修复：openclaw browser evaluate 返回的 JSON 被双重转义
        # _parse_output 可能已经解析了一次，如果结果是列表，直接返回
        if isinstance(result_value, list):
            self.logger.debug(f"Result is already a list: {len(result_value)} items")
            return result_value

        # 如果是字符串且以 [ 或 { 开头，尝试解析
        if isinstance(result_value, str) and result_value.strip().startswith(('[', '{')):
            try:
                result_value = json.loads(result_value)
                self.logger.debug(f"Parsed evaluate result: string -> {type(result_value)}")
                # 解析后可能还是字符串（双重转义）
                if isinstance(result_value, str) and result_value.strip().startswith(('[', '{')):
                    result_value = json.loads(result_value)
                    self.logger.debug(f"Double-parsed evaluate result: string -> {type(result_value)}")
            except json.JSONDecodeError as e:
                self.logger.warning(f"Failed to parse evaluate result: {e}")
                return None

        return result_value

    def press(self, key: str) -> bool:
        """按键"""
        result = self._execute_action(
            action="press",
            cmd=["openclaw", "browser", "press", key]
        )
        return result is not None

    def wait_for_content_loaded(self, timeout: int) -> bool:
        """智能等待：检查页面是否真的加载完成"""
        js_code = "document.querySelectorAll('article').length > 0"

        start_time = time.time()
        while time.time() - start_time < timeout:
            result = self.evaluate(js_code)
            if result is True:
                self.logger.debug("Content loaded successfully")
                return True
            time.sleep(self.config.scroll_check_interval)

        self.logger.warning(f"Content not fully loaded after {timeout}s, proceeding anyway")
        return False


# ============================================================================
# Twitter API 模块
# ============================================================================

class TwitterApiClient:
    """Twitter API 客户端（fxtwitter + syndication）"""

    def __init__(self, config: Config, logger: Logger):
        self.config = config
        self.logger = logger

    def _fetch_via_fxtwitter(self, url: str) -> Optional[Dict]:
        """通过 fxtwitter API 获取内容"""
        api_url = re.sub(r'(x\.com|twitter\.com)', 'api.fxtwitter.com', url)
        try:
            # 增加超时时间：15s → 30s
            resp = requests.get(api_url, headers=self.config.request_headers, timeout=30)
            if resp.status_code == 200:
                return resp.json()
            self.logger.warning(f"fxtwitter API returned {resp.status_code}")
        except Exception as e:
            self.logger.warning(f"fxtwitter error: {str(e)}")
        return None

    def _fetch_via_syndication(self, tweet_id: str) -> Optional[Dict]:
        """通过 syndication API 获取内容"""
        url = f"https://cdn.syndication.twimg.com/tweet-result?id={tweet_id}&token=0"
        try:
            # 增加超时时间：10s → 20s
            resp = requests.get(url, headers=self.config.request_headers, timeout=20)
            if resp.status_code == 200:
                return resp.json()
            self.logger.warning(f"syndication API returned {resp.status_code}")
        except Exception as e:
            self.logger.warning(f"syndication error: {str(e)}")
        return None

    def fetch_post(self, url: str) -> Optional[Dict]:
        """获取帖子内容（尝试多个 API）"""
        tweet_id = self._extract_tweet_id(url)
        if not tweet_id:
            self.logger.warning(f"Cannot extract tweet ID from URL: {url}")
            return None

        # 方法1: fxtwitter
        data = self._fetch_via_fxtwitter(url)
        if data and data.get("tweet"):
            self.logger.debug(f"Successfully fetched via fxtwitter: {url}")
            return {"data": data, "source": "fxtwitter"}

        # 方法2: syndication
        data = self._fetch_via_syndication(tweet_id)
        if data and data.get("text"):
            self.logger.debug(f"Successfully fetched via syndication: {url}")
            return {"data": data, "source": "syndication"}

        self.logger.warning(f"Failed to fetch content: {url}")
        return None

    @staticmethod
    def _extract_tweet_id(url: str) -> Optional[str]:
        """从 URL 提取 tweet ID"""
        patterns = [
            r'(?:x\.com|twitter\.com)/\w+/status/(\d+)',
            r'(?:x\.com|twitter\.com)/\w+/statuses/(\d+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None


# ============================================================================
# 帖子格式化模块
# ============================================================================

class PostFormatter:
    """帖子内容格式化器"""

    def __init__(self, config: Config, logger: Logger):
        self.config = config
        self.logger = logger

    def format_as_markdown(self, post_data: Dict, source: str, url: str) -> str:
        """将帖子数据格式化为 Markdown"""
        if source == "fxtwitter":
            return self._format_fxtwitter(post_data, url)
        elif source == "syndication":
            return self._format_syndication(post_data, url)
        # 兜底方案：如果 source 不识别，返回一个基本的格式
        self.logger.warning(f"Unknown source: {source}, using basic format")
        return f"# Unknown Source\n\n> 原文链接: {url}\n\n---\n\n> ⚠️ 无法解析帖子内容\n"

    def _format_fxtwitter(self, data: Dict, url: str) -> str:
        """格式化 fxtwitter 数据"""
        tweet = data.get("tweet", {})
        article = tweet.get("article")

        if article:
            return self._format_article(tweet, article, url)
        else:
            return self._format_tweet(tweet, url)

    def _format_syndication(self, data: Dict, url: str) -> str:
        """格式化 syndication 数据"""
        user = data.get("user", {})
        lines = [
            f"# @{user.get('screen_name', '')} 的推文",
            "",
            f"> 作者: **{user.get('name', '')}** (@{user.get('screen_name', '')})",
            f"> 发布时间: {data.get('created_at', '')}",
            f"> 原文链接: {url}",
            "",
            "---",
            "",
            data.get("text", ""),
            "",
        ]

        # 媒体
        media_urls = [m.get("media_url_https") for m in data.get("mediaDetails", []) if m.get("media_url_https")]
        if media_urls:
            lines.extend(["## 媒体", ""])
            lines.extend([f"![媒体{i}]({m})" for i, m in enumerate(media_urls, 1)])
            lines.append("")

        lines.extend([
            "---",
            "",
            "## 互动数据",
            "",
            f"- ❤️ 点赞: {data.get('favorite_count', 0):,}",
            f"- 🔁 转发: {data.get('retweet_count', 0):,}",
        ])

        return "\n".join(lines)

    def _format_article(self, tweet: Dict, article: Dict, url: str) -> str:
        """格式化 X Article"""
        lines = [
            f"# {article.get('title', 'Untitled')}",
            "",
            f"> 作者: **{tweet.get('author', {}).get('name', '')}** (@{tweet.get('author', {}).get('screen_name', '')})",
            f"> 发布时间: {article.get('created_at', '')}",
        ]

        if article.get('modified_at'):
            lines.append(f"> 修改时间: {article.get('modified_at', '')}")

        lines.extend([
            f"> 原文链接: {url}",
            "",
            "---",
            "",
        ])

        # 封面图
        if article.get("cover_image"):
            lines.extend([
                f"![封面]({article.get('cover_image')})",
                "",
            ])

        # 正文
        full_text = self._extract_article_content(article)
        if full_text:
            lines.extend([
                full_text,
                "",
            ])

        lines.extend([
            "---",
            "",
            "## 互动数据",
            "",
            f"- ❤️ 点赞: {tweet.get('likes', 0):,}",
            f"- 🔁 转发: {tweet.get('retweets', 0):,}",
            f"- 👀 浏览: {tweet.get('views', 0):,}",
            f"- 🔖 书签: {tweet.get('bookmarks', 0):,}",
        ])

        return "\n".join(lines)

    def _format_tweet(self, tweet: Dict, url: str) -> str:
        """格式化普通推文"""
        lines = [
            f"# @{tweet.get('author', {}).get('screen_name', '')} 的推文",
            "",
            f"> 作者: **{tweet.get('author', {}).get('name', '')}** (@{tweet.get('author', {}).get('screen_name', '')})",
            f"> 发布时间: {tweet.get('created_at', '')}",
            f"> 原文链接: {url}",
            "",
            "---",
            "",
            tweet.get("text", ""),
            "",
        ]

        # 媒体
        media_urls = [m.get("url") for m in tweet.get("media", {}).get("all", []) if m.get("url")]
        if media_urls:
            lines.extend(["## 媒体", ""])
            lines.extend([f"![媒体{i}]({m})" for i, m in enumerate(media_urls, 1)])
            lines.append("")

        lines.extend([
            "---",
            "",
            "## 互动数据",
            "",
            f"- ❤️ 点赞: {tweet.get('likes', 0):,}",
            f"- 🔁 转发: {tweet.get('retweets', 0):,}",
            f"- 👀 浏览: {tweet.get('views', 0):,}",
            f"- 💬 回复: {tweet.get('replies', 0):,}",
        ])

        return "\n".join(lines)

    def _extract_article_content(self, article: Dict) -> Optional[str]:
        """从 X Article 中提取完整内容"""
        if not article:
            return None

        content_blocks = article.get("content", {}).get("blocks", [])
        paragraphs = []

        for block in content_blocks:
            text = block.get("text", "").strip()
            block_type = block.get("type", "unstyled")

            if not text:
                continue

            type_to_format = {
                "header-one": f"# {text}",
                "header-two": f"## {text}",
                "header-three": f"### {text}",
                "blockquote": f"> {text}",
                "unordered-list-item": f"- {text}",
                "ordered-list-item": f"1. {text}",
            }

            paragraphs.append(type_to_format.get(block_type, text))

        return "\n\n".join(paragraphs)


# ============================================================================
# 抓取模块
# ============================================================================

class PostCrawler:
    """帖子抓取器"""

    def __init__(self, config: Config, logger: Logger, browser: BrowserClient):
        self.config = config
        self.logger = logger
        self.browser = browser

    def _get_scroll_js(self) -> str:
        """获取滚动的 JavaScript 代码"""
        # 使用 IIFE 立即执行并返回结果（箭头函数隐式返回）
        return """(() => {
            const articles = document.querySelectorAll('article');
            const now = new Date();
            const oneDayAgo = new Date(now.getTime() - 24 * 60 * 60 * 1000);
            const result = [];

            for (let i = 0; i < articles.length; i++) {
                const article = articles[i];
                const timeElement = article.querySelector('time');
                if (!timeElement) continue;

                const datetime = timeElement.getAttribute('datetime');
                if (!datetime) continue;

                const tweetDate = new Date(datetime);
                if (tweetDate < oneDayAgo) continue;

                const links = article.querySelectorAll('a[href*="/status/"]');
                for (let j = 0; j < links.length; j++) {
                    const link = links[j];
                    const href = link.getAttribute('href');
                    if (href && href.includes('/status/')) {
                        const statusId = href.split('/status/')[1].split('/')[0];
                        const fullUrl = 'https://x.com' + href.split('/status/')[0] + '/status/' + statusId;
                        if (!result.includes(fullUrl)) {
                            result.push(fullUrl);
                        }
                        break;
                    }
                }
            }

            return result
        })()"""

    def crawl_user(self, username: str) -> List[str]:
        """抓取单个用户的帖子"""
        self.logger.info(f"Starting crawl for @{username}")

        if not self.browser.ensure_available():
            raise Exception("Browser not available")

        if not self.browser.navigate(f"https://x.com/{username}"):
            raise Exception(f"Failed to navigate to @{username}")

        # 智能等待页面加载
        if self.browser.wait_for_content_loaded(self.config.page_load_timeout):
            self.logger.debug("Page loaded, ready to scroll")
        else:
            time.sleep(random.uniform(1, 2))  # 备用等待

        # 滚动并收集 URL
        urls = self._scroll_and_collect(username)

        if not urls:
            raise NoPostsFoundError(f"No posts found for @{username} in the last 24 hours")

        return urls

    def _scroll_and_collect(self, username: str) -> List[str]:
        """滚动页面并收集 URL（智能策略）"""
        urls = []
        seen_ids = set()
        no_new_count = 0
        consecutive_errors = 0
        found_yesterday = False  # 检测是否找到昨天的帖子

        for scroll_num in range(1, self.config.scroll_max_attempts + 1):
            self.logger.debug(f"Scroll {scroll_num}/{self.config.scroll_max_attempts}")

            # 执行 JavaScript
            js_code = self._get_scroll_js()
            result = self.browser.evaluate(js_code)

            if result is not None:
                consecutive_errors = 0
                try:
                    # result 可能已经是列表，或者需要 json.loads 解析
                    if isinstance(result, list):
                        page_urls = result
                    else:
                        page_urls = json.loads(result)
                    new_urls = [u for u in page_urls if u not in seen_ids]

                    if new_urls:
                        self.logger.debug(f"Found {len(new_urls)} new URLs")
                        seen_ids.update(new_urls)
                        urls.extend(new_urls)
                        no_new_count = 0
                    else:
                        no_new_count += 1
                        self.logger.debug(f"No new posts (count: {no_new_count})")

                        # 优化：连续 2 次无新帖就停止（原为 3 次）
                        if no_new_count >= self.config.scroll_no_new_threshold:
                            self.logger.info("No new posts for 2 scrolls, stopping early")
                            break

                        # 优化：如果配置了，检测到昨天的帖子就立即停止
                        # 通过观察第一个帖子的 URL 中的时间戳判断是否是昨天的
                        if self.config.scroll_early_stop_on_yesterday and scroll_num == 1 and urls:
                            first_url = urls[0]
                            # 从 URL 中提取 tweet ID，判断时间
                            # 格式：https://x.com/username/status/1234567890
                            tweet_id = first_url.split('/status/')[-1]
                            if tweet_id:
                                tweet_timestamp = int(tweet_id)
                                # Twitter 的 Snowflake ID 中，时间戳是前 41 位
                                # 当前时间戳（毫秒）转换为秒
                                import time as time_module
                                current_ts = time_module.time() * 1000
                                # 计算 24 小时前的时间戳
                                one_day_ago = current_ts - (24 * 60 * 60 * 1000)
                                if tweet_timestamp < one_day_ago:
                                    self.logger.info("Detected yesterday's post, stopping immediately")
                                    found_yesterday = True
                                    break
                except json.JSONDecodeError as e:
                    self.logger.error(f"Failed to parse URLs: {str(e)}")
                    consecutive_errors += 1
            else:
                consecutive_errors += 1

            # 检查是否需要放弃
            if consecutive_errors >= self.config.scroll_max_consecutive_errors:
                self.logger.error(f"Too many consecutive errors, giving up on @{username}")
                break

            # 优化：如果已经检测到昨天的帖子，立即停止
            if found_yesterday:
                break

            # 滚动
            if scroll_num < self.config.scroll_max_attempts:
                self.browser.press("PageDown")
                time.sleep(random.uniform(
                    self.config.scroll_check_interval,
                    self.config.scroll_check_interval * 2
                ))

        self.logger.info(f"Collected {len(urls)} URLs for @{username}")
        return urls


# ============================================================================
# 用户管理模块
# ============================================================================

class UserManager:
    """用户列表管理"""

    def __init__(self, config: Config, logger: Logger):
        self.config = config
        self.logger = logger

    def load(self) -> List[str]:
        """加载用户列表"""
        if not self.config.users_file.exists():
            self.logger.warning(f"Users file not found: {self.config.users_file}")
            return []

        users = []
        with open(self.config.users_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    users.append(line)

        self.logger.info(f"Loaded {len(users)} users from {self.config.users_file}")
        return users

    def add(self, username: str) -> None:
        """添加用户"""
        users = self.load()
        if username in users:
            self.logger.warning(f"User already exists: {username}")
            return

        users.append(username)
        self._save(users)
        self.logger.info(f"Added user: {username}")

    def remove(self, username: str) -> None:
        """删除用户"""
        users = self.load()
        if username not in users:
            self.logger.warning(f"User not found: {username}")
            return

        users.remove(username)
        self._save(users)
        self.logger.info(f"Removed user: {username}")

    def list(self) -> None:
        """列出所有用户"""
        users = self.load()
        self.logger.info(f"User list ({len(users)} users):")
        for i, user in enumerate(users, 1):
            self.logger.info(f"  {i}. {user}")

    def _save(self, users: List[str]) -> None:
        """保存用户列表"""
        with open(self.config.users_file, "w", encoding="utf-8") as f:
            for user in users:
                f.write(f"{user}\n")
        self.logger.info(f"Saved {len(users)} users")


# ============================================================================
# 文件管理模块
# ============================================================================

class ResultFileManager:
    """结果文件管理"""

    def __init__(self, config: Config, logger: Logger):
        self.config = config
        self.logger = logger
        self.config.results_dir.mkdir(parents=True, exist_ok=True)

    def _get_filename(self, timestamp: datetime) -> tuple[Path, Path]:
        """生成文件名"""
        basename = f"posts_{timestamp.strftime('%Y%m%d_%H%M%S')}"
        return (
            self.config.results_dir / f"{basename}.txt",
            self.config.results_dir / f"{basename}.md"
        )

    def create_txt(self, timestamp: datetime, users: List[str]) -> Path:
        """创建 TXT 文件"""
        filepath, _ = self._get_filename(timestamp)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# Crawl Results - {timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# Total users: {len(users)}\n")
            f.write(f"# Started at: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        self.logger.info(f"Created TXT file: {filepath}")
        return filepath

    def append_user_results(self, filepath: Path, username: str, urls: List[str],
                          current: int, total: int) -> None:
        """追加用户结果到 TXT 文件"""
        with open(filepath, "a", encoding="utf-8") as f:
            f.write(f"# @{username} ({len(urls)} posts) - [{current}/{total}]\n")
            for url in urls:
                f.write(f"{url}\n")
            f.write("\n")
            f.flush()

    def finalize_txt(self, filepath: Path, total_posts: int) -> None:
        """完成 TXT 文件"""
        with open(filepath, "a", encoding="utf-8") as f:
            f.write(f"\n# Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# Total posts: {total_posts}\n")
            f.flush()

    def save_markdown(self, results: Dict[str, List[str]], timestamp: datetime,
                      api_client: TwitterApiClient, formatter: PostFormatter) -> Path:
        """生成 Markdown 文件（并发获取内容，使用单一占位符字符串）"""
        import uuid
        _, md_filepath = self._get_filename(timestamp)

        # 准备标题
        header = [
            "# X 帖子抓取结果",
            f"\n**抓取时间:** {timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            f"**总用户数:** {len(results)}",
            f"**总帖子数:** {sum(len(urls) for urls in results.values())}",
            "\n---\n"
        ]

        # 收集所有帖子信息
        post_infos = []
        content = list(header)
        placeholders = {}

        for user, urls in results.items():
            if not urls:
                continue

            content.extend([f"\n## @{user} 的帖子 ({len(urls)} 条)\n", "---\n"])

            for i, url in enumerate(urls, 1):
                # 生成唯一占位符字符串（单一字符串）
                placeholder = f"PLACEHOLDER_{uuid.uuid4().hex[:8]}"
                placeholders[placeholder] = None

                # 占位符内容（单一字符串，包含占位符）
                placeholder_content = f"\n### 帖子 {i}\n\n{placeholder}\n\n- URL: {url}\n\n---\n\n"

                # 添加占位符字符串到 content
                content.append(placeholder_content)
                # 调试：打印占位符内容
                self.logger.debug(f"Appended placeholder for post {i}: {placeholder[:20]}...")
                self.logger.debug(f"Content length: {len(content)}")

                post_infos.append({
                    'user': user,
                    'url': url,
                    'index': i,
                    'total': len(urls),
                    'placeholder': placeholder
                })

        # 并发获取内容
        from concurrent.futures import ThreadPoolExecutor, as_completed

        self.logger.info(f"Fetching content for {len(post_infos)} posts concurrently...")

        def fetch_content(info):
            post_data = api_client.fetch_post(info['url'])
            if post_data:
                return info, formatter.format_as_markdown(
                    post_data['data'],
                    post_data['source'],
                    info['url']
                )
            return info, None

        with ThreadPoolExecutor(max_workers=self.config.content_fetch_workers) as executor:
            futures = {executor.submit(fetch_content, info): info for info in post_infos}

            completed = 0
            for future in as_completed(futures):
                completed += 1
                info = futures[future]

                try:
                    _, markdown = future.result()
                    if markdown:
                        placeholders[info['placeholder']] = markdown + "\n\n---\n\n"
                        self.logger.info(f"Fetched {info['user']} post {info['index']}/{info['total']} [{completed}/{len(post_infos)}]")
                    else:
                        placeholders[info['placeholder']] = (
                            f"\n### 帖子 {info['index']}\n\n> ⚠️ 无法获取帖子内容\n\n- URL: {info['url']}\n\n---\n\n"
                        )
                        self.logger.warning(f"Failed to fetch {info['url']}")
                except Exception as e:
                    self.logger.error(f"Error fetching {info['url']}: {str(e)}")

        # 一次性替换所有占位符
        final_content = "".join(content)
        self.logger.debug(f"Final content length before replacement: {len(final_content)}")
        self.logger.debug(f"Placeholders dict size: {len(placeholders)}")
        self.logger.debug(f"Placeholders keys: {list(placeholders.keys())}")

        for placeholder, replacement in placeholders.items():
            self.logger.debug(f"Replacing placeholder: {placeholder[:20]}..., has replacement: {replacement is not None}")
            final_content = final_content.replace(placeholder, replacement)

        self.logger.debug(f"Final content length after replacement: {len(final_content)}")
        self.logger.debug(f"'正在获取内容' count in final_content: {final_content.count('正在获取内容')}")
        self.logger.debug(f"'PLACEHOLDER' count in final_content: {final_content.count('PLACEHOLDER')}")

        # 保存
        with open(md_filepath, "w", encoding="utf-8") as f:
            f.write(final_content)

        self.logger.info(f"Markdown saved to {md_filepath}")
        return md_filepath

class CrawlHot:
    """Crawl Hot 主控制器（协调所有模块）"""

    def __init__(self):
        # 初始化配置
        self.config = Config()
        self.logger = Logger(self.config.log_file)

        # 进程锁
        self.lock = ProcessLock(self.config.base_dir / ".craw_hot.lock")
        if not self.lock.acquire():
            print(f"❌ Error: Another craw-hot instance is already running!")
            print(f"   Lock file: {self.lock.lock_file}")
            print(f"   Command: rm {self.lock.lock_file}")
            sys.exit(1)

        # 初始化各个模块
        self.browser = BrowserClient(self.config, self.logger)
        self.api_client = TwitterApiClient(self.config, self.logger)
        self.formatter = PostFormatter(self.config, self.logger)
        self.user_manager = UserManager(self.config, self.logger)
        self.result_manager = ResultFileManager(self.config, self.logger)

        # 浏览器操作锁（用于并发抓取）
        self.browser_lock = threading.Lock()

        self.logger.info("=" * 60)
        self.logger.info("CrawlHot initialized")

    def __del__(self):
        """析构函数"""
        if hasattr(self, 'lock'):
            self.lock.release()

    def _retry_with_timeout(self, func: Callable, username: str, timeout: int) -> List[str]:
        """带超时和重试的执行器"""
        import threading

        result = []
        exception = [None]

        def _worker():
            try:
                result.extend(func())
            except NoPostsFoundError:
                pass  # 正常情况，不记录
            except Exception as e:
                exception[0] = e

        def _timeout_handler():
            exception[0] = CrawlTimeoutError(f"Crawl for @{username} timed out after {timeout}s")

        thread = threading.Thread(target=_worker)
        timer = threading.Timer(timeout, _timeout_handler)

        try:
            thread.start()
            timer.start()
            thread.join(timeout=timeout + 5)
            timer.cancel()

            if exception[0]:
                self.logger.error(f"Exception: {str(exception[0])}")
                return []

            return result
        except Exception as e:
            self.logger.error(f"Unexpected error: {str(e)}")
            return []

    def crawl_single_user(self, username: str) -> List[str]:
        """抓取单个用户（带浏览器锁保护）"""
        with self.browser_lock:
            return self._retry_with_timeout(
                lambda: self._retry_crawl_user(username),
                username=username,
                timeout=self.config.user_crawl_timeout
            )

    def _retry_crawl_user(self, username: str) -> List[str]:
        """带重试的抓取"""
        for attempt in range(1, self.config.max_retries + 1):
            try:
                self.logger.debug(f"Attempt {attempt}/{self.config.max_retries}")
                crawler = PostCrawler(self.config, self.logger, self.browser)
                return crawler.crawl_user(username)
            except NoPostsFoundError:
                self.logger.info(f"@{username}: no posts found in the last 24 hours")
                return []
            except Exception as e:
                self.logger.error(f"Attempt {attempt} failed: {str(e)}")

                if attempt < self.config.max_retries:
                    wait_time = random.uniform(1, 3) * attempt
                    self.logger.warning(f"Retrying in {wait_time:.2f}s...")
                    time.sleep(wait_time)

        self.logger.error(f"All attempts failed for @{username}")
        return []

    def crawl_single_user_full(self, username: str) -> Dict[str, List[str]]:
        """抓取单个用户（完整流程：抓取 + 生成 Markdown + 下载媒体）"""
        timestamp = datetime.now()
        results = {}

        self.logger.info(f"Starting crawl for single user: @{username}")

        # 抓取 URL
        urls = self.crawl_single_user(username)
        results[username] = urls

        if not urls:
            self.logger.info(f"@{username}: no posts found today")
            return results

        # 生成 Markdown 文件（使用与全部用户相同的格式）
        self.logger.info(f"Generating Markdown for {len(urls)} posts...")
        md_filepath = self.result_manager.save_markdown(
            results,
            timestamp,
            self.api_client,
            self.formatter
        )

        # 下载媒体并替换 URL
        self.logger.info("Starting media download and URL replacement...")
        try:
            from media_downloader import MediaDownloader
            downloader = MediaDownloader(md_filepath, self.config.images_dir, self.logger)
            downloaded = downloader.process_markdown()
            if downloaded > 0:
                self.logger.info(f"✓ Successfully downloaded {downloaded} media files")
        except Exception as e:
            self.logger.error(f"Media download failed: {str(e)}")
            import traceback
            self.logger.debug(traceback.format_exc())

        # 打印结果摘要
        print(f"\n@{username} found {len(urls)} posts:")
        for url in urls:
            print(f"  {url}")
        print(f"\nResults saved to:")
        print(f"  - {md_filepath}")
        if self.config.images_dir.exists():
            print(f"  - Media files: {self.config.images_dir}")

        return results

    def crawl_all_users(self) -> Dict[str, List[str]]:
        """抓取所有用户（并发模式）"""
        users = self.user_manager.load()
        if not users:
            self.logger.warning("No users to crawl")
            return {}

        timestamp = datetime.now()
        all_results = {}

        # 创建结果文件
        txt_filepath = self.result_manager.create_txt(timestamp, users)

        # 并发抓取
        self.logger.info(f"Starting crawl (concurrent mode, {self.config.user_crawl_workers} workers)...")

        completed_count = 0
        with ThreadPoolExecutor(max_workers=self.config.user_crawl_workers) as executor:
            # 提交所有用户的抓取任务
            future_to_user = {
                executor.submit(self.crawl_single_user, user): user
                for user in users
            }

            # 按完成顺序处理结果
            for future in as_completed(future_to_user):
                user = future_to_user[future]
                completed_count += 1

                try:
                    urls = future.result()
                    all_results[user] = urls

                    # 立即保存
                    self.result_manager.append_user_results(txt_filepath, user, urls, completed_count, len(users))

                    if urls:
                        self.logger.info(f"@{user}: {len(urls)} posts [{completed_count}/{len(users)}]")
                    else:
                        self.logger.warning(f"@{user}: no posts found [{completed_count}/{len(users)}]")
                except Exception as e:
                    self.logger.error(f"Failed to crawl @{user}: {str(e)}")
                    all_results[user] = []

                    # 即使失败也追加空结果
                    self.result_manager.append_user_results(txt_filepath, user, [], completed_count, len(users))

        # 完成 TXT 文件
        total_posts = sum(len(urls) for urls in all_results.values())
        self.result_manager.finalize_txt(txt_filepath, total_posts)

        # 生成 Markdown 文件
        md_filepath = self.result_manager.save_markdown(
            all_results,
            timestamp,
            self.api_client,
            self.formatter
        )

        # 下载媒体并替换 URL（新增功能）
        self.logger.info("Starting media download and URL replacement...")
        try:
            # 导入媒体下载器
            import sys
            script_dir = Path(__file__).parent / 'scripts'
            if script_dir.exists():
                sys.path.insert(0, str(script_dir))
            else:
                sys.path.insert(0, str(Path(__file__).parent))
            
            from media_downloader import MediaDownloader
            downloader = MediaDownloader(md_filepath, self.config.images_dir, self.logger)
            downloaded = downloader.process_markdown()
            if downloaded > 0:
                self.logger.info(f"✓ Successfully downloaded {downloaded} media files")
        except Exception as e:
            self.logger.error(f"Media download failed: {str(e)}")
            import traceback
            self.logger.debug(traceback.format_exc())

        self._print_summary(all_results)
        return all_results

    def _print_summary(self, results: Dict[str, List[str]]) -> None:
        """打印摘要"""
        total_posts = sum(len(urls) for urls in results.values())
        self.logger.info("=" * 60)
        self.logger.info("CRAWL SUMMARY")
        self.logger.info("=" * 60)
        self.logger.info(f"Total users: {len(results)}")
        self.logger.info(f"Total posts: {total_posts}")
        self.logger.info("")
        for user, urls in results.items():
            self.logger.info(f"@{user}: {len(urls)} posts")
        self.logger.info("=" * 60)


# ============================================================================
# CLI 入口
# ============================================================================

def main():
    """CLI 入口"""
    crawler = None

    try:
        crawler = CrawlHot()

        if len(sys.argv) < 2:
            print("Usage: python craw_hot_refactored.py <command> [args]")
            print("\nCommands:")
            print("  add <username>     - Add a user to list")
            print("  remove <username>  - Remove a user from list")
            print("  list               - List all users")
            print("  crawl              - Crawl all users' today posts")
            print("  crawl <username>   - Crawl a single user's today posts")
            sys.exit(1)

        command = sys.argv[1].lower()

        if command == "add":
            if len(sys.argv) < 3:
                print("Error: username required")
                sys.exit(1)
            crawler.user_manager.add(sys.argv[2])

        elif command == "remove":
            if len(sys.argv) < 3:
                print("Error: username required")
                sys.exit(1)
            crawler.user_manager.remove(sys.argv[2])

        elif command == "list":
            crawler.user_manager.list()

        elif command == "crawl":
            if len(sys.argv) >= 3:
                # 单用户抓取：使用与全部用户相同的策略
                username = sys.argv[2]
                results = crawler.crawl_single_user_full(username)
            else:
                results = crawler.crawl_all_users()

        else:
            print(f"Unknown command: {command}")
            sys.exit(1)

    finally:
        if crawler:
            crawler.lock.release()


if __name__ == "__main__":
    main()
