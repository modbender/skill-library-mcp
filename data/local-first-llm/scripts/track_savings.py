#!/usr/bin/env python3
"""Track token and cost savings when requests are routed to local LLMs.

Subcommands:
  log     --tokens N --model MODEL --routed-to local|cloud
  summary
  reset

Data is persisted to ~/.openclaw/local-first-llm/savings.json
"""
import argparse
import json
import os
from datetime import datetime, timezone

DB_PATH = os.path.expanduser("~/.openclaw/local-first-llm/savings.json")

# Blended cost per 1K tokens (input + output average) for common cloud models
CLOUD_COSTS_PER_1K = {
    "gpt-4o": 0.005,
    "gpt-4o-mini": 0.000225,
    "claude-3-5-sonnet": 0.009,
    "claude-3-5-haiku": 0.001,
    "claude-3-opus": 0.045,
    "gemini-1.5-pro": 0.00175,
    "gemini-1.5-flash": 0.000125,
    "default": 0.005,
}


def load_db() -> dict:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    if os.path.exists(DB_PATH):
        with open(DB_PATH) as f:
            return json.load(f)
    return {
        "requests": [],
        "totals": {"local": 0, "cloud": 0, "tokens_saved": 0, "cost_saved_usd": 0.0},
    }


def save_db(db: dict) -> None:
    with open(DB_PATH, "w") as f:
        json.dump(db, f, indent=2)


parser = argparse.ArgumentParser()
sub = parser.add_subparsers(dest="cmd", required=True)

log_p = sub.add_parser("log", help="Record a routed request")
log_p.add_argument("--tokens", type=int, required=True, help="Token count for this request")
log_p.add_argument("--model", default="default", help="Cloud model that would have been used")
log_p.add_argument("--routed-to", choices=["local", "cloud"], required=True)

sub.add_parser("summary", help="Print cumulative savings as JSON")
sub.add_parser("reset", help="Clear all saved data")

args = parser.parse_args()
db = load_db()

if args.cmd == "log":
    cost_per_k = CLOUD_COSTS_PER_1K.get(args.model, CLOUD_COSTS_PER_1K["default"])
    cost_saved = (args.tokens / 1000) * cost_per_k if args.routed_to == "local" else 0.0

    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "tokens": args.tokens,
        "model": args.model,
        "routed_to": args.routed_to,
        "cost_saved_usd": round(cost_saved, 6),
    }
    db["requests"].append(entry)
    db["totals"][args.routed_to] += 1
    if args.routed_to == "local":
        db["totals"]["tokens_saved"] += args.tokens
        db["totals"]["cost_saved_usd"] = round(
            db["totals"].get("cost_saved_usd", 0.0) + cost_saved, 6
        )
    save_db(db)
    print(json.dumps(entry))

elif args.cmd == "summary":
    t = db["totals"]
    total = t["local"] + t["cloud"]
    pct_local = round((t["local"] / total * 100), 1) if total > 0 else 0.0
    print(json.dumps({
        "total_requests": total,
        "local_requests": t["local"],
        "cloud_requests": t["cloud"],
        "pct_local": pct_local,
        "tokens_saved": t.get("tokens_saved", 0),
        "cost_saved_usd": round(t.get("cost_saved_usd", 0.0), 4),
    }))

elif args.cmd == "reset":
    save_db({
        "requests": [],
        "totals": {"local": 0, "cloud": 0, "tokens_saved": 0, "cost_saved_usd": 0.0},
    })
    print(json.dumps({"reset": True, "db_path": DB_PATH}))
