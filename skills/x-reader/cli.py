# -*- coding: utf-8 -*-
"""
x-reader CLI — fetch content from any platform.

Usage:
    x-reader <url>                     # Fetch a single URL
    x-reader <url1> <url2> ...         # Fetch multiple URLs
    x-reader list                      # Show inbox contents
    x-reader clear                     # Clear inbox
"""

import sys
import asyncio
import json
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

from x_reader.reader import UniversalReader
from x_reader.schema import UnifiedInbox, SourceType


def get_inbox_path() -> str:
    import os
    return os.getenv("INBOX_FILE", "unified_inbox.json")


def cmd_fetch(urls: list[str]):
    """Fetch one or more URLs."""
    inbox = UnifiedInbox(get_inbox_path())
    reader = UniversalReader(inbox=inbox)

    async def run():
        if len(urls) == 1:
            item = await reader.read(urls[0])
            print(f"✅ [{item.source_type.value}] {item.title[:60]}")
            print(f"   {item.url}")
            print(f"   {item.content[:200]}...")
        else:
            items = await reader.read_batch(urls)
            for item in items:
                print(f"✅ [{item.source_type.value}] {item.title[:60]}")
            print(f"\n📦 Fetched {len(items)}/{len(urls)} URLs")

    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        print("\n⏹ Cancelled")
    except Exception as e:
        print(f"❌ {e}")
        sys.exit(1)


def cmd_list():
    """Show inbox contents."""
    inbox = UnifiedInbox(get_inbox_path())
    if not inbox.items:
        print("📦 Inbox is empty")
        return

    print(f"📦 Inbox: {len(inbox.items)} items\n")

    emoji_map = {
        SourceType.TELEGRAM: "📢", SourceType.RSS: "📰",
        SourceType.BILIBILI: "🎬", SourceType.XIAOHONGSHU: "📕",
        SourceType.TWITTER: "🐦", SourceType.WECHAT: "💬",
        SourceType.YOUTUBE: "▶️", SourceType.MANUAL: "✏️",
    }

    for i, item in enumerate(inbox.items[-20:], 1):
        emoji = emoji_map.get(item.source_type, "📄")
        print(f"  {i:2d}. {emoji} [{item.source_type.value:8s}] {item.title[:50]}")


def cmd_clear():
    """Clear inbox."""
    path = Path(get_inbox_path())
    if path.exists():
        confirm = input("Clear inbox? (y/N) ")
        if confirm.lower() == 'y':
            path.write_text("[]")
            print("✅ Inbox cleared")
    else:
        print("📦 Inbox is already empty")


def cmd_login(platform: str, headless: bool = False):
    """Open browser for manual login to a platform."""
    from x_reader.login import login
    login(platform, headless=headless)


def main():
    if len(sys.argv) < 2:
        print("""
📖 x-reader — Universal content reader

Usage:
    x-reader <url>              Fetch content from any URL
    x-reader <url1> <url2>      Fetch multiple URLs
    x-reader login <platform>   Login to a platform (saves session for browser fallback)
    x-reader list               Show inbox contents
    x-reader clear              Clear inbox

Supported platforms:
    WeChat, Telegram, X/Twitter, YouTube,
    Bilibili, Xiaohongshu, RSS, and any web page

Examples:
    x-reader https://mp.weixin.qq.com/s/abc123
    x-reader https://x.com/elonmusk/status/123456
    x-reader https://www.xiaohongshu.com/explore/abc123
    x-reader login xhs
""")
        return

    cmd = sys.argv[1].lower()

    if cmd == "login":
        if len(sys.argv) < 3:
            print("❌ Usage: x-reader login <platform> [--headless]")
            print("   Supported: xhs, wechat")
            sys.exit(1)
        headless = "--headless" in sys.argv
        cmd_login(sys.argv[2], headless=headless)
    elif cmd == "list":
        cmd_list()
    elif cmd == "clear":
        cmd_clear()
    elif cmd.startswith("http") or cmd.startswith("www.") or "." in cmd:
        urls = [arg for arg in sys.argv[1:] if arg.startswith(("http", "www.")) or "." in arg]
        cmd_fetch(urls)
    else:
        print(f"❌ Unknown command: {cmd}")
        print("   Run 'x-reader' with no args for help")


if __name__ == "__main__":
    main()
