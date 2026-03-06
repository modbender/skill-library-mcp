#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "tweepy>=4.14.0",
# ]
# ///
"""X (Twitter) skill setup — credential import, validation, and budget config."""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import tweepy

sys.path.insert(0, str(Path(__file__).resolve().parent))
from x_common import CONFIG_DIR, CONFIG_PATH, DATA_DIR, USAGE_PATH, VERSION

ENV_PATH = Path.home() / ".openclaw" / ".env"

BUDGET_TIERS = {
    "lite": {"daily_budget": 0.03, "desc": "Morning brief only, ~$0.50/mo"},
    "standard": {"daily_budget": 0.10, "desc": "Brief + a few checks/day, ~$1.50/mo"},
    "intense": {"daily_budget": 0.25, "desc": "Frequent checks, hourly monitoring, ~$5/mo"},
}

BUDGET_MODES = {
    "guarded": "Warn at 50/80/100%, block at limit (default)",
    "relaxed": "Warn at 50/80/100%, never block",
    "unlimited": "No warnings, no blocks",
}


def load_env(path: Path) -> dict[str, str]:
    """Parse a simple KEY=VALUE .env file."""
    env = {}
    if not path.exists():
        return env
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip("'\"")
    return env


def validate_credentials(api_key: str, api_secret: str, access_token: str,
                         access_secret: str, bearer_token: str) -> dict | None:
    """Validate credentials by calling get_me(). Returns user data or None."""
    try:
        client = tweepy.Client(
            bearer_token=bearer_token,
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_secret,
            wait_on_rate_limit=True,
        )
        resp = client.get_me(user_fields=["public_metrics", "created_at", "description"])
        if resp.data:
            return {
                "user_id": str(resp.data.id),
                "username": resp.data.username,
                "name": resp.data.name,
                "followers": resp.data.public_metrics["followers_count"],
                "tweets": resp.data.public_metrics["tweet_count"],
            }
    except tweepy.errors.Unauthorized:
        print("Error: Invalid credentials (401 Unauthorized)")
    except tweepy.errors.Forbidden as e:
        print(f"Error: Access forbidden — {e}")
    except Exception as e:
        print(f"Error: {e}")
    return None


