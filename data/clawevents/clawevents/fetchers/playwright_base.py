"""Base class for Playwright-based scrapers.

Install Playwright to enable these fetchers:
  pip install playwright
  playwright install chromium
"""

from __future__ import annotations
import logging
from typing import Optional

log = logging.getLogger(__name__)

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    log.debug("playwright not installed — browser-based fetchers disabled")


def fetch_page_html(url: str, wait_selector: Optional[str] = None,
                    timeout_ms: int = 15000) -> Optional[str]:
    """Fetch fully-rendered HTML via headless Chromium."""
    if not PLAYWRIGHT_AVAILABLE:
        log.warning("playwright not installed. Run: pip install playwright && playwright install chromium")
        return None
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36")
            page.goto(url, timeout=timeout_ms)
            if wait_selector:
                page.wait_for_selector(wait_selector, timeout=timeout_ms)
            else:
                page.wait_for_load_state("networkidle", timeout=timeout_ms)
            html = page.content()
            browser.close()
            return html
    except Exception as exc:
        log.warning("Playwright fetch error for %s: %s", url, exc)
        return None
