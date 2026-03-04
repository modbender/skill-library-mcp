#!/usr/bin/env python3
"""🐾 AI Usage & Cost Tracker — logging library.

Usage:
    from tracker import log_usage
    log_usage("claude-opus-4", 1200, 800, "coding", "refactored auth module")
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path

# 🐾 paw print: every log entry is a little footprint in the snow
_HERE = Path(__file__).resolve().parent
_PRICING_PATH = _HERE / "pricing.json"
_USAGE_PATH = _HERE / "usage.jsonl"


def _load_pricing() -> dict:
    with open(_PRICING_PATH) as f:
        return json.load(f)


def _resolve_model(name: str, models: dict) -> str | None:
    """Fuzzy-match model name against pricing table."""
    low = name.lower()
    # exact
    if low in models:
        return low
    # substring match
    for key in models:
        if key in low or low in key:
            return key
    return None


def estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """Calculate cost in USD from token counts. 🐾"""
    pricing = _load_pricing()
    models = pricing["models"]
    key = _resolve_model(model, models)
    if key is None:
        return 0.0
    p = models[key]
    return (input_tokens * p["input"] + output_tokens * p["output"]) / 1_000_000


def log_usage(
    model: str,
    input_tokens: int,
    output_tokens: int,
    task_type: str = "general",
    description: str = "",
    source: str = "manual",
    cost_override: float | None = None,
) -> dict:
    """Append a usage entry to the JSONL log. Returns the entry. 🐾"""
    total = input_tokens + output_tokens
    cost = cost_override if cost_override is not None else estimate_cost(model, input_tokens, output_tokens)

    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "model": model,
        "tokens": {"input": input_tokens, "output": output_tokens, "total": total},
        "taskType": task_type,
        "description": description,
        "costEstimate": round(cost, 6),
        "source": source,
    }

    with open(_USAGE_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")  # 🐾 another paw in the log

    return entry


# --- CLI quick-log ---
if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser(description="Log an AI usage entry 🐾")
    p.add_argument("model")
    p.add_argument("input_tokens", type=int)
    p.add_argument("output_tokens", type=int)
    p.add_argument("--task", default="general")
    p.add_argument("--desc", default="")
    p.add_argument("--source", default="cli")
    args = p.parse_args()

    e = log_usage(args.model, args.input_tokens, args.output_tokens, args.task, args.desc, args.source)
    print(json.dumps(e, indent=2))
