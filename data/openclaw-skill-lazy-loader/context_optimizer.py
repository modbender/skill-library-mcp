#!/usr/bin/env python3
"""
context_optimizer.py — OpenClaw Skill Lazy Loader
Recommends which skill files to load for a given task description.

No network requests. No subprocess calls. No system modifications.
Runs entirely on local data — reads SKILLS.md in the current directory.

Usage:
    python3 context_optimizer.py recommend "Write a Python script to upload to S3"
    python3 context_optimizer.py list
    python3 context_optimizer.py estimate "your task description"

Part of: OpenClaw Skill Lazy Loader v1.0.0
Author: M Asif Rahman (@Asif2BD) | Apache 2.0
"""

import sys
import os
import re
from pathlib import Path

# ---------------------------------------------------------------------------
# Keyword → skill mapping (extend this to match your SKILLS.md catalog)
# ---------------------------------------------------------------------------
SKILL_KEYWORDS: dict[str, list[str]] = {
    "python": ["python", "py", "pip", "pytest", "django", "flask", "fastapi", "pandas", "numpy"],
    "javascript": ["javascript", "typescript", "js", "ts", "node", "react", "vue", "angular", "npm", "yarn"],
    "git": ["git", "commit", "branch", "pull request", "pr", "merge", "rebase", "push", "clone"],
    "docker": ["docker", "container", "image", "dockerfile", "compose", "kubernetes", "k8s", "helm"],
    "browser": ["browser", "scrape", "playwright", "selenium", "puppeteer", "webpage", "web automation", "ui test"],
    "aws": ["aws", "s3", "lambda", "ec2", "cloudformation", "iam", "dynamodb", "rds", "ecr", "ecs"],
    "sql": ["sql", "database", "postgres", "mysql", "sqlite", "query", "schema", "migration", "orm"],
    "api": ["api", "rest", "endpoint", "openapi", "swagger", "authentication", "oauth", "jwt", "webhook"],
    "shell": ["bash", "shell", "linux", "cron", "systemd", "chmod", "grep", "awk", "sed", "ssh"],
    "review": ["review", "code review", "pr review", "pull request review", "quality", "linting"],
}

CONFIDENCE_COLORS = {
    "high":   "✅ high  ",
    "medium": "⚡ medium",
    "low":    "💭 low   ",
}


def load_skills_catalog(catalog_path: str = "SKILLS.md") -> dict[str, str]:
    """Parse SKILLS.md to extract skill → file path mapping."""
    skills = {}
    path = Path(catalog_path)
    if not path.exists():
        return skills

    for line in path.read_text().splitlines():
        # Match table rows: | Name | `path/to/SKILL.md` | ... |
        m = re.match(r"\|\s*([^|]+?)\s*\|\s*`([^`]+)`\s*\|", line)
        if m:
            name = m.group(1).strip().lower()
            file_path = m.group(2).strip()
            skills[name] = file_path
    return skills


def score_task(task: str) -> dict[str, str]:
    """Score a task description against skill keywords, return skill → confidence."""
    task_lower = task.lower()
    scores: dict[str, int] = {}

    for skill, keywords in SKILL_KEYWORDS.items():
        hits = sum(1 for kw in keywords if kw in task_lower)
        if hits > 0:
            scores[skill] = hits

    if not scores:
        return {}

    max_hits = max(scores.values())
    result = {}
    for skill, hits in sorted(scores.items(), key=lambda x: -x[1]):
        if hits == max_hits:
            result[skill] = "high"
        elif hits >= max_hits * 0.5:
            result[skill] = "medium"
        else:
            result[skill] = "low"
    return result


def cmd_recommend(task: str) -> None:
    """Recommend skills to load for a given task."""
    if not task.strip():
        print("Usage: context_optimizer.py recommend \"your task description\"")
        sys.exit(1)

    catalog = load_skills_catalog()
    scores = score_task(task)

    print(f"\nTask: \"{task}\"")
    print("-" * 60)

    if not scores:
        print("No specific skills detected. Proceed without loading any skill files.")
        print("\nEst. token cost: ~0 (beyond base catalog)\n")
        return

    print("Recommended skills to load:\n")
    total_tokens = 0
    SKILL_SIZES = {
        "python": 600, "javascript": 700, "git": 400, "docker": 550,
        "browser": 800, "aws": 900, "sql": 500, "api": 600,
        "shell": 450, "review": 350,
    }
    load_these = []
    skip_these = []

    for skill, confidence in scores.items():
        file_path = catalog.get(skill, f"skills/{skill}/SKILL.md")
        size = SKILL_SIZES.get(skill, 500)
        badge = CONFIDENCE_COLORS.get(confidence, confidence)

        if confidence in ("high", "medium"):
            load_these.append((skill, file_path, badge, size))
            total_tokens += size
        else:
            skip_these.append((skill, file_path, badge))

    for skill, path, badge, size in load_these:
        print(f"  LOAD  [{badge}] {path}  (~{size} tok)")

    if skip_these:
        print()
        for skill, path, badge in skip_these:
            print(f"  SKIP  [{badge}] {path}  (low relevance)")

    print(f"\nEst. token cost: ~{total_tokens:,} tokens (context loading)")
    if total_tokens == 0:
        print("No files to load — proceed directly.")
    print()


def cmd_list() -> None:
    """List all skills in the catalog."""
    catalog = load_skills_catalog()
    if not catalog:
        print("No SKILLS.md found in current directory.")
        print("Copy SKILLS.md.template → SKILLS.md and fill in your skills.")
        return

    print(f"\nAvailable skills ({len(catalog)} total):\n")
    for name, path in catalog.items():
        print(f"  {name:<20} → {path}")
    print()


def cmd_estimate(task: str) -> None:
    """Estimate token cost with vs without lazy loading."""
    catalog = load_skills_catalog()
    total_skills = max(len(catalog), 5)  # assume at least 5 if catalog missing

    avg_skill_size = 600
    catalog_size = 300
    recommended = len(score_task(task))

    cost_naive = total_skills * avg_skill_size
    cost_lazy = catalog_size + min(recommended, 3) * avg_skill_size

    savings = max(0, cost_naive - cost_lazy)
    pct = int(savings / cost_naive * 100) if cost_naive > 0 else 0

    print(f"\nToken Estimate for: \"{task}\"")
    print("-" * 60)
    print(f"  Without lazy loading: ~{cost_naive:,} tokens ({total_skills} skills loaded)")
    print(f"  With lazy loading:    ~{cost_lazy:,} tokens (catalog + {min(recommended,3)} relevant skills)")
    print(f"  Savings:              ~{savings:,} tokens ({pct}% reduction)\n")


def print_help() -> None:
    print("""
OpenClaw Skill Lazy Loader — context_optimizer.py

Commands:
  recommend "<task>"   Recommend which skills to load for a task
  list                 List all skills in your SKILLS.md catalog
  estimate "<task>"    Show token cost comparison (lazy vs naive)

Examples:
  python3 context_optimizer.py recommend "Write a Python function to parse JSON"
  python3 context_optimizer.py recommend "Build a Docker image and push to ECR"
  python3 context_optimizer.py list
  python3 context_optimizer.py estimate "Review this pull request"

No network access. No file writes. Local data only.
""")


def main() -> None:
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help", "help"):
        print_help()
        return

    cmd = args[0]
    task = " ".join(args[1:]) if len(args) > 1 else ""

    if cmd == "recommend":
        cmd_recommend(task)
    elif cmd == "list":
        cmd_list()
    elif cmd == "estimate":
        cmd_estimate(task)
    else:
        print(f"Unknown command: {cmd}")
        print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
