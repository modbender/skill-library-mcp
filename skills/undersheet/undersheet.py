#!/usr/bin/env python3
"""
UnderSheet — Platform-agnostic persistent thread memory for OpenClaw agents.
Zero dependencies. Pure Python stdlib.

Gives any agent:
  - Persistent state tracking across heartbeats (per platform)
  - Thread comment-count diffing (surfaces new replies only)
  - Feed cursor (unseen posts only)
  - Pluggable platform adapters (Moltbook, HN, Reddit, Discord, etc.)

Usage:
  python3 undersheet.py heartbeat --platform moltbook
  python3 undersheet.py feed-new  --platform hackernews
  python3 undersheet.py track     --platform moltbook --thread-id <id>
"""

import argparse
import importlib
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# State management
# ---------------------------------------------------------------------------

DEFAULT_STATE_DIR = os.path.expanduser("~/.config/undersheet")
PROXY_CONFIG_PATH = os.path.expanduser("~/.config/undersheet/proxy.json")
MAX_SEEN_IDS = 1000


# ---------------------------------------------------------------------------
# Proxy support
# ---------------------------------------------------------------------------

def load_proxy_config(override_url: str = None) -> dict:
    """
    Load proxy settings. Priority order:
      1. --proxy CLI flag
      2. Env vars: ALL_PROXY, HTTPS_PROXY, HTTP_PROXY
      3. ~/.config/undersheet/proxy.json

    Supported: http://host:port  |  https://host:port
    System VPNs (Mullvad, WireGuard, ProtonVPN): no setup needed — they route all traffic.
    """
    if override_url:
        return {"url": override_url, "source": "flag"}
    for key in ("ALL_PROXY", "HTTPS_PROXY", "HTTP_PROXY",
                "all_proxy", "https_proxy", "http_proxy"):
        val = os.environ.get(key, "")
        if val:
            return {"url": val, "source": key}
    if os.path.exists(PROXY_CONFIG_PATH):
        try:
            with open(PROXY_CONFIG_PATH) as f:
                cfg = json.load(f)
            url = cfg.get("url") or cfg.get("socks5") or cfg.get("http") or ""
            if url:
                return {"url": url, "source": "config"}
        except Exception:
            pass
    return {}


def apply_proxy(proxy: dict, verbose: bool = False):
    """
    Wire proxy into urllib so all subsequent HTTP calls route through it.
    Pure stdlib — sets env vars that urllib respects automatically.
    Supports http:// and https:// proxies. For SOCKS5, use a system-level
    VPN (Mullvad, WireGuard, ProtonVPN) — no config needed, all traffic routes.
    """
    if not proxy or not proxy.get("url"):
        return
    url = proxy["url"]
    if verbose:
        print(f"[undersheet] proxy: {url} (from {proxy.get('source', '?')})")
    if url.startswith("socks5"):
        print("[undersheet] ⚠️  SOCKS5 proxy requires a system VPN — set HTTP_PROXY instead.")
        return
    os.environ.setdefault("HTTP_PROXY",  url)
    os.environ.setdefault("HTTPS_PROXY", url)
    os.environ.setdefault("ALL_PROXY",   url)


def _state_path(platform_name: str) -> str:
    d = os.environ.get("UNDERSHEET_STATE_DIR", DEFAULT_STATE_DIR)
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, f"{platform_name}_state.json")


def load_state(platform_name: str) -> dict:
    defaults = {
        "threads": {},
        "seen_post_ids": [],
        "last_heartbeat": None,
        "replied_comment_ids": [],  # dupe guard — IDs we've already replied to
    }
    path = _state_path(platform_name)
    if os.path.exists(path):
        try:
            with open(path) as f:
                state = json.load(f)
            # Backfill new keys for existing state files
            for k, v in defaults.items():
                state.setdefault(k, v)
            return state
        except (json.JSONDecodeError, OSError):
            # Torn write or corrupt file — start fresh, don't crash
            pass
    return defaults


def save_state(platform_name: str, state: dict):
    """Atomic write — temp file + os.replace() so readers never see a partial write."""
    path = _state_path(platform_name)
    # Cap seen_post_ids
    if len(state.get("seen_post_ids", [])) > MAX_SEEN_IDS:
        state["seen_post_ids"] = state["seen_post_ids"][-MAX_SEEN_IDS:]
    # Cap replied_comment_ids
    if len(state.get("replied_comment_ids", [])) > 2000:
        state["replied_comment_ids"] = state["replied_comment_ids"][-2000:]
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(state, f, indent=2)
    os.replace(tmp, path)  # atomic on POSIX, near-atomic on Windows


