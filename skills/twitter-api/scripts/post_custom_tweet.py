import os
import sys
import asyncio

from twitter_api.core.client import TwitterAPIClient
from twitter_api.api.tweet import TweetAPI

# Map logical account labels to env variable names.
# Rename or extend as needed for your workspace.
ACCOUNT_ENV = {
    "account_a": ("ACCOUNT_A_AUTH_TOKEN", "ACCOUNT_A_CT0"),
    "account_b": ("ACCOUNT_B_AUTH_TOKEN", "ACCOUNT_B_CT0"),
    "account_c": ("ACCOUNT_C_AUTH_TOKEN", "ACCOUNT_C_CT0"),
    "account_d": ("ACCOUNT_D_AUTH_TOKEN", "ACCOUNT_D_CT0"),
}


def load_env():
    cwd = os.path.abspath(os.getcwd())
    for path in [os.path.join(cwd, ".env"), os.path.join(cwd, "social_ops", ".env")]:
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        os.environ.setdefault(k.strip(), v.strip())
            break


async def post(account: str, text: str):
    if account not in ACCOUNT_ENV:
        raise SystemExit(f"Unknown account: {account}")
    auth_env, ct0_env = ACCOUNT_ENV[account]
    auth = os.environ.get(auth_env, "").strip()
    ct0 = os.environ.get(ct0_env, "").strip()
    if not auth or not ct0:
        raise SystemExit(f"Missing auth or ct0 env for account {account}")
    client = TwitterAPIClient(auth, ct0=ct0)
    api = TweetAPI(client)
    resp = await api.create_tweet(text)
    if not resp:
        raise SystemExit("Empty response from API")
    data = resp.get("data", {})
    ct = data.get("create_tweet") or {}
    tweet_results = ct.get("tweet_results") or {}
    result = tweet_results.get("result") if isinstance(tweet_results, dict) else {}
    tweet_id = result.get("rest_id") if isinstance(result, dict) else None
    print(f"Posted tweet for {account}, id={tweet_id}")


def main():
    if len(sys.argv) < 3:
        print("Usage: py post_custom_tweet.py <account> <tweet text>")
        raise SystemExit(1)
    account = sys.argv[1]
    text = " ".join(sys.argv[2:])
    load_env()
    asyncio.run(post(account, text))


if __name__ == "__main__":
    main()
