"""
Run all read-only Twitter API actions with rate limiting.
Write/destructive actions are skipped (listed at end).
Run from social_ops: py -m twitter_api.run_all_readonly_tests
"""
import asyncio
import os
import sys
from typing import Any, Callable, Coroutine, Dict, List, Optional, Tuple

# Rate limit: seconds between requests to avoid hitting Twitter limits
RATE_LIMIT_SECONDS = 2.5

# Test fixtures (read-only targets)
TEST_SCREEN_NAME = "pixelagents_app"
TEST_USER_ID = "2017188256090112000"  # pixelagents_app rest_id
TEST_USERNAME_CHECK = "this_username_probably_not_taken_xyz_123"


def _load_dotenv() -> None:
    cwd = os.path.abspath(os.getcwd())
    for path in [os.path.join(cwd, ".env"), os.path.join(cwd, "social_ops", ".env")]:
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        os.environ.setdefault(k.strip(), v.strip())
            return


def _summarize(data: Any, max_len: int = 80) -> str:
    if data is None:
        return "null"
    if isinstance(data, dict):
        keys = list(data.keys())[:5]
        return "{" + ", ".join(str(k) for k in keys) + ("..." if len(data) > 5 else "") + "}"
    if isinstance(data, list):
        return f"[{len(data)} items]"
    s = str(data)
    return s[:max_len] + "..." if len(s) > max_len else s


async def _run_one(
    name: str,
    coro: Callable[[], Coroutine[Any, Any, Any]],
    delay_after: float,
) -> Tuple[str, str, Optional[str]]:
    """Run one action; return (name, status, detail)."""
    try:
        result = await coro()
        await asyncio.sleep(delay_after)
        if result is None:
            return (name, "OK", "no data")
        return (name, "OK", _summarize(result))
    except Exception as e:
        await asyncio.sleep(delay_after)
        return (name, "FAIL", str(e))


async def _run_all(tw: Any) -> None:
    # Build list: (section, action_name, coroutine)
    tasks: List[Tuple[str, str, Callable[[], Coroutine[Any, Any, Any]]]] = []

    # Client-level
    tasks.append(("Client", "fetch_csrf_token", lambda: tw.fetch_csrf_token()))

    # Tweet API (read-only)
    tasks.append((
        "Tweet",
        "get_home_timeline",
        lambda: tw.tweet.get_home_timeline(count=5, include_promoted_content=False),
    ))

    # User API
    tasks.append((
        "User",
        "get_user_by_screen_name",
        lambda: tw.user.get_user_by_screen_name(TEST_SCREEN_NAME),
    ))
    tasks.append((
        "User",
        "get_user_id_by_screen_name",
        lambda: tw.user.get_user_id_by_screen_name(TEST_SCREEN_NAME),
    ))
    tasks.append((
        "User",
        "get_user_by_id",
        lambda: tw.user.get_user_by_id(TEST_USER_ID),
    ))
    tasks.append((
        "User",
        "check_username_availability",
        lambda: tw.user.check_username_availability(TEST_USERNAME_CHECK),
    ))
    tasks.append((
        "User",
        "fetch_user_info(screen_name)",
        lambda: tw.user.fetch_user_info(screen_name=TEST_SCREEN_NAME),
    ))
    tasks.append((
        "User",
        "fetch_user_id",
        lambda: tw.user.fetch_user_id(TEST_SCREEN_NAME),
    ))
    tasks.append((
        "User",
        "get_notifications",
        lambda: tw.user.get_notifications(),
    ))
    tasks.append((
        "User",
        "get_user_tweets",
        lambda: tw.user.get_user_tweets(TEST_USER_ID, count=5),
    ))
    tasks.append((
        "User",
        "get_user_tweets_and_replies",
        lambda: tw.user.get_user_tweets_and_replies(TEST_USER_ID, count=5),
    ))
    tasks.append((
        "User",
        "get_user_media_tweets",
        lambda: tw.user.get_user_media_tweets(TEST_USER_ID, count=5),
    ))
    tasks.append((
        "User",
        "get_user_followings",
        lambda: tw.user.get_user_followings(TEST_USER_ID, count=5),
    ))

    # Subscription API
    tasks.append((
        "Subscription",
        "verify_subscription",
        lambda: tw.subscription.verify_subscription(),
    ))

    # Timeline Service (read-only)
    tasks.append((
        "Timeline",
        "get_home_timeline_data",
        lambda: tw.timeline.get_home_timeline_data(count=5),
    ))

    # Run with rate limiting
    results: List[Tuple[str, str, str, Optional[str]]] = []
    for section, action_name, coro_fn in tasks:
        name = f"{section}.{action_name}"
        _, status, detail = await _run_one(name, coro_fn, RATE_LIMIT_SECONDS)
        results.append((section, action_name, status, detail))

    # Print report
    print("\n" + "=" * 60)
    print("READ-ONLY ACTIONS TEST REPORT")
    print("=" * 60)
    for section, action_name, status, detail in results:
        sym = "OK" if status == "OK" else "FAIL"
        line = f"  [{sym}] {section}.{action_name}"
        if detail and detail != "no data":
            line += f"  -> {detail}"
        print(line)
    ok_count = sum(1 for r in results if r[2] == "OK")
    fail_count = sum(1 for r in results if r[2] == "FAIL")
    print("=" * 60)
    print(f"  Passed: {ok_count}  Failed: {fail_count}  Total: {len(results)}")
    print("=" * 60)

    # Skipped (write) actions
    skipped = [
        "Tweet: create_tweet, delete_tweet, like_tweet, unlike_tweet, retweet, unretweet, reply, quote_tweet, mass_tweet",
        "User: (all read-only exercised)",
        "Direct Message: send_dm, send_dm_to_multiple, send_dm_by_screen_name, send_dm_with_memory",
        "Relationship: follow_user, unfollow_user, block_user, unblock_user, follow_by_screen_name, unfollow_by_screen_name, block_by_screen_name, unblock_by_screen_name",
        "Profile: update_profile_*, update_profile_photo, update_profile_banner, change_username, change_password, delete_phone",
        "Subscription: create_subscription",
    ]
    print("\nSkipped (write/destructive):")
    for s in skipped:
        print(f"  {s}")
    print()


async def main() -> None:
    _load_dotenv()
    auth = os.environ.get("GANCLAW_X_PRIMARY_AUTH_TOKEN") or os.environ.get("PICLAW_TWITTER_AUTH_TOKEN") or ""
    ct0 = os.environ.get("GANCLAW_X_PRIMARY_CT0") or os.environ.get("PICLAW_TWITTER_CT0") or ""
    if not auth or not ct0:
        print("Set GANCLAW_X_PRIMARY_AUTH_TOKEN and GANCLAW_X_PRIMARY_CT0 (e.g. in .env)")
        sys.exit(1)

    from .twitter import Twitter
    tw = Twitter(auth, ct0=ct0)
    await _run_all(tw)


if __name__ == "__main__":
    asyncio.run(main())
