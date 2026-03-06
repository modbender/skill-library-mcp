#!/usr/bin/env python3
"""
Read-only Twitter session verification for Piclaw.
Uses twitter_api in the same extension folder (piclaw_runtime/extensions/twitter_api).
Outputs JSON to stdout only. No credentials printed.
"""
import asyncio
import json
import os
import sys

# This script lives in extensions/twitter_api/; add parent so "from twitter_api.X" works
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
EXTENSIONS_ROOT = os.path.dirname(SCRIPT_DIR)
if EXTENSIONS_ROOT not in sys.path:
    sys.path.insert(0, EXTENSIONS_ROOT)


def extract_user_from_response(data):
    """Extract screen_name and followers_count from GraphQL user response."""
    if not data or not isinstance(data, dict):
        return None, None
    result = None
    if "data" in data:
        d = data["data"]
        if "user" in d and "result" in d["user"]:
            result = d["user"]["result"]
        elif "user_result_by_screen_name" in d and "result" in d["user_result_by_screen_name"]:
            result = d["user_result_by_screen_name"]["result"]
    if not result or not isinstance(result, dict):
        return None, None
    legacy = result.get("legacy")
    if not legacy:
        return None, 0
    return legacy.get("screen_name"), legacy.get("followers_count", 0)


async def main():
    auth_token = (os.environ.get("PICLAW_TWITTER_AUTH_TOKEN") or "").strip()
    ct0 = (os.environ.get("PICLAW_TWITTER_CT0") or "").strip()
    screen_name = (os.environ.get("PICLAW_TWITTER_SCREEN_NAME") or "").strip()

    if not auth_token or not ct0:
        print(json.dumps({"ok": False, "reason": "missing_config"}))
        return
    if not screen_name:
        print(json.dumps({"ok": False, "reason": "missing_screen_name"}))
        return

    try:
        from twitter_api.twitter import Twitter
    except ImportError as e:
        print(json.dumps({"ok": False, "reason": f"import_error:{e!s}"}))
        return

    try:
        client = Twitter(auth_token, ct0)
        raw = await client.user.fetch_user_info(screen_name=screen_name)
        if not raw:
            print(json.dumps({"ok": False, "reason": "no_response"}))
            return
        sn, followers = extract_user_from_response(raw)
        if sn is None and followers is None:
            print(json.dumps({"ok": False, "reason": "parse_error"}))
            return
        out = {
            "ok": True,
            "screen_name": sn or screen_name,
            "followers": followers if isinstance(followers, int) else 0,
        }
        print(json.dumps(out))
    except Exception as e:
        print(json.dumps({"ok": False, "reason": str(e).replace('"', "'")[:200]}))


if __name__ == "__main__":
    asyncio.run(main())
