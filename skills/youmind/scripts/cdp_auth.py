#!/usr/bin/env python3
"""
Dynamic cookie fetching from OpenClaw browser via CDP.

Instead of relying on a manually-exported state.json (which expires),
this module fetches fresh YouMind cookies from the OpenClaw browser
(a running Chromium instance, default CDP port 18800) on every call.

Behavior:
  - Cookies are cached locally in data/cdp_cache.json with a 5-hour TTL
  - Falls back to state.json if the browser is not running
  - On first use with no cookies, guides user through sign-in
  - No extra dependencies: uses patchright (already required)
  - CDP port is configurable via OPENCLAW_CDP_URL env var

Similar to how birdx reads Twitter cookies from the OpenClaw browser via
CDP, this reads YouMind cookies from the live browser session.
"""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Optional

# ── Constants ──────────────────────────────────────────────────────────────────

# Respect custom gateway/port configs; default openclaw profile is always 18800
CDP_HTTP = os.environ.get("OPENCLAW_CDP_URL", "http://127.0.0.1:18800").rstrip("/")

CACHE_TTL_SECONDS = 5 * 3600  # 5 hours

_SKILL_DIR = Path(__file__).parent.parent
_DATA_DIR = _SKILL_DIR / "data"
CACHE_FILE = _DATA_DIR / "cdp_cache.json"

YOUMIND_DOMAINS = ("youmind.com", "gooo.ai")

# YouMind uses Supabase auth; session cookies match this prefix.
# Non-session cookies (NEXT_LOCALE, g_state) are excluded.
# The pattern covers both token segments: auth-token.0, auth-token.1
AUTH_COOKIE_PATTERN = "auth-token"

# Sign-in poll: check every N seconds for up to MAX_WAIT_SECONDS
SIGNIN_POLL_INTERVAL = 2
SIGNIN_MAX_WAIT = 600  # 10 minutes


# ── Helpers ────────────────────────────────────────────────────────────────────

def _load_cache() -> Optional[str]:
    """Return cached cookie string if still within TTL, else None."""
    try:
        if not CACHE_FILE.exists():
            return None
        data = json.loads(CACHE_FILE.read_text())
        age = time.time() - data.get("saved_at", 0)
        if age < CACHE_TTL_SECONDS:
            return data.get("cookie_str") or None
    except Exception:
        pass
    return None


def _save_cache(cookie_str: str) -> None:
    """Persist cookie string with current timestamp."""
    try:
        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        CACHE_FILE.write_text(
            json.dumps({"cookie_str": cookie_str, "saved_at": time.time()}, indent=2)
        )
    except Exception:
        pass


def _fetch_from_cdp() -> Optional[str]:
    """
    Connect to the OpenClaw browser via CDP and extract YouMind cookies.

    Uses patchright's connect_over_cdp() which accepts an HTTP endpoint
    and handles the WebSocket upgrade internally.

    Note: connect_over_cdp() only opens a remote connection; the browser
    process is NOT affected when the Playwright context exits.
    """
    try:
        from patchright.sync_api import sync_playwright

        with sync_playwright() as p:
            # connect_over_cdp: attaches to existing browser, never closes it
            browser = p.chromium.connect_over_cdp(CDP_HTTP)
            contexts = browser.contexts
            if not contexts:
                return None
            cookies = contexts[0].cookies(["https://youmind.com"])
            # Include ALL youmind.com cookies (needed for full session context),
            # but require at least one auth-token cookie to confirm login.
            all_pairs = [
                f"{c['name']}={c['value']}"
                for c in cookies
                if c.get("name") and c.get("value") is not None
                and any(d in c.get("domain", "") for d in YOUMIND_DOMAINS)
            ]
            has_auth = any(
                AUTH_COOKIE_PATTERN in c.get("name", "")
                for c in cookies
                if any(d in c.get("domain", "") for d in YOUMIND_DOMAINS)
            )
            pairs = all_pairs if has_auth else []
            # No explicit browser.close() — Playwright remote connections
            # disconnect cleanly when the sync_playwright() context exits,
            # leaving the actual Chrome process untouched.
            return "; ".join(pairs) if pairs else None

    except Exception as exc:
        print(f"[cdp_auth] CDP fetch failed: {exc}", file=sys.stderr)
        return None


