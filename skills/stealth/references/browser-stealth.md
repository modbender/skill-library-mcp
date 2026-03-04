# Stealth Browser Configuration

## Why This Matters

Even with a residential proxy, sites can detect automation through browser fingerprinting. Headless Chrome leaks signals: `navigator.webdriver` is true, WebGL renderer says "SwiftShader", plugin list is empty, etc.

## Playwright Stealth Config

```python
from playwright.async_api import async_playwright

async def launch_stealth(proxy=None):
    pw = await async_playwright().start()
    
    launch_args = [
        "--disable-blink-features=AutomationControlled",
        "--disable-features=IsolateOrigins,site-per-process",
        "--disable-dev-shm-usage",
        "--no-first-run",
    ]
    
    launch_opts = {"args": launch_args, "headless": True}
    if proxy:
        launch_opts["proxy"] = {
            "server": f"http://{proxy['host']}:{proxy['port']}",
            "username": proxy["username"],
            "password": proxy["password"],
        }
    
    browser = await pw.chromium.launch(**launch_opts)
    
    context = await browser.new_context(
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/131.0.0.0 Safari/537.36",
        viewport={"width": 1920, "height": 1080},
        locale="en-US",
        timezone_id="America/Los_Angeles",
        color_scheme="light",
    )
    
    # Remove webdriver flag
    await context.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5]
        });
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en']
        });
        window.chrome = { runtime: {} };
    """)
    
    return browser, context
```

## Request Headers

Always send realistic headers. Missing or wrong headers are a detection signal.

```python
STEALTH_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "DNT": "1",
}
```

## User-Agent Rotation

Don't use the same UA forever. Rotate from a realistic pool:

```python
import random

USER_AGENTS = [
    # Chrome on Mac
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    # Chrome on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    # Firefox on Mac
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:132.0) Gecko/20100101 Firefox/132.0",
    # Chrome on Linux
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    # Safari on Mac
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Safari/605.1.15",
]

ua = random.choice(USER_AGENTS)
```

## Human-Like Behavior

Bot detection systems analyze behavior patterns. Real users don't navigate instantly.

```python
import random, asyncio

async def human_delay(min_ms=200, max_ms=800):
    """Random delay between actions."""
    await asyncio.sleep(random.uniform(min_ms, max_ms) / 1000)

async def human_click(page, selector):
    """Move to element, small pause, then click."""
    element = await page.query_selector(selector)
    await element.scroll_into_view_if_needed()
    await human_delay(100, 300)
    await element.hover()
    await human_delay(50, 150)
    await element.click()

async def human_type(page, selector, text):
    """Type with random delays between keystrokes."""
    await page.click(selector)
    for char in text:
        await page.keyboard.press(char)
        await asyncio.sleep(random.uniform(0.05, 0.15))
```

## Nuclear Option: Camoufox

If Playwright stealth isn't enough (rare, but some sites like Datadome catch everything):

```bash
npm install @askjo/camoufox-browser
```

Camoufox is Firefox-based with C++ level anti-detection. Bypasses Canvas, WebGL, AudioContext, and font fingerprinting. Use when Playwright stealth fails on hardened targets.

## Detection Test

Test your stealth config against common detection tools:

```python
# Load these pages and check results:
test_urls = [
    "https://bot.sannysoft.com/",           # Shows all browser fingerprint leaks
    "https://abrahamjuliot.github.io/creepjs/", # Advanced fingerprinting test
    "https://browserleaks.com/webgl",        # WebGL fingerprint
]
```

If sannysoft shows all green, your stealth config is working.
