"""
Post one test tweet from each configured account with rate limiting.
Run from social_ops: py -m twitter_api.post_all_accounts
"""
import asyncio
import os
import sys
from datetime import datetime

# Seconds to wait between each account's post to avoid rate limits
RATE_LIMIT_SECONDS = 45


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


# One proxy for all: set GANCLAW_X_PROXY_URL in .env (optional)
PROXY_URL_ENV = "GANCLAW_X_PROXY_URL"

# (label, auth_env, ct0_env) for each account
ACCOUNTS = [
    ("primary", "GANCLAW_X_PRIMARY_AUTH_TOKEN", "GANCLAW_X_PRIMARY_CT0"),
    ("pixelagents_app", "GANCLAW_X_PIXELAGENTS_APP_AUTH_TOKEN", "GANCLAW_X_PIXELAGENTS_APP_CT0"),
    ("alien_pxlagents", "GANCLAW_X_ALIEN_PXLAGENTS_AUTH_TOKEN", "GANCLAW_X_ALIEN_PXLAGENTS_CT0"),
    ("piclaw_pxlagent", "GANCLAW_X_PICLAW_PXLAGENT_AUTH_TOKEN", "GANCLAW_X_PICLAW_PXLAGENT_CT0"),
]


async def _post_one(label: str, auth: str, ct0: str, proxy_url: str = ""):
    from .core.client import TwitterAPIClient
    from .api.tweet import TweetAPI

    if not auth or not ct0:
        return (label, False, "missing auth or ct0 in env")
    try:
        client = TwitterAPIClient(auth, ct0=ct0, proxy_url=proxy_url or None)
        tweet_api = TweetAPI(client)
        text = f"Test post from @{label} — {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}"
        result = await tweet_api.create_tweet(text)
        if not result:
            return (label, False, "empty response")
        data = result.get("data", {}) or {}
        ct = data.get("create_tweet") or {}
        tweet_results = ct.get("tweet_results") or ct.get("CreateTweet", {}).get("tweet_results")
        if tweet_results:
            return (label, True, "posted")
        errs = result.get("errors", []) or ct.get("errors", [])
        if errs:
            e = errs[0]
            msg = e.get("message") or e.get("extensions", {}).get("message") or str(e)
            return (label, False, msg)
        import json
        raw = json.dumps(result, default=str)[:400]
        return (label, False, "no tweet in response: " + raw)
    except Exception as e:
        return (label, False, str(e))


async def main() -> None:
    _load_dotenv()
    print("Posting one test tweet per account with", RATE_LIMIT_SECONDS, "s delay between posts.\n")
    proxy_url = (os.environ.get(PROXY_URL_ENV, "").strip() or None)
    for i, (label, auth_env, ct0_env) in enumerate(ACCOUNTS):
        auth = os.environ.get(auth_env, "").strip()
        ct0 = os.environ.get(ct0_env, "").strip()
        status, ok, detail = await _post_one(label, auth, ct0, proxy_url or "")
        sym = "OK" if ok else "FAIL"
        print(f"  [{sym}] {status}: {detail}")
        if i < len(ACCOUNTS) - 1:
            print(f"  Waiting {RATE_LIMIT_SECONDS}s before next account...")
            await asyncio.sleep(RATE_LIMIT_SECONDS)
    print("\nDone.")


if __name__ == "__main__":
    asyncio.run(main())
