#!/usr/bin/env python3
"""
Test a Discord bot token without starting the full bot.
Usage: ./test-token.py <token>
       ./test-token.py  # reads from DISCORD_BOT_TOKEN env
"""

import os
import sys
import json
from urllib.request import Request, urlopen
from urllib.error import HTTPError

DISCORD_API = "https://discord.com/api/v10"


def test_token(token: str) -> dict:
    """Test a Discord bot token and return user info."""
    url = f"{DISCORD_API}/users/@me"
    headers = {
        "Authorization": f"Bot {token}",
        "Content-Type": "application/json",
    }

    req = Request(url, headers=headers)

    try:
        with urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            return {
                "valid": True,
                "user": {
                    "id": data["id"],
                    "username": data["username"],
                    "discriminator": data.get("discriminator", "0"),
                    "bot": data.get("bot", False),
                },
            }
    except HTTPError as e:
        error_body = e.read().decode() if e.fp else str(e)
        try:
            error_json = json.loads(error_body)
            message = error_json.get("message", str(e))
        except:
            message = str(e)
        return {"valid": False, "error": message}


def get_guilds(token: str) -> list:
    """Get list of guilds the bot is in."""
    url = f"{DISCORD_API}/users/@me/guilds"
    headers = {
        "Authorization": f"Bot {token}",
        "Content-Type": "application/json",
    }

    req = Request(url, headers=headers)

    try:
        with urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except HTTPError:
        return []


def main():
    # Get token from args or environment
    if len(sys.argv) > 1:
        token = sys.argv[1]
    else:
        token = os.environ.get("DISCORD_BOT_TOKEN", "")

    if not token:
        print("Usage: ./test-token.py <token>")
        print("   or: DISCORD_BOT_TOKEN=xxx ./test-token.py")
        sys.exit(1)

    print("Testing Discord bot token...")
    print(f"Token: ****{token[-4:]}")
    print()

    result = test_token(token)

    if result["valid"]:
        user = result["user"]
        print("✅ Token is valid!")
        print(f"   Username: {user['username']}")
        print(f"   User ID:  {user['id']}")
        print(f"   Is Bot:   {user['bot']}")

        if not user["bot"]:
            print()
            print("⚠️  Warning: This appears to be a user token, not a bot token.")
            print("   Bot tokens are required for Discord bots.")
            sys.exit(1)

        # Get guilds
        print()
        guilds = get_guilds(token)
        if guilds:
            print(f"📋 Bot is in {len(guilds)} server(s):")
            for guild in guilds[:10]:  # Show first 10
                print(f"   • {guild['name']} ({guild['id']})")
            if len(guilds) > 10:
                print(f"   ... and {len(guilds) - 10} more")
        else:
            print("📋 Bot is not in any servers yet.")
            print("   Use the invite URL to add it to a server.")

    else:
        print("❌ Token is invalid!")
        print(f"   Error: {result['error']}")
        sys.exit(1)


if __name__ == "__main__":
    main()
