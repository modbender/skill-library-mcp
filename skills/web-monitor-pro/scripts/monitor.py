#!/usr/bin/env python3
"""
Web Monitor Pro — Track changes on web pages and get alerts.

A CLI tool for monitoring web pages for price drops, stock changes, content
updates, and custom conditions. Stores all data in ~/.web-monitor/ (or the
directory set by WEB_MONITOR_DIR). Uses curl (via subprocess) to fetch pages
because Python's urllib often gets blocked by sites that expect a real browser
User-Agent string, and curl handles redirects/compression/TLS more reliably.

v3.0.0 additions:
- AI-powered change summaries (algorithmic, no LLM)
- HTML diff generation (side-by-side visual comparison)
- Multi-source price comparison across groups
- Monitor templates (price-drop, restock, content-update, sale, new-release)
- JS rendering via Playwright (optional, try/except import)
- Webhook notifications (uses urllib.request.urlopen for POST)

Version: 3.0.0
"""

import argparse
import difflib
import hashlib
import html as html_module
import json
import os
import re
import subprocess
import sys
import time
import webbrowser
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Conditional Playwright import — only needed if --browser flag is used.
# If not installed, we fall back to curl and print a helpful message.
try:
    from playwright.sync_api import sync_playwright
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False

# cloudscraper handles Cloudflare JS challenges without a full browser.
# Lightweight alternative to Playwright for Cloudflare-protected sites.
try:
    import cloudscraper as _cloudscraper_module
    HAS_CLOUDSCRAPER = True
except ImportError:
    _cloudscraper_module = None
    HAS_CLOUDSCRAPER = False

# Webhook POSTs use urllib.request.urlopen — standard library, no extra deps.
import urllib.request
import urllib.error

VERSION = "3.5.0"

WHATS_NEW = "Quickstart command with smart suggestions. Better first-run experience."

# --- Storage paths ---
STORE_DIR = Path(os.environ.get("WEB_MONITOR_DIR", Path.home() / ".web-monitor"))
MONITORS_FILE = STORE_DIR / "monitors.json"
SNAPSHOTS_DIR = STORE_DIR / "snapshots"
SCREENSHOTS_DIR = STORE_DIR / "screenshots"
MAX_SNAPSHOTS_PER_MONITOR = 50

# --- Color support ---
NO_COLOR = os.environ.get("NO_COLOR") is not None

def _c(code, text):
    """Wrap text in ANSI color codes, unless NO_COLOR is set."""
    if NO_COLOR or not sys.stdout.isatty():
        return text
    return f"\033[{code}m{text}\033[0m"

def _bold(t): return _c("1", t)
def _green(t): return _c("32", t)
def _yellow(t): return _c("33", t)
def _red(t): return _c("31", t)
def _dim(t): return _c("2", t)
def _cyan(t): return _c("36", t)


# --- Templates ---

TEMPLATES = {
    "price-drop": {
        "description": "Monitor for price decreases. Takes initial snapshot as baseline.",
        "condition": None,  # set dynamically after first fetch
        "interval_minutes": 360,
        "priority": "high",
        "label_prefix": "[Price Drop]",
        "type": "price",
    },
    "restock": {
        "description": "Watch for item to come back in stock.",
        "condition": "contains 'in stock'",
        "interval_minutes": 120,
        "priority": "high",
        "label_prefix": "[Restock]",
        "type": "stock",
    },
    "content-update": {
        "description": "Track page content changes with smart diff.",
        "condition": None,
        "interval_minutes": 360,
        "priority": "medium",
        "label_prefix": "[Content]",
        "type": "content",
    },
    "sale": {
        "description": "Watch for sale, discount, or % off keywords.",
        "condition": "contains 'sale'",
        "interval_minutes": 360,
        "priority": "medium",
        "label_prefix": "[Sale]",
        "type": "content",
    },
    "new-release": {
        "description": "Watch for new items or versions on a page.",
        "condition": None,
        "interval_minutes": 720,
        "priority": "low",
        "label_prefix": "[New Release]",
        "type": "content",
    },
}


# --- Helpers ---

META_FILE = STORE_DIR / "meta.json"


def _load_meta():
    if META_FILE.exists():
        try:
            return json.loads(META_FILE.read_text())
        except Exception:
            pass
    return {}


def _save_meta(meta):
    ensure_dirs()
    META_FILE.write_text(json.dumps(meta, indent=2))


def _check_whats_new():
    """Show what's new message once after upgrade. Returns True if shown."""
    meta = _load_meta()
    last_seen = meta.get("last_seen_version")
    if last_seen == VERSION:
        return False
    meta["last_seen_version"] = VERSION
    _save_meta(meta)
    if last_seen is not None:
        print()
        print(f"🆕 Web Monitor Pro v{VERSION} — What's new:")
        print(f"   {WHATS_NEW}")
        print(f"   Run: monitor.py help for details")
        print()
    return last_seen is not None


def ensure_dirs():
    STORE_DIR.mkdir(parents=True, exist_ok=True)
    SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)


def load_monitors():
    if MONITORS_FILE.exists():
        return json.loads(MONITORS_FILE.read_text())
    return {}


def save_monitors(monitors):
    ensure_dirs()
    MONITORS_FILE.write_text(json.dumps(monitors, indent=2))


def gen_id(url, label):
    slug = re.sub(r'[^a-z0-9]+', '-', (label or url).lower()).strip('-')[:40]
    short_hash = hashlib.md5(url.encode()).hexdigest()[:6]
    return f"{slug}-{short_hash}"


def find_monitor(monitors, query):
    """Find a monitor by exact ID or partial match."""
    if query in monitors:
        return query, monitors[query]
    matches = [(k, v) for k, v in monitors.items() if query.lower() in k.lower()]
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        print(_red(f"Ambiguous ID '{query}'. Matches:"))
        for k, v in matches:
            print(f"  {k} — {v.get('label', v['url'])}")
        return None, None
    return None, None


def relative_time(iso_str):
    """Convert ISO timestamp to relative time string like '2h ago'."""
    if not iso_str:
        return "never"
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        diff = now - dt
        secs = int(diff.total_seconds())
        if secs < 60:
            return "just now"
        if secs < 3600:
            m = secs // 60
            return f"{m}m ago"
        if secs < 86400:
            h = secs // 3600
            return f"{h}h ago"
        d = secs // 86400
        return f"{d}d ago"
    except Exception:
        return "unknown"


def days_since(iso_str):
    """Days since a timestamp."""
    if not iso_str:
        return 0
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        return max(0, (now - dt).days)
    except Exception:
        return 0


def _extract_prices_from_jsonld(data):
    """Recursively extract prices from JSON-LD structured data."""
    prices = []
    if isinstance(data, list):
        for item in data:
            prices.extend(_extract_prices_from_jsonld(item))
    elif isinstance(data, dict):
        if 'price' in data:
            try:
                prices.append(float(str(data['price']).replace(',', '')))
            except (ValueError, TypeError):
                pass
        if 'lowPrice' in data:
            try:
                prices.append(float(str(data['lowPrice']).replace(',', '')))
            except (ValueError, TypeError):
                pass
        if 'offers' in data:
            prices.extend(_extract_prices_from_jsonld(data['offers']))
        for v in data.values():
            if isinstance(v, (dict, list)):
                prices.extend(_extract_prices_from_jsonld(v))
    return prices


def extract_prices(content):
    """Extract all prices from content text. Returns list of floats."""
    prices = []
    for p in re.findall(r'STRUCTURED_PRICE:R([\d,.]+)', content):
        try:
            prices.append(float(p.replace(',', '')))
        except ValueError:
            pass
    for p in re.findall(r'[R$£€]\s?([\d,]+(?:\.\d{2})?)', content):
        try:
            val = float(p.replace(',', ''))
            if val >= 10:
                prices.append(val)
        except ValueError:
            pass
    return prices