def mark_replied(state: dict, comment_id: str):
    """
    Record that we've replied to a comment — the ONLY correct dupe guard.
    Call this after every successful reply. Never check comment.replies[] instead.
    """
    replied = state.get("replied_comment_ids", [])
    if comment_id not in replied:
        replied.append(comment_id)
    state["replied_comment_ids"] = replied


def get_unanswered_comments(adapter, state: dict, thread_ids: list) -> list:
    """
    Return individual comments on tracked threads that we haven't replied to yet.
    Requires adapter to implement get_thread_comments(thread_id) -> list[dict].
    Each comment dict must have at minimum: { "id": str, "author": str, "content": str }

    Uses replied_comment_ids in state as the sole source of truth — not content
    matching or nested-reply scanning, both of which produce false negatives.
    """
    if not hasattr(adapter, "get_thread_comments"):
        return []  # adapter doesn't support per-comment fetching yet
    replied = set(state.get("replied_comment_ids", []))
    unanswered = []
    for tid in thread_ids:
        try:
            comments = adapter.get_thread_comments(tid)
        except Exception as e:
            print(f"[undersheet] Warning: could not fetch comments for {tid}: {e}")
            continue
        for c in comments:
            if c.get("id") in replied:
                continue
            if c.get("is_deleted") or c.get("is_spam"):
                continue
            unanswered.append({**c, "_thread_id": tid})
    return unanswered


# ---------------------------------------------------------------------------
# Platform adapter base class
# ---------------------------------------------------------------------------

class PlatformAdapter:
    """
    Subclass this and implement all methods to add a new platform.
    Register via: undersheet.py --platform <name>
    Platform file lives at: platforms/<name>.py
    Class must be named: Adapter
    """

    name: str = "base"

    def get_threads(self, thread_ids: list[str]) -> list[dict]:
        """
        Return a list of thread dicts for the given IDs.
        Each dict must have at minimum:
          { "id": str, "comment_count": int, "title": str, "url": str }
        """
        raise NotImplementedError

    def get_feed(self, limit: int = 25, **kwargs) -> list[dict]:
        """
        Return recent posts/threads from the platform.
        Each dict must have at minimum:
          { "id": str, "title": str, "url": str, "score": int, "created_at": str }
        """
        raise NotImplementedError

    def get_thread_comments(self, thread_id: str) -> list[dict]:
        """
        Optional. Return individual comments for a thread — enables get_unanswered_comments().
        Each dict must have at minimum: { "id": str, "author": str, "content": str }
        Implement this in your adapter to unlock per-comment reply deduplication.
        """
        raise NotImplementedError

    def post_comment(self, thread_id: str, content: str, **kwargs) -> dict:
        """
        Post a comment to a thread. Returns the API response dict.
        """
        raise NotImplementedError

    def get_credentials(self) -> dict:
        """
        Load credentials for this platform from the standard config location.
        Override in subclass.
        """
        return {}


# ---------------------------------------------------------------------------
# Core engine
# ---------------------------------------------------------------------------

def load_adapter(platform_name: str) -> PlatformAdapter:
    """Dynamically load a platform adapter from platforms/<name>.py"""
    platforms_dir = os.path.join(os.path.dirname(__file__), "platforms")
    sys.path.insert(0, platforms_dir)
    try:
        mod = importlib.import_module(platform_name)
        adapter = mod.Adapter()
        return adapter
    except ModuleNotFoundError:
        print(f"[undersheet] No adapter found for platform '{platform_name}'.")
        print(f"  Expected: {platforms_dir}/{platform_name}.py")
        print(f"  Available: {', '.join(_list_adapters())}")
        sys.exit(1)
    except AttributeError:
        print(f"[undersheet] Adapter file found but missing 'Adapter' class: {platform_name}.py")
        sys.exit(1)


def _list_adapters() -> list[str]:
    platforms_dir = os.path.join(os.path.dirname(__file__), "platforms")
    if not os.path.isdir(platforms_dir):
        return []
    return [
        f[:-3] for f in os.listdir(platforms_dir)
        if f.endswith(".py") and not f.startswith("_")
    ]


def track_thread(state: dict, thread_id: str, comment_count: int, title: str = "", url: str = ""):
    """Register or update a thread in state."""
    state.setdefault("threads", {})[thread_id] = {
        "comment_count": comment_count,
        "title": title,
        "url": url,
        "last_seen": datetime.now(timezone.utc).isoformat(),
    }


