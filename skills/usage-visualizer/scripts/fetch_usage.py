#!/usr/bin/env python3
"""
Fetch usage data from OpenClaw session logs. 100% Local.
"""
import argparse
import json
import os
import sys
import glob
from datetime import datetime, timedelta
from typing import Dict, List

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
                model_lower = model.lower()
                if "claude" in model_lower or "anthropic" in model_lower:
                    provider = "anthropic"
                elif "gpt" in model_lower or "openai" in model_lower:
                    provider = "openai"
                elif "gemini" in model_lower:
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

                # Cost - prefer real cost if available
                cost = None
                if isinstance(usage.get("cost"), dict):
                    cost = usage.get("cost", {}).get("total")
                elif "cost" in usage:
                    cost = usage.get("cost")
                elif "totalCost" in usage:
                    cost = usage.get("totalCost")
                
                # If no real cost, calculate it
                if cost is None:
                    cost_val, savings = calculate_cost(model, input_tokens, output_tokens, cache_read_tokens, cache_creation_tokens)
                else:
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
        pass

    return usage_records


def fetch_openclow_usage(date: str = None, storage_path: str = "~/.llm-cost-monitor", force_full: bool = False) -> int:
    """Fetch usage from OpenClaw sessions"""
    store = UsageStore(storage_path)

    if date and not force_full:
        store.clear_records(date=date, source="session")
    elif force_full:
        store.clear_records(source="session")

    session_files = find_session_files()
    if not session_files:
        return 0

    total_records = 0
    for file_path in session_files:
        records = parse_openclaw_session(file_path, date)
        for record in records:
            # Use the agent directory name as the unique source identifier
            source_id = os.path.basename(os.path.dirname(os.path.dirname(file_path)))
            app = "openclaw" if ".openclaw" in file_path else "clawdbot"

            store.add_usage(
                date=record["date"],
                provider=record["provider"],
                source_id=source_id,
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

    return total_records


def main():
    parser = argparse.ArgumentParser(description="Fetch LLM usage data")
    parser.add_argument("--date", type=str, help="Specific date (YYYY-MM-DD)")
    parser.add_argument("--today", action="store_true", help="Fetch today's usage")
    parser.add_argument("--yesterday", action="store_true", help="Fetch yesterday's usage")
    parser.add_argument("--last-days", type=int, help="Fetch last N days")
    parser.add_argument("--full", action="store_true", help="Full scan")

    args = parser.parse_args()

    dates = []
    today = datetime.now()

    if args.today:
        dates.append(today.strftime("%Y-%m-%d"))
    elif args.yesterday:
        dates.append((today - timedelta(days=1)).strftime("%Y-%m-%d"))
    elif args.last_days:
        for i in range(args.last_days):
            dates.append((today - timedelta(days=i+1)).strftime("%Y-%m-%d"))
    elif args.date:
        dates.append(args.date)
    else:
        dates.append(today.strftime("%Y-%m-%d"))

    # Workspace handling
    storage_path = os.environ.get("OPENCLAW_WORKSPACE", "~/.llm-cost-monitor")

    if args.full:
        fetch_openclow_usage(date=None, storage_path=storage_path, force_full=True)
    else:
        for date in dates:
            fetch_openclow_usage(date, storage_path)


if __name__ == "__main__":
    main()