def extract_best_price(content, target=None):
    """Get the most likely product price from content."""
    prices = extract_prices(content)
    if not prices:
        return None
    if target:
        return min(prices, key=lambda x: abs(x - target))
    prices.sort()
    return prices[len(prices) // 2]


def _strip_html(html_text):
    """Strip scripts, styles, and tags from HTML, return clean text."""
    text = re.sub(r'<script[^>]*>.*?</script>', '', html_text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def _extract_structured_prices(html):
    """Extract prices from JSON-LD and meta tags in raw HTML."""
    structured_prices = []
    json_ld_blocks = re.findall(
        r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        html, re.DOTALL | re.IGNORECASE
    )
    for block in json_ld_blocks:
        try:
            data = json.loads(block)
            structured_prices.extend(_extract_prices_from_jsonld(data))
        except (json.JSONDecodeError, ValueError):
            pass

    meta_prices = re.findall(
        r'<meta[^>]*(?:property|name)=["\'](?:og:price:amount|product:price:amount|price)["\']'
        r'[^>]*content=["\']([^"\']+)["\']',
        html, re.IGNORECASE
    )
    for mp in meta_prices:
        try:
            structured_prices.append(float(mp.replace(',', '')))
        except ValueError:
            pass
    return structured_prices


def fetch_url(url, selector=None):
    """
    Fetch URL content using curl.

    We use subprocess to call curl because:
    1. curl handles TLS, redirects, and compression better than urllib
    2. We can set a realistic User-Agent to avoid bot detection
    3. Many e-commerce sites block Python's default HTTP clients
    """
    try:
        result = subprocess.run(
            ["curl", "-sL", "--max-time", "30", "-A",
             "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
             "AppleWebKit/537.36 (KHTML, like Gecko) "
             "Chrome/120.0.0.0 Safari/537.36",
             url],
            capture_output=True, text=True, timeout=35
        )
        if result.returncode != 0:
            return None, f"curl failed: {result.stderr[:200]}", ""
        html = result.stdout

        text = _strip_html(html)
        structured_prices = _extract_structured_prices(html)

        title_match = re.search(r'<title[^>]*>(.*?)</title>', html, re.DOTALL | re.IGNORECASE)
        page_title = title_match.group(1).strip() if title_match else ""
        page_title = re.sub(r'<[^>]+>', '', page_title).strip()

        if len(text) < 200 and not structured_prices:
            return None, (f"Page returned minimal content ({len(text)} chars). "
                          "Likely JS-rendered. Try --browser flag or OpenClaw browser tool."), page_title

        if structured_prices:
            price_str = " ".join(f"STRUCTURED_PRICE:R{p:.2f}" for p in structured_prices)
            text = price_str + " " + text

        if selector:
            pattern = None
            if selector.startswith('#'):
                pattern = rf'id="{re.escape(selector[1:])}"[^>]*>(.*?)</\w+>'
            elif selector.startswith('.'):
                pattern = rf'class="[^"]*{re.escape(selector[1:])}[^"]*"[^>]*>(.*?)</\w+>'
            if pattern:
                match = re.search(pattern, html, re.DOTALL | re.IGNORECASE)
                if match:
                    extracted = re.sub(r'<[^>]+>', ' ', match.group(1))
                    text = re.sub(r'\s+', ' ', extracted).strip()

        return text, None, page_title
    except Exception as e:
        return None, str(e), ""


def fetch_url_cloudscraper(url, selector=None):
    """
    Fetch URL using cloudscraper to bypass Cloudflare JS challenges.
    cloudscraper handles Cloudflare JS challenges without a full browser.
    Requires: pip3 install cloudscraper
    """
    if not HAS_CLOUDSCRAPER:
        return None, ("Cloudscraper not installed. Install with: "
                      "pip3 install cloudscraper"), ""
    try:
        scraper = _cloudscraper_module.create_scraper(
            browser={'browser': 'chrome', 'platform': 'darwin', 'mobile': False}
        )
        resp = scraper.get(url, timeout=30)
        resp.raise_for_status()
        html = resp.text

        text = _strip_html(html)
        structured_prices = _extract_structured_prices(html)

        title_match = re.search(r'<title[^>]*>(.*?)</title>', html, re.DOTALL | re.IGNORECASE)
        page_title = title_match.group(1).strip() if title_match else ""
        page_title = re.sub(r'<[^>]+>', '', page_title).strip()

        if len(text) < 200 and not structured_prices:
            return None, (f"Page returned minimal content ({len(text)} chars) via cloudscraper. "
                          "Site may require full browser rendering."), page_title

        if structured_prices:
            price_str = " ".join(f"STRUCTURED_PRICE:R{p:.2f}" for p in structured_prices)
            text = price_str + " " + text

        if selector:
            pattern = None
            if selector.startswith('#'):
                pattern = rf'id="{re.escape(selector[1:])}"[^>]*>(.*?)</\w+>'
            elif selector.startswith('.'):
                pattern = rf'class="[^"]*{re.escape(selector[1:])}[^"]*"[^>]*>(.*?)</\w+>'
            if pattern:
                match = re.search(pattern, html, re.DOTALL | re.IGNORECASE)
                if match:
                    extracted = re.sub(r'<[^>]+>', ' ', match.group(1))
                    text = re.sub(r'\s+', ' ', extracted).strip()

        return text, None, page_title
    except Exception as e:
        return None, f"cloudscraper error: {e}", ""


def fetch_url_browser_playwright(url, selector=None):
    """
    Fetch URL using Playwright headless browser for JS-rendered pages.

    Requires: pip3 install playwright && python3 -m playwright install chromium
    Falls back gracefully if Playwright is not available.
    """
    if not HAS_PLAYWRIGHT:
        return None, ("JS rendering needs Playwright. Install with: "
                      "pip3 install playwright && python3 -m playwright install chromium"), ""

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                           "AppleWebKit/537.36 (KHTML, like Gecko) "
                           "Chrome/120.0.0.0 Safari/537.36"
            )
            page.goto(url, timeout=30000, wait_until="networkidle")

            html = page.content()
            page_title = page.title() or ""

            text = _strip_html(html)
            structured_prices = _extract_structured_prices(html)

            if structured_prices:
                price_str = " ".join(f"STRUCTURED_PRICE:R{p:.2f}" for p in structured_prices)
                text = price_str + " " + text

            if selector:
                try:
                    el = page.query_selector(selector)
                    if el:
                        text = el.inner_text()
                except Exception:
                    pass

            browser.close()
            return text, None, page_title
    except Exception as e:
        return None, f"Playwright error: {e}", ""


def fetch_url_auto(url, selector=None, use_browser=False, engine="auto"):
    """
    Fetch URL with smart engine fallback chain.

    Engine options:
      auto: curl -> cloudscraper -> playwright (tries each on failure)
      curl: curl only
      cloudscraper: cloudscraper only
      browser: Playwright only
    """
    if engine == "openclaw":
        # openclaw engine means content is fetched externally (via OpenClaw browser tool)
        # and passed in via --content-file. If we reach here during a fetch, it means
        # the caller didn't provide pre-fetched content.
        return None, ("This monitor uses the 'openclaw' engine. Content must be provided "
                       "externally via --content-file. Use OpenClaw's browser tool to fetch "
                       "the page, save to a file, then: monitor.py check --id <id> --content-file <path>"), ""
    if engine == "curl":
        return fetch_url(url, selector)
    if engine == "cloudscraper":
        return fetch_url_cloudscraper(url, selector)
    if engine == "browser" or use_browser:
        content, err, title = fetch_url_browser_playwright(url, selector)
        if err and not HAS_PLAYWRIGHT:
            content, err2, title = fetch_url(url, selector)
            if content:
                return content, None, title
            return content, err, title
        return content, err, title

    # engine == "auto": try curl -> cloudscraper -> playwright
    content, err, title = fetch_url(url, selector)
    if content:
        return content, None, title

    # curl failed or returned minimal content, try cloudscraper
    if HAS_CLOUDSCRAPER:
        content2, err2, title2 = fetch_url_cloudscraper(url, selector)
        if content2:
            return content2, None, title2 or title

    # cloudscraper failed or unavailable, try playwright
    if HAS_PLAYWRIGHT:
        content3, err3, title3 = fetch_url_browser_playwright(url, selector)
        if content3:
            return content3, None, title3 or title

    # Nothing worked. Build helpful error message.
    suggestions = []
    if not HAS_CLOUDSCRAPER:
        suggestions.append("pip3 install cloudscraper (for Cloudflare sites)")
    if not HAS_PLAYWRIGHT:
        suggestions.append("pip3 install playwright && python3 -m playwright install chromium (for JS-heavy sites)")
    hint = ""
    if suggestions:
        hint = " Try installing: " + "; ".join(suggestions)
    return None, (err or "Failed to fetch page.") + hint, title


def fetch_url_simple(url, selector=None):
    result = fetch_url(url, selector)
    if len(result) == 3:
        return result[0], result[1]
    return result


def save_snapshot(monitor_id, content, content_hash, note=None):
    ensure_dirs()
    snap_dir = SNAPSHOTS_DIR / monitor_id
    snap_dir.mkdir(exist_ok=True)

    timestamp = datetime.now(timezone.utc).isoformat()
    snap = {
        "timestamp": timestamp,
        "hash": content_hash,
        "content": content[:10000],
    }
    if note:
        snap["note"] = note

    snap_file = snap_dir / f"{int(time.time())}.json"
    snap_file.write_text(json.dumps(snap, indent=2))

    snaps = sorted(snap_dir.glob("*.json"), key=lambda f: f.name, reverse=True)
    for old in snaps[MAX_SNAPSHOTS_PER_MONITOR:]:
        old.unlink()

    return snap


def get_latest_snapshot(monitor_id):
    snap_dir = SNAPSHOTS_DIR / monitor_id
    if not snap_dir.exists():
        return None
    snaps = sorted(snap_dir.glob("*.json"), key=lambda f: f.name, reverse=True)
    if not snaps:
        return None
    return json.loads(snaps[0].read_text())


def get_snapshots(monitor_id, limit=None):
    snap_dir = SNAPSHOTS_DIR / monitor_id
    if not snap_dir.exists():
        return []
    snaps = sorted(snap_dir.glob("*.json"), key=lambda f: f.name, reverse=True)
    if limit:
        snaps = snaps[:limit]
    results = []
    for s in snaps:
        results.append(json.loads(s.read_text()))
    return results


# --- Feature 1: AI-powered Change Summaries ---

def generate_change_summary(old_content, new_content, monitor):
    """
    Generate a human-readable summary of what changed.
    Algorithmic diffing with smart formatting, no LLM needed.
    """
    if not old_content:
        return "First snapshot taken."

    condition = (monitor.get("condition") or "").lower()
    target = monitor.get("target")

    old_prices = extract_prices(old_content)
    new_prices = extract_prices(new_content)

    # Price change summary
    if ("price" in condition or target or monitor.get("price_history")) and old_prices and new_prices:
        ref_price = target or old_prices[0]
        old_best = min(old_prices, key=lambda x: abs(x - ref_price))
        new_best = min(new_prices, key=lambda x: abs(x - ref_price))
        if old_best != new_best:
            pct = abs(new_best - old_best) / old_best * 100
            if new_best < old_best:
                summary = f"Price dropped from R{old_best:,.0f} to R{new_best:,.0f} ({pct:.0f}% off)"
            else:
                summary = f"Price increased from R{old_best:,.0f} to R{new_best:,.0f} ({pct:.0f}% up)"

            # Check if lowest in history
            ph = monitor.get("price_history", [])
            if ph and new_best <= min(p["price"] for p in ph):
                days_tracked = days_since(ph[0]["date"]) if ph else 0
                if days_tracked > 1:
                    summary += f". Lowest price in {days_tracked} days."
                else:
                    summary += ". New lowest price."
            return summary

    # Stock change summary
    stock_in = ["in stock", "available", "add to cart", "add to basket"]
    stock_out = ["out of stock", "sold out", "unavailable", "notify me"]
    old_lower = old_content.lower()
    new_lower = new_content.lower()

    old_in_stock = any(t in old_lower for t in stock_in)
    old_out_stock = any(t in old_lower for t in stock_out)
    new_in_stock = any(t in new_lower for t in stock_in)
    new_out_stock = any(t in new_lower for t in stock_out)

    if old_out_stock and new_in_stock and not new_out_stock:
        # Try to figure out how long it was out of stock
        ph = monitor.get("price_history", [])
        snaps = get_snapshots(monitor.get("id", ""), limit=20)
        out_days = 0
        for snap in snaps[1:]:
            sc = snap.get("content", "").lower()
            if any(t in sc for t in stock_out):
                out_days = days_since(snap.get("timestamp"))
                break
        if out_days > 0:
            return f"Back in stock! Was out of stock for {out_days} day{'s' if out_days != 1 else ''}."
        return "Back in stock!"

    if old_in_stock and new_out_stock and not new_in_stock:
        return "Gone out of stock."

    # Content diff: extract actual changes
    old_sentences = [s.strip() for s in re.split(r'[.!?\n]+', old_content) if len(s.strip()) > 15]
    new_sentences = [s.strip() for s in re.split(r'[.!?\n]+', new_content) if len(s.strip()) > 15]

    old_set = set(s.lower() for s in old_sentences)
    new_set = set(s.lower() for s in new_sentences)

    added_lower = new_set - old_set
    removed_lower = old_set - new_set

    # Get original-case versions of added sentences
    added = [s for s in new_sentences if s.lower() in added_lower]
    removed = [s for s in old_sentences if s.lower() in removed_lower]

    if not added and not removed:
        # Minor formatting changes
        old_words = set(old_content.lower().split())
        new_words = set(new_content.lower().split())
        new_w = new_words - old_words
        gone_w = old_words - new_words
        if new_w or gone_w:
            parts = []
            if new_w:
                parts.append(f"{len(new_w)} new words")
            if gone_w:
                parts.append(f"{len(gone_w)} removed words")
            return "Minor changes: " + ", ".join(parts) + "."
        return "Content reformatted (no meaningful text changes)."

    parts = []
    if added:
        # Show the most meaningful added content
        added.sort(key=len, reverse=True)
        best = added[0]
        if len(best) > 120:
            best = best[:120] + "..."
        if len(added) == 1:
            parts.append(f'New: "{best}"')
        else:
            parts.append(f'{len(added)} new sections. Top: "{best}"')

    if removed:
        removed.sort(key=len, reverse=True)
        best = removed[0]
        if len(best) > 80:
            best = best[:80] + "..."
        if len(removed) == 1:
            parts.append(f'Removed: "{best}"')
        else:
            parts.append(f"{len(removed)} sections removed")

    return ". ".join(parts) + "."


# --- Feature 2: HTML Diff ---

def save_html_snapshot(monitor_id, content, label="current"):
    """Save content for HTML diffing."""
    ensure_dirs()
    ss_dir = SCREENSHOTS_DIR / monitor_id
    ss_dir.mkdir(parents=True, exist_ok=True)
    filepath = ss_dir / f"{label}.txt"
    filepath.write_text(content[:50000])
    return filepath


def generate_html_diff(monitor_id, old_content, new_content, monitor_label=""):
    """Generate a side-by-side HTML diff page. Returns path to the diff file."""
    ensure_dirs()
    ss_dir = SCREENSHOTS_DIR / monitor_id
    ss_dir.mkdir(parents=True, exist_ok=True)

    # Save old/new for reference
    (ss_dir / "old.txt").write_text(old_content[:50000])
    (ss_dir / "new.txt").write_text(new_content[:50000])

    # Split into lines for diffing
    old_lines = old_content[:20000].splitlines() or old_content[:20000].split('. ')
    new_lines = new_content[:20000].splitlines() or new_content[:20000].split('. ')

    # If content is one big blob, split on sentences
    if len(old_lines) <= 2:
        old_lines = [s.strip() + '.' for s in old_content[:20000].split('.') if s.strip()]
    if len(new_lines) <= 2:
        new_lines = [s.strip() + '.' for s in new_content[:20000].split('.') if s.strip()]

    differ = difflib.HtmlDiff(wrapcolumn=80)
    diff_table = differ.make_table(
        old_lines[:200], new_lines[:200],
        fromdesc="Previous", todesc="Current",
        context=True, numlines=3
    )

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    diff_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Diff: {html_module.escape(monitor_label or monitor_id)}</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 20px; background: #1a1a2e; color: #eee; }}
h1 {{ color: #e94560; }}
.info {{ color: #888; margin-bottom: 20px; }}
table.diff {{ border-collapse: collapse; width: 100%; font-size: 13px; font-family: 'SF Mono', Monaco, monospace; }}
table.diff td {{ padding: 4px 8px; border: 1px solid #333; vertical-align: top; }}
table.diff th {{ padding: 8px; background: #16213e; border: 1px solid #333; }}
.diff_add {{ background-color: #1b4332; color: #95d5b2; }}
.diff_sub {{ background-color: #5c1a1a; color: #f4a4a4; }}
.diff_chg {{ background-color: #3d3200; color: #ffd166; }}
td.diff_header {{ background: #16213e; color: #0f3460; font-weight: bold; }}
.legend {{ margin-top: 20px; }}
.legend span {{ display: inline-block; padding: 4px 12px; margin-right: 10px; border-radius: 4px; font-size: 13px; }}
.leg-add {{ background: #1b4332; color: #95d5b2; }}
.leg-rem {{ background: #5c1a1a; color: #f4a4a4; }}
.leg-chg {{ background: #3d3200; color: #ffd166; }}
</style>
</head>
<body>
<h1>Web Monitor Diff</h1>
<div class="info">
    <strong>{html_module.escape(monitor_label or monitor_id)}</strong><br>
    Generated: {timestamp}
</div>
{diff_table}
<div class="legend">
    <span class="leg-add">Added</span>
    <span class="leg-rem">Removed</span>
    <span class="leg-chg">Changed</span>
</div>
</body>
</html>"""

    diff_path = ss_dir / "diff.html"
    diff_path.write_text(diff_html)
    return str(diff_path)


# --- Feature 6: Webhooks ---

def fire_webhooks(monitor, event_data):
    """
    POST event data to all configured webhooks for a monitor.
    Uses urllib.request.urlopen for the HTTP POST (standard library).
    """
    webhooks = monitor.get("webhooks", [])
    if not webhooks:
        return

    payload = json.dumps({
        "monitor_id": monitor.get("id", ""),
        "label": monitor.get("label", ""),
        "url": monitor.get("url", ""),
        "event": event_data,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }).encode("utf-8")

    for wh_url in webhooks:
        try:
            # urllib.request.urlopen POST — sends JSON payload to webhook URL
            req = urllib.request.Request(
                wh_url,
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            urllib.request.urlopen(req, timeout=10)
        except Exception as e:
            # Don't crash on webhook failures, just note it
            print(_dim(f"  Webhook failed ({wh_url[:40]}...): {e}"), file=sys.stderr)


# --- Existing helpers (smart_diff now wraps generate_change_summary) ---

def smart_diff(old_content, new_content, monitor):
    """Generate a meaningful diff summary based on monitor type."""
    return generate_change_summary(old_content, new_content, monitor)


def update_price_history(monitor, content):
    """Extract current price and update price_history array."""
    target = monitor.get("target")
    price = extract_best_price(content, target)
    if price is None:
        return None

    if "price_history" not in monitor:
        monitor["price_history"] = []

    now = datetime.now(timezone.utc).isoformat()
    monitor["price_history"].append({"date": now, "price": price})
    monitor["price_history"] = monitor["price_history"][-200:]
    return price


def check_condition(condition, content, monitor=None):
    """Check if a condition is met. Returns (bool, description)."""
    if not condition or not content:
        return False, None

    cond_lower = condition.lower()
    content_lower = content.lower()

    price_match = re.search(r'price\s*(below|above|<|>|<=|>=)\s*[\$£€R]?\s*([\d,.]+)', cond_lower)
    if price_match:
        op = price_match.group(1)
        threshold = float(price_match.group(2).replace(',', ''))
        prices = extract_prices(content)
        if prices:
            best = min(prices, key=lambda x: abs(x - threshold))
            met = False
            if op in ('below', '<') and best < threshold:
                met = True
            elif op in ('above', '>') and best > threshold:
                met = True
            elif op == '<=' and best <= threshold:
                met = True
            elif op == '>=' and best >= threshold:
                met = True
            desc = f"Price is R{best:,.0f} (threshold: {op} R{threshold:,.0f})"
            return met, desc

    contains_match = re.search(r"contains\s+['\"](.+?)['\"]", cond_lower)
    if contains_match:
        search = contains_match.group(1)
        met = search in content_lower
        return met, f"'{search}' {'found' if met else 'not found'}"

    not_match = re.search(r"not\s+contains\s+['\"](.+?)['\"]", cond_lower)
    if not_match:
        search = not_match.group(1)
        met = search not in content_lower
        return met, f"'{search}' {'absent (good)' if met else 'still present'}"

    return False, None


# --- Commands ---

def cmd_engines(args):
    """Show which fetch engines are available on this system."""
    print()
    print(_bold("🔧 Fetch Engines"))
    print()

    # curl
    try:
        result = subprocess.run(["curl", "--version"], capture_output=True, text=True, timeout=5)
        version = result.stdout.split('\n')[0].strip() if result.returncode == 0 else None
        if version:
            print(f"  curl: {_green('✅ installed')} ({version.split()[1] if len(version.split()) > 1 else version})")
        else:
            print(f"  curl: {_red('❌ not found')}")
    except Exception:
        print(f"  curl: {_red('❌ not found')}")

    # cloudscraper
    if HAS_CLOUDSCRAPER:
        try:
            cs_version = _cloudscraper_module.__version__
        except AttributeError:
            cs_version = "unknown"
        print(f"  cloudscraper: {_green('✅ installed')} (v{cs_version})")
    else:
        print(f"  cloudscraper: {_red('❌ not installed')} (pip3 install cloudscraper)")

    # playwright
    if HAS_PLAYWRIGHT:
        print(f"  playwright: {_green('✅ installed')}")
    else:
        print(f"  playwright: {_red('❌ not installed')} (pip3 install playwright && python3 -m playwright install chromium)")

    print()
    print(_dim("  Engine fallback order (auto mode): curl -> cloudscraper -> playwright"))
    print()


def cmd_setup(args):
    print()
    print(_bold("👁️  Web Monitor Pro v" + VERSION))
    print()
    print("Track web pages for price drops, stock changes, and content updates.")
    print("All data is stored locally in ~/.web-monitor/")
    print()
    print(_bold("Quick start:"))
    print(f"  {_cyan('monitor.py watch <url>')}    Auto-detect and set up monitoring")
    print(f"  {_cyan('monitor.py dashboard')}      See all your monitors at a glance")
    print(f"  {_cyan('monitor.py check')}          Check all monitors for changes")
    print()
    print(_bold("New in v3:"))
    print(f"  {_cyan('monitor.py template list')}  Pre-built monitoring templates")
    print(f"  {_cyan('monitor.py compare <g>')}    Compare prices across a group")
    print(f"  {_cyan('monitor.py diff <id>')}      Visual side-by-side diff")
    print(f"  {_cyan('--engine <e>')}              Fetch engine: auto, curl, cloudscraper, browser, openclaw")
    print(f"  {_cyan('--browser')}                 JS rendering via Playwright")
    print(f"  {_cyan('--webhook <url>')}           Webhook notifications")
    print()
    print(_bold("Feedback:"))
    print(f"  feedback <message>         Send feedback or suggestions")
    print(f"  feedback --bug <msg>       Report a bug")
    print(f"  feedback --idea <msg>      Suggest a feature")
    print(f"  debug                      System info for bug reports")
    print()
    print(_bold("Examples:"))
    print(f"  monitor.py watch https://amazon.com/dp/B09V3KXJPB")
    print(f"  monitor.py add https://example.com --label 'My Page' --condition \"price below 500\"")
    print(f"  monitor.py template use price-drop https://example.com/product")
    print()
    print(f"Run {_cyan('monitor.py help')} for all commands.")
    print()
    ensure_dirs()
    print(_green("✅ Storage directory ready: " + str(STORE_DIR)))
    print()
    print(_bold("Engines:"))
    engines_available = ["curl"]
    if HAS_CLOUDSCRAPER:
        engines_available.append("cloudscraper")
    if HAS_PLAYWRIGHT:
        engines_available.append("playwright")
    print(f"  Available: {', '.join(engines_available)}")
    if not HAS_CLOUDSCRAPER:
        print(f"  {_dim('Install cloudscraper for Cloudflare bypass: pip3 install cloudscraper')}")
    if not HAS_PLAYWRIGHT:
        print(f"  {_dim('Install Playwright for JS rendering: pip3 install playwright && python3 -m playwright install chromium')}")
    print(f"  Run {_cyan('monitor.py engines')} for details.")
    print()


def cmd_feedback(args):
    """Save feedback locally and generate a GitHub issue URL."""
    import platform
    from urllib.parse import quote

    message = args.message
    label = "web-monitor-pro"
    extra_labels = []

    if args.bug:
        message = args.bug
        extra_labels.append("bug")
    elif args.idea:
        message = args.idea
        extra_labels.append("enhancement")

    if not message:
        print(_red("Please provide a message: monitor.py feedback \"your message\""))
        return

    # Gather system info
    monitors = load_monitors()
    monitor_count = len(monitors)

    sys_info = (
        f"Web Monitor Pro v{VERSION}\n"
        f"Python {sys.version.split()[0]}\n"
        f"OS: {platform.system()} {platform.release()}\n"
        f"Monitors: {monitor_count}\n"
        f"Playwright: {'yes' if HAS_PLAYWRIGHT else 'no'}"
    )

    # Save to local log
    feedback_log = STORE_DIR / "feedback.log"
    ensure_dirs()
    timestamp = datetime.now(timezone.utc).isoformat()
    with open(feedback_log, "a", encoding="utf-8") as f:
        f.write(f"\n--- {timestamp} ---\n{message}\n{sys_info}\n")

    # Build GitHub issue URL
    title = message[:60].replace("\n", " ")
    body = f"{message}\n\n---\n```\n{sys_info}\n```"
    labels = ",".join([label] + extra_labels)
    url = (
        f"https://github.com/openclaw/openclaw/issues/new"
        f"?title={quote(title)}&body={quote(body)}&labels={quote(labels)}"
    )

    print()
    print(f"Thanks! Your feedback helps make Web Monitor Pro better. 👁️")
    print()
    print(f"Open an issue:")
    print(f"  {url}")
    print()


def cmd_debug(args):
    """Print system info for bug reports."""
    import platform

    monitors = load_monitors()
    monitor_count = len(monitors)
    enabled = sum(1 for m in monitors.values() if m.get("enabled", True))

    # Check install method
    install_via = "manual"
    skill_dir = Path(__file__).resolve().parent.parent
    if (skill_dir / ".clawhub").exists() or "clawhub" in str(skill_dir).lower():
        install_via = "clawhub"

    store_size = "unknown"
    if STORE_DIR.exists():
        total_bytes = sum(f.stat().st_size for f in STORE_DIR.rglob("*") if f.is_file())
        if total_bytes > 1_000_000:
            store_size = f"{total_bytes / 1_000_000:.1f} MB"
        else:
            store_size = f"{total_bytes / 1_000:.1f} KB"

    print()
    print(_bold("👁️  Web Monitor Pro Debug Info"))
    print()
    print(f"  Version:       {VERSION}")
    print(f"  Python:        {sys.version.split()[0]}")
    print(f"  OS:            {platform.system()} {platform.release()} ({platform.machine()})")
    print(f"  Data dir:      {STORE_DIR}")
    print(f"  Data size:     {store_size}")
    print(f"  Monitors:      {monitor_count} ({enabled} enabled)")
    print(f"  Cloudscraper:  {'installed' if HAS_CLOUDSCRAPER else 'not installed'}")
    print(f"  Playwright:    {'installed' if HAS_PLAYWRIGHT else 'not installed'}")
    print(f"  Installed via: {install_via}")

    # Recent feedback
    feedback_log = STORE_DIR / "feedback.log"
    if feedback_log.exists():
        content = feedback_log.read_text(encoding="utf-8")
        lines = content.strip().split("\n")
        recent = lines[-10:] if len(lines) > 10 else lines
        if recent:
            print()
            print(f"  Recent feedback log:")
            for line in recent:
                print(f"    {line}")
    print()


def cmd_quickstart(args):
    """Smart first-run helper. Reports available engines and suggests monitoring setups."""
    ensure_dirs()
    monitors = load_monitors()

    engines = ["curl"]
    if HAS_CLOUDSCRAPER:
        engines.append("cloudscraper")
    if HAS_PLAYWRIGHT:
        engines.append("playwright")

    suggestions = [
        {
            "category": "price",
            "icon": "💰",
            "label": "Price Drop Alert",
            "description": "Track product prices on Amazon, Takealot, eBay, or any store",
            "command": 'monitor.py watch "<product-url>"',
            "template": "price-drop",
        },
        {
            "category": "restock",
            "icon": "📦",
            "label": "Back in Stock Alert",
            "description": "Get notified when a sold-out item comes back",
            "command": 'monitor.py template use restock "<product-url>"',
            "template": "restock",
        },
        {
            "category": "news",
            "icon": "📰",
            "label": "Page Change Tracker",
            "description": "Watch news sites, blogs, docs, or competitor pages for updates",
            "command": 'monitor.py watch "<page-url>"',
            "template": "content-update",
        },
        {
            "category": "sale",
            "icon": "🏷️",
            "label": "Sale & Discount Watcher",
            "description": "Get alerted when a sale or discount appears on a page",
            "command": 'monitor.py template use sale "<deals-page-url>"',
            "template": "sale",
        },
    ]

    result = {
        "status": "ok",
        "version": VERSION,
        "total_monitors": len(monitors),
        "data_dir": str(STORE_DIR),
        "engines_available": engines,
        "suggestions": suggestions,
        "templates": list(TEMPLATES.keys()),
        "tips": [],
    }

    if not HAS_CLOUDSCRAPER:
        result["tips"].append("Install cloudscraper for Cloudflare-protected sites: pip3 install cloudscraper")
    if not HAS_PLAYWRIGHT:
        result["tips"].append("Install Playwright for JS-heavy sites (Amazon, SPAs): pip3 install playwright && python3 -m playwright install chromium")

    if len(monitors) == 0:
        result["tips"].append("Start with: monitor.py watch <url> - it auto-detects if it's a price page, stock page, or content page")

    # Also print human-readable
    print()
    print(_bold("👁️  Web Monitor Pro v" + VERSION))
    print()

    if len(monitors) > 0:
        active = sum(1 for m in monitors.values() if m.get("enabled", True))
        print(f"  You have {_bold(str(len(monitors)))} monitors ({active} active)")
        print()
    else:
        print("  No monitors yet. Here's what you can track:")
        print()
        for s in suggestions:
            print(f"  {s['icon']} {_bold(s['label'])}")
            print(f"     {s['description']}")
            print(f"     {_cyan(s['command'])}")
            print()

    print(f"  Engines: {', '.join(engines)}")
    if result["tips"]:
        print()
        for tip in result["tips"]:
            print(f"  💡 {tip}")
    print()

    print(json.dumps(result, indent=2))


def cmd_help(args):
    print()
    print(_bold("👁️  Web Monitor Pro v" + VERSION))
    print()
    print(_bold("Get started:"))
    print(f"  quickstart                 Smart setup with suggestions and engine check")
    print()
    print(_bold("Start monitoring:"))
    print(f"  watch <url>                Auto-detect and set up monitoring")
    print(f"  add <url> [options]        Add a monitor with specific settings")
    print(f"  template list              Show available templates")
    print(f"  template use <name> <url>  Apply a template to a URL")
    print(f"  add-competitor <id> <url>  Link a competitor to existing monitor")
    print(f"  import <file>              Import monitors from a JSON file")
    print()
    print(_bold("Check on things:"))
    print(f"  check [--id ID]            Check all or one monitor for changes")
    print(f"  dashboard                  All monitors at a glance")
    print(f"  trend <id> [--days N]      Price history over time")
    print(f"  compare <group>            Compare prices across a group")
    print(f"  compare --all              Compare all price monitors")
    print(f"  diff <id>                  Open visual diff in browser")
    print(f"  screenshot <id>            Save page content for diffing")
    print(f"  history <id> [-n N]        Recent snapshots")
    print()
    print(_bold("Manage:"))
    print(f"  list [--group G]           List monitors (optionally filtered)")
    print(f"  pause <id>                 Pause a monitor")
    print(f"  resume <id>                Resume a paused monitor")
    print(f"  remove <id>                Delete a monitor")
    print(f"  note <id> 'text'           Add a note to a monitor")
    print(f"  notes <id>                 View notes for a monitor")
    print(f"  snapshot <id> [--note ..]  Take a manual snapshot")
    print(f"  export                     Export all monitor configs")
    print()
    print(_bold("Reports:"))
    print(f"  report                     Weekly summary")
    print(f"  groups                     List all groups")
    print()
    print(_bold("Engines:"))
    print(f"  engines                    Show available fetch engines")
    print()
    print(_bold("Options for 'add' and 'watch':"))
    print(f"  --label/-l        Human-friendly name")
    print(f"  --selector/-s     CSS-like selector (#id or .class)")
    print(f"  --condition/-c    Alert condition (e.g. 'price below 500')")
    print(f"  --interval/-i     Check interval in minutes (default: 360)")
    print(f"  --group/-g        Group/category name")
    print(f"  --priority/-p     Priority: high, medium, low (default: medium)")
    print(f"  --target/-t       Price target (e.g. 3000)")
    print(f"  --engine/-e       Fetch engine: auto, curl, cloudscraper, browser, openclaw (default: auto)")
    print(f"  --browser/-b      Use Playwright for JS-rendered pages")
    print(f"  --webhook/-w      Webhook URL (repeatable)")
    print()
    print(_bold("Feedback:"))
    print(f"  feedback <message>         Send feedback or suggestions")
    print(f"  feedback --bug <msg>       Report a bug")
    print(f"  feedback --idea <msg>      Suggest a feature")
    print(f"  debug                      System info for bug reports")
    print()


def cmd_add(args):
    monitors = load_monitors()
    mid = gen_id(args.url, args.label)

    monitor = {
        "id": mid,
        "url": args.url,
        "label": args.label or args.url,
        "selector": args.selector,
        "condition": args.condition,
        "interval_minutes": args.interval or 360,
        "created": datetime.now(timezone.utc).isoformat(),
        "enabled": True,
        "group": getattr(args, 'group', None),
        "priority": getattr(args, 'priority', 'medium') or 'medium',
        "target": float(args.target) if getattr(args, 'target', None) else None,
        "notes": [],
        "price_history": [],
        "browser": getattr(args, 'browser', False),
        "engine": getattr(args, 'engine', 'auto') or 'auto',
        "webhooks": getattr(args, 'webhook', []) or [],
    }

    monitors[mid] = monitor
    save_monitors(monitors)

    use_browser = monitor.get("browser", False)
    engine = monitor.get("engine", "auto")
    content, err, title = fetch_url_auto(args.url, args.selector, use_browser=use_browser, engine=engine)
    if content:
        content_hash = hashlib.md5(content.encode()).hexdigest()
        save_snapshot(mid, content, content_hash)
        price = update_price_history(monitor, content)
        save_monitors(monitors)
        print(json.dumps({"status": "added", "monitor": monitor, "initial_snapshot": True,
                          "current_price": price}))
    else:
        print(json.dumps({"status": "added", "monitor": monitor, "initial_snapshot": False, "error": err}))


def cmd_remove(args):
    monitors = load_monitors()
    mid, m = find_monitor(monitors, args.id)
    if not mid:
        print(_red(f"No monitor with ID '{args.id}'. Run `monitor.py list` to see your monitors."))
        return
    removed = monitors.pop(mid)
    save_monitors(monitors)
    snap_dir = SNAPSHOTS_DIR / mid
    if snap_dir.exists():
        for f in snap_dir.glob("*.json"):
            f.unlink()
        snap_dir.rmdir()
    print(json.dumps({"status": "removed", "monitor": removed}))


def cmd_list(args):
    monitors = load_monitors()
    if not monitors:
        print(_yellow("No monitors yet. Start with: monitor.py watch <url>"))
        return

    group_filter = getattr(args, 'group', None)
    output = []
    for mid, m in monitors.items():
        if group_filter and m.get("group") != group_filter:
            continue
        latest = get_latest_snapshot(mid)
        m["last_checked"] = latest["timestamp"] if latest else None
        output.append(m)

    if not output:
        print(_yellow(f"No monitors in group '{group_filter}'."))
        return
    print(json.dumps(output, indent=2))


def cmd_check(args):
    monitors = load_monitors()
    if not monitors:
        print(_yellow("No monitors yet. Start with: monitor.py watch <url>"))
        return

    results = []
    targets = {}
    if args.id:
        mid, m = find_monitor(monitors, args.id)
        if not mid:
            print(_red(f"No monitor with ID '{args.id}'. Run `monitor.py list` to see your monitors."))
            return
        targets[mid] = m
    else:
        targets = {k: v for k, v in monitors.items() if v.get("enabled", True)}

    if not targets:
        print(_yellow("All monitors are paused. Use `monitor.py resume <id>` to re-enable one."))
        return

    # Pre-fetched content support: if --content-file is provided, read it once
    prefetched_content = None
    if getattr(args, 'content_file', None):
        if not args.id:
            print(_red("--content-file requires --id to specify which monitor to update."))
            return
        cf = args.content_file
        if cf == "-":
            prefetched_content = sys.stdin.read()
        else:
            try:
                with open(cf, "r") as f:
                    prefetched_content = f.read()
            except (IOError, OSError) as e:
                print(_red(f"Cannot read content file: {e}"))
                return
        if not prefetched_content or len(prefetched_content.strip()) < 10:
            print(_red("Content file is empty or too short."))
            return

    for mid, m in targets.items():
        # Use pre-fetched content if provided, otherwise fetch normally
        if prefetched_content is not None:
            content, err = prefetched_content, None
        else:
            use_browser = m.get("browser", False)
            engine = m.get("engine", "auto")
            content, err, _ = fetch_url_auto(m["url"], m.get("selector"), use_browser=use_browser, engine=engine)
        if err:
            results.append({
                "id": mid, "label": m["label"], "status": "error", "error": err,
            })
            continue

        content_hash = hashlib.md5(content.encode()).hexdigest()
        previous = get_latest_snapshot(mid)

        changed = False
        condition_met = False
        condition_desc = None
        diff_summary = None
        change_summary = None
        diff_path = None

        if previous:
            if content_hash != previous["hash"]:
                changed = True
                diff_summary = smart_diff(previous.get("content", ""), content, m)
                change_summary = generate_change_summary(previous.get("content", ""), content, m)

                # Generate HTML diff
                diff_path = generate_html_diff(mid, previous.get("content", ""), content, m.get("label", ""))

                # Save HTML snapshots for screenshot/diff command
                save_html_snapshot(mid, content, "current")
        else:
            changed = True
            diff_summary = "first snapshot"
            change_summary = "First snapshot taken."

        # Check condition
        condition = m.get("condition")
        if condition and content:
            condition_met, condition_desc = check_condition(condition, content, m)

        # Price tracking
        price = update_price_history(m, content)
        target_val = m.get("target")
        target_info = None
        if target_val and price:
            pct_away = abs(price - target_val) / target_val * 100
            if price <= target_val:
                target_info = f"Target hit! Currently R{price:,.0f} (target was R{target_val:,.0f})"
            else:
                target_info = f"Currently R{price:,.0f}, {pct_away:.0f}% above target of R{target_val:,.0f}"

        save_snapshot(mid, content, content_hash)
        save_monitors(monitors)

        result = {
            "id": mid,
            "label": m["label"],
            "url": m["url"],
            "status": "changed" if changed else "unchanged",
            "condition": condition,
            "condition_met": condition_met if condition else None,
            "condition_detail": condition_desc,
            "diff": diff_summary,
            "change_summary": change_summary,
            "diff_path": diff_path,
            "current_price": price,
            "target_info": target_info,
            "priority": m.get("priority", "medium"),
            "content_preview": content[:500] if getattr(args, 'verbose', False) else None,
            "checked_at": datetime.now(timezone.utc).isoformat(),
        }
        results.append(result)

        # Fire webhooks if condition met or changed
        if (condition_met or changed) and m.get("webhooks"):
            fire_webhooks(m, {
                "status": result["status"],
                "condition_met": condition_met,
                "change_summary": change_summary,
                "current_price": price,
            })

    print(json.dumps(results, indent=2))


def cmd_history(args):
    monitors = load_monitors()
    mid, m = find_monitor(monitors, args.id)
    if not mid:
        print(_red(f"No monitor with ID '{args.id}'. Run `monitor.py list` to see your monitors."))
        return
    snaps = get_snapshots(mid, limit=args.limit or 5)
    if not snaps:
        print(_yellow(f"No snapshots yet for '{mid}'."))
        return
    print(json.dumps(snaps, indent=2))


def cmd_dashboard(args):
    monitors = load_monitors()
    if not monitors:
        print(_yellow("No monitors yet. Start with: monitor.py watch <url>"))
        return

    groups = {}
    for mid, m in monitors.items():
        g = m.get("group") or "ungrouped"
        if g not in groups:
            groups[g] = []
        latest = get_latest_snapshot(mid)
        groups[g].append((mid, m, latest))

    whatsapp = getattr(args, 'whatsapp', False)

    lines = []
    if whatsapp:
        lines.append("*👁️ Web Monitor Dashboard*")
        lines.append("")
    else:
        lines.append(_bold("👁️  Web Monitor Dashboard"))
        lines.append("")

    for group_name in sorted(groups.keys()):
        items = groups[group_name]
        if len(groups) > 1 or group_name != "ungrouped":
            if whatsapp:
                lines.append(f"*{group_name.upper()}*")
            else:
                lines.append(_bold(f"  {group_name.upper()}"))

        for mid, m, latest in items:
            enabled = m.get("enabled", True)
            priority = m.get("priority", "medium")
            label = m.get("label", m["url"])[:50]

            if not enabled:
                status = "⏸️"
            elif not latest:
                status = "⏳"
            else:
                condition = m.get("condition")
                if condition and latest:
                    met, _ = check_condition(condition, latest.get("content", ""), m)
                    if met:
                        status = "🔴"
                    else:
                        status = "✅"
                else:
                    status = "✅"

            last = relative_time(latest["timestamp"] if latest else None)
            days = days_since(m.get("created"))
            pri_icon = {"high": "🔥", "low": "💤"}.get(priority, "")

            price_str = ""
            ph = m.get("price_history", [])
            if ph:
                current = ph[-1]["price"]
                target_val = m.get("target")
                price_str = f" R{current:,.0f}"
                if target_val:
                    if current <= target_val:
                        price_str += " 🎯"
                    else:
                        pct = (current - target_val) / target_val * 100
                        price_str += f" ({pct:.0f}% above target)"

            browser_icon = " 🌐" if m.get("browser") else ""
            webhook_icon = " 🔔" if m.get("webhooks") else ""

            if whatsapp:
                lines.append(f"{status} *{label}*{price_str}{browser_icon}{webhook_icon}")
                lines.append(f"    {last} | {days}d monitored {pri_icon}")
            else:
                lines.append(f"  {status} {_bold(label)}{price_str}{browser_icon}{webhook_icon}")
                lines.append(f"     {_dim(f'{last} | {days}d monitored')} {pri_icon}")

        lines.append("")

    total = len(monitors)
    paused = sum(1 for m in monitors.values() if not m.get("enabled", True))
    if whatsapp:
        lines.append(f"_{total} monitors, {paused} paused_")
    else:
        lines.append(_dim(f"  {total} monitors, {paused} paused"))

    print("\n".join(lines))


def cmd_trend(args):
    monitors = load_monitors()
    mid, m = find_monitor(monitors, args.id)
    if not mid:
        print(_red(f"No monitor with ID '{args.id}'. Run `monitor.py list` to see your monitors."))
        return

    ph = m.get("price_history", [])
    if not ph:
        snaps = get_snapshots(mid)
        for snap in reversed(snaps):
            price = extract_best_price(snap.get("content", ""), m.get("target"))
            if price:
                ph.append({"date": snap["timestamp"], "price": price})
        if ph:
            m["price_history"] = ph
            save_monitors(monitors)

    if not ph:
        print(_yellow(f"No price data for '{m.get('label', mid)}'. Need snapshots with prices."))
        return

    days_limit = getattr(args, 'days', None)
    if days_limit:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days_limit)
        ph = [p for p in ph if datetime.fromisoformat(p["date"].replace("Z", "+00:00")) > cutoff]

    if not ph:
        print(_yellow(f"No price data in the last {days_limit} days."))
        return

    prices = [p["price"] for p in ph]
    dates = [p["date"] for p in ph]

    min_price = min(prices)
    max_price = max(prices)
    avg_price = sum(prices) / len(prices)
    current = prices[-1]

    min_date = dates[prices.index(min_price)]
    max_date = dates[prices.index(max_price)]

    if len(prices) >= 2:
        recent = prices[-3:] if len(prices) >= 3 else prices
        if recent[-1] > recent[0]:
            direction = "↗️ rising"
        elif recent[-1] < recent[0]:
            direction = "↘️ dropping"
        else:
            direction = "→ stable"
    else:
        direction = "→ stable"

    def fmt_date(iso):
        try:
            dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
            return dt.strftime("%b %d")
        except Exception:
            return iso[:10]

    print()
    print(_bold(f"📈 Price Trend: {m.get('label', mid)}"))
    print(f"  Direction: {direction}")
    print(f"  Current:  R{current:,.0f}")
    print(f"  Lowest:   R{min_price:,.0f} on {fmt_date(min_date)}")
    print(f"  Highest:  R{max_price:,.0f} on {fmt_date(max_date)}")
    print(f"  Average:  R{avg_price:,.0f}")
    print(f"  Points:   {len(prices)} data points")

    target_val = m.get("target")
    if target_val:
        if current <= target_val:
            print(f"  🎯 Target of R{target_val:,.0f} reached!")
        else:
            pct = (current - target_val) / target_val * 100
            print(f"  Target:   R{target_val:,.0f} (currently {pct:.0f}% above)")

    if len(prices) >= 3:
        mn, mx = min(prices), max(prices)
        if mx > mn:
            chars = "▁▂▃▄▅▆▇█"
            spark = ""
            for p in prices[-20:]:
                idx = int((p - mn) / (mx - mn) * (len(chars) - 1))
                spark += chars[idx]
            print(f"  {spark}")
    print()


def cmd_pause(args):
    monitors = load_monitors()
    mid, m = find_monitor(monitors, args.id)
    if not mid:
        print(_red(f"No monitor with ID '{args.id}'. Run `monitor.py list` to see your monitors."))
        return
    m["enabled"] = False
    save_monitors(monitors)
    print(json.dumps({"status": "paused", "id": mid, "label": m.get("label")}))


def cmd_resume(args):
    monitors = load_monitors()
    mid, m = find_monitor(monitors, args.id)
    if not mid:
        print(_red(f"No monitor with ID '{args.id}'. Run `monitor.py list` to see your monitors."))
        return
    m["enabled"] = True
    save_monitors(monitors)
    print(json.dumps({"status": "resumed", "id": mid, "label": m.get("label")}))


def cmd_snapshot(args):
    monitors = load_monitors()
    mid, m = find_monitor(monitors, args.id)
    if not mid:
        print(_red(f"No monitor with ID '{args.id}'. Run `monitor.py list` to see your monitors."))
        return

    use_browser = m.get("browser", False)
    engine = m.get("engine", "auto")
    content, err, _ = fetch_url_auto(m["url"], m.get("selector"), use_browser=use_browser, engine=engine)
    if err:
        print(_red(f"Error fetching: {err}"))
        return

    content_hash = hashlib.md5(content.encode()).hexdigest()
    note = getattr(args, 'note', None)
    snap = save_snapshot(mid, content, content_hash, note=note)
    update_price_history(m, content)
    save_monitors(monitors)
    print(json.dumps({"status": "snapshot_taken", "id": mid, "timestamp": snap["timestamp"],
                      "note": note}))


def cmd_note(args):
    monitors = load_monitors()
    mid, m = find_monitor(monitors, args.id)
    if not mid:
        print(_red(f"No monitor with ID '{args.id}'. Run `monitor.py list` to see your monitors."))
        return

    if "notes" not in m:
        m["notes"] = []

    m["notes"].append({
        "text": args.text,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
    save_monitors(monitors)
    print(json.dumps({"status": "note_added", "id": mid, "note": args.text}))


def cmd_notes(args):
    monitors = load_monitors()
    mid, m = find_monitor(monitors, args.id)
    if not mid:
        print(_red(f"No monitor with ID '{args.id}'. Run `monitor.py list` to see your monitors."))
        return

    notes = m.get("notes", [])
    if not notes:
        print(_yellow(f"No notes for '{m.get('label', mid)}'."))
        return

    print(_bold(f"📝 Notes for {m.get('label', mid)}"))
    for n in notes:
        t = relative_time(n.get("timestamp"))
        print(f"  [{t}] {n['text']}")


def cmd_groups(args):
    monitors = load_monitors()
    if not monitors:
        print(_yellow("No monitors yet. Start with: monitor.py watch <url>"))
        return

    groups = {}
    for m in monitors.values():
        g = m.get("group") or "ungrouped"
        groups[g] = groups.get(g, 0) + 1

    print(_bold("📁 Groups"))
    for g, count in sorted(groups.items()):
        print(f"  {g}: {count} monitor{'s' if count != 1 else ''}")


def cmd_report(args):
    monitors = load_monitors()
    if not monitors:
        print(_yellow("No monitors to report on."))
        return

    week_ago = datetime.now(timezone.utc) - timedelta(days=7)
    total_checked = 0
    total_changes = 0
    conditions_met = 0
    price_movements = []
    change_counts = {}

    for mid, m in monitors.items():
        snaps = get_snapshots(mid)
        week_snaps = []
        for s in snaps:
            try:
                dt = datetime.fromisoformat(s["timestamp"].replace("Z", "+00:00"))
                if dt > week_ago:
                    week_snaps.append(s)
            except Exception:
                pass

        if week_snaps:
            total_checked += 1
            hashes = [s["hash"] for s in week_snaps]
            changes = len(set(hashes)) - 1
            if changes > 0:
                total_changes += changes
                change_counts[m.get("label", mid)] = changes

        ph = m.get("price_history", [])
        week_prices = []
        for p in ph:
            try:
                dt = datetime.fromisoformat(p["date"].replace("Z", "+00:00"))
                if dt > week_ago:
                    week_prices.append(p["price"])
            except Exception:
                pass

        if len(week_prices) >= 2:
            change_pct = (week_prices[-1] - week_prices[0]) / week_prices[0] * 100
            if abs(change_pct) > 1:
                price_movements.append((m.get("label", mid), week_prices[0], week_prices[-1], change_pct))

    lines = []
    lines.append("*👁️ Weekly Monitor Report*")
    lines.append("")
    lines.append(f"📊 {total_checked} monitors checked")
    lines.append(f"🔄 {total_changes} changes detected")
    lines.append("")

    if price_movements:
        lines.append("*Price Movements*")
        drops = sorted([p for p in price_movements if p[3] < 0], key=lambda x: x[3])
        rises = sorted([p for p in price_movements if p[3] > 0], key=lambda x: -x[3])
        for label, old, new, pct in drops[:5]:
            lines.append(f"  ↘️ {label}: R{old:,.0f} → R{new:,.0f} ({pct:+.0f}%)")
        for label, old, new, pct in rises[:5]:
            lines.append(f"  ↗️ {label}: R{old:,.0f} → R{new:,.0f} ({pct:+.0f}%)")
        lines.append("")

    if change_counts:
        lines.append("*Most Active*")
        for label, count in sorted(change_counts.items(), key=lambda x: -x[1])[:5]:
            lines.append(f"  {label}: {count} changes")
        lines.append("")

    if not price_movements and not change_counts:
        lines.append("_Quiet week. No significant changes._")

    print("\n".join(lines))


def cmd_watch(args):
    """Smart auto-detect and setup."""
    url = args.url
    print(f"Fetching {url}...")

    use_browser = getattr(args, 'browser', False)
    engine = getattr(args, 'engine', 'auto') or 'auto'

    # OpenClaw engine: skip fetch, create monitor without initial snapshot.
    # First check will need --content-file to provide the page content.
    if engine == "openclaw":
        content = None
        title = None
        print(f"  🔧 OpenClaw engine: skipping initial fetch.")
        print(f"  First check needs: monitor.py check --id <id> --content-file <path>")
    else:
        content, err, title = fetch_url_auto(url, use_browser=use_browser, engine=engine)
        if err:
            print(_red(f"Couldn't fetch: {err}"))
            return

    monitor_type = "content"
    condition = None
    label = (title[:60] if title else None) or url[:60]
    label = re.sub(r'\s*[\|–\-]\s*.*$', '', label).strip() or url[:60]

    if content:
        prices = extract_prices(content)
        content_lower = content.lower()

        stock_terms = ["in stock", "out of stock", "sold out", "add to cart", "add to basket",
                       "available", "unavailable", "notify me"]
        has_stock = any(t in content_lower for t in stock_terms)

        if prices:
            monitor_type = "price"
            best_price = prices[0]
            condition = f"price below {best_price * 0.9:.0f}"
            print(f"  💰 Detected price: R{best_price:,.0f}")
            print(f"  Auto-set alert: price drops below R{best_price * 0.9:,.0f}")
        elif has_stock:
            monitor_type = "stock"
            if any(t in content_lower for t in ["out of stock", "sold out", "unavailable"]):
                condition = "contains 'in stock'"
                print(f"  📦 Currently out of stock. Will alert when back in stock.")
            else:
                condition = "not contains 'out of stock'"
                print(f"  📦 Currently in stock. Will alert if it goes out of stock.")
        else:
            print(f"  📄 Set up for content change monitoring.")
    else:
        print(f"  📄 Set up for content change monitoring (no initial snapshot).")

    mid = gen_id(url, label)
    monitors = load_monitors()

    group = getattr(args, 'group', None)
    webhooks = getattr(args, 'webhook', []) or []
    monitor = {
        "id": mid,
        "url": url,
        "label": label,
        "selector": None,
        "condition": condition,
        "interval_minutes": 360,
        "created": datetime.now(timezone.utc).isoformat(),
        "enabled": True,
        "group": group,
        "priority": "medium",
        "target": None,
        "notes": [],
        "price_history": [],
        "type": monitor_type,
        "browser": use_browser,
        "engine": engine,
        "webhooks": webhooks,
    }

    if content:
        content_hash = hashlib.md5(content.encode()).hexdigest()
        save_snapshot(mid, content, content_hash)
        update_price_history(monitor, content)

    monitors[mid] = monitor
    save_monitors(monitors)

    print()
    print(_green(f"✅ Now monitoring: {label}"))
    print(f"   ID: {mid}")
    if engine == "openclaw":
        print(f"   First check: monitor.py check --id {mid} --content-file <path>")
    else:
        print(f"   Check with: monitor.py check --id {mid}")
    print(f"   Dashboard:  monitor.py dashboard")


def cmd_export(args):
    monitors = load_monitors()
    if not monitors:
        print(_yellow("No monitors to export."))
        return

    export = {}
    for mid, m in monitors.items():
        export[mid] = {k: v for k, v in m.items() if k != "price_history"}
    print(json.dumps(export, indent=2))


def cmd_import(args):
    try:
        data = json.loads(Path(args.file).read_text())
    except Exception as e:
        print(_red(f"Couldn't read file: {e}"))
        return

    monitors = load_monitors()
    added = 0
    skipped = 0

    existing_urls = {m["url"] for m in monitors.values()}

    for mid, m in data.items():
        if m.get("url") in existing_urls:
            skipped += 1
            continue
        if "price_history" not in m:
            m["price_history"] = []
        if "notes" not in m:
            m["notes"] = []
        monitors[mid] = m
        added += 1

    save_monitors(monitors)
    print(json.dumps({"status": "imported", "added": added, "skipped_duplicates": skipped}))


# --- Feature 2: Screenshot and Diff commands ---

def cmd_screenshot(args):
    """Save page content snapshot for visual diffing."""
    monitors = load_monitors()
    mid, m = find_monitor(monitors, args.id)
    if not mid:
        print(_red(f"No monitor with ID '{args.id}'. Run `monitor.py list` to see your monitors."))
        return

    use_browser = m.get("browser", False)
    engine = m.get("engine", "auto")
    content, err, _ = fetch_url_auto(m["url"], m.get("selector"), use_browser=use_browser, engine=engine)
    if err:
        print(_red(f"Error fetching: {err}"))
        return

    path = save_html_snapshot(mid, content, "current")
    print(json.dumps({"status": "screenshot_saved", "id": mid, "path": str(path)}))


def cmd_diff(args):
    """Generate and open an HTML diff for a monitor."""
    monitors = load_monitors()
    mid, m = find_monitor(monitors, args.id)
    if not mid:
        print(_red(f"No monitor with ID '{args.id}'. Run `monitor.py list` to see your monitors."))
        return

    # Get last two different snapshots
    snaps = get_snapshots(mid, limit=10)
    if len(snaps) < 2:
        print(_yellow(f"Need at least 2 snapshots to generate a diff. Run check first."))
        return

    old_content = snaps[1].get("content", "")
    new_content = snaps[0].get("content", "")

    if not old_content or not new_content:
        print(_yellow("Snapshot content is empty."))
        return

    diff_path = generate_html_diff(mid, old_content, new_content, m.get("label", mid))
    print(f"Diff generated: {diff_path}")

    # Try to open in browser
    try:
        webbrowser.open(f"file://{diff_path}")
        print("Opened in browser.")
    except Exception:
        print(f"Open manually: file://{diff_path}")


# --- Feature 3: Price Comparison ---

def cmd_compare(args):
    """Compare prices across monitors in a group."""
    monitors = load_monitors()
    if not monitors:
        print(_yellow("No monitors yet."))
        return

    compare_all = getattr(args, 'all', False)
    group_name = getattr(args, 'group', None)

    # Collect price monitors
    price_monitors = []
    for mid, m in monitors.items():
        ph = m.get("price_history", [])
        if not ph:
            continue
        if not compare_all and group_name and m.get("group") != group_name:
            continue
        if compare_all or group_name:
            price_monitors.append((mid, m))

    if not price_monitors:
        if group_name:
            print(_yellow(f"No price monitors in group '{group_name}'."))
        else:
            print(_yellow("No price monitors found. Use --all or specify a group."))
        return

    # Sort by current price
    def current_price(item):
        ph = item[1].get("price_history", [])
        return ph[-1]["price"] if ph else float('inf')

    price_monitors.sort(key=current_price)

    all_prices = [current_price(pm) for pm in price_monitors]
    avg_price = sum(all_prices) / len(all_prices) if all_prices else 0

    print()
    title = f"group '{group_name}'" if group_name else "all price monitors"
    print(_bold(f"💰 Price Comparison: {title}"))
    print()

    for i, (mid, m) in enumerate(price_monitors):
        ph = m.get("price_history", [])
        price = ph[-1]["price"] if ph else 0
        prices_list = [p["price"] for p in ph]
        low = min(prices_list) if prices_list else price
        high = max(prices_list) if prices_list else price

        label = m.get("label", mid)[:40]
        rank = "🥇" if i == 0 else ("🥈" if i == 1 else ("🥉" if i == 2 else f"  {i+1}."))

        pct_vs_avg = ((price - avg_price) / avg_price * 100) if avg_price else 0
        vs_avg = f"{pct_vs_avg:+.0f}% vs avg" if abs(pct_vs_avg) > 1 else "at avg"

        print(f"  {rank} {_bold(label)}")
        print(f"     R{price:,.0f} ({vs_avg}) | Low: R{low:,.0f} | High: R{high:,.0f}")

    print()
    if price_monitors:
        best_mid, best_m = price_monitors[0]
        best_ph = best_m.get("price_history", [])
        best_price = best_ph[-1]["price"] if best_ph else 0
        pct_below = ((avg_price - best_price) / avg_price * 100) if avg_price else 0
        label = best_m.get("label", best_mid)[:40]
        print(_green(f"  Best deal: {label} at R{best_price:,.0f} ({pct_below:.0f}% below average)"))
    print()


# --- Feature 3: Add Competitor ---

def cmd_add_competitor(args):
    """Link a competitor URL to an existing monitor."""
    monitors = load_monitors()
    mid, m = find_monitor(monitors, args.id)
    if not mid:
        print(_red(f"No monitor with ID '{args.id}'."))
        return

    # Make sure the original has a group
    group = m.get("group")
    if not group:
        group = f"compare-{mid[:20]}"
        m["group"] = group
        save_monitors(monitors)

    # Create new monitor with same condition
    new_mid = gen_id(args.url, None)
    new_monitor = {
        "id": new_mid,
        "url": args.url,
        "label": args.url,
        "selector": m.get("selector"),
        "condition": m.get("condition"),
        "interval_minutes": m.get("interval_minutes", 360),
        "created": datetime.now(timezone.utc).isoformat(),
        "enabled": True,
        "group": group,
        "priority": m.get("priority", "medium"),
        "target": m.get("target"),
        "notes": [],
        "price_history": [],
        "browser": m.get("browser", False),
        "engine": m.get("engine", "auto"),
        "webhooks": [],
    }

    monitors[new_mid] = new_monitor
    save_monitors(monitors)

    # Take initial snapshot
    use_browser = new_monitor.get("browser", False)
    engine = new_monitor.get("engine", "auto")
    content, err, title = fetch_url_auto(args.url, new_monitor.get("selector"), use_browser=use_browser, engine=engine)
    if content:
        if title:
            label = re.sub(r'\s*[\|–\-]\s*.*$', '', title[:60]).strip() or args.url[:60]
            new_monitor["label"] = label
        content_hash = hashlib.md5(content.encode()).hexdigest()
        save_snapshot(new_mid, content, content_hash)
        price = update_price_history(new_monitor, content)
        save_monitors(monitors)
        print(json.dumps({"status": "competitor_added", "id": new_mid, "group": group,
                          "label": new_monitor["label"], "current_price": price}))
    else:
        save_monitors(monitors)
        print(json.dumps({"status": "competitor_added", "id": new_mid, "group": group,
                          "initial_snapshot": False, "error": err}))


# --- Feature 4: Templates ---

def cmd_template(args):
    """Handle template subcommands."""
    sub = args.template_command if hasattr(args, 'template_command') else None
    if sub == "list":
        cmd_template_list(args)
    elif sub == "use":
        cmd_template_use(args)
    else:
        print(_bold("📋 Monitor Templates"))
        print()
        print(f"  template list              Show available templates")
        print(f"  template use <name> <url>  Apply a template to a URL")
        print()


def cmd_template_list(args):
    print()
    print(_bold("📋 Available Templates"))
    print()
    for name, t in TEMPLATES.items():
        print(f"  {_cyan(name)}")
        print(f"    {t['description']}")
        if t.get("condition"):
            print(f"    Condition: {t['condition']}")
        print(f"    Interval: {t['interval_minutes']}min | Priority: {t['priority']}")
        print()


def cmd_template_use(args):
    name = args.template_name
    url = args.template_url

    if name not in TEMPLATES:
        print(_red(f"Unknown template '{name}'. Run `monitor.py template list` to see options."))
        return

    tmpl = TEMPLATES[name]

    print(f"Applying '{name}' template to {url}...")

    use_browser = getattr(args, 'browser', False)
    engine = getattr(args, 'engine', 'auto') or 'auto'
    content, err, title = fetch_url_auto(url, use_browser=use_browser, engine=engine)
    if err:
        print(_red(f"Couldn't fetch: {err}"))
        return

    label_prefix = tmpl["label_prefix"]
    label = title[:50] if title else url[:50]
    label = re.sub(r'\s*[\|–\-]\s*.*$', '', label).strip() or url[:50]
    label = f"{label_prefix} {label}"

    condition = tmpl.get("condition")

    # For price-drop template, auto-set condition based on current price
    if name == "price-drop":
        prices = extract_prices(content)
        if prices:
            best = prices[0]
            condition = f"price below {best * 0.9:.0f}"
            print(f"  💰 Current price: R{best:,.0f}. Alert below R{best * 0.9:,.0f}")
        else:
            print(_yellow("  No price detected. Monitoring for content changes instead."))

    mid = gen_id(url, label)
    monitors = load_monitors()

    webhooks = getattr(args, 'webhook', []) or []
    monitor = {
        "id": mid,
        "url": url,
        "label": label,
        "selector": None,
        "condition": condition,
        "interval_minutes": tmpl["interval_minutes"],
        "created": datetime.now(timezone.utc).isoformat(),
        "enabled": True,
        "group": getattr(args, 'group', None),
        "priority": tmpl["priority"],
        "target": None,
        "notes": [],
        "price_history": [],
        "type": tmpl.get("type", "content"),
        "browser": use_browser,
        "engine": engine,
        "webhooks": webhooks,
    }

    content_hash = hashlib.md5(content.encode()).hexdigest()
    save_snapshot(mid, content, content_hash)
    update_price_history(monitor, content)

    monitors[mid] = monitor
    save_monitors(monitors)

    print(_green(f"✅ Template '{name}' applied: {label}"))
    print(f"   ID: {mid}")


def cmd_gui(args):
    """Generate and open the GUI console."""
    monitors = load_monitors()
    no_open = getattr(args, 'no_open', False)

    # Gather all data
    monitor_data = []
    all_snapshots = []
    week_ago = datetime.now(timezone.utc) - timedelta(days=7)

    for mid, m in monitors.items():
        snaps = get_snapshots(mid, limit=20)
        latest = snaps[0] if snaps else None

        # Determine status
        status = "stable"
        if not m.get("enabled", True):
            status = "paused"
        elif latest:
            condition = m.get("condition")
            if condition:
                met, _ = check_condition(condition, latest.get("content", ""), m)
                if met:
                    status = "condition_met"
            # Check if changed recently (compare last 2 snaps)
            if len(snaps) >= 2 and snaps[0].get("hash") != snaps[1].get("hash") and status != "condition_met":
                status = "changed"

        # Count changes in last 7 days
        snap_hashes_week = []
        for s in snaps:
            try:
                dt = datetime.fromisoformat(s["timestamp"].replace("Z", "+00:00"))
                if dt > week_ago:
                    snap_hashes_week.append(s.get("hash"))
            except Exception:
                pass
        changes_7d = max(0, len(set(snap_hashes_week)) - 1)

        # Snapshot entries for global list
        for s in snaps[:5]:
            all_snapshots.append({
                "timestamp": s.get("timestamp"),
                "monitor_label": m.get("label", mid),
                "monitor_id": mid,
                "hash": s.get("hash"),
            })

        monitor_data.append({
            "id": mid,
            "url": m.get("url", ""),
            "label": m.get("label", mid),
            "status": status,
            "enabled": m.get("enabled", True),
            "priority": m.get("priority", "medium"),
            "group": m.get("group") or "",
            "condition": m.get("condition") or "",
            "target": m.get("target"),
            "created": m.get("created"),
            "last_checked": latest["timestamp"] if latest else None,
            "price_history": m.get("price_history", []),
            "notes_count": len(m.get("notes", [])),
            "type": m.get("type", "content"),
            "browser": m.get("browser", False),
            "webhooks": len(m.get("webhooks", [])),
            "changes_7d": changes_7d,
        })

    # Build alert history from snapshots
    alert_history = []
    for mid, m in monitors.items():
        snaps = get_snapshots(mid, limit=20)
        for i in range(len(snaps) - 1):
            if snaps[i].get("hash") != snaps[i + 1].get("hash"):
                # Generate summary
                summary = generate_change_summary(
                    snaps[i + 1].get("content", ""),
                    snaps[i].get("content", ""),
                    m
                )
                alert_history.append({
                    "timestamp": snaps[i].get("timestamp"),
                    "monitor_label": m.get("label", mid),
                    "monitor_id": mid,
                    "summary": summary,
                })
    alert_history.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    alert_history = alert_history[:20]

    # Sort global snapshots
    all_snapshots.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    # Mark changed/unchanged
    snap_by_monitor = {}
    recent_snapshots = []
    for s in all_snapshots[:30]:
        mid = s["monitor_id"]
        prev_hash = snap_by_monitor.get(mid)
        s["changed"] = prev_hash is not None and prev_hash != s["hash"]
        snap_by_monitor[mid] = s["hash"]
        recent_snapshots.append(s)
    recent_snapshots = recent_snapshots[:10]

    # Groups
    groups = {}
    for md in monitor_data:
        g = md["group"] or "ungrouped"
        if g not in groups:
            groups[g] = {"name": g, "count": 0, "alerts": 0}
        groups[g]["count"] += 1
        if md["status"] in ("changed", "condition_met"):
            groups[g]["alerts"] += 1

    # Templates
    template_data = []
    for name, t in TEMPLATES.items():
        template_data.append({
            "name": name,
            "description": t["description"],
            "condition": t.get("condition") or "Auto-detected",
            "type": t.get("type", "content"),
            "interval": t["interval_minutes"],
            "priority": t["priority"],
        })

    data = {
        "version": VERSION,
        "generated": datetime.now(timezone.utc).isoformat(),
        "monitors": monitor_data,
        "alerts": alert_history,
        "snapshots": recent_snapshots,
        "groups": list(groups.values()),
        "templates": template_data,
    }

    html = _generate_gui_html(data)

    out_path = STORE_DIR / "console.html"
    ensure_dirs()
    out_path.write_text(html, encoding="utf-8")
    print(f"Console generated: {out_path}")
    size_kb = len(html.encode()) / 1024
    print(f"Size: {size_kb:.0f}KB")

    if not no_open:
        try:
            webbrowser.open(f"file://{out_path}")
            print("Opened in browser.")
        except Exception:
            print(f"Open manually: file://{out_path}")


def _generate_gui_html(data):
    """Generate the full self-contained HTML console."""
    data_json = json.dumps(data, indent=None, default=str)

    return '''<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Web Monitor Pro Console</title>
<style>
:root[data-theme="dark"] {
  --bg: #0a0a0a; --bg-card: #141414; --bg-card-hover: #1a1a1a; --bg-input: #1e1e1e;
  --text: #e5e5e5; --text-dim: #737373; --text-muted: #525252;
  --accent: #3b82f6; --accent-dim: #1d4ed8;
  --green: #22c55e; --green-dim: #166534;
  --amber: #f59e0b; --amber-dim: #92400e;
  --red: #ef4444; --red-dim: #991b1b;
  --border: #262626; --shadow: rgba(0,0,0,0.5);
}
:root[data-theme="light"] {
  --bg: #fafafa; --bg-card: #ffffff; --bg-card-hover: #f5f5f5; --bg-input: #f0f0f0;
  --text: #171717; --text-dim: #737373; --text-muted: #a3a3a3;
  --accent: #2563eb; --accent-dim: #1e40af;
  --green: #16a34a; --green-dim: #bbf7d0;
  --amber: #d97706; --amber-dim: #fef3c7;
  --red: #dc2626; --red-dim: #fecaca;
  --border: #e5e5e5; --shadow: rgba(0,0,0,0.08);
}
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
  background: var(--bg); color: var(--text); line-height: 1.6;
  -webkit-font-smoothing: antialiased;
}
h1, h2, h3, .mono {
  font-family: 'SF Mono', 'Fira Code', 'Cascadia Code', 'JetBrains Mono', ui-monospace, monospace;
}
.container { max-width: 1200px; margin: 0 auto; padding: 0 24px; }
a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }

/* Header */
.header {
  padding: 32px 0 24px; border-bottom: 1px solid var(--border);
  display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 16px;
}
.header-left { display: flex; align-items: center; gap: 16px; }
.header h1 { font-size: 24px; font-weight: 700; letter-spacing: -0.5px; }
.version-badge {
  background: var(--accent); color: #fff; padding: 2px 10px; border-radius: 20px;
  font-size: 12px; font-weight: 600;
}
.header-right { display: flex; align-items: center; gap: 16px; font-size: 14px; color: var(--text-dim); }
.theme-toggle {
  background: var(--bg-input); border: 1px solid var(--border); border-radius: 8px;
  padding: 6px 12px; cursor: pointer; color: var(--text); font-size: 14px;
  transition: all 0.2s;
}
.theme-toggle:hover { border-color: var(--accent); }
.header-stats span { margin-left: 12px; }

/* Section */
section { padding: 32px 0; }
section h2 { font-size: 18px; font-weight: 600; margin-bottom: 20px; letter-spacing: -0.3px; }

/* Metric Cards */
.metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 12px; }
.metric-card {
  background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px;
  padding: 20px; transition: all 0.2s;
}
.metric-card:hover { background: var(--bg-card-hover); transform: translateY(-1px); }
.metric-value { font-size: 32px; font-weight: 700; font-family: 'SF Mono', monospace; }
.metric-label { font-size: 13px; color: var(--text-dim); margin-top: 4px; }
.metric-card.green .metric-value { color: var(--green); }
.metric-card.amber .metric-value { color: var(--amber); }
.metric-card.red .metric-value { color: var(--red); }
.metric-card.blue .metric-value { color: var(--accent); }

/* Controls */
.controls {
  display: flex; gap: 12px; margin-bottom: 20px; flex-wrap: wrap; align-items: center;
}
.controls select, .controls input {
  background: var(--bg-input); border: 1px solid var(--border); border-radius: 8px;
  padding: 8px 12px; color: var(--text); font-size: 14px; outline: none;
}
.controls select:focus, .controls input:focus { border-color: var(--accent); }

/* Monitor Cards */
.monitor-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 16px; }
.monitor-card {
  background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px;
  padding: 20px; transition: all 0.2s; position: relative; overflow: hidden;
}
.monitor-card:hover { background: var(--bg-card-hover); transform: translateY(-2px); box-shadow: 0 8px 24px var(--shadow); }
.monitor-card .card-top { display: flex; justify-content: space-between; align-items: flex-start; gap: 8px; }
.monitor-label { font-size: 16px; font-weight: 600; margin-bottom: 4px; }
.monitor-url {
  font-size: 12px; color: var(--text-dim); white-space: nowrap; overflow: hidden;
  text-overflow: ellipsis; max-width: 280px; display: block; margin-bottom: 12px;
}
.badge {
  display: inline-flex; align-items: center; gap: 4px; padding: 3px 10px;
  border-radius: 20px; font-size: 11px; font-weight: 600; white-space: nowrap;
}
.badge-stable { background: var(--green-dim); color: var(--green); }
.badge-changed { background: var(--amber-dim); color: var(--amber); }
.badge-condition_met { background: var(--red-dim); color: var(--red); }
.badge-paused { background: var(--bg-input); color: var(--text-muted); }
.badge-error { background: var(--red-dim); color: var(--red); }
.badge-high { background: var(--red-dim); color: var(--red); }
.badge-low { background: var(--bg-input); color: var(--text-muted); }
.badge-group { background: var(--accent-dim); color: var(--accent); cursor: pointer; }
[data-theme="light"] .badge-stable { background: #dcfce7; }
[data-theme="light"] .badge-changed { background: #fef3c7; }
[data-theme="light"] .badge-condition_met { background: #fecaca; }
[data-theme="light"] .badge-high { background: #fecaca; }
[data-theme="light"] .badge-group { background: #dbeafe; }

.card-meta { display: flex; flex-wrap: wrap; gap: 8px; margin: 12px 0; align-items: center; }
.card-detail { font-size: 12px; color: var(--text-dim); }
.card-detail b { color: var(--text); }

/* Price section */
.price-current { font-size: 20px; font-weight: 700; font-family: 'SF Mono', monospace; margin: 8px 0; }
.price-target-bar {
  height: 6px; background: var(--bg-input); border-radius: 3px; overflow: hidden; margin: 6px 0;
}
.price-target-fill { height: 100%; border-radius: 3px; transition: width 0.5s ease; }
.price-target-text { font-size: 11px; color: var(--text-dim); }

/* Sparkline */
.sparkline { margin: 8px 0; }
.sparkline svg { display: block; }

/* Condition */
.condition-text { font-size: 12px; color: var(--text-dim); font-style: italic; margin-top: 8px; padding-top: 8px; border-top: 1px solid var(--border); }

/* Notes badge */
.notes-badge {
  position: absolute; top: 12px; right: 12px; background: var(--accent);
  color: #fff; width: 22px; height: 22px; border-radius: 50%;
  font-size: 11px; display: flex; align-items: center; justify-content: center; font-weight: 700;
}

/* Price Trends */
.trend-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(360px, 1fr)); gap: 16px; }
.trend-card {
  background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px; padding: 20px;
}
.trend-card h3 { font-size: 14px; margin-bottom: 12px; }
.trend-stats { display: flex; gap: 16px; flex-wrap: wrap; margin: 12px 0; }
.trend-stat { font-size: 12px; color: var(--text-dim); }
.trend-stat b { color: var(--text); display: block; font-size: 14px; }
.trend-chart { margin-top: 12px; }

/* Alert Timeline */
.timeline { display: flex; flex-direction: column; gap: 8px; }
.timeline-item {
  background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px;
  padding: 14px 18px; display: flex; gap: 12px; align-items: flex-start; transition: all 0.2s;
}
.timeline-item:hover { background: var(--bg-card-hover); }
.timeline-time { font-size: 12px; color: var(--text-muted); white-space: nowrap; min-width: 60px; font-family: 'SF Mono', monospace; }
.timeline-label { font-size: 13px; font-weight: 600; }
.timeline-summary { font-size: 13px; color: var(--text-dim); }

/* Groups */
.group-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 12px; }
.group-card {
  background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px;
  padding: 18px; cursor: pointer; transition: all 0.2s;
}
.group-card:hover { background: var(--bg-card-hover); border-color: var(--accent); transform: translateY(-1px); }
.group-name { font-size: 16px; font-weight: 600; }
.group-count { font-size: 13px; color: var(--text-dim); margin-top: 4px; }
.group-alerts { font-size: 12px; color: var(--red); margin-top: 2px; }

/* Templates */
.template-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 12px; }
.template-card {
  background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px; padding: 20px;
}
.template-card h3 { font-size: 15px; margin-bottom: 6px; }
.template-card .desc { font-size: 13px; color: var(--text-dim); margin-bottom: 8px; }
.template-card .tmpl-meta { font-size: 12px; color: var(--text-muted); }
.template-cmd {
  font-family: 'SF Mono', monospace; font-size: 11px; background: var(--bg-input);
  padding: 8px 12px; border-radius: 6px; margin-top: 10px; color: var(--accent);
  word-break: break-all;
}

/* Snapshot list */
.snap-list { display: flex; flex-direction: column; gap: 6px; }
.snap-item {
  background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px;
  padding: 10px 16px; display: flex; justify-content: space-between; align-items: center;
  font-size: 13px;
}
.snap-changed { border-left: 3px solid var(--amber); }
.snap-unchanged { border-left: 3px solid var(--green); }

/* Footer */
.footer {
  padding: 32px 0; border-top: 1px solid var(--border); text-align: center;
  font-size: 13px; color: var(--text-muted);
}
.footer a { color: var(--text-dim); }

/* Empty state */
.empty-state {
  text-align: center; padding: 40px 20px; color: var(--text-dim);
  font-size: 14px;
}
.empty-state .emoji { font-size: 32px; margin-bottom: 8px; display: block; }
.empty-state code {
  background: var(--bg-input); padding: 4px 10px; border-radius: 6px;
  font-family: 'SF Mono', monospace; font-size: 13px;
}

/* Animations */
@keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
.monitor-card, .metric-card, .timeline-item, .group-card, .template-card, .trend-card {
  animation: fadeIn 0.3s ease both;
}
.monitor-grid > :nth-child(2) { animation-delay: 0.03s; }
.monitor-grid > :nth-child(3) { animation-delay: 0.06s; }
.monitor-grid > :nth-child(4) { animation-delay: 0.09s; }
.monitor-grid > :nth-child(5) { animation-delay: 0.12s; }
.monitor-grid > :nth-child(6) { animation-delay: 0.15s; }

/* Responsive */
@media (max-width: 768px) {
  .header { flex-direction: column; align-items: flex-start; }
  .monitor-grid { grid-template-columns: 1fr; }
  .metrics { grid-template-columns: repeat(2, 1fr); }
}
</style>
</head>
<body>
<div class="container">

<!-- Header -->
<div class="header">
  <div class="header-left">
    <h1>&#x1F441;&#xFE0F; Web Monitor Pro</h1>
    <span class="version-badge" id="version"></span>
  </div>
  <div class="header-right">
    <span id="header-stats"></span>
    <button class="theme-toggle" onclick="toggleTheme()" id="theme-btn">&#x1F319; Dark</button>
  </div>
</div>

<!-- Status Overview -->
<section>
  <h2>&#x1F4CA; Status Overview</h2>
  <div class="metrics" id="metrics"></div>
</section>

<!-- Monitor Cards -->
<section>
  <h2>&#x1F4E1; Monitors</h2>
  <div class="controls">
    <select id="filter-group" onchange="renderMonitors()"><option value="">All Groups</option></select>
    <select id="filter-status" onchange="renderMonitors()">
      <option value="">All Statuses</option>
      <option value="stable">Stable</option>
      <option value="changed">Changed</option>
      <option value="condition_met">Alert</option>
      <option value="paused">Paused</option>
    </select>
    <select id="sort-by" onchange="renderMonitors()">
      <option value="status">Sort: Status</option>
      <option value="priority">Sort: Priority</option>
      <option value="name">Sort: Name</option>
      <option value="last_checked">Sort: Last Checked</option>
    </select>
  </div>
  <div class="monitor-grid" id="monitor-grid"></div>
</section>

<!-- Price Trends -->
<section id="sec-trends">
  <h2>&#x1F4C8; Price Trends</h2>
  <div class="trend-grid" id="trend-grid"></div>
</section>

<!-- Alert History -->
<section id="sec-alerts">
  <h2>&#x26A1; Alert History</h2>
  <div class="timeline" id="alert-timeline"></div>
</section>

<!-- Groups -->
<section id="sec-groups">
  <h2>&#x1F4C1; Groups</h2>
  <div class="group-grid" id="group-grid"></div>
</section>

<!-- Templates -->
<section>
  <h2>&#x1F4CB; Templates</h2>
  <div class="template-grid" id="template-grid"></div>
</section>

<!-- Recent Snapshots -->
<section id="sec-snapshots">
  <h2>&#x1F4F8; Recent Snapshots</h2>
  <div class="snap-list" id="snap-list"></div>
</section>

<!-- Footer -->
<div class="footer">
  <p>Made with &#x1F441;&#xFE0F; by @jakes420</p>
  <p style="margin-top:4px"><code>monitor.py feedback</code> to share ideas</p>
  <p style="margin-top:4px" id="footer-version"></p>
</div>

</div>

<script>
const DATA = ''' + data_json + ''';

function relTime(iso) {
  if (!iso) return 'never';
  const diff = (Date.now() - new Date(iso).getTime()) / 1000;
  if (diff < 60) return 'just now';
  if (diff < 3600) return Math.floor(diff/60) + 'm ago';
  if (diff < 86400) return Math.floor(diff/3600) + 'h ago';
  const d = Math.floor(diff/86400);
  return d === 1 ? 'yesterday' : d + 'd ago';
}
function daysSince(iso) {
  if (!iso) return 0;
  return Math.max(0, Math.floor((Date.now() - new Date(iso).getTime()) / 86400000));
}
function esc(s) { const d = document.createElement('div'); d.textContent = s; return d.innerHTML; }
function truncUrl(u, n) { try { const p = new URL(u); return (p.hostname + p.pathname).slice(0, n || 40); } catch(e) { return u.slice(0, n || 40); } }

const STATUS_MAP = {
  stable: { icon: '\\u2705', label: 'Stable', cls: 'badge-stable' },
  changed: { icon: '\\u26A0\\uFE0F', label: 'Changed', cls: 'badge-changed' },
  condition_met: { icon: '\\uD83D\\uDD34', label: 'Alert', cls: 'badge-condition_met' },
  paused: { icon: '\\u23F8\\uFE0F', label: 'Paused', cls: 'badge-paused' },
  error: { icon: '\\u274C', label: 'Error', cls: 'badge-error' },
};
const PRI_MAP = { high: '\\uD83D\\uDD25 High', low: '\\uD83D\\uDCA4 Low' };
const STATUS_ORDER = { condition_met: 0, changed: 1, stable: 2, paused: 3, error: 4 };
const PRI_ORDER = { high: 0, medium: 1, low: 2 };

function sparklineSVG(prices, w, h) {
  if (!prices || prices.length < 2) return '';
  const vals = prices.map(p => p.price);
  const mn = Math.min(...vals), mx = Math.max(...vals);
  const range = mx - mn || 1;
  const pts = vals.map((v, i) => {
    const x = (i / (vals.length - 1)) * w;
    const y = h - ((v - mn) / range) * (h - 2) - 1;
    return x.toFixed(1) + ',' + y.toFixed(1);
  }).join(' ');
  const trending = vals[vals.length-1] > vals[0];
  const color = trending ? 'var(--red)' : 'var(--green)';
  return '<svg class="sparkline" width="'+w+'" height="'+h+'" viewBox="0 0 '+w+' '+h+'"><polyline fill="none" stroke="'+color+'" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" points="'+pts+'"/></svg>';
}

function trendChart(prices, w, h, target) {
  if (!prices || prices.length < 2) return '';
  const vals = prices.map(p => p.price);
  const mn = Math.min(...vals), mx = Math.max(...vals);
  const allVals = target ? [...vals, target] : vals;
  const gMn = Math.min(...allVals), gMx = Math.max(...allVals);
  const range = gMx - gMn || 1;
  const pts = vals.map((v, i) => {
    const x = (i / (vals.length - 1)) * w;
    const y = h - ((v - gMn) / range) * (h - 8) - 4;
    return x.toFixed(1) + ',' + y.toFixed(1);
  }).join(' ');
  const trending = vals[vals.length-1] > vals[0];
  const color = trending ? 'var(--red)' : 'var(--green)';
  let targetLine = '';
  if (target) {
    const ty = (h - ((target - gMn) / range) * (h - 8) - 4).toFixed(1);
    targetLine = '<line x1="0" y1="'+ty+'" x2="'+w+'" y2="'+ty+'" stroke="var(--accent)" stroke-width="1" stroke-dasharray="4,3" opacity="0.6"/><text x="'+w+'" y="'+(parseFloat(ty)-4)+'" fill="var(--accent)" font-size="10" text-anchor="end">Target</text>';
  }
  return '<svg width="'+w+'" height="'+h+'" viewBox="0 0 '+w+' '+h+'"><polyline fill="none" stroke="'+color+'" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" points="'+pts+'"/>'+targetLine+'</svg>';
}

// Theme
function toggleTheme() {
  const html = document.documentElement;
  const cur = html.getAttribute('data-theme');
  const next = cur === 'dark' ? 'light' : 'dark';
  html.setAttribute('data-theme', next);
  document.getElementById('theme-btn').innerHTML = next === 'dark' ? '&#x1F319; Dark' : '&#x2600;&#xFE0F; Light';
  localStorage.setItem('wm-theme', next);
}
(function() {
  const saved = localStorage.getItem('wm-theme');
  if (saved) {
    document.documentElement.setAttribute('data-theme', saved);
    document.getElementById('theme-btn').innerHTML = saved === 'dark' ? '&#x1F319; Dark' : '&#x2600;&#xFE0F; Light';
  }
})();

// Init
document.getElementById('version').textContent = 'v' + DATA.version;
document.getElementById('footer-version').textContent = 'Web Monitor Pro v' + DATA.version;

// Header stats
const totalM = DATA.monitors.length;
const activeM = DATA.monitors.filter(m => m.enabled).length;
const pausedM = totalM - activeM;
document.getElementById('header-stats').innerHTML = totalM + ' monitors <span>' + activeM + ' active</span><span>' + pausedM + ' paused</span>';

// Metrics
(function() {
  const week = DATA.monitors.reduce((s, m) => s + (m.changes_7d || 0), 0);
  const condMet = DATA.monitors.filter(m => m.status === 'condition_met').length;
  const priceM = DATA.monitors.filter(m => m.price_history && m.price_history.length > 0).length;
  const groupCount = DATA.groups.filter(g => g.name !== 'ungrouped').length || DATA.groups.length;

  const cards = [
    { value: totalM, label: 'Total Monitors', cls: 'blue' },
    { value: activeM, label: 'Active', cls: 'green' },
    { value: pausedM, label: 'Paused', cls: '' },
    { value: week, label: 'Changes (7d)', cls: 'amber' },
    { value: condMet, label: 'Conditions Met', cls: 'red' },
    { value: priceM, label: 'Price Tracking', cls: 'blue' },
    { value: groupCount, label: 'Groups', cls: '' },
  ];
  document.getElementById('metrics').innerHTML = cards.map(c =>
    '<div class="metric-card ' + c.cls + '"><div class="metric-value">' + c.value + '</div><div class="metric-label">' + c.label + '</div></div>'
  ).join('');
})();

// Populate group filter
(function() {
  const sel = document.getElementById('filter-group');
  const groups = [...new Set(DATA.monitors.map(m => m.group).filter(Boolean))].sort();
  groups.forEach(g => {
    const o = document.createElement('option');
    o.value = g; o.textContent = g;
    sel.appendChild(o);
  });
})();

function renderMonitors() {
  const group = document.getElementById('filter-group').value;
  const status = document.getElementById('filter-status').value;
  const sort = document.getElementById('sort-by').value;

  let ms = DATA.monitors.slice();
  if (group) ms = ms.filter(m => m.group === group);
  if (status) ms = ms.filter(m => m.status === status);

  if (sort === 'status') ms.sort((a,b) => (STATUS_ORDER[a.status]||9) - (STATUS_ORDER[b.status]||9));
  else if (sort === 'priority') ms.sort((a,b) => (PRI_ORDER[a.priority]||9) - (PRI_ORDER[b.priority]||9));
  else if (sort === 'name') ms.sort((a,b) => a.label.localeCompare(b.label));
  else if (sort === 'last_checked') ms.sort((a,b) => (b.last_checked||'').localeCompare(a.last_checked||''));

  if (ms.length === 0) {
    document.getElementById('monitor-grid').innerHTML = '<div class="empty-state"><span class="emoji">\\uD83D\\uDC41\\uFE0F</span>Nothing to watch yet. Start with:<br><code>monitor.py watch &lt;url&gt;</code></div>';
    return;
  }

  document.getElementById('monitor-grid').innerHTML = ms.map(m => {
    const st = STATUS_MAP[m.status] || STATUS_MAP.stable;
    const ph = m.price_history || [];
    const hasPrice = ph.length > 0;
    const curPrice = hasPrice ? ph[ph.length-1].price : null;
    const days = daysSince(m.created);

    let priceHTML = '';
    if (hasPrice) {
      priceHTML += '<div class="price-current">R' + curPrice.toLocaleString() + '</div>';
      if (m.target) {
        const pct = Math.min(100, Math.max(0, (1 - (curPrice - m.target) / curPrice) * 100));
        const color = curPrice <= m.target ? 'var(--green)' : 'var(--accent)';
        priceHTML += '<div class="price-target-bar"><div class="price-target-fill" style="width:'+pct+'%;background:'+color+'"></div></div>';
        priceHTML += '<div class="price-target-text">Target: R' + m.target.toLocaleString() + (curPrice <= m.target ? ' \\uD83C\\uDFAF Hit!' : '') + '</div>';
      }
      priceHTML += sparklineSVG(ph.slice(-20), 80, 24);
    }

    let notesHTML = m.notes_count > 0 ? '<div class="notes-badge">' + m.notes_count + '</div>' : '';

    let badges = '<span class="badge ' + st.cls + '">' + st.icon + ' ' + st.label + '</span>';
    if (m.priority === 'high' || m.priority === 'low') badges += ' <span class="badge badge-' + m.priority + '">' + (PRI_MAP[m.priority]||'') + '</span>';
    if (m.group) badges += ' <span class="badge badge-group" onclick="filterGroup(\\'' + esc(m.group) + '\\')">' + esc(m.group) + '</span>';

    let condHTML = m.condition ? '<div class="condition-text">Condition: ' + esc(m.condition) + '</div>' : '';

    return '<div class="monitor-card">' + notesHTML +
      '<div class="card-top"><div><div class="monitor-label">' + esc(m.label) + '</div><a class="monitor-url" href="' + esc(m.url) + '" target="_blank" title="' + esc(m.url) + '">' + esc(truncUrl(m.url)) + '</a></div></div>' +
      '<div class="card-meta">' + badges + '</div>' +
      '<div class="card-detail">Checked ' + relTime(m.last_checked) + ' &middot; ' + days + 'd monitored' + (m.browser ? ' &middot; \\uD83C\\uDF10 JS' : '') + (m.webhooks ? ' &middot; \\uD83D\\uDD14' : '') + '</div>' +
      priceHTML + condHTML +
    '</div>';
  }).join('');
}
renderMonitors();

function filterGroup(g) {
  document.getElementById('filter-group').value = g;
  renderMonitors();
  document.getElementById('monitor-grid').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Price Trends
(function() {
  const priceMonitors = DATA.monitors.filter(m => m.price_history && m.price_history.length >= 2);
  const grid = document.getElementById('trend-grid');
  if (priceMonitors.length === 0) {
    grid.innerHTML = '<div class="empty-state"><span class="emoji">\\uD83D\\uDCC9</span>Price tracking starts after the second check</div>';
    return;
  }
  grid.innerHTML = priceMonitors.map(m => {
    const ph = m.price_history;
    const vals = ph.map(p => p.price);
    const mn = Math.min(...vals), mx = Math.max(...vals);
    const avg = vals.reduce((a,b)=>a+b,0)/vals.length;
    const cur = vals[vals.length-1];
    const recent = vals.slice(-3);
    const dir = recent[recent.length-1] > recent[0] ? '\\u2197\\uFE0F rising' : recent[recent.length-1] < recent[0] ? '\\u2198\\uFE0F dropping' : '\\u2192 stable';

    function fmtDate(iso) { try { return new Date(iso).toLocaleDateString('en-ZA',{month:'short',day:'numeric'}); } catch(e) { return iso; } }
    const mnDate = fmtDate(ph[vals.indexOf(mn)].date);
    const mxDate = fmtDate(ph[vals.indexOf(mx)].date);

    return '<div class="trend-card"><h3>' + esc(m.label) + ' <span style="font-weight:400;font-size:12px;color:var(--text-dim)">' + dir + '</span></h3>' +
      '<div class="trend-stats">' +
      '<div class="trend-stat"><b>R' + cur.toLocaleString() + '</b>Current</div>' +
      '<div class="trend-stat"><b>R' + mn.toLocaleString() + '</b>Low (' + mnDate + ')</div>' +
      '<div class="trend-stat"><b>R' + mx.toLocaleString() + '</b>High (' + mxDate + ')</div>' +
      '<div class="trend-stat"><b>R' + Math.round(avg).toLocaleString() + '</b>Average</div>' +
      '</div><div class="trend-chart">' + trendChart(ph.slice(-30), 320, 60, m.target) + '</div></div>';
  }).join('');
})();

// Alert History
(function() {
  const tl = document.getElementById('alert-timeline');
  if (DATA.alerts.length === 0) {
    tl.innerHTML = '<div class="empty-state"><span class="emoji">\\uD83D\\uDE0C</span>All quiet. Your monitors are behaving.</div>';
    return;
  }
  tl.innerHTML = DATA.alerts.map(a =>
    '<div class="timeline-item"><div class="timeline-time">' + relTime(a.timestamp) + '</div><div><div class="timeline-label">' + esc(a.monitor_label) + '</div><div class="timeline-summary">' + esc(a.summary) + '</div></div></div>'
  ).join('');
})();

// Groups
(function() {
  const grid = document.getElementById('group-grid');
  if (DATA.groups.length === 0) {
    grid.innerHTML = '<div class="empty-state"><span class="emoji">\\uD83D\\uDCC1</span>Organize monitors into groups:<br><code>monitor.py add &lt;url&gt; --group wishlist</code></div>';
    return;
  }
  grid.innerHTML = DATA.groups.map(g =>
    '<div class="group-card" onclick="filterGroup(\\'' + esc(g.name) + '\\')">' +
    '<div class="group-name">' + esc(g.name) + '</div>' +
    '<div class="group-count">' + g.count + ' monitor' + (g.count !== 1 ? 's' : '') + '</div>' +
    (g.alerts > 0 ? '<div class="group-alerts">' + g.alerts + ' alert' + (g.alerts !== 1 ? 's' : '') + '</div>' : '') +
    '</div>'
  ).join('');
})();

// Templates
(function() {
  const grid = document.getElementById('template-grid');
  grid.innerHTML = DATA.templates.map(t =>
    '<div class="template-card"><h3>' + esc(t.name) + '</h3>' +
    '<div class="desc">' + esc(t.description) + '</div>' +
    '<div class="tmpl-meta">Condition: ' + esc(t.condition) + ' &middot; Every ' + t.interval + 'min &middot; ' + t.priority + ' priority</div>' +
    '<div class="template-cmd">monitor.py template use ' + esc(t.name) + ' &lt;url&gt;</div></div>'
  ).join('');
})();

// Snapshots
(function() {
  const list = document.getElementById('snap-list');
  if (DATA.snapshots.length === 0) {
    list.innerHTML = '<div class="empty-state"><span class="emoji">\\uD83D\\uDCF8</span>No snapshots yet</div>';
    return;
  }
  list.innerHTML = DATA.snapshots.map(s =>
    '<div class="snap-item ' + (s.changed ? 'snap-changed' : 'snap-unchanged') + '">' +
    '<span>' + esc(s.monitor_label) + '</span>' +
    '<span style="display:flex;gap:8px;align-items:center"><span class="badge ' + (s.changed ? 'badge-changed' : 'badge-stable') + '">' + (s.changed ? 'Changed' : 'Unchanged') + '</span><span style="font-size:12px;color:var(--text-muted)">' + relTime(s.timestamp) + '</span></span>' +
    '</div>'
  ).join('');
})();

// Hide empty sections
if (DATA.monitors.filter(m => m.price_history && m.price_history.length >= 2).length === 0 && DATA.monitors.length > 0) {
  // keep trends section visible with empty state
}
</script>
</body>
</html>'''


def main():
    if len(sys.argv) < 2:
        cmd_help(None)
        return

    if sys.argv[1] == "help":
        cmd_help(None)
        return
    if sys.argv[1] == "gui":
        class GuiArgs:
            no_open = "--no-open" in sys.argv
        cmd_gui(GuiArgs())
        return
    if sys.argv[1] == "setup":
        cmd_setup(None)
        return
    if sys.argv[1] == "quickstart":
        cmd_quickstart(None)
        return
    if sys.argv[1] == "debug":
        cmd_debug(None)
        return
    if sys.argv[1] == "engines":
        cmd_engines(None)
        return
    if sys.argv[1] == "feedback":
        class FeedbackArgs:
            message = ""
            bug = None
            idea = None
        fa = FeedbackArgs()
        rest = sys.argv[2:]
        if "--bug" in rest:
            idx = rest.index("--bug")
            if idx + 1 < len(rest):
                fa.bug = rest[idx + 1]
        elif "--idea" in rest:
            idx = rest.index("--idea")
            if idx + 1 < len(rest):
                fa.idea = rest[idx + 1]
        else:
            fa.message = " ".join(rest)
        cmd_feedback(fa)
        return
    # Handle 'template' and 'templates' without argparse
    if sys.argv[1] in ("template", "templates"):
        if len(sys.argv) < 3 or sys.argv[2] == "list":
            cmd_template_list(None)
            return
        elif sys.argv[2] == "use" and len(sys.argv) >= 5:
            # template use <name> <url> [--browser] [--group g] [--webhook w]
            class Args:
                pass
            a = Args()
            a.template_name = sys.argv[3]
            a.template_url = sys.argv[4]
            a.browser = "--browser" in sys.argv or "-b" in sys.argv
            a.group = None
            a.webhook = []
            a.engine = "auto"
            for i, arg in enumerate(sys.argv):
                if arg in ("--group", "-g") and i + 1 < len(sys.argv):
                    a.group = sys.argv[i + 1]
                if arg in ("--webhook", "-w") and i + 1 < len(sys.argv):
                    a.webhook.append(sys.argv[i + 1])
                if arg in ("--engine", "-e") and i + 1 < len(sys.argv):
                    a.engine = sys.argv[i + 1]
            cmd_template_use(a)
            return
        else:
            cmd_template(type('Args', (), {'template_command': None})())
            return

    parser = argparse.ArgumentParser(description="Web Monitor Pro — Track web page changes")
    sub = parser.add_subparsers(dest="command")

    # add
    p_add = sub.add_parser("add", help="Add a new monitor")
    p_add.add_argument("url", help="URL to monitor")
    p_add.add_argument("--label", "-l", help="Human-friendly label")
    p_add.add_argument("--selector", "-s", help="CSS-like selector")
    p_add.add_argument("--condition", "-c", help="Alert condition")
    p_add.add_argument("--interval", "-i", type=int, help="Check interval in minutes")
    p_add.add_argument("--group", "-g", help="Group/category")
    p_add.add_argument("--priority", "-p", choices=["high", "medium", "low"], default="medium")
    p_add.add_argument("--target", "-t", type=float, help="Price target")
    p_add.add_argument("--browser", "-b", action="store_true", help="Use Playwright for JS rendering")
    p_add.add_argument("--engine", "-e", choices=["auto", "curl", "cloudscraper", "browser", "openclaw"], default="auto", help="Fetch engine (openclaw = skip fetch, use --content-file on check)")
    p_add.add_argument("--webhook", "-w", action="append", help="Webhook URL (repeatable)")

    # remove
    p_rm = sub.add_parser("remove", help="Remove a monitor")
    p_rm.add_argument("id", help="Monitor ID")

    # list
    p_list = sub.add_parser("list", help="List all monitors")
    p_list.add_argument("--group", "-g", help="Filter by group")

    # check
    p_check = sub.add_parser("check", help="Check monitors for changes")
    p_check.add_argument("--id", help="Check specific monitor")
    p_check.add_argument("--verbose", "-v", action="store_true")
    p_check.add_argument("--content-file", help="Use pre-fetched content from file instead of fetching (use - for stdin). Requires --id.")

    # history
    p_hist = sub.add_parser("history", help="Show snapshot history")
    p_hist.add_argument("id", help="Monitor ID")
    p_hist.add_argument("--limit", "-n", type=int, default=5)

    # dashboard
    p_dash = sub.add_parser("dashboard", help="Monitor dashboard")
    p_dash.add_argument("--whatsapp", action="store_true", help="WhatsApp format")

    # trend
    p_trend = sub.add_parser("trend", help="Price trend")
    p_trend.add_argument("id", help="Monitor ID")
    p_trend.add_argument("--days", "-d", type=int, help="Limit to N days")

    # pause
    p_pause = sub.add_parser("pause", help="Pause a monitor")
    p_pause.add_argument("id", help="Monitor ID")

    # resume
    p_resume = sub.add_parser("resume", help="Resume a monitor")
    p_resume.add_argument("id", help="Monitor ID")

    # snapshot
    p_snap = sub.add_parser("snapshot", help="Take a manual snapshot")
    p_snap.add_argument("id", help="Monitor ID")
    p_snap.add_argument("--note", "-n", help="Attach a note")

    # screenshot
    p_ss = sub.add_parser("screenshot", help="Save page content for diffing")
    p_ss.add_argument("id", help="Monitor ID")

    # diff
    p_diff = sub.add_parser("diff", help="Generate and open HTML diff")
    p_diff.add_argument("id", help="Monitor ID")

    # compare
    p_cmp = sub.add_parser("compare", help="Compare prices across monitors")
    p_cmp.add_argument("group", nargs="?", help="Group name")
    p_cmp.add_argument("--all", action="store_true", help="Compare all price monitors")

    # add-competitor
    p_comp = sub.add_parser("add-competitor", help="Link competitor URL to a monitor")
    p_comp.add_argument("id", help="Original monitor ID")
    p_comp.add_argument("url", help="Competitor URL")

    # note
    p_note = sub.add_parser("note", help="Add a note to a monitor")
    p_note.add_argument("id", help="Monitor ID")
    p_note.add_argument("text", help="Note text")

    # notes
    p_notes = sub.add_parser("notes", help="View notes for a monitor")
    p_notes.add_argument("id", help="Monitor ID")

    # groups
    sub.add_parser("groups", help="List all groups")

    # report
    sub.add_parser("report", help="Weekly report")

    # watch
    p_watch = sub.add_parser("watch", help="Smart auto-detect and setup")
    p_watch.add_argument("url", help="URL to monitor")
    p_watch.add_argument("--group", "-g", help="Group/category")
    p_watch.add_argument("--browser", "-b", action="store_true", help="Use Playwright for JS rendering")
    p_watch.add_argument("--engine", "-e", choices=["auto", "curl", "cloudscraper", "browser", "openclaw"], default="auto", help="Fetch engine (openclaw = skip fetch, use --content-file on check)")
    p_watch.add_argument("--webhook", "-w", action="append", help="Webhook URL (repeatable)")

    # export
    sub.add_parser("export", help="Export monitor configs")

    # import
    p_imp = sub.add_parser("import", help="Import monitors from file")
    p_imp.add_argument("file", help="JSON file to import")

    args = parser.parse_args()

    if not args.command:
        cmd_help(None)
        return

    ensure_dirs()
    _check_whats_new()

    commands = {
        "add": cmd_add,
        "remove": cmd_remove,
        "list": cmd_list,
        "check": cmd_check,
        "history": cmd_history,
        "dashboard": cmd_dashboard,
        "trend": cmd_trend,
        "pause": cmd_pause,
        "resume": cmd_resume,
        "snapshot": cmd_snapshot,
        "screenshot": cmd_screenshot,
        "diff": cmd_diff,
        "compare": cmd_compare,
        "add-competitor": cmd_add_competitor,
        "note": cmd_note,
        "notes": cmd_notes,
        "groups": cmd_groups,
        "report": cmd_report,
        "watch": cmd_watch,
        "export": cmd_export,
        "import": cmd_import,
    }

    cmd_func = commands.get(args.command)
    if cmd_func:
        cmd_func(args)
    else:
        print(_red(f"Unknown command: {args.command}"))
        cmd_help(None)


if __name__ == "__main__":
    main()