def _open_signin_tab() -> bool:
    """
    Open youmind.com/sign-in in the OpenClaw browser via the openclaw CLI.
    Uses `openclaw browser open <url>` — the same command used by the
    browser tool internally. Works cross-platform wherever openclaw is installed.
    Returns True if the tab was opened successfully.
    """
    import subprocess
    import shutil
    try:
        if not shutil.which("openclaw"):
            print("[cdp_auth] openclaw CLI not found in PATH", file=sys.stderr)
            return False
        result = subprocess.run(
            ["openclaw", "browser", "open",
             "--browser-profile", "openclaw",
             "https://youmind.com/sign-in"],
            capture_output=True, text=True, timeout=10
        )
        return result.returncode == 0
    except Exception as exc:
        print(f"[cdp_auth] Could not open sign-in tab: {exc}", file=sys.stderr)
        return False


# ── Public API ─────────────────────────────────────────────────────────────────

def is_cdp_available() -> bool:
    """Return True if the OpenClaw browser CDP endpoint is reachable."""
    try:
        with urllib.request.urlopen(f"{CDP_HTTP}/json/version", timeout=2) as resp:
            data = json.loads(resp.read())
            return bool(data.get("Browser"))
    except Exception:
        return False


def get_cdp_cookie_str(force_refresh: bool = False) -> Optional[str]:
    """
    Return a 'name=value; ...' cookie string for youmind.com, or None.

    Strategy:
      1. Return cached value if within TTL (unless force_refresh=True)
      2. Fetch live cookies from the OpenClaw browser via CDP
      3. Cache and return, or None if browser is unavailable
    """
    if not force_refresh:
        cached = _load_cache()
        if cached:
            return cached

    cookie_str = _fetch_from_cdp()
    if cookie_str:
        _save_cache(cookie_str)

    return cookie_str


def ensure_authenticated(interactive: bool = True) -> Optional[str]:
    """
    Ensure YouMind cookies are available, guiding the user through sign-in
    if needed (when running interactively).

    Flow:
      1. Try to get cookies from CDP cache or live browser
      2. If no cookies but browser is available → open sign-in page + poll
      3. Return cookie string on success, None on failure/timeout

    Args:
        interactive: If False, skip the guided sign-in and return None immediately.
    """
    # Fast path: already have cookies
    cookie_str = get_cdp_cookie_str()
    if cookie_str:
        return cookie_str

    if not interactive or not is_cdp_available():
        return None

    # Browser is running but no YouMind cookies — guide user through login
    print("🔐 YouMind session not found in OpenClaw browser.")
    print(f"   Opening sign-in page: https://youmind.com/sign-in")
    if not _open_signin_tab():
        print("   ⚠️  Could not open sign-in tab automatically. Please navigate manually.")

    print(f"   Waiting for login (up to {SIGNIN_MAX_WAIT // 60} min)... ", end="", flush=True)

    elapsed = 0
    while elapsed < SIGNIN_MAX_WAIT:
        time.sleep(SIGNIN_POLL_INTERVAL)
        elapsed += SIGNIN_POLL_INTERVAL
        cookie_str = get_cdp_cookie_str(force_refresh=True)
        if cookie_str:
            print("✅")
            print("   Login successful! Cookies cached.")
            return cookie_str
        if elapsed % 30 == 0:
            print(f"\r   Still waiting... ({elapsed}s elapsed)", end="", flush=True)

    print("\n   ❌ Login timeout. Run auth setup manually:")
    print("      python3 scripts/run.py auth_manager.py login")
    return None


def invalidate_cache() -> None:
    """Remove the CDP cookie cache (forces fresh fetch on next call)."""
    try:
        if CACHE_FILE.exists():
            CACHE_FILE.unlink()
    except Exception:
        pass


# ── CLI ────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="CDP cookie manager for YouMind skill")
    parser.add_argument("--refresh", action="store_true", help="Force refresh from CDP")
    parser.add_argument("--status", action="store_true", help="Show CDP + cache status")
    parser.add_argument("--login", action="store_true", help="Guided sign-in via browser")
    args = parser.parse_args()

    if args.status:
        cdp_ok = is_cdp_available()
        print(f"CDP ({CDP_HTTP}): {'✅ available' if cdp_ok else '❌ not available'}")
        if CACHE_FILE.exists():
            try:
                cache_data = json.loads(CACHE_FILE.read_text())
                age_min = (time.time() - cache_data.get("saved_at", 0)) / 60
                preview = (cache_data.get("cookie_str") or "")[:60]
                print(f"Cache: {age_min:.0f} min old | {preview}...")
            except Exception:
                print("Cache: unreadable")
        else:
            print("Cache: none")
    elif args.login:
        result = ensure_authenticated(interactive=True)
        if not result:
            sys.exit(1)
    else:
        cookie_str = get_cdp_cookie_str(force_refresh=args.refresh)
        if cookie_str:
            print(f"✅ Cookies ({len(cookie_str)} chars): {cookie_str[:80]}...")
        else:
            print("❌ No cookies available via CDP")