def get_unread_threads(adapter: PlatformAdapter, state: dict) -> list[dict]:
    """
    Check all tracked threads for new replies.
    Returns list of { id, title, url, new_replies } for threads with activity.
    """
    thread_ids = list(state.get("threads", {}).keys())
    if not thread_ids:
        return []

    results = []
    try:
        threads = adapter.get_threads(thread_ids)
    except Exception as e:
        print(f"[undersheet] Warning: could not fetch threads: {e}")
        return []

    for thread in threads:
        tid = str(thread.get("id", ""))
        current_count = int(thread.get("comment_count", 0))
        stored = state["threads"].get(tid, {})
        prev_count = int(stored.get("comment_count", 0))
        new_replies = current_count - prev_count
        if new_replies > 0:
            results.append({
                "id": tid,
                "title": thread.get("title", stored.get("title", "")),
                "url": thread.get("url", stored.get("url", "")),
                "new_replies": new_replies,
                "total_comments": current_count,
            })
            # Update state
            state["threads"][tid]["comment_count"] = current_count
            state["threads"][tid]["title"] = thread.get("title", stored.get("title", ""))

    return results


def get_new_feed_posts(adapter: PlatformAdapter, state: dict, min_score: int = 0, limit: int = 5, **kwargs) -> list[dict]:
    """
    Return feed posts not yet seen. Updates seen_post_ids in state.
    """
    seen = set(state.get("seen_post_ids", []))
    try:
        posts = adapter.get_feed(limit=25, **kwargs)
    except Exception as e:
        print(f"[undersheet] Warning: could not fetch feed: {e}")
        return []

    new_posts = []
    for post in posts:
        pid = str(post.get("id", ""))
        if pid in seen:
            continue
        if int(post.get("score", 0)) < min_score:
            continue
        new_posts.append(post)
        seen.add(pid)
        if len(new_posts) >= limit:
            break

    state["seen_post_ids"] = list(seen)
    return new_posts


def heartbeat(platform_name: str, min_score: int = 0, verbose: bool = False):
    """
    Main heartbeat loop:
      1. Load state for this platform
      2. Check tracked threads for new replies
      3. Check feed for new posts
      4. Print summary
      5. Save state
    """
    adapter = load_adapter(platform_name)
    state = load_state(platform_name)

    print(f"[undersheet:{platform_name}] heartbeat @ {datetime.now(timezone.utc).strftime('%H:%M UTC')}")

    # --- New replies in tracked threads ---
    unread = get_unread_threads(adapter, state)
    if unread:
        print(f"\n💬 {len(unread)} thread(s) with new replies:")
        for t in unread:
            print(f"  +{t['new_replies']} — {t['title'] or t['id']} ({t['url']})")
    else:
        print("  No new replies in tracked threads.")

    # --- New feed posts ---
    new_posts = get_new_feed_posts(adapter, state, min_score=min_score)
    if new_posts:
        print(f"\n📰 {len(new_posts)} new post(s) in feed:")
        for p in new_posts:
            score = p.get("score", 0)
            print(f"  [{score}↑] {p.get('title', p.get('id', ''))} — {p.get('url', '')}")
    else:
        print("  No new feed posts.")

    state["last_heartbeat"] = datetime.now(timezone.utc).isoformat()
    save_state(platform_name, state)
    print("\n[undersheet] State saved.")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def status(platform_name: str):
    """Print a quick overview: tracked threads, unseen feed count, last run."""
    state = load_state(platform_name)
    threads = state.get("threads", {})
    seen_count = len(state.get("seen_post_ids", []))
    last_hb = state.get("last_heartbeat", "never")

    print(f"[undersheet:{platform_name}] status")
    print(f"  Last heartbeat : {last_hb}")
    print(f"  Tracked threads: {len(threads)}")
    print(f"  Seen post IDs  : {seen_count}")

    if threads:
        print("\n  Threads:")
        for tid, meta in threads.items():
            title = meta.get("title") or tid
            count = meta.get("comment_count", 0)
            last = meta.get("last_seen", "")[:10]
            url   = meta.get("url", "")
            print(f"    [{count}💬] {title[:60]}  (last seen {last})")
            if url:
                print(f"         {url}")


