#!/usr/bin/env python3
"""
Social Playwright — browser automation for social media actions.

Uses Playwright (via playwright-mcp or direct) to post, reply, like,
repost, follow, and monitor on Twitter/X, LinkedIn, and other platforms.

Importable as a module or runnable as CLI:
    python3 social_playwright.py post --platform twitter --content "Hello world" --json
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional


PLATFORM_URLS: Dict[str, Dict[str, str]] = {
    "twitter": {
        "home": "https://twitter.com",
        "compose": "https://twitter.com/compose/tweet",
        "notifications": "https://twitter.com/notifications",
        "search": "https://twitter.com/search?q={query}&src=typed_query&f=live",
    },
    "linkedin": {
        "home": "https://www.linkedin.com/feed/",
        "compose": "https://www.linkedin.com/feed/",
        "notifications": "https://www.linkedin.com/notifications/",
        "search": "https://www.linkedin.com/search/results/content/?keywords={query}",
    },
}

SELECTORS: Dict[str, Dict[str, str]] = {
    "twitter": {
        "compose_input": '[data-testid="tweetTextarea_0"]',
        "submit_button": '[data-testid="tweetButtonInline"]',
        "reply_input": '[data-testid="tweetTextarea_0"]',
        "reply_button": '[data-testid="tweetButtonInline"]',
        "like_button": '[data-testid="like"]',
        "retweet_button": '[data-testid="retweet"]',
        "retweet_confirm": '[data-testid="retweetConfirm"]',
        "follow_button": '[data-testid="placementTracking"] [role="button"]',
        "notification_item": '[data-testid="notification"]',
        "tweet_text": '[data-testid="tweetText"]',
    },
    "linkedin": {
        "compose_trigger": "button.share-box-feed-entry__trigger",
        "compose_input": ".ql-editor[data-placeholder]",
        "submit_button": "button.share-actions__primary-action",
        "like_button": "button.react-button",
        "comment_button": "button.comment-button",
        "notification_item": ".nt-card",
    },
}


def _find_playwright_mcp() -> Optional[Path]:
    """Find the playwright-mcp skill entry point."""
    candidates = [
        Path.home() / ".openclaw" / "workspace" / "skills" / "playwright-mcp",
        Path.home() / ".openclaw" / "workspace" / "skills" / "playwright-commander",
    ]
    for c in candidates:
        if c.is_dir():
            return c
    return None


class SocialPlaywright:
    """Browser automation for social media platforms."""

    def __init__(self, headless: bool = True, use_mcp: bool = True):
        self.headless = headless
        self.use_mcp = use_mcp
        self.mcp_path = _find_playwright_mcp() if use_mcp else None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _run_playwright_script(self, script: str) -> Dict[str, Any]:
        """Execute a Playwright script via subprocess."""
        try:
            result = subprocess.run(
                ["python3", "-c", script],
                capture_output=True,
                text=True,
                timeout=120,
            )
            if result.returncode != 0:
                return {"ok": False, "error": result.stderr.strip()}
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError:
                return {"ok": True, "output": result.stdout.strip()}
        except subprocess.TimeoutExpired:
            return {"ok": False, "error": "Playwright script timed out (120s)"}
        except FileNotFoundError:
            return {"ok": False, "error": "python3 not found"}
        except Exception as exc:
            return {"ok": False, "error": str(exc)}

    def _build_script(self, platform: str, actions: str) -> str:
        """Build a complete Playwright script with browser setup."""
        urls = PLATFORM_URLS.get(platform, {})
        sels = SELECTORS.get(platform, {})
        headless_flag = "True" if self.headless else "False"
        return f"""\
import json, sys
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print(json.dumps({{"ok": False, "error": "playwright not installed — pip install playwright && playwright install"}}))
    sys.exit(1)

URLS = {json.dumps(urls)}
SEL  = {json.dumps(sels)}

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless={headless_flag})
    ctx = browser.new_context(storage_state=None)
    page = ctx.new_page()
    result = {{"ok": True}}
    try:
{actions}
    except Exception as exc:
        result = {{"ok": False, "error": str(exc)}}
    finally:
        browser.close()
    print(json.dumps(result))
"""

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def post(
        self, platform: str, content: str, media: Optional[str] = None
    ) -> Dict[str, Any]:
        """Post content to a social platform."""
        if platform not in PLATFORM_URLS:
            return {"ok": False, "error": f"Unsupported platform: {platform}"}

        actions = f"""\
        page.goto(URLS["compose"])
        page.wait_for_selector(SEL["compose_input"], timeout=15000)
        page.click(SEL["compose_input"])
        page.keyboard.type({json.dumps(content)}, delay=30)
        page.wait_for_timeout(500)
        page.click(SEL["submit_button"])
        page.wait_for_timeout(2000)
        result["action"] = "post"
        result["platform"] = {json.dumps(platform)}
        result["content"] = {json.dumps(content)}