def cmd_setup(args):
    """Interactive setup flow."""
    if CONFIG_PATH.exists() and not args.reconfig:
        config = json.loads(CONFIG_PATH.read_text())
        print(f"Already configured for @{config.get('handle', '?')}")
        print(f"Run with --reconfig to reconfigure, or --check to validate.")
        return

    # Try to import from .env
    env = load_env(ENV_PATH)
    if all(k in env for k in ["X_API_KEY", "X_API_SECRET", "X_ACCESS_TOKEN", "X_ACCESS_SECRET"]):
        print(f"Found X API credentials in {ENV_PATH}")
        api_key = env["X_API_KEY"]
        api_secret = env["X_API_SECRET"]
        access_token = env["X_ACCESS_TOKEN"]
        access_secret = env["X_ACCESS_SECRET"]
        bearer_token = env.get("X_BEARER_TOKEN", "")
    else:
        print("No .env credentials found. Enter your X API keys:")
        print("(Get them at https://developer.x.com)")
        print()
        api_key = input("API Key (Consumer Key): ").strip()
        api_secret = input("API Secret (Consumer Secret): ").strip()
        access_token = input("Access Token: ").strip()
        access_secret = input("Access Token Secret: ").strip()
        bearer_token = input("Bearer Token (optional, press Enter to skip): ").strip()

    # Get handle
    handle = args.handle
    if not handle:
        handle = input("Your X handle (without @): ").strip().lstrip("@")

    print("\nValidating credentials...")
    user = validate_credentials(api_key, api_secret, access_token, access_secret, bearer_token)
    if not user:
        print("Setup failed. Check your credentials and try again.")
        sys.exit(1)

    print(f"Authenticated as @{user['username']} ({user['name']})")
    print(f"  Followers: {user['followers']:,}")
    print(f"  Tweets: {user['tweets']:,}")

    if handle and handle.lower() != user["username"].lower():
        print(f"\nWarning: You entered @{handle} but authenticated as @{user['username']}")
        handle = user["username"]

    # Budget tier
    tier = args.tier or "standard"
    if not args.tier and not args.reconfig:
        print("\nBudget tier (controls daily API spend limit):")
        for name, info in BUDGET_TIERS.items():
            marker = " (default)" if name == "standard" else ""
            print(f"  {name}: {info['desc']}{marker}")
        tier_input = input("Choose tier [standard]: ").strip().lower()
        if tier_input in BUDGET_TIERS:
            tier = tier_input

    budget = BUDGET_TIERS[tier]

    # Save config
    config = {
        "handle": user["username"],
        "user_id": user["user_id"],
        "api_key": api_key,
        "api_secret": api_secret,
        "access_token": access_token,
        "access_secret": access_secret,
        "bearer_token": bearer_token,
        "tier": tier,
        "daily_budget": budget["daily_budget"],
        "budget_mode": "guarded",
        "setup_at": datetime.now(timezone.utc).isoformat(),
        "last_timeline_id": None,
        "last_mention_id": None,
        "follower_history": [],
    }

    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(config, indent=2))
    os.chmod(CONFIG_PATH, 0o600)

    print(f"\nSetup complete!")
    print(f"  Config: {CONFIG_PATH}")
    print(f"  Tier: {tier} (${budget['daily_budget']}/day cap)")
    print(f"  Handle: @{user['username']}")

    # First-run sizing info
    if user["tweets"] > 100:
        est_cost = (user["tweets"] / 100) * 0.005
        print(f"\n  Note: You have {user['tweets']:,} tweets.")
        print(f"  Pulling all would cost ~${est_cost:.2f}.")
        print(f"  The skill pulls incrementally (newest first), so daily use is ~$0.02/day.")


def cmd_spend_report(args):
    """Show weekly spend summary."""
    if not CONFIG_PATH.exists():
        print(f"No config found. Run setup first.")
        sys.exit(1)

    config = json.loads(CONFIG_PATH.read_text())
    usage = {}
    if USAGE_PATH.exists():
        usage = json.loads(USAGE_PATH.read_text())
    if not usage:
        print("No usage data yet. Make some API calls first.")
        return

    today = datetime.now(timezone.utc)
    daily_budget = config.get("daily_budget", 0.10)
    mode = config.get("budget_mode", "guarded")

    # Determine period
    days = args.days if args.days else 7
    print(f"Spend Report — last {days} days")
    print("=" * 45)

    total_cost = 0.0
    total_tweet_reads = 0
    total_user_reads = 0
    total_posts_created = 0
    day_count = 0

    for i in range(days):
        day = (today - timedelta(days=i)).strftime("%Y-%m-%d")
        if day in usage:
            d = usage[day]
            cost = d.get("est_cost", 0.0)
            tr = d.get("tweet_reads", 0)
            ur = d.get("user_reads", 0)
            pc = d.get("posts_created", 0)
            total_cost += cost
            total_tweet_reads += tr
            total_user_reads += ur
            total_posts_created += pc
            day_count += 1
            pct = (cost / daily_budget * 100) if daily_budget > 0 else 0
            bar = "#" * min(int(pct / 5), 20)
            print(f"  {day}: ${cost:.3f} / ${daily_budget:.2f} ({pct:.0f}%) {bar}")
        else:
            print(f"  {day}: $0.000 / ${daily_budget:.2f} (0%)")

    print()
    print(f"Total:     ${total_cost:.3f}")
    print(f"Daily avg: ${total_cost / max(day_count, 1):.3f}")
    budget_total = daily_budget * days
    print(f"Budget:    ${budget_total:.2f} ({days}d x ${daily_budget:.2f})")
    pct_used = (total_cost / budget_total * 100) if budget_total > 0 else 0
    print(f"Used:      {pct_used:.1f}% of budget")
    print(f"API calls: {total_tweet_reads} tweet reads, {total_user_reads} user reads, {total_posts_created} posts created")
    print(f"Budget mode: {mode}")

    # Monthly projection
    if day_count > 0:
        monthly = (total_cost / day_count) * 30
        print(f"\nProjected monthly: ~${monthly:.2f}")


