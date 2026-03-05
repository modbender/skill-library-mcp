#!/usr/bin/env python3
"""
UnderSheet — 60-second verification script.
Confirms the core engine + installed adapters work correctly.

Usage:
    python3 verify.py
    python3 verify.py --platform hackernews   # test a specific adapter
"""

import argparse
import json
import os
import sys
import traceback

sys.path.insert(0, os.path.dirname(__file__))
from undersheet import (
    load_state, save_state, track_thread,
    get_unread_threads, get_new_feed_posts,
    load_adapter, _list_adapters,
)

PASS = "✅"
FAIL = "❌"
SKIP = "⏭️ "

results = []

def test(name: str, fn):
    try:
        result = fn()
        status = PASS if result else FAIL
        results.append((status, name, None))
        print(f"{status} {name}")
        return result
    except Exception as e:
        results.append((FAIL, name, str(e)))
        print(f"{FAIL} {name}: {e}")
        if os.environ.get("VERBOSE"):
            traceback.print_exc()
        return None

def skip(name: str, reason: str):
    results.append((SKIP, name, reason))
    print(f"{SKIP} {name} ({reason})")


# ---------------------------------------------------------------------------
# Core engine tests (no network, no credentials)
# ---------------------------------------------------------------------------

print("\n── Core engine ──────────────────────────────────")

def _test_state_roundtrip():
    save_state("_test", {"threads": {"abc": {"comment_count": 5}}, "seen_post_ids": []})
    s = load_state("_test")
    # Cleanup
    import glob
    for f in glob.glob(os.path.expanduser("~/.config/undersheet/_test_state.json")):
        os.remove(f)
    return s["threads"]["abc"]["comment_count"] == 5

test("State save/load roundtrip", _test_state_roundtrip)

def _test_track_thread():
    state = {"threads": {}, "seen_post_ids": []}
    track_thread(state, "thread_1", 7, title="Test Thread", url="https://example.com/t/1")
    return state["threads"]["thread_1"]["comment_count"] == 7

test("track_thread() registers correctly", _test_track_thread)

def _test_feed_cursor():
    state = {"threads": {}, "seen_post_ids": ["a", "b"]}

    class FakeAdapter:
        def get_feed(self, limit=25, **kw):
            return [
                {"id": "a", "title": "Old", "url": "", "score": 10, "created_at": ""},
                {"id": "c", "title": "New", "url": "", "score": 20, "created_at": ""},
            ]
        def get_threads(self, ids): return []

    posts = get_new_feed_posts(FakeAdapter(), state)
    return len(posts) == 1 and posts[0]["id"] == "c"

test("Feed cursor filters seen posts", _test_feed_cursor)

def _test_unread_detection():
    state = {
        "threads": {"t1": {"comment_count": 3, "title": "Thing", "url": ""}},
        "seen_post_ids": []
    }
    class FakeAdapter:
        def get_threads(self, ids):
            return [{"id": "t1", "title": "Thing", "url": "", "comment_count": 7, "score": 0}]

    unread = get_unread_threads(FakeAdapter(), state)
    return len(unread) == 1 and unread[0]["new_replies"] == 4

test("Unread thread detection (+4 new replies)", _test_unread_detection)

def _test_adapter_discovery():
    adapters = _list_adapters()
    return len(adapters) > 0

test("Adapter discovery finds installed platforms", _test_adapter_discovery)

def _test_proxy_config_load():
    from undersheet import load_proxy_config
    # Should return empty when nothing configured (env may have proxy set in CI)
    p = load_proxy_config(override_url="http://127.0.0.1:8080")
    return p["url"] == "http://127.0.0.1:8080" and p["source"] == "flag"

def _test_proxy_apply_http():
    import os
    from undersheet import apply_proxy
    for k in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY"):
        os.environ.pop(k, None)
    apply_proxy({"url": "http://verify-test:9999", "source": "test"})
    result = os.environ.get("HTTP_PROXY") == "http://verify-test:9999"
    for k in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY"):
        os.environ.pop(k, None)
    return result

test("Proxy config: CLI flag override", _test_proxy_config_load)
test("Proxy apply: HTTP sets env vars", _test_proxy_apply_http)


# ---------------------------------------------------------------------------
# Platform-specific tests (network + credentials)
# ---------------------------------------------------------------------------

def _test_platform(platform: str):
    print(f"\n── Platform: {platform} ─────────────────────────────")

    try:
        adapter = load_adapter(platform)
    except SystemExit:
        skip(f"{platform}: load adapter", "adapter file not found")
        return
    except Exception as e:
        skip(f"{platform}: load adapter", f"init error: {e}")
        return

    try:
        adapter.get_credentials()
        creds_ok = True
    except Exception as e:
        skip(f"{platform}: credentials", str(e))
        creds_ok = False

    if not creds_ok:
        return

    def _test_feed():
        posts = adapter.get_feed(limit=3)
        if isinstance(posts, str):
            raise Exception(posts)
        return isinstance(posts, list) and len(posts) > 0

    def _test_feed_fields():
        posts = adapter.get_feed(limit=1)
        if isinstance(posts, str):
            raise Exception(posts)
        if not posts:
            return False
        p = posts[0]
        return all(k in p for k in ("id", "title", "url"))

    try:
        test(f"{platform}: get_feed() returns posts", _test_feed)
        test(f"{platform}: feed posts have required fields (id/title/url)", _test_feed_fields)
    except Exception as e:
        if "credentials" in str(e).lower() or "not configured" in str(e).lower():
            skip(f"{platform}: feed tests", "credentials not configured")
        else:
            raise


parser = argparse.ArgumentParser()
parser.add_argument("--platform", "-p", help="Test a specific platform adapter")
args = parser.parse_args()

if args.platform:
    _test_platform(args.platform)
else:
    for p in _list_adapters():
        _test_platform(p)

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

print("\n── Summary ──────────────────────────────────────")
passed  = sum(1 for r in results if r[0] == PASS)
failed  = sum(1 for r in results if r[0] == FAIL)
skipped = sum(1 for r in results if r[0] == SKIP)
total   = passed + failed

print(f"{passed}/{total} tests passed  |  {skipped} skipped")

if failed:
    print("\nFailing tests:")
    for status, name, err in results:
        if status == FAIL:
            print(f"  {FAIL} {name}" + (f": {err}" if err else ""))
    print("\nRun with VERBOSE=1 python3 verify.py for full tracebacks.")
    sys.exit(1)
else:
    print("\nAll good. UnderSheet is working correctly.")
