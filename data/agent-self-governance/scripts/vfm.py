#!/usr/bin/env python3
"""Value-For-Money (VFM) — Track cost vs value of agent actions.

Monitors token spend per task, evaluates whether expensive operations
were worth it, and suggests cheaper alternatives.

Usage:
  vfm.py log <agent_id> <task> <model> <tokens> <cost> <outcome_score>
  vfm.py score <agent_id> [--limit N]     # Calculate VFM scores
  vfm.py report <agent_id>                # Cost breakdown report
  vfm.py suggest <agent_id>               # Suggest optimizations
  vfm.py history <agent_id> [--limit N]   # View history
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_DIR = os.path.join(os.environ.get("HOME", "."), "clawd", "memory", "governance")
VFM_FILE = "vfm-costs.jsonl"

# Model cost tiers (approximate $/1M tokens)
MODEL_TIERS = {
    "opus": {"input": 15.0, "output": 75.0, "tier": "premium"},
    "sonnet": {"input": 3.0, "output": 15.0, "tier": "standard"},
    "haiku": {"input": 0.25, "output": 1.25, "tier": "budget"},
    "gemini": {"input": 0.5, "output": 1.5, "tier": "budget"},
    "deepseek": {"input": 0.14, "output": 0.28, "tier": "budget"},
    "glm": {"input": 0.1, "output": 0.1, "tier": "budget"},
    "llama": {"input": 0.0, "output": 0.0, "tier": "local"},
    "qwen": {"input": 0.0, "output": 0.0, "tier": "local"},
}

# Task complexity → recommended tier
TASK_TIER_MAP = {
    "simple_query": "budget",
    "code_generation": "standard",
    "complex_analysis": "premium",
    "monitoring": "budget",
    "creative_writing": "standard",
    "debugging": "standard",
    "architecture": "premium",
    "formatting": "budget",
    "summarization": "budget",
}


def vfm_path(gov_dir: str) -> Path:
    return Path(gov_dir) / VFM_FILE


def log_task(gov_dir: str, agent_id: str, task: str, model: str,
             tokens: int, cost: float, outcome_score: float) -> dict:
    os.makedirs(gov_dir, exist_ok=True)
    vfm = outcome_score / cost if cost > 0 else float('inf')
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "agent_id": agent_id,
        "task": task,
        "model": model,
        "tokens": tokens,
        "cost_usd": round(cost, 4),
        "outcome_score": outcome_score,
        "vfm_score": round(vfm, 2),
    }
    with open(vfm_path(gov_dir), "a") as f:
        f.write(json.dumps(entry) + "\n")
    return entry


def get_entries(gov_dir: str, agent_id: str) -> list[dict]:
    path = vfm_path(gov_dir)
    if not path.exists():
        return []
    entries = []
    for line in path.read_text().strip().split("\n"):
        if line:
            e = json.loads(line)
            if e["agent_id"] == agent_id:
                entries.append(e)
    return entries


def calculate_scores(gov_dir: str, agent_id: str, limit: int = 50) -> dict:
    entries = get_entries(gov_dir, agent_id)[-limit:]
    if not entries:
        return {"avg_vfm": 0, "total_cost": 0, "total_tokens": 0, "entries": 0}

    total_cost = sum(e["cost_usd"] for e in entries)
    total_tokens = sum(e["tokens"] for e in entries)
    avg_vfm = sum(e["vfm_score"] for e in entries if e["vfm_score"] != float('inf')) / len(entries)
    avg_outcome = sum(e["outcome_score"] for e in entries) / len(entries)

    return {
        "avg_vfm": round(avg_vfm, 2),
        "avg_outcome": round(avg_outcome, 2),
        "total_cost_usd": round(total_cost, 4),
        "total_tokens": total_tokens,
        "entries": len(entries),
        "cost_per_task": round(total_cost / len(entries), 4),
    }


def cost_report(gov_dir: str, agent_id: str) -> dict:
    entries = get_entries(gov_dir, agent_id)
    if not entries:
        return {"models": {}, "tasks": {}, "total_cost": 0}

    by_model = {}
    by_task = {}
    for e in entries:
        model = e["model"]
        task = e["task"]
        by_model[model] = by_model.get(model, 0) + e["cost_usd"]
        by_task[task] = by_task.get(task, 0) + e["cost_usd"]

    return {
        "by_model": {k: round(v, 4) for k, v in sorted(by_model.items(), key=lambda x: -x[1])},
        "by_task": {k: round(v, 4) for k, v in sorted(by_task.items(), key=lambda x: -x[1])},
        "total_cost_usd": round(sum(e["cost_usd"] for e in entries), 4),
        "total_entries": len(entries),
    }


def suggest_optimizations(gov_dir: str, agent_id: str) -> list[str]:
    entries = get_entries(gov_dir, agent_id)
    if not entries:
        return ["No data yet. Log some tasks first."]

    suggestions = []

    # Find expensive low-value tasks
    for e in entries[-20:]:
        if e["cost_usd"] > 0.10 and e["outcome_score"] < 0.5:
            suggestions.append(
                f"⚠️ '{e['task']}' cost ${e['cost_usd']:.3f} but scored {e['outcome_score']}/1.0 — consider cheaper model"
            )

    # Find tasks using premium models that could use budget
    for e in entries[-20:]:
        model_lower = e["model"].lower()
        for name, info in MODEL_TIERS.items():
            if name in model_lower and info["tier"] == "premium":
                task_tier = TASK_TIER_MAP.get(e["task"], "standard")
                if task_tier in ("budget", "standard"):
                    suggestions.append(
                        f"💡 '{e['task']}' used {e['model']} (premium) but task type suggests {task_tier} tier is enough"
                    )

    # Overall cost trend
    if len(entries) >= 10:
        recent = entries[-5:]
        older = entries[-10:-5]
        recent_avg = sum(e["cost_usd"] for e in recent) / 5
        older_avg = sum(e["cost_usd"] for e in older) / 5
        if recent_avg > older_avg * 1.5:
            suggestions.append(f"📈 Cost trending up: recent avg ${recent_avg:.3f}/task vs ${older_avg:.3f}/task before")

    if not suggestions:
        suggestions.append("✅ Costs look reasonable. No optimization suggestions.")

    return suggestions


def main():
    parser = argparse.ArgumentParser(description="Value-For-Money Tracker")
    parser.add_argument("command", choices=["log", "score", "report", "suggest", "history"])
    parser.add_argument("args", nargs="*")
    parser.add_argument("--dir", default=DEFAULT_DIR)
    parser.add_argument("--limit", type=int, default=50)
    args = parser.parse_args()

    if args.command == "log":
        if len(args.args) < 6:
            print("Usage: vfm.py log <agent_id> <task> <model> <tokens> <cost> <outcome_score>", file=sys.stderr)
            sys.exit(1)
        entry = log_task(
            args.dir, args.args[0], args.args[1], args.args[2],
            int(args.args[3]), float(args.args[4]), float(args.args[5])
        )
        print(json.dumps(entry, indent=2))

    elif args.command == "score":
        if not args.args:
            print("Usage: vfm.py score <agent_id>", file=sys.stderr)
            sys.exit(1)
        print(json.dumps(calculate_scores(args.dir, args.args[0], args.limit), indent=2))

    elif args.command == "report":
        if not args.args:
            print("Usage: vfm.py report <agent_id>", file=sys.stderr)
            sys.exit(1)
        print(json.dumps(cost_report(args.dir, args.args[0]), indent=2))

    elif args.command == "suggest":
        if not args.args:
            print("Usage: vfm.py suggest <agent_id>", file=sys.stderr)
            sys.exit(1)
        for s in suggest_optimizations(args.dir, args.args[0]):
            print(s)

    elif args.command == "history":
        if not args.args:
            print("Usage: vfm.py history <agent_id>", file=sys.stderr)
            sys.exit(1)
        entries = get_entries(args.dir, args.args[0])[-args.limit:]
        print(json.dumps(entries, indent=2))


if __name__ == "__main__":
    main()
