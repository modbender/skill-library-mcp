#!/usr/bin/env python3
"""
x-cli auth — Manage X/Twitter authentication.

Usage:
  python x_auth.py check              Check auth status
  python x_auth.py whoami             Show current user
  python x_auth.py login              Login with config credentials
  python x_auth.py login --username USER --password PASS
"""

import argparse
import json
import sys

from x_utils import load_config, get_client, run, SKILL_DIR


async def cmd_check(args):
    config = load_config()
    cookies_path = SKILL_DIR / config.get("cookies_file", "cookies.json")
    proxy = config.get("proxy")

    print("𝕏 x-cli auth check")
    print("─" * 40)
    print(f"{'✅' if cookies_path.exists() else '❌'} Cookies: {cookies_path.name} {'(found)' if cookies_path.exists() else '(missing)'}")
    print(f"{'✅' if proxy else '⚪'} Proxy: {proxy.split('@')[-1] if proxy else 'none'}")
    print(f"{'✅' if config.get('x_username') else '⚪'} Username: {'configured' if config.get('x_username') else 'not set'}")

    if cookies_path.exists():
        try:
            client = await get_client(config)
            user = await client.user()
            print(f"\n✅ Authenticated as @{user.screen_name} ({user.name})")
        except Exception as e:
            print(f"\n⚠️ Cookies exist but auth failed: {e}")
    else:
        print("\n❌ Not authenticated. Run: python x_auth.py login")


async def cmd_whoami(args):
    client = await get_client()
    user = await client.user()
    if args.json:
        print(json.dumps({
            "id": user.id,
            "username": user.screen_name,
            "name": user.name,
            "followers": getattr(user, "followers_count", 0),
            "following": getattr(user, "following_count", 0),
        }, ensure_ascii=False))
    else:
        print(f"@{user.screen_name} ({user.name})")
        print(f"Followers: {getattr(user, 'followers_count', '?')} | Following: {getattr(user, 'following_count', '?')}")


async def cmd_login(args):
    config = load_config()

    username = args.username or config.get("x_username")
    password = args.password or config.get("x_password")
    email = args.email or config.get("x_email", username)

    if not username or not password:
        print("❌ Username and password required. Use --username/--password or set in config.json", file=sys.stderr)
        sys.exit(1)

    from twikit import Client
    proxy = config.get("proxy")
    lang = config.get("language", "en-US")
    client = Client(lang, proxy=proxy) if proxy else Client(lang)

    cookies_path = SKILL_DIR / config.get("cookies_file", "cookies.json")

    print(f"🔐 Logging in as {username}...")
    await client.login(
        auth_info_1=username,
        auth_info_2=email,
        password=password,
        cookies_file=str(cookies_path)
    )

    user = await client.user()
    print(f"✅ Logged in as @{user.screen_name}")
    print(f"🍪 Cookies saved to {cookies_path.name}")


def main():
    parser = argparse.ArgumentParser(description="x-cli auth — Manage X/Twitter auth")
    parser.add_argument("--json", action="store_true", help="JSON output")

    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("check", help="Check auth status")
    sub.add_parser("whoami", help="Show current user")

    p_login = sub.add_parser("login", help="Login to X")
    p_login.add_argument("--username", help="X username")
    p_login.add_argument("--password", help="X password")
    p_login.add_argument("--email", help="X email (defaults to username)")

    args = parser.parse_args()

    if args.command == "check":
        run(cmd_check(args))
    elif args.command == "whoami":
        run(cmd_whoami(args))
    elif args.command == "login":
        run(cmd_login(args))


if __name__ == "__main__":
    main()
