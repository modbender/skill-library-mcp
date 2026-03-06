#!/usr/bin/env python3
"""
Fetch usage data from OpenClaw sessions AND optionally from external APIs
"""
import argparse
import json
import os
import sys
import glob
import yaml
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from store import UsageStore
from calc_cost import calculate_cost


# Default OpenClaw session paths
DEFAULT_OPENCLAW_PATHS = [
    os.path.expanduser("~/.openclaw/agents/*/sessions/*.jsonl"),
    os.path.expanduser("~/.clawdbot/agents/*/sessions/*.jsonl"),
]


def find_session_files(patterns: List[str] = None) -> List[str]:
    """Find all OpenClaw session JSONL files"""
    if patterns is None:
        patterns = DEFAULT_OPENCLAW_PATHS

    files = []
    for pattern in patterns:
        files.extend(glob.glob(pattern))

    return sorted(set(files))


def parse_openclaw_session(file_path: str, date: str = None) -> List[Dict]:
    """Parse OpenClaw session file and extract usage data"""
    usage_records = []

    try:
        with open(file_path, 'r') as f:
            for line in f:
                if not line.strip():
                    continue

                try:
                    data = json.loads(line)
                except json.JSONDecodeError:
                    continue

                # Extract timestamp to filter by date
                timestamp = data.get("timestamp") or data.get("created_at")
                record_date = datetime.now().strftime("%Y-%m-%d")
                if timestamp:
                    try:
                        # Handle various timestamp formats
                        if isinstance(timestamp, (int, float)):
                            record_date = datetime.fromtimestamp(timestamp / 1000).strftime("%Y-%m-%d")
                        else:
                            record_date = datetime.fromisoformat(timestamp.replace("Z", "+00:00")).strftime("%Y-%m-%d")

                        if date and record_date != date:
                            continue
                    except (ValueError, OSError):
                        pass

                # Extract usage data from message
                message = data.get("message", {})

                # Try different paths for usage
                usage = (
                    message.get("usage") or
                    data.get("usage") or
                    data.get("metrics", {}).get("usage")
                )

                if not usage:
                    continue

                # Extract model info
                model = (
                    message.get("model") or
                    data.get("model") or
                    data.get("model_alias") or
                    "unknown"
                )

                # Determine provider from model
                if "claude" in model.lower() or "anthropic" in model.lower():
                    provider = "anthropic"
                elif "gpt" in model.lower() or "openai" in model.lower():
                    provider = "openai"
                elif "gemini" in model.lower():
                    provider = "gemini"
                else:
                    provider = "unknown"

                # Extract token counts
                input_tokens = usage.get("inputTokens", 0) or usage.get("input_tokens", 0) or 0
                output_tokens = usage.get("outputTokens", 0) or usage.get("output_tokens", 0) or 0
                total_tokens = usage.get("totalTokens", 0) or usage.get("total_tokens", 0) or 0

                # Handle combined total if separate not available
                if not input_tokens and not output_tokens and total_tokens:
                    input_tokens = total_tokens // 2
                    output_tokens = total_tokens - input_tokens

                # Cache tokens (Anthropic)
                cache_read_tokens = usage.get("cacheReadTokens", 0) or usage.get("cache_read_tokens", 0) or 0
                cache_creation_tokens = usage.get("cacheCreationTokens", 0) or usage.get("cache_creation_tokens", 0) or 0

                # Cost - prefer real cost if available (check if field exists first)
                cost = None
                
                # Try different paths for cost
                if isinstance(usage.get("cost"), dict):
                    cost = usage.get("cost", {}).get("total")
                elif "cost" in usage:
                    cost = usage.get("cost")
                elif "totalCost" in usage:
                    cost = usage.get("totalCost")
                
                # If no real cost (None), calculate it
                if cost is None:
                    cost_val, savings = calculate_cost(model, input_tokens, output_tokens, cache_read_tokens, cache_creation_tokens)
                else:
                    # If cost provided by API/OpenClaw, we estimate savings for consistent reporting
                    cost_val = cost
                    _, savings = calculate_cost(model, input_tokens, output_tokens, cache_read_tokens, cache_creation_tokens)

                if input_tokens or output_tokens or cost_val:
                    usage_records.append({
                        "date": record_date,
                        "provider": provider,
                        "model": model,
                        "input_tokens": input_tokens,
                        "output_tokens": output_tokens,
                        "cache_read_tokens": cache_read_tokens,
                        "cache_creation_tokens": cache_creation_tokens,
                        "cost": cost_val,
                        "savings": savings
                    })

    except Exception as e:
        print(f"Error reading {file_path}: {e}")

    return usage_records