def cmd_budget_mode(args):
    """Set budget mode."""
    if not CONFIG_PATH.exists():
        print(f"No config found. Run setup first.")
        sys.exit(1)

    config = json.loads(CONFIG_PATH.read_text())
    old_mode = config.get("budget_mode", "guarded")
    new_mode = args.mode

    config["budget_mode"] = new_mode
    CONFIG_PATH.write_text(json.dumps(config, indent=2))

    print(f"Budget mode: {old_mode} -> {new_mode}")
    print(f"  {BUDGET_MODES[new_mode]}")


def cmd_check(args):
    """Validate existing credentials."""
    if not CONFIG_PATH.exists():
        print(f"No config found at {CONFIG_PATH}")
        print("Run: uv run x_setup.py")
        sys.exit(1)

    config = json.loads(CONFIG_PATH.read_text())
    print(f"Config: {CONFIG_PATH}")
    print(f"Handle: @{config.get('handle', '?')}")
    print(f"Tier: {config.get('tier', '?')} (${config.get('daily_budget', '?')}/day)")
    print(f"Budget mode: {config.get('budget_mode', 'guarded')}")
    print(f"Setup: {config.get('setup_at', '?')}")
    print()

    print("Validating credentials...")
    user = validate_credentials(
        config["api_key"], config["api_secret"],
        config["access_token"], config["access_secret"],
        config.get("bearer_token", ""),
    )
    if user:
        print(f"Credentials valid. @{user['username']} — {user['followers']:,} followers, {user['tweets']:,} tweets")
    else:
        print("Credentials INVALID. Re-run setup or check your API keys.")
        sys.exit(1)


def cmd_show(args):
    """Show config with secrets redacted."""
    if not CONFIG_PATH.exists():
        print(f"No config found at {CONFIG_PATH}")
        sys.exit(1)

    config = json.loads(CONFIG_PATH.read_text())
    redacted = config.copy()
    for key in ["api_key", "api_secret", "access_token", "access_secret", "bearer_token"]:
        val = redacted.get(key, "")
        if val:
            redacted[key] = val[:8] + "..." + val[-4:] if len(val) > 12 else "****"

    print(json.dumps(redacted, indent=2))


def main():
    parser = argparse.ArgumentParser(description="X (Twitter) skill setup")
    parser.add_argument("--check", action="store_true", help="Validate existing credentials")
    parser.add_argument("--show", action="store_true", help="Show config (secrets redacted)")
    parser.add_argument("--reconfig", action="store_true", help="Reconfigure existing setup")
    parser.add_argument("--handle", help="X handle (without @)")
    parser.add_argument("--tier", choices=["lite", "standard", "intense"], help="Budget tier")
    parser.add_argument("--spend-report", action="store_true", help="Show spend summary")
    parser.add_argument("--days", type=int, default=7, help="Days for spend report (default: 7)")
    parser.add_argument("--budget-mode", dest="budget_mode",
                        choices=["guarded", "relaxed", "unlimited"],
                        help="Set budget enforcement mode")
    parser.add_argument("--version", action="store_true", help="Print version")
    args = parser.parse_args()

    if args.version:
        print(f"x-twitter v{VERSION}")
    elif args.spend_report:
        cmd_spend_report(args)
    elif args.budget_mode:
        # Create a simple namespace for cmd_budget_mode
        class ModeArgs:
            mode = args.budget_mode
        cmd_budget_mode(ModeArgs())
    elif args.check:
        cmd_check(args)
    elif args.show:
        cmd_show(args)
    else:
        cmd_setup(args)


if __name__ == "__main__":
    main()
