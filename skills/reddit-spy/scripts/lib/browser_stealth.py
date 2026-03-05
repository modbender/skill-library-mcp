"""Browser-based stealth fetcher using Playwright + playwright-stealth.

Bypasses Reddit's bot detection with realistic browser fingerprints,
randomized viewports, and cookie persistence.
"""

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from .ua_pool import get_random_ua, get_random_viewport
from .rate_limiter import wait, mark

BASE_URL = "https://old.reddit.com"
CACHE_DIR = Path.home() / ".openclaw" / ".reddit-spy-cache"
COOKIE_DIR = CACHE_DIR / "browser-cookies"
BROWSER_TIMEOUT = 30000

try:
    from playwright.sync_api import sync_playwright
    from playwright_stealth import Stealth
    STEALTH_AVAILABLE = True
except ImportError:
    STEALTH_AVAILABLE = False


def _ensure_cookie_dir() -> None:
    COOKIE_DIR.mkdir(parents=True, exist_ok=True)


def _cookie_path() -> Path:
    _ensure_cookie_dir()
    return COOKIE_DIR / "state.json"


def is_available() -> bool:
    return STEALTH_AVAILABLE


def _extract_json_from_page(page: Any, url: str) -> Dict[str, Any]:
    content = page.content()
    body = page.locator("body").inner_text()
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        if "<html" in content[:200].lower():
            raise ValueError(f"Reddit served HTML instead of JSON: {url}")
        raise ValueError(f"Could not parse JSON from: {url}")


def fetch_json(path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    if not STEALTH_AVAILABLE:
        raise RuntimeError("playwright-stealth not installed. Run: pip install playwright-stealth playwright && playwright install chromium")

    url = _build_url(path, params)
    wait("browser.reddit.com")

    with Stealth().use_sync(sync_playwright()) as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-setuid-sandbox"])
        context = _create_context(browser)
        page = context.new_page()
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=BROWSER_TIMEOUT)
            mark("browser.reddit.com")
            result = _extract_json_from_page(page, url)
            context.storage_state(path=str(_cookie_path()))
            return result
        finally:
            browser.close()


def _build_url(path: str, params: Optional[Dict[str, Any]]) -> str:
    url = f"{BASE_URL}{path}"
    if params:
        query = "&".join(f"{k}={v}" for k, v in params.items())
        url = f"{url}?{query}"
    return url


def _create_context(browser: Any) -> Any:
    viewport = get_random_viewport()
    cookie_file = _cookie_path()
    if cookie_file.exists():
        return browser.new_context(
            storage_state=str(cookie_file),
            user_agent=get_random_ua(),
            viewport=viewport,
        )
    return browser.new_context(user_agent=get_random_ua(), viewport=viewport)


def _extract_children(data: Dict) -> List[Dict]:
    return [c.get("data", c) for c in data.get("data", {}).get("children", [])]


def fetch_about(subreddit: str) -> Dict[str, Any]:
    data = fetch_json(f"/r/{subreddit}/about.json")
    return data.get("data", data)


def fetch_posts(subreddit: str, sort: str = "hot", timeframe: str = "week", limit: int = 25) -> List[Dict]:
    params = {"limit": min(limit, 100), "t": timeframe, "raw_json": 1}
    return _extract_children(fetch_json(f"/r/{subreddit}/{sort}.json", params))


def fetch_comments_raw(post_url: str, depth: int = 8, limit: int = 200) -> Any:
    path = post_url.rstrip("/")
    if "reddit.com" in path:
        path = path.split("reddit.com")[1]
    if not path.endswith(".json"):
        path = f"{path}/.json"
    return fetch_json(path, {"depth": depth, "limit": limit, "raw_json": 1})
