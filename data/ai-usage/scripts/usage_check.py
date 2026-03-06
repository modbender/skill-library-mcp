#!/usr/bin/env python3
"""AI Usage Checker - Anthropic quota via OAuth + OpenClaw session log stats.

Requirements:
  - Claude Code installed and authenticated (`claude` CLI in PATH)
  - OpenClaw installed (~/.openclaw/agents/*/sessions/*.jsonl for log stats)
  - Python 3.10+ (no pip dependencies)

Usage:
    python3 usage_check.py           # Pretty report with gauges
    python3 usage_check.py --json    # JSON output for scripting
"""

import json
import glob
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta
from pathlib import Path

# --- Configuration (override via environment variables) ---

# OpenClaw session logs directory
SESSIONS_DIR = Path(
    os.environ.get("OPENCLAW_SESSIONS_DIR",
                    Path.home() / ".openclaw" / "agents" / "main" / "sessions")
)

# Claude Code credentials (needs user:profile scope for usage endpoint)
CLAUDE_CREDS_PATH = Path(
    os.environ.get("CLAUDE_CREDENTIALS_PATH",
                    Path.home() / ".claude" / ".credentials.json")
)

ANTHROPIC_USAGE_URL = "https://api.anthropic.com/api/oauth/usage"

# Display names for known models (extend as needed)
MODEL_NAMES = {
    "claude-sonnet-4-5": "Sonnet 4.5",
    "claude-opus-4-6": "Opus 4.6",
    "claude-haiku-4-5": "Haiku 4.5",
    "claude-sonnet-4-0": "Sonnet 4",
    "claude-opus-4-0": "Opus 4",
    "claude-3-5-sonnet": "Sonnet 3.5",
    "claude-3-5-haiku": "Haiku 3.5",
}


# --- Token Management ---

def _refresh_claude_token() -> str | None:
    """Refresh expired Claude Code OAuth token by invoking Claude Code.

    Claude Code auto-refreshes its token on any invocation. We trigger a
    minimal call, then re-read the credentials file for the new token.
    """
    import subprocess
    try:
        subprocess.run(
            ["claude", "--print", "-p", "ok"],
            capture_output=True, timeout=30,
        )
        creds = json.loads(CLAUDE_CREDS_PATH.read_text())
        return creds["claudeAiOauth"]["accessToken"]
    except Exception:
        return None


def _is_token_expired() -> bool:
    """Check if the Claude Code OAuth token has expired."""
    try:
        creds = json.loads(CLAUDE_CREDS_PATH.read_text())
        expires_at_ms = creds["claudeAiOauth"]["expiresAt"]
        import time
        return time.time() * 1000 > expires_at_ms
    except Exception:
        return True


def _fetch_usage(token: str) -> dict | None:
    """Make the actual usage API call with a given token."""
    req = urllib.request.Request(ANTHROPIC_USAGE_URL)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("anthropic-beta", "oauth-2025-04-20")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError:
        return None
    except Exception:
        return None


def get_anthropic_usage() -> dict | None:
    """Fetch real usage from Anthropic OAuth endpoint, refreshing token if needed.

    Flow:
    1. Check if token is expired → refresh via Claude Code if so
    2. Try the API call
    3. If it fails (edge case: just expired), try one more refresh + retry
    """
    if not CLAUDE_CREDS_PATH.exists():
        return None

    try:
        creds = json.loads(CLAUDE_CREDS_PATH.read_text())
        token = creds["claudeAiOauth"]["accessToken"]
    except Exception:
        return None

    # If token is expired, refresh before trying
    if _is_token_expired():
        token = _refresh_claude_token()
        if not token:
            return None

    # Try the API call
    result = _fetch_usage(token)
    if result is not None:
        return result

    # If it failed (maybe token just expired), try one refresh
    token = _refresh_claude_token()
    if not token:
        return None
    return _fetch_usage(token)


# --- OpenClaw Log Parsing ---

