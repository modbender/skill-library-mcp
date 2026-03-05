import os
import sys
import asyncio

from twitter_api.core.client import TwitterAPIClient
from twitter_api.api.user import UserAPI
from twitter_api.api.relationship import RelationshipAPI

# Map logical account labels to env variable names.
# Adjust or extend the mapping for your workspace.
ACCOUNT_ENV = {
    "account_a": ("ACCOUNT_A_AUTH_TOKEN", "ACCOUNT_A_CT0"),
    "account_b": ("ACCOUNT_B_AUTH_TOKEN", "ACCOUNT_B_CT0"),
    "account_c": ("ACCOUNT_C_AUTH_TOKEN", "ACCOUNT_C_CT0"),
    "account_d": ("ACCOUNT_D_AUTH_TOKEN", "ACCOUNT_D_CT0"),
}


def load_env() -> None:
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


def get_client(account: str) -> TwitterAPIClient:
    if account not in ACCOUNT_ENV:
        raise SystemExit(f"Unknown account: {account}")
    auth_env, ct0_env = ACCOUNT_ENV[account]
    auth = os.environ.get(auth_env, "").strip()
    ct0 = os.environ.get(ct0_env, "").strip()
    if not auth or not ct0:
        raise SystemExit(f"Missing auth or ct0 env for {account}")
    return TwitterAPIClient(auth, ct0=ct0)


async def follow(account: str, target: str) -> str:
    client = get_client(account)
    user_api = UserAPI(client)
    rel_api = RelationshipAPI(client)
    user_id = await user_api.get_user_id_by_screen_name(target)
    if not user_id:
        return f"{account}: failed to resolve @{target}"
    resp = await rel_api.follow_user(user_id)
    if isinstance(resp, dict):
        if resp.get("following") or resp.get("result") == "following":
            return f"{account}: now following @{target}"
        if resp.get("errors"):
            return f"{account}: {resp.get('errors')}"
    return f"{account}: follow request sent"


def main():
    if len(sys.argv) < 2:
        print("Usage: py follow_account.py <screen_name>")
        raise SystemExit(1)
    target = sys.argv[1].lstrip("@")
    load_env()
    async def runner():
        for account in ACCOUNT_ENV.keys():
            try:
                msg = await follow(account, target)
                print(msg)
            except Exception as exc:
                print(f"{account}: error {exc}")
    asyncio.run(runner())


if __name__ == "__main__":
    main()
