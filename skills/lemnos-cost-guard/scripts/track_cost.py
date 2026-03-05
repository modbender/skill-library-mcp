#!/usr/bin/env python3
"""
track_cost.py — Log a cost entry to the daily cost log.
Usage: python3 track_cost.py --task "email batch" --input 45000 --output 1200 --model claude-sonnet-4-6
"""
import json, argparse, os
from datetime import datetime, timezone

# Model pricing per 1M tokens (update as pricing changes)
PRICING = {
    "claude-haiku-3-5":  {"input": 0.80,  "output": 4.00},
    "claude-sonnet-4-5": {"input": 3.00,  "output": 15.00},
    "claude-sonnet-4-6": {"input": 3.00,  "output": 15.00},
    "claude-opus-4":     {"input": 15.00, "output": 75.00},
    "claude-opus-4-5":   {"input": 15.00, "output": 75.00},
}
DEFAULT_MODEL = "claude-sonnet-4-6"
LOG_DIR = os.path.join(os.path.dirname(__file__), "../../logs")

def calc_cost(input_tokens, output_tokens, model):
    p = PRICING.get(model, PRICING[DEFAULT_MODEL])
    return (input_tokens / 1_000_000 * p["input"]) + (output_tokens / 1_000_000 * p["output"])

def log_entry(task, input_tokens, output_tokens, model, notes=""):
    os.makedirs(LOG_DIR, exist_ok=True)
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    log_file = os.path.join(LOG_DIR, f"cost-{date_str}.jsonl")

    cost = calc_cost(input_tokens, output_tokens, model)
    ratio = round(input_tokens / max(output_tokens, 1), 1)

    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "task": task,
        "model": model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "ratio": ratio,
        "cost_usd": round(cost, 4),
        "notes": notes
    }

    with open(log_file, "a") as f:
        f.write(json.dumps(entry) + "\n")

    # Alerts
    alerts = []
    if input_tokens > 500_000:
        alerts.append(f"🔴 ALERT: Single call exceeded 500K input tokens ({input_tokens:,})")
    if ratio > 50:
        alerts.append(f"⚠️  Context bloat: {ratio}:1 input:output ratio (threshold: 50:1)")

    print(f"Logged: {task} | ${cost:.4f} | {input_tokens:,} in / {output_tokens:,} out | ratio {ratio}:1")
    for a in alerts:
        print(a)

    return entry

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", required=True)
    parser.add_argument("--input", type=int, required=True)
    parser.add_argument("--output", type=int, required=True)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--notes", default="")
    args = parser.parse_args()
    log_entry(args.task, args.input, args.output, args.model, args.notes)