def parse_usage_from_logs(since: datetime) -> dict:
    """Parse OpenClaw session logs for token usage stats by provider/model."""
    anthropic = {"input": 0, "output": 0, "total": 0, "cost": 0.0, "requests": 0}
    anthropic_models = {}
    other = {"input": 0, "output": 0, "total": 0, "requests": 0}
    other_models = {}

    pattern = str(SESSIONS_DIR / "*.jsonl")
    for logfile in glob.glob(pattern):
        try:
            with open(logfile, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line or '"usage"' not in line:
                        continue
                    try:
                        entry = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    msg = entry.get("message", {})
                    timestamp_ms = msg.get("timestamp")
                    if not timestamp_ms:
                        ts_str = entry.get("timestamp", "")
                        if ts_str:
                            try:
                                ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                                if ts < since:
                                    continue
                            except Exception:
                                continue
                        else:
                            continue
                    else:
                        ts = datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc)
                        if ts < since:
                            continue

                    usage = msg.get("usage", {})
                    if not usage:
                        continue

                    provider = msg.get("provider", "")
                    model = msg.get("model", "unknown")
                    total = usage.get("totalTokens", 0)
                    cost_val = usage.get("cost", {}).get("total", 0) if isinstance(usage.get("cost"), dict) else 0

                    if provider == "anthropic":
                        anthropic["total"] += total
                        anthropic["cost"] += cost_val
                        anthropic["requests"] += 1
                        if model not in anthropic_models:
                            anthropic_models[model] = {"total": 0, "requests": 0, "cost": 0.0}
                        anthropic_models[model]["total"] += total
                        anthropic_models[model]["requests"] += 1
                        anthropic_models[model]["cost"] += cost_val
                    else:
                        other["total"] += total
                        other["requests"] += 1
                        key = f"{provider}/{model}" if provider else model
                        if key not in other_models:
                            other_models[key] = {"total": 0, "requests": 0}
                        other_models[key]["total"] += total
                        other_models[key]["requests"] += 1
        except Exception:
            continue

    return {
        "anthropic": anthropic, "anthropic_models": anthropic_models,
        "other": other, "other_models": other_models,
    }


# --- Formatting ---

def get_week_start() -> datetime:
    now = datetime.now(timezone.utc)
    days_since_monday = now.weekday()
    return now - timedelta(
        days=days_since_monday, hours=now.hour,
        minutes=now.minute, seconds=now.second,
        microseconds=now.microsecond,
    )


def fmt(n: int) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    elif n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)


def gauge(pct: float, width: int = 20) -> str:
    pct = max(0, min(100, pct))
    filled = round(pct / 100 * width)
    bar = "\u2588" * filled + "\u2591" * (width - filled)
    return f"[{bar}] {pct:.0f}%"


