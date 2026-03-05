#!/usr/bin/env python3
"""Anti-Divergence Limit (ADL) — Track and limit behavioral drift.

Monitors how much the agent's behavior drifts from its defined persona
(SOUL.md). Tracks response patterns, flags drift, suggests correction.

Usage:
  adl.py log <agent_id> <category> <observation>   # Log a behavioral observation
  adl.py score <agent_id>                           # Calculate divergence score
  adl.py check <agent_id> [--threshold 0.7]         # Check if within limits
  adl.py history <agent_id> [--limit N]             # View drift history
  adl.py reset <agent_id>                           # Reset tracking (new baseline)
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_DIR = os.path.join(os.environ.get("HOME", "."), "clawd", "memory", "governance")
ADL_FILE = "adl-drift.jsonl"

# Behavioral categories and their anti-patterns (things SOUL.md says NOT to do)
ANTI_PATTERNS = {
    "sycophancy": [
        "Great question!", "I'd be happy to help!", "That's a wonderful idea!",
        "Absolutely!", "Of course!", "What a great",
    ],
    "verbosity": [],  # Tracked by response length, not keywords
    "passivity": [
        "Would you like me to", "Shall I", "Do you want me to",
        "If you'd like", "Let me know if",
    ],
    "hedging": [
        "I think maybe", "It might be possible", "Perhaps we could consider",
        "I'm not sure but", "It could potentially",
    ],
}

# Persona traits from SOUL.md (positive signals)
PERSONA_SIGNALS = {
    "direct": ["Here's", "Done", "Fixed", "Ship", "Built", "Pushed"],
    "opinionated": ["I'd argue", "Better to", "The right call is", "No —"],
    "action_oriented": ["Spawning", "On it", "Kicking off", "Running"],
}


def adl_path(gov_dir: str) -> Path:
    return Path(gov_dir) / ADL_FILE


def log_observation(gov_dir: str, agent_id: str, category: str, observation: str) -> dict:
    os.makedirs(gov_dir, exist_ok=True)
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "agent_id": agent_id,
        "category": category,
        "observation": observation,
    }
    with open(adl_path(gov_dir), "a") as f:
        f.write(json.dumps(entry) + "\n")
    return entry


def analyze_text(text: str) -> dict:
    """Analyze text for anti-patterns and persona signals."""
    scores = {}

    # Check anti-patterns (higher = more drift)
    for category, patterns in ANTI_PATTERNS.items():
        if category == "verbosity":
            # Score based on length (>2000 chars for a simple response = verbose)
            scores[f"anti_{category}"] = min(len(text) / 2000, 1.0)
        else:
            hits = sum(1 for p in patterns if p.lower() in text.lower())
            scores[f"anti_{category}"] = min(hits / max(len(patterns), 1), 1.0)

    # Check persona signals (higher = more aligned)
    for trait, signals in PERSONA_SIGNALS.items():
        hits = sum(1 for s in signals if s.lower() in text.lower())
        scores[f"persona_{trait}"] = min(hits / max(len(signals), 1), 1.0)

    return scores


def calculate_divergence(gov_dir: str, agent_id: str) -> dict:
    """Calculate overall divergence score (0 = perfectly aligned, 1 = fully diverged)."""
    path = adl_path(gov_dir)
    if not path.exists():
        return {"divergence": 0.0, "details": {}, "entries": 0}

    entries = []
    for line in path.read_text().strip().split("\n"):
        if line:
            e = json.loads(line)
            if e["agent_id"] == agent_id:
                entries.append(e)

    if not entries:
        return {"divergence": 0.0, "details": {}, "entries": 0}

    # Count categories
    category_counts = {}
    for e in entries:
        cat = e["category"]
        category_counts[cat] = category_counts.get(cat, 0) + 1

    # Weight anti-pattern observations more heavily
    anti_count = sum(v for k, v in category_counts.items() if k.startswith("anti_"))
    persona_count = sum(v for k, v in category_counts.items() if k.startswith("persona_"))
    total = len(entries)

    # Divergence = anti-pattern ratio (more anti-patterns = more drift)
    divergence = anti_count / total if total > 0 else 0.0

    return {
        "divergence": round(divergence, 3),
        "anti_pattern_count": anti_count,
        "persona_signal_count": persona_count,
        "total_observations": total,
        "categories": category_counts,
    }


def check_limit(gov_dir: str, agent_id: str, threshold: float = 0.7) -> dict:
    result = calculate_divergence(gov_dir, agent_id)
    within_limit = result["divergence"] <= threshold
    return {
        "within_limit": within_limit,
        "divergence": result["divergence"],
        "threshold": threshold,
        "recommendation": "OK" if within_limit else "DRIFT ALERT: Review SOUL.md, recalibrate behavior",
    }


def get_history(gov_dir: str, agent_id: str, limit: int = 20) -> list[dict]:
    path = adl_path(gov_dir)
    if not path.exists():
        return []
    entries = []
    for line in path.read_text().strip().split("\n"):
        if line:
            e = json.loads(line)
            if e["agent_id"] == agent_id:
                entries.append(e)
    return entries[-limit:]


def reset(gov_dir: str, agent_id: str) -> dict:
    path = adl_path(gov_dir)
    if path.exists():
        entries = []
        for line in path.read_text().strip().split("\n"):
            if line:
                e = json.loads(line)
                if e["agent_id"] != agent_id:
                    entries.append(e)
        with open(path, "w") as f:
            for e in entries:
                f.write(json.dumps(e) + "\n")
    return {"reset": True, "agent_id": agent_id}


def main():
    parser = argparse.ArgumentParser(description="Anti-Divergence Limit")
    parser.add_argument("command", choices=["log", "score", "check", "history", "reset", "analyze"])
    parser.add_argument("args", nargs="*")
    parser.add_argument("--dir", default=DEFAULT_DIR)
    parser.add_argument("--threshold", type=float, default=0.7)
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args()

    if args.command == "log":
        if len(args.args) < 3:
            print("Usage: adl.py log <agent_id> <category> <observation>", file=sys.stderr)
            sys.exit(1)
        entry = log_observation(args.dir, args.args[0], args.args[1], " ".join(args.args[2:]))
        print(json.dumps(entry, indent=2))

    elif args.command == "analyze":
        text = " ".join(args.args) if args.args else sys.stdin.read()
        print(json.dumps(analyze_text(text), indent=2))

    elif args.command == "score":
        if not args.args:
            print("Usage: adl.py score <agent_id>", file=sys.stderr)
            sys.exit(1)
        print(json.dumps(calculate_divergence(args.dir, args.args[0]), indent=2))

    elif args.command == "check":
        if not args.args:
            print("Usage: adl.py check <agent_id>", file=sys.stderr)
            sys.exit(1)
        print(json.dumps(check_limit(args.dir, args.args[0], args.threshold), indent=2))

    elif args.command == "history":
        if not args.args:
            print("Usage: adl.py history <agent_id>", file=sys.stderr)
            sys.exit(1)
        print(json.dumps(get_history(args.dir, args.args[0], args.limit), indent=2))

    elif args.command == "reset":
        if not args.args:
            print("Usage: adl.py reset <agent_id>", file=sys.stderr)
            sys.exit(1)
        print(json.dumps(reset(args.dir, args.args[0]), indent=2))


if __name__ == "__main__":
    main()
