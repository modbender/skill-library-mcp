#!/usr/bin/env python3
"""
Discord Connect Hub - Health Check Script

Runs comprehensive diagnostics on the Discord bot connection.

Usage:
    ./health-check.py [options]

Options:
    --token TOKEN    Discord bot token (or set DISCORD_BOT_TOKEN env)
    --verbose        Show detailed output
    --json           Output as JSON
"""

import os
import sys
import json
import socket
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from datetime import datetime

DISCORD_API = "https://discord.com/api/v10"
DISCORD_GATEWAY = "wss://gateway.discord.gg"

# Required bot permissions
REQUIRED_PERMISSIONS = {
    "SEND_MESSAGES": 1 << 11,
    "READ_MESSAGE_HISTORY": 1 << 16,
    "ADD_REACTIONS": 1 << 6,
    "EMBED_LINKS": 1 << 14,
    "ATTACH_FILES": 1 << 15,
}


class HealthChecker:
    def __init__(self, token: str, verbose: bool = False):
        self.token = token
        self.verbose = verbose
        self.results = []
        self.user = None

    def log(self, msg: str):
        if self.verbose:
            print(f"  {msg}")

    def add_result(
        self,
        check: str,
        status: str,
        message: str,
        details: dict = None
    ):
        result = {
            "check": check,
            "status": status,  # pass, fail, warn
            "message": message,
        }
        if details:
            result["details"] = details
        self.results.append(result)

    def api_request(self, endpoint: str) -> tuple:
        """Make API request, return (success, data_or_error)"""
        url = f"{DISCORD_API}{endpoint}"
        headers = {
            "Authorization": f"Bot {self.token}",
            "Content-Type": "application/json",
        }
        req = Request(url, headers=headers)

        try:
            with urlopen(req, timeout=10) as resp:
                return True, json.loads(resp.read().decode())
        except HTTPError as e:
            try:
                error = json.loads(e.read().decode())
                return False, error.get("message", str(e))
            except:
                return False, str(e)
        except URLError as e:
            return False, f"Network error: {e.reason}"
        except Exception as e:
            return False, str(e)

    def check_token(self) -> bool:
        """Validate bot token"""
        self.log("Checking token validity...")

        if not self.token:
            self.add_result("token", "fail", "No token provided")
            return False

        if len(self.token) < 50:
            self.add_result("token", "fail", "Token appears too short")
            return False

        success, data = self.api_request("/users/@me")

        if success:
            self.user = data
            if data.get("bot"):
                self.add_result(
                    "token",
                    "pass",
                    f"Valid bot token for {data['username']}",
                    {"user_id": data["id"], "username": data["username"]}
                )
                return True
            else:
                self.add_result(
                    "token",
                    "fail",
                    "This is a user token, not a bot token"
                )
                return False
        else:
            self.add_result("token", "fail", f"Invalid token: {data}")
            return False

    def check_gateway(self) -> bool:
        """Check Discord gateway connectivity"""
        self.log("Checking gateway connectivity...")

        success, data = self.api_request("/gateway/bot")

        if success:
            self.add_result(
                "gateway",
                "pass",
                "Gateway accessible",
                {
                    "url": data.get("url"),
                    "shards": data.get("shards"),
                    "session_start_limit": data.get("session_start_limit", {})
                }
            )
            return True
        else:
            self.add_result("gateway", "fail", f"Gateway check failed: {data}")
            return False

    def check_guilds(self) -> bool:
        """Check bot guild membership"""
        self.log("Checking guild membership...")

        success, data = self.api_request("/users/@me/guilds")

        if success:
            guild_count = len(data)
            if guild_count > 0:
                self.add_result(
                    "guilds",
                    "pass",
                    f"Bot is in {guild_count} server(s)",
                    {"count": guild_count, "guilds": [g["name"] for g in data[:5]]}
                )
                return True
            else:
                self.add_result(
                    "guilds",
                    "warn",
                    "Bot is not in any servers. Use invite URL to add it."
                )
                return True  # Not a failure, just a warning
        else:
            self.add_result("guilds", "fail", f"Could not fetch guilds: {data}")
            return False

    def check_application(self) -> bool:
        """Check application settings"""
        self.log("Checking application settings...")

        success, data = self.api_request("/oauth2/applications/@me")

        if success:
            flags = data.get("flags", 0)

            # Check for Message Content Intent (bit 15)
            has_message_content = bool(flags & (1 << 15))

            if has_message_content:
                self.add_result(
                    "intents",
                    "pass",
                    "Message Content Intent is enabled",
                    {"application_id": data.get("id")}
                )
            else:
                self.add_result(
                    "intents",
                    "warn",
                    "Message Content Intent may not be enabled. "
                    "Enable it in Discord Developer Portal > Bot > Privileged Gateway Intents"
                )
            return True
        else:
            # This endpoint might not be available for all bots
            self.add_result(
                "intents",
                "warn",
                "Could not verify intents. Ensure Message Content Intent is enabled."
            )
            return True

    def check_network(self) -> bool:
        """Check basic network connectivity"""
        self.log("Checking network connectivity...")

        try:
            socket.create_connection(("discord.com", 443), timeout=5)
            self.add_result("network", "pass", "Network connectivity OK")
            return True
        except Exception as e:
            self.add_result("network", "fail", f"Network error: {e}")
            return False

    def run_all_checks(self) -> dict:
        """Run all health checks"""
        checks = [
            self.check_network,
            self.check_token,
            self.check_gateway,
            self.check_guilds,
            self.check_application,
        ]

        for check in checks:
            try:
                check()
            except Exception as e:
                self.add_result(check.__name__, "fail", f"Check failed: {e}")

        # Summary
        passed = sum(1 for r in self.results if r["status"] == "pass")
        failed = sum(1 for r in self.results if r["status"] == "fail")
        warned = sum(1 for r in self.results if r["status"] == "warn")

        return {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "summary": {
                "passed": passed,
                "failed": failed,
                "warnings": warned,
                "healthy": failed == 0,
            },
            "checks": self.results,
            "user": self.user,
        }


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Discord bot health check")
    parser.add_argument("--token", help="Discord bot token")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    token = args.token or os.environ.get("DISCORD_BOT_TOKEN", "")

    if not token:
        print("Error: No token provided")
        print("Usage: ./health-check.py --token YOUR_TOKEN")
        print("   or: DISCORD_BOT_TOKEN=xxx ./health-check.py")
        sys.exit(1)

    checker = HealthChecker(token, verbose=args.verbose)
    results = checker.run_all_checks()

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print()
        print("🎮 Discord Bot Health Check")
        print("=" * 40)
        print()

        for check in results["checks"]:
            status_icon = {
                "pass": "✅",
                "fail": "❌",
                "warn": "⚠️",
            }.get(check["status"], "?")

            print(f"{status_icon} {check['check'].upper()}: {check['message']}")

        print()
        print("-" * 40)
        summary = results["summary"]
        print(f"Passed: {summary['passed']} | "
              f"Failed: {summary['failed']} | "
              f"Warnings: {summary['warnings']}")

        if summary["healthy"]:
            print("✨ Bot is healthy!")
        else:
            print("❌ Issues detected - see above")
            sys.exit(1)


if __name__ == "__main__":
    main()