def time_until(iso_str: str) -> str:
    """Human-readable time until a reset timestamp."""
    try:
        reset = datetime.fromisoformat(iso_str)
        delta = reset - datetime.now(timezone.utc)
        if delta.total_seconds() <= 0:
            return "now"
        hours = int(delta.total_seconds() // 3600)
        mins = int((delta.total_seconds() % 3600) // 60)
        if hours > 24:
            return f"{hours // 24}d {hours % 24}h"
        elif hours > 0:
            return f"{hours}h {mins}m"
        return f"{mins}m"
    except Exception:
        return "?"


def model_name(mid: str) -> str:
    """Resolve a model ID to a friendly display name."""
    if mid in MODEL_NAMES:
        return MODEL_NAMES[mid]
    # Strip provider prefix for display (e.g., "ollama/kimi-k2.5:cloud" → "kimi-k2.5:cloud")
    if "/" in mid:
        return mid.split("/", 1)[1]
    return mid


# --- Main ---

def main():
    json_output = "--json" in sys.argv

    week_start = get_week_start()
    now = datetime.now(timezone.utc)
    weekly_logs = parse_usage_from_logs(week_start)

    # Real Anthropic usage from OAuth API
    anthropic_usage = get_anthropic_usage()

    if json_output:
        result = {
            "timestamp": now.isoformat(),
            "anthropic_quota": anthropic_usage,
            "openclaw_logs": {
                "anthropic": {
                    "weekly_tokens": weekly_logs["anthropic"]["total"],
                    "weekly_cost": round(weekly_logs["anthropic"]["cost"], 2),
                    "weekly_requests": weekly_logs["anthropic"]["requests"],
                    "models": {model_name(k): v for k, v in weekly_logs["anthropic_models"].items()},
                },
                "other_providers": {
                    "weekly_tokens": weekly_logs["other"]["total"],
                    "weekly_requests": weekly_logs["other"]["requests"],
                    "models": {model_name(k): v for k, v in weekly_logs["other_models"].items()},
                },
            },
        }
        print(json.dumps(result, indent=2))
        return

    print("\U0001f4ca AI Usage Report")
    print()

    # --- Anthropic real quota ---
    if anthropic_usage:
        # Get subscription info from credentials file (more reliable than API response)
        try:
            creds = json.loads(CLAUDE_CREDS_PATH.read_text())
            sub_type = creds.get("claudeAiOauth", {}).get("subscriptionType", "").replace("_", " ").title()
            rate_tier = creds.get("claudeAiOauth", {}).get("rateLimitTier", "")
        except Exception:
            sub_type = ""
            rate_tier = ""
        label = sub_type or "Pro"
        if "5x" in rate_tier:
            label += " 5x"
        print(f"\u2601\ufe0f  Anthropic ({label})")

        seven = anthropic_usage.get("seven_day")
        if seven:
            pct = seven["utilization"]
            reset = time_until(seven["resets_at"])
            print(f"  Weekly    {gauge(pct)}  resets {reset}")

        five = anthropic_usage.get("five_hour")
        if five:
            pct = five["utilization"]
            reset = time_until(five["resets_at"])
            print(f"  5-hour    {gauge(pct)}  resets {reset}")

        sonnet = anthropic_usage.get("seven_day_sonnet")
        if sonnet:
            pct = sonnet["utilization"]
            print(f"  Sonnet    {gauge(pct)}")

        opus = anthropic_usage.get("seven_day_opus")
        if opus:
            pct = opus["utilization"]
            print(f"  Opus      {gauge(pct)}")

        extra = anthropic_usage.get("extra_usage")
        if extra and extra.get("is_enabled"):
            pct = extra["utilization"]
            used = extra["used_credits"] * 0.01
            limit = extra["monthly_limit"] * 0.01
            print(f"  Extra $   {gauge(pct)}  ${used:.2f}/${limit:.0f}")
    else:
        print("\u2601\ufe0f  Anthropic: not available")
        print("  (Claude Code not installed, not authenticated, or token refresh failed)")

    print()

    # --- Other providers (from OpenClaw logs) ---
    if weekly_logs["other"]["requests"] > 0:
        print("\U0001f310 Other Providers (from OpenClaw logs)")
        print(f"  {fmt(weekly_logs['other']['total'])} tokens | {weekly_logs['other']['requests']} calls this week")
        if weekly_logs["other_models"]:
            parts = []
            for mid, d in sorted(weekly_logs["other_models"].items(), key=lambda x: x[1]["total"], reverse=True):
                parts.append(f"{model_name(mid)} {fmt(d['total'])}")
            print(f"  Models: {', '.join(parts)}")
        print()

    # --- OpenClaw Anthropic breakdown ---
    if weekly_logs["anthropic"]["requests"] > 0:
        print("\U0001f4dd OpenClaw Anthropic breakdown")
        cost_str = f" | ${weekly_logs['anthropic']['cost']:.0f} equiv" if weekly_logs["anthropic"]["cost"] > 0 else ""
        print(f"  {fmt(weekly_logs['anthropic']['total'])} tokens | {weekly_logs['anthropic']['requests']} calls{cost_str}")
        if weekly_logs["anthropic_models"]:
            parts = []
            for mid, d in sorted(weekly_logs["anthropic_models"].items(), key=lambda x: x[1]["total"], reverse=True):
                parts.append(f"{model_name(mid)} {fmt(d['total'])}")
            print(f"  Models: {', '.join(parts)}")


if __name__ == "__main__":
    main()