"""
        return self._run_playwright_script(self._build_script(platform, actions))

    def reply(
        self, platform: str, post_id: str, content: str
    ) -> Dict[str, Any]:
        """Reply to a specific post."""
        if platform not in PLATFORM_URLS:
            return {"ok": False, "error": f"Unsupported platform: {platform}"}

        post_url = f"{PLATFORM_URLS[platform]['home']}/status/{post_id}" if platform == "twitter" else post_id
        actions = f"""\
        page.goto({json.dumps(post_url)})
        page.wait_for_selector(SEL.get("reply_input", SEL.get("compose_input", "textarea")), timeout=15000)
        page.click(SEL.get("reply_input", SEL.get("compose_input", "textarea")))
        page.keyboard.type({json.dumps(content)}, delay=30)
        page.wait_for_timeout(500)
        page.click(SEL.get("reply_button", SEL.get("submit_button", "button")))
        page.wait_for_timeout(2000)
        result["action"] = "reply"
        result["platform"] = {json.dumps(platform)}
        result["post_id"] = {json.dumps(post_id)}
        result["content"] = {json.dumps(content)}
"""
        return self._run_playwright_script(self._build_script(platform, actions))

    def like(self, platform: str, post_id: str) -> Dict[str, Any]:
        """Like a specific post."""
        if platform not in PLATFORM_URLS:
            return {"ok": False, "error": f"Unsupported platform: {platform}"}

        post_url = f"{PLATFORM_URLS[platform]['home']}/status/{post_id}" if platform == "twitter" else post_id
        actions = f"""\
        page.goto({json.dumps(post_url)})
        page.wait_for_selector(SEL["like_button"], timeout=15000)
        page.click(SEL["like_button"])
        page.wait_for_timeout(1000)
        result["action"] = "like"
        result["platform"] = {json.dumps(platform)}
        result["post_id"] = {json.dumps(post_id)}
"""
        return self._run_playwright_script(self._build_script(platform, actions))

    def repost(self, platform: str, post_id: str) -> Dict[str, Any]:
        """Repost/retweet a post."""
        if platform not in PLATFORM_URLS:
            return {"ok": False, "error": f"Unsupported platform: {platform}"}

        post_url = f"{PLATFORM_URLS[platform]['home']}/status/{post_id}" if platform == "twitter" else post_id
        actions = f"""\
        page.goto({json.dumps(post_url)})
        page.wait_for_selector(SEL["retweet_button"], timeout=15000)
        page.click(SEL["retweet_button"])
        page.wait_for_timeout(500)
        confirm = SEL.get("retweet_confirm")
        if confirm:
            page.wait_for_selector(confirm, timeout=5000)
            page.click(confirm)
        page.wait_for_timeout(1000)
        result["action"] = "repost"
        result["platform"] = {json.dumps(platform)}
        result["post_id"] = {json.dumps(post_id)}
"""
        return self._run_playwright_script(self._build_script(platform, actions))

    def follow(self, platform: str, username: str) -> Dict[str, Any]:
        """Follow a user."""
        if platform not in PLATFORM_URLS:
            return {"ok": False, "error": f"Unsupported platform: {platform}"}

        profile_url = f"{PLATFORM_URLS[platform]['home']}/{username}"
        actions = f"""\
        page.goto({json.dumps(profile_url)})
        page.wait_for_selector(SEL.get("follow_button", '[role="button"]'), timeout=15000)
        buttons = page.query_selector_all(SEL.get("follow_button", '[role="button"]'))
        for btn in buttons:
            text = btn.inner_text().lower()
            if "follow" in text and "following" not in text:
                btn.click()
                break
        page.wait_for_timeout(1000)
        result["action"] = "follow"
        result["platform"] = {json.dumps(platform)}
        result["username"] = {json.dumps(username)}
"""
        return self._run_playwright_script(self._build_script(platform, actions))

    def monitor(
        self,
        platform: str,
        keywords: List[str],
        duration_minutes: int = 60,
    ) -> Dict[str, Any]:
        """Monitor for keywords on a platform. Returns found items."""
        if platform not in PLATFORM_URLS:
            return {"ok": False, "error": f"Unsupported platform: {platform}"}

        query = " OR ".join(keywords)
        search_url = PLATFORM_URLS[platform]["search"].format(query=query)
        actions = f"""\
        page.goto({json.dumps(search_url)})
        page.wait_for_timeout(3000)
        tweet_sel = SEL.get("tweet_text", "article")
        items = page.query_selector_all(tweet_sel)
        found = []
        for item in items[:20]:
            found.append(item.inner_text())
        result["action"] = "monitor"
        result["platform"] = {json.dumps(platform)}
        result["keywords"] = {json.dumps(keywords)}
        result["found_count"] = len(found)
        result["items"] = found