def load_config(config_path: str = "config/config.yaml") -> Dict:
    """Load optional configuration"""
    base_dir = os.path.dirname(os.path.dirname(__file__))
    paths_to_try = [
        config_path,
        os.path.join(base_dir, config_path),
        os.path.expanduser("~/.llm-cost-monitor/config.yaml"),
    ]

    for path in paths_to_try:
        if os.path.exists(path):
            with open(path, 'r') as f:
                return yaml.safe_load(f) or {}

    return {}


def fetch_openclow_usage(date: str = None, storage_path: str = "~/.llm-cost-monitor", force_full: bool = False) -> int:
    """Fetch usage from OpenClaw sessions (no config needed!)"""
    store = UsageStore(storage_path)

    # If date is specified, clear it first to avoid double counting
    if date and not force_full:
        store.clear_records(date=date, source="session")
    elif force_full:
        print("Force full scan: clearing all session records first")
        store.clear_records(source="session")

    # Find all session files
    session_files = find_session_files()

    if not session_files:
        print("No OpenClaw session files found")
        return 0

    print(f"Found {len(session_files)} session files")

    total_records = 0

    for file_path in session_files:
        records = parse_openclaw_session(file_path, date)

        for record in records:
            # Use file path as api_key hash for OpenClaw sessions
            api_key = os.path.basename(os.path.dirname(os.path.dirname(file_path)))
            
            # Determine app from path (openclaw or clawdbot)
            if ".openclaw" in file_path:
                app = "openclaw"
            elif ".clawdbot" in file_path:
                app = "clawdbot"
            else:
                app = "openclaw"

            store.add_usage(
                date=record["date"],
                provider=record["provider"],
                api_key=api_key,
                model=record["model"],
                app=app,
                source="session",
                input_tokens=record["input_tokens"],
                output_tokens=record["output_tokens"],
                cache_read_tokens=record.get("cache_read_tokens", 0),
                cache_creation_tokens=record.get("cache_creation_tokens", 0),
                cost=record["cost"],
                savings=record.get("savings", 0)
            )
            total_records += 1

    print(f"Processed {total_records} usage records from OpenClaw")
    return total_records


def main():
    parser = argparse.ArgumentParser(description="Fetch LLM usage data")
    parser.add_argument("--date", type=str, help="Specific date (YYYY-MM-DD)")
    parser.add_argument("--today", action="store_true", help="Fetch today's usage")
    parser.add_argument("--yesterday", action="store_true", help="Fetch yesterday's usage")
    parser.add_argument("--last-days", type=int, help="Fetch last N days")
    parser.add_argument("--full", action="store_true", help="Full scan of all historical sessions")
    parser.add_argument("--openclaw-only", action="store_true", help="Only read OpenClaw sessions (no external APIs)")
    parser.add_argument("--config", type=str, help="Config file path")
    parser.add_argument("--dry-run", action="store_true", help="Don't save to database")

    args = parser.parse_args()

    # Determine date(s)
    dates = []
    today = datetime.now()

    if args.today:
        dates.append(today.strftime("%Y-%m-%d"))
    elif args.yesterday:
        dates.append((today - timedelta(days=1)).strftime("%Y-%m-%d"))
    elif args.last_days:
        for i in range(args.last_days):
            date = (today - timedelta(days=i+1)).strftime("%Y-%m-%d")
            dates.append(date)
    elif args.date:
        dates.append(args.date)
    else:
        # Default to today
        dates.append(today.strftime("%Y-%m-%d"))

    # Load optional config
    config = {}
    if args.config:
        config = load_config(args.config)
    elif os.path.exists("config/config.yaml"):
        config = load_config("config/config.yaml")
    elif os.path.exists(os.path.expanduser("~/.llm-cost-monitor/config.yaml")):
        config = load_config(os.path.expanduser("~/.llm-cost-monitor/config.yaml"))

    storage_path = config.get("storage", {}).get("path", "~/.llm-cost-monitor")

    if args.full:
        print("\n🚀 Performing FULL SCAN of all sessions...")
        fetch_openclow_usage(date=None, storage_path=storage_path, force_full=True)
    else:
        # Fetch for specific dates (idempotent)
        for date in dates:
            print(f"\n{'='*50}")
            print(f"Fetching usage for {date}")
            print('='*50)

            if args.openclaw_only or not config.get("providers"):
                # Default: just OpenClaw sessions
                fetch_openclow_usage(date, storage_path)
            else:
                # TODO: Add external API fetching when config is provided
                fetch_openclow_usage(date, storage_path)
                print("\n⚠️ External API fetching not yet implemented")
                print("Config detected but only OpenClaw sessions are being read")


if __name__ == "__main__":
    main()
