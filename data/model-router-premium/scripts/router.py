#!/usr/bin/env python3
"""
Simple model router CLI/library.
Reads a JSON file with models, each model entry should include:
  - name (string)
  - provider (string)
  - cost_score (number): lower is cheaper
  - capabilities (list of strings): e.g. ["chat","code","summarize"]

Heuristics:
  - short tasks (<=40 chars) and low complexity keywords -> choose cheapest model
  - presence of keywords like "fix", "code", "debug", "legal", "medical" -> prefer capable models
  - explicit --min-capability or --prefer flags override

Output: prints chosen model JSON line and short reasoning
"""
import argparse
import json
import os
import sys
from typing import List, Dict

COMPLEX_KEYWORDS = ["design", "analysis", "explain", "compare", "translate", "optimize", "refactor", "bug", "debug", "legal", "medical", "code", "implement", "security", "accuracy"]


def load_models(path: str) -> List[Dict]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def score_task(task: str) -> int:
    t = task.lower()
    score = 0
    # length heuristic
    if len(t) > 200:
        score += 3
    elif len(t) > 80:
        score += 2
    elif len(t) > 40:
        score += 1
    # keywords
    for kw in COMPLEX_KEYWORDS:
        if kw in t:
            score += 2
    return score


def pick_model(models: List[Dict], task: str, min_capability: str=None, prefer: List[str]=None) -> Dict:
    task_score = score_task(task)
    # Sort models by cost then capability (lower cost_score preferred)
    candidates = sorted(models, key=lambda m: (m.get("cost_score", 1000), -m.get("power_score", 0)))

    # Apply min_capability filter if provided
    if min_capability:
        candidates = [m for m in candidates if min_capability in m.get("capabilities", [])]

    # If task is low complexity, return the cheapest that supports basic "chat" capability
    if task_score <= 1:
        for m in candidates:
            if "chat" in m.get("capabilities", []) or "general" in m.get("capabilities", []):
                reason = f"low complexity (score={task_score}) → cheapest suitable model"
                return {"model": m, "reason": reason}

    # For higher complexity, prefer models that list "analysis" or have higher power_score
    if task_score >= 3:
        # apply prefers
        if prefer:
            for p in prefer:
                for m in candidates:
                    if p.lower() in m.get("name", "").lower() or p.lower() in m.get("provider", "").lower():
                        reason = f"task_complex (score={task_score}) + preference {p} → selected"
                        return {"model": m, "reason": reason}
        # pick highest power_score among the top N cheapest
        sorted_by_power = sorted(candidates, key=lambda m: (-m.get("power_score", 0), m.get("cost_score", 1000)))
        if sorted_by_power:
            m = sorted_by_power[0]
            reason = f"high complexity (score={task_score}) → best-power model"
            return {"model": m, "reason": reason}

    # Fallback: return cheapest overall
    m = candidates[0]
    reason = f"fallback cheapest (score={task_score})"
    return {"model": m, "reason": reason}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--models", required=True, help="path to models JSON")
    p.add_argument("--task", required=True, help="task description")
    p.add_argument("--min-capability", help="require model to have this capability (e.g. code, analysis)")
    p.add_argument("--prefer", action='append', help="prefer model/provider name (can repeat)")
    p.add_argument("--dry", action='store_true', help="don't print JSON output, only reasoning")
    args = p.parse_args()

    models = load_models(args.models)
    res = pick_model(models, args.task, args.min_capability, args.prefer)

    if not args.dry:
        print(json.dumps(res["model"], ensure_ascii=False, indent=2))
    print("---")
    print("Reason:", res["reason"]) 

if __name__ == '__main__':
    main()