"""
        return self._run_playwright_script(self._build_script(platform, actions))

    def get_notifications(
        self, platform: str, count: int = 20
    ) -> Dict[str, Any]:
        """Fetch recent notifications."""
        if platform not in PLATFORM_URLS:
            return {"ok": False, "error": f"Unsupported platform: {platform}"}

        actions = f"""\
        page.goto(URLS["notifications"])
        page.wait_for_timeout(3000)
        notif_sel = SEL.get("notification_item", "article")
        items = page.query_selector_all(notif_sel)
        notifications = []
        for item in items[:{count}]:
            notifications.append(item.inner_text()[:300])
        result["action"] = "get_notifications"
        result["platform"] = {json.dumps(platform)}
        result["count"] = len(notifications)
        result["notifications"] = notifications
"""
        return self._run_playwright_script(self._build_script(platform, actions))


# ======================================================================
# CLI
# ======================================================================

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Social Playwright — browser automation for social media"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # post
    p = sub.add_parser("post", help="Post content to a platform")
    p.add_argument("--platform", required=True, choices=list(PLATFORM_URLS))
    p.add_argument("--content", required=True)
    p.add_argument("--media")
    p.add_argument("--json", action="store_true", dest="json_out")

    # reply
    r = sub.add_parser("reply", help="Reply to a post")
    r.add_argument("--platform", required=True, choices=list(PLATFORM_URLS))
    r.add_argument("--post-id", required=True)
    r.add_argument("--content", required=True)
    r.add_argument("--json", action="store_true", dest="json_out")

    # like
    lk = sub.add_parser("like", help="Like a post")
    lk.add_argument("--platform", required=True, choices=list(PLATFORM_URLS))
    lk.add_argument("--post-id", required=True)
    lk.add_argument("--json", action="store_true", dest="json_out")

    # repost
    rp = sub.add_parser("repost", help="Repost/retweet a post")
    rp.add_argument("--platform", required=True, choices=list(PLATFORM_URLS))
    rp.add_argument("--post-id", required=True)
    rp.add_argument("--json", action="store_true", dest="json_out")

    # follow
    fl = sub.add_parser("follow", help="Follow a user")
    fl.add_argument("--platform", required=True, choices=list(PLATFORM_URLS))
    fl.add_argument("--username", required=True)
    fl.add_argument("--json", action="store_true", dest="json_out")

    # monitor
    mn = sub.add_parser("monitor", help="Monitor keywords")
    mn.add_argument("--platform", required=True, choices=list(PLATFORM_URLS))
    mn.add_argument("--keywords", required=True, help="Comma-separated keywords")
    mn.add_argument("--duration", type=int, default=60)
    mn.add_argument("--json", action="store_true", dest="json_out")

    # notifications
    nt = sub.add_parser("notifications", help="Get recent notifications")
    nt.add_argument("--platform", required=True, choices=list(PLATFORM_URLS))
    nt.add_argument("--count", type=int, default=20)
    nt.add_argument("--json", action="store_true", dest="json_out")

    # global
    parser.add_argument("--no-headless", action="store_true")

    args = parser.parse_args()
    sp = SocialPlaywright(headless=not getattr(args, "no_headless", False))

    if args.command == "post":
        result = sp.post(args.platform, args.content, media=getattr(args, "media", None))
    elif args.command == "reply":
        result = sp.reply(args.platform, args.post_id, args.content)
    elif args.command == "like":
        result = sp.like(args.platform, args.post_id)
    elif args.command == "repost":
        result = sp.repost(args.platform, args.post_id)
    elif args.command == "follow":
        result = sp.follow(args.platform, args.username)
    elif args.command == "monitor":
        kw = [k.strip() for k in args.keywords.split(",")]
        result = sp.monitor(args.platform, kw, duration_minutes=args.duration)
    elif args.command == "notifications":
        result = sp.get_notifications(args.platform, count=args.count)
    else:
        result = {"ok": False, "error": f"Unknown command: {args.command}"}

    if getattr(args, "json_out", False):
        json.dump(result, sys.stdout, indent=2)
        print()
    else:
        for k, v in result.items():
            print(f"{k}: {v}")

    sys.exit(0 if result.get("ok", True) else 1)


if __name__ == "__main__":
    main()