def digest():
    """Cross-platform summary: activity across ALL configured adapters at a glance.

    Shows per-platform: active threads, new feed posts, last heartbeat time.
    Reads from state files only — no network calls. Instant.
    """
    adapters = _list_adapters()
    now = datetime.now(timezone.utc)
    print(f"\n📊 UnderSheet digest — {now.strftime('%H:%M UTC')}")
    print("─" * 52)

    total_threads = 0
    total_posts   = 0
    live_count    = 0

    for platform in adapters:
        state     = load_state(platform)
        threads   = state.get("threads", {})
        seen      = len(state.get("seen_post_ids", []))
        last_hb   = state.get("last_heartbeat")

        # Calculate time since last heartbeat
        if last_hb:
            try:
                last_dt  = datetime.fromisoformat(last_hb.replace("Z", "+00:00"))
                delta    = now - last_dt
                mins     = int(delta.total_seconds() / 60)
                age      = f"{mins}m ago" if mins < 60 else f"{mins//60}h ago"
                status_icon = "✅"
                live_count += 1
            except Exception:
                age, status_icon = "unknown", "⚠️ "
        else:
            age, status_icon = "never run", "⚙️ "

        # Count threads with new activity
        active_threads = sum(
            1 for meta in threads.values()
            if meta.get("comment_count", 0) > meta.get("last_seen_count", 0)
        )
        total_threads += active_threads
        total_posts   += seen

        thread_str = f"{active_threads} active thread{'s' if active_threads != 1 else ''}"
        post_str   = f"{seen} posts seen"

        print(f"  {status_icon} {platform:<14} {thread_str:<24} {post_str:<18} {age}")

    print("─" * 52)
    print(f"  Total: {total_threads} active threads | {total_posts} posts tracked | {live_count}/{len(adapters)} platforms live\n")


def main():
    parser = argparse.ArgumentParser(
        description="UnderSheet — persistent thread memory for OpenClaw agents"
    )
    parser.add_argument("cmd",
                        choices=["heartbeat", "feed-new", "track", "unread", "status", "platforms", "digest"],
                        help="Command to run")
    parser.add_argument("--platform", "-p", default="moltbook",
                        help="Platform adapter to use (default: moltbook)")
    parser.add_argument("--thread-id", help="Thread ID to track (for 'track' command)")
    parser.add_argument("--min-score", type=int, default=0,
                        help="Minimum score/upvotes for feed posts")
    parser.add_argument("--limit", type=int, default=5,
                        help="Max feed posts to return")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Show extra detail (full URLs, error traces)")
    parser.add_argument("--proxy", metavar="URL",
                        help="Route traffic through HTTP proxy: http://host:port")
    args = parser.parse_args()

    # Apply proxy before any network calls
    proxy = load_proxy_config(override_url=args.proxy)
    apply_proxy(proxy, verbose=args.verbose)

    if args.cmd == "platforms":
        adapters = _list_adapters()
        print("Available platform adapters:")
        for a in adapters:
            print(f"  - {a}")
        return

    if args.cmd == "digest":
        digest()
        return

    if args.cmd == "status":
        status(args.platform)

    elif args.cmd == "heartbeat":
        heartbeat(args.platform, min_score=args.min_score, verbose=args.verbose)

    elif args.cmd == "feed-new":
        adapter = load_adapter(args.platform)
        state = load_state(args.platform)
        posts = get_new_feed_posts(adapter, state, min_score=args.min_score, limit=args.limit)
        save_state(args.platform, state)
        if posts:
            for p in posts:
                score = p.get('score', 0)
                title = p.get('title', p.get('id', ''))
                url   = p.get('url', '')
                print(f"[{score}↑] {title}")
                if args.verbose and url:
                    print(f"     {url}")
        else:
            print("No new posts.")

    elif args.cmd == "track":
        if not args.thread_id:
            print("Error: --thread-id required for 'track'")
            sys.exit(1)
        adapter = load_adapter(args.platform)
        state = load_state(args.platform)
        try:
            threads = adapter.get_threads([args.thread_id])
        except Exception as e:
            print(f"Error fetching thread: {e}")
            if args.verbose:
                import traceback; traceback.print_exc()
            sys.exit(1)
        if threads:
            t = threads[0]
            track_thread(state, args.thread_id, t.get("comment_count", 0),
                         title=t.get("title", ""), url=t.get("url", ""))
            save_state(args.platform, state)
            print(f"Now tracking: {t.get('title', args.thread_id)}")
            print(f"  Comments: {t.get('comment_count', 0)}  |  {t.get('url', '')}")
        else:
            print(f"Error: could not fetch thread '{args.thread_id}' on {args.platform}")
            sys.exit(1)

    elif args.cmd == "unread":
        adapter = load_adapter(args.platform)
        state = load_state(args.platform)
        try:
            unread = get_unread_threads(adapter, state)
        except Exception as e:
            print(f"Error checking threads: {e}")
            if args.verbose:
                import traceback; traceback.print_exc()
            sys.exit(1)
        save_state(args.platform, state)
        if unread:
            for t in unread:
                print(f"+{t['new_replies']} new replies — {t['title'] or t['id']}")
                if args.verbose:
                    print(f"  {t['url']}")
        else:
            print("All threads up to date.")


if __name__ == "__main__":
    main()
