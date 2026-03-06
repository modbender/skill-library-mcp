"""Shared utilities for x-twitter skill scripts."""

import json
from datetime import datetime, timezone
from pathlib import Path

import tweepy

# Paths
CONFIG_DIR = Path.home() / ".openclaw" / "skills-config" / "x-twitter"
CONFIG_PATH = CONFIG_DIR / "config.json"
DATA_DIR = CONFIG_DIR / "data"
USAGE_PATH = DATA_DIR / "usage.json"
SCRIPT_DIR = Path(__file__).resolve().parent

VERSION = "2.0.1"


def load_config() -> dict | None:
    if not CONFIG_PATH.exists():
        print(f"Error: No config found at {CONFIG_PATH}")
        print(f"Run: uv run {SCRIPT_DIR / 'x_setup.py'}")
        return None
    return json.loads(CONFIG_PATH.read_text())


def save_config(config: dict):
    CONFIG_PATH.write_text(json.dumps(config, indent=2))


def get_client(config: dict) -> tweepy.Client:
    return tweepy.Client(
        bearer_token=config.get("bearer_token"),
        consumer_key=config["api_key"],
        consumer_secret=config["api_secret"],
        access_token=config["access_token"],
        access_token_secret=config["access_secret"],
        wait_on_rate_limit=True,
    )


def track_usage(tweet_reads: int = 0, user_reads: int = 0, posts_created: int = 0) -> dict:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    usage = {}
    if USAGE_PATH.exists():
        usage = json.loads(USAGE_PATH.read_text())
    if today not in usage:
        usage[today] = {"tweet_reads": 0, "user_reads": 0, "posts_created": 0, "est_cost": 0.0}
    if "posts_created" not in usage[today]:
        usage[today]["posts_created"] = 0
    usage[today]["tweet_reads"] += tweet_reads
    usage[today]["user_reads"] += user_reads
    usage[today]["posts_created"] += posts_created
    usage[today]["est_cost"] = (usage[today]["tweet_reads"] * 0.005 +
                                 usage[today]["user_reads"] * 0.01)
    USAGE_PATH.write_text(json.dumps(usage, indent=2))
    return usage[today]


def budget_warning(config: dict, suppress: bool = False):
    """Print budget warning at 50%, 80%, 100% thresholds."""
    mode = config.get("budget_mode", "guarded")
    if suppress or mode == "unlimited":
        return
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    budget = config.get("daily_budget", 0.25)
    if not USAGE_PATH.exists() or budget <= 0:
        return
    usage = json.loads(USAGE_PATH.read_text())
    if today not in usage:
        return
    cost = usage[today].get("est_cost", 0.0)
    pct = cost / budget * 100
    if pct >= 100:
        print(f"[!] BUDGET EXCEEDED: ${cost:.3f} / ${budget:.2f} ({pct:.0f}%)")
    elif pct >= 80:
        print(f"[!] Budget warning: ${cost:.3f} / ${budget:.2f} ({pct:.0f}%) — approaching limit")
    elif pct >= 50:
        print(f"[i] Budget note: ${cost:.3f} / ${budget:.2f} ({pct:.0f}%) used today")


def check_budget(config: dict, force: bool = False) -> bool:
    """Check if daily budget is exceeded. Returns True if OK to proceed."""
    mode = config.get("budget_mode", "guarded")
    if force or mode in ("relaxed", "unlimited"):
        return True
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if USAGE_PATH.exists():
        usage = json.loads(USAGE_PATH.read_text())
        if today in usage and usage[today]["est_cost"] >= config.get("daily_budget", 0.25):
            print(f"Daily budget exceeded (${usage[today]['est_cost']:.3f} / ${config['daily_budget']:.2f})")
            print("Use --force to override.")
            return False
    return True


def format_time(dt) -> str:
    """Format datetime to readable local time."""
    if isinstance(dt, str):
        dt = datetime.fromisoformat(dt.replace("Z", "+00:00"))
    local = dt.astimezone()
    return local.strftime("%Y-%m-%d %H:%M %Z")


def time_ago(dt) -> str:
    """Human-readable time ago."""
    if isinstance(dt, str):
        dt = datetime.fromisoformat(dt.replace("Z", "+00:00"))
    now = datetime.now(timezone.utc)
    diff = now - dt
    if diff.total_seconds() < 60:
        return f"{int(diff.total_seconds())}s ago"
    if diff.total_seconds() < 3600:
        return f"{int(diff.total_seconds() / 60)}m ago"
    if diff.total_seconds() < 86400:
        return f"{int(diff.total_seconds() / 3600)}h ago"
    return f"{diff.days}d ago"


def format_number(n: int) -> str:
    """Format large numbers for display (e.g., 12.3K, 1.5M)."""
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 10_000:
        return f"{n/1_000:.1f}K"
    return f"{n:,}"


def handle_api_error(e: Exception) -> None:
    """Consistent error handling: 401, 402, 403, 429."""
    msg = str(e)
    if "401" in msg:
        print("Error: Invalid credentials (401). Re-run x_setup.py or check your API keys.")
    elif "402" in msg:
        print("Error: No API credits. Add credits at https://developer.x.com")
    elif "403" in msg:
        print("Error: Forbidden (403). Check your app permissions at developer.x.com")
    elif "429" in msg:
        print("Error: Rate limited (429). Wait 15 minutes and try again.")
    else:
        print(f"Error: {e}")
