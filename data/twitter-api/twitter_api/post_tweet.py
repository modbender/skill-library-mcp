"""
Post a single tweet from a chosen account.
Usage (from social_ops): py -m twitter_api.post_tweet <account> <tweet_text>
Example: py -m twitter_api.post_tweet alien_pxlagents "Hello from Sentinel"
Twitter limit: 280 characters.
"""
import asyncio
import os
import sys

# One proxy for all accounts (optional): set GANCLAW_X_PROXY_URL in .env
PROXY_URL_ENV = "GANCLAW_X_PROXY_URL"

# (auth_env, ct0_env)
ACCOUNTS = {
    "primary": ("GANCLAW_X_PRIMARY_AUTH_TOKEN", "GANCLAW_X_PRIMARY_CT0"),
    "pixelagents_app": ("GANCLAW_X_PIXELAGENTS_APP_AUTH_TOKEN", "GANCLAW_X_PIXELAGENTS_APP_CT0"),
    "alien_pxlagents": ("GANCLAW_X_ALIEN_PXLAGENTS_AUTH_TOKEN", "GANCLAW_X_ALIEN_PXLAGENTS_CT0"),
    "piclaw_pxlagent": ("GANCLAW_X_PICLAW_PXLAGENT_AUTH_TOKEN", "GANCLAW_X_PICLAW_PXLAGENT_CT0"),
}


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


async def post_tweet(account: str, text: str) -> tuple[bool, str]:
    row = ACCOUNTS.get(account)
    if not row:
        return False, f"Unknown account: {account}. Use one of: {list(ACCOUNTS)}"
    auth_env, ct0_env = row[0], row[1]
    auth = os.environ.get(auth_env, "").strip()
    ct0 = os.environ.get(ct0_env, "").strip()
    if not auth or not ct0:
        return False, f"Missing {auth_env} or {ct0_env} in .env"
    proxy_url = (os.environ.get(PROXY_URL_ENV, "").strip() or None)
    if proxy_url:
        print(f"(Using proxy: {PROXY_URL_ENV})")
    else:
        print("(No proxy set — if you get (226), set GANCLAW_X_PROXY_URL in .env)")
    from .core.client import TwitterAPIClient
    from .api.tweet import TweetAPI
    try:
        client = TwitterAPIClient(auth, ct0=ct0, proxy_url=proxy_url or None)
        api = TweetAPI(client)
        result = await api.create_tweet(text)
        if not result:
            return False, "Empty response"
        data = result.get("data", {}) or {}
        ct = data.get("create_tweet") or {}
        tweet_results = ct.get("tweet_results") or ct.get("CreateTweet", {}).get("tweet_results")
        if tweet_results:
            return True, "Posted"
        errs = result.get("errors", []) or ct.get("errors", [])
        if errs:
            e = errs[0]
            msg = e.get("message") or (e.get("extensions") or {}).get("message") or str(e)
            if "226" in msg or "automated" in msg.lower():
                msg += " — Try setting GANCLAW_X_PROXY_URL in .env (same network as account)."
            return False, msg
        import json
        return False, "No tweet in response: " + json.dumps(result, default=str)[:300]
    except Exception as e:
        return False, str(e)


def main() -> None:
    _load_dotenv()
    if len(sys.argv) < 3:
        print("Usage: py -m twitter_api.post_tweet <account> <tweet_text>")
        print("Accounts:", list(ACCOUNTS))
        sys.exit(1)
    account = sys.argv[1].strip().lower()
    text = " ".join(sys.argv[2:]).strip()
    if not text:
        print("Tweet text is empty.")
        sys.exit(1)
    ok, msg = asyncio.run(post_tweet(account, text))
    if ok:
        print("OK:", msg)
    else:
        print("FAIL:", msg)
        sys.exit(1)


if __name__ == "__main__":
    main()
