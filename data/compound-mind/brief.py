#!/usr/bin/env python3
"""
CompoundMind v0.1 - Pre-Session Briefing
Generates targeted briefing from accumulated wisdom before any task.
Uses rule-based synthesis (no API required). LLM synthesis optional.

Usage: python brief.py "task description or topic"
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

from index import search, get_db, init_db

DATA_DIR = BASE_DIR / "data"
BRIEFS_DIR = DATA_DIR / "briefs"

# Domain keyword detection
DOMAIN_KEYWORDS = {
    "trading": ["trade", "trading", "polymarket", "bet", "market", "kelly", "position", "usdc",
                "btc", "crypto", "buy", "sell", "order", "wallet", "price", "pnl", "snipe"],
    "coding": ["code", "git", "python", "script", "bug", "deploy", "build", "function", "api",
               "error", "debug", "cron", "service", "fix", "install", "implement"],
    "social": ["tweet", "post", "twitter", "x ", " x.", "moltx", "moltbook", "farcaster",
               "instagram", "youtube", "content", "followers", "viral", "upload", "publish"],
    "communication": ["chartist", "message", "telegram", "reply", "conversation", "talk"],
    "system": ["server", "vps", "cron", "systemd", "config", "env", "memory", "skill", "heartbeat"],
}


def detect_domains(task: str) -> list[str]:
    task_lower = task.lower()
    matches = []
    for domain, keywords in DOMAIN_KEYWORDS.items():
        if any(kw in task_lower for kw in keywords):
            matches.append(domain)
    return matches if matches else ["general"]


def detect_persons(task: str) -> list[str]:
    known = ["chartist", "xanalystx"]
    return [p for p in known if p in task.lower()]


def gather_wisdom(task: str, domains: list[str]) -> dict:
    """Pull relevant wisdom from the index."""
    wisdom = {"lessons": [], "decisions": [], "facts": [], "relationships": [], "skills": []}

    # Task-based search
    results = search(task, limit=20)
    for r in results:
        cat = r.get("category", "")
        key = {"lesson": "lessons", "decision": "decisions", "fact": "facts",
               "relationship": "relationships", "skill": "skills"}.get(cat)
        if key:
            wisdom[key].append(r)

    # Domain-specific pull
    for domain in domains:
        if domain == "general":
            continue
        domain_results = search(task, domain=domain, limit=10)
        for r in domain_results:
            cat = r.get("category", "")
            key = {"lesson": "lessons", "decision": "decisions", "fact": "facts",
                   "relationship": "relationships", "skill": "skills"}.get(cat)
            if key and r not in wisdom[key]:
                wisdom[key].append(r)

    # Person-specific relationship pull
    for person in detect_persons(task):
        rel_results = search(person, category="relationship", limit=5)
        for r in rel_results:
            if r not in wisdom["relationships"]:
                wisdom["relationships"].append(r)

    return wisdom


def build_briefing_rule_based(task: str, wisdom: dict, domains: list[str]) -> str:
    """Build a structured briefing without LLM."""
    lines = []

    domain_str = ", ".join(domains)
    lines.append(f"PRE-SESSION BRIEF: {task.upper()}")
    lines.append(f"Domains: {domain_str}")
    lines.append("=" * 50)

    # Top lessons
    negative_lessons = [r for r in wisdom["lessons"] if r.get("quality") == "negative" or r.get("outcome") == "negative"]
    positive_lessons = [r for r in wisdom["lessons"] if r.get("quality") == "positive" or r.get("outcome") == "positive"]
    other_lessons = [r for r in wisdom["lessons"] if r not in negative_lessons and r not in positive_lessons]

    if positive_lessons or other_lessons:
        lines.append("\nTOP LESSONS:")
        shown = 0
        for r in (positive_lessons + other_lessons)[:5]:
            text = r.get("text", "").strip()
            if text:
                date_str = r.get("source_date", "")[:7]
                lines.append(f"  - {text[:200]} [{date_str}]")
                shown += 1
                if shown >= 4:
                    break

    if negative_lessons:
        lines.append("\nWATCH OUT (past failures):")
        for r in negative_lessons[:3]:
            text = r.get("text", "").strip()
            if text:
                date_str = r.get("source_date", "")[:7]
                lines.append(f"  * {text[:200]} [{date_str}]")

    if wisdom["decisions"]:
        lines.append("\nPAST DECISIONS:")
        for r in wisdom["decisions"][:3]:
            text = r.get("text", "").strip()
            quality = r.get("quality", "")
            q_tag = f"[{quality}]" if quality and quality != "neutral" else ""
            if text:
                lines.append(f"  -> {text[:200]} {q_tag}")

    if wisdom["facts"]:
        lines.append("\nKEY FACTS:")
        for r in wisdom["facts"][:5]:
            text = r.get("text", "").strip()
            if text:
                lines.append(f"  i {text[:200]}")

    if wisdom["relationships"]:
        lines.append("\nRELATIONSHIP CONTEXT:")
        for r in wisdom["relationships"][:3]:
            text = r.get("text", "").strip()
            if text:
                lines.append(f"  @ {text[:200]}")

    if wisdom["skills"]:
        lines.append("\nSKILL HISTORY:")
        for r in wisdom["skills"][:3]:
            text = r.get("text", "").strip()
            if text:
                lines.append(f"  ^ {text[:200]}")

    total = sum(len(v) for v in wisdom.values())
    if total == 0:
        lines.append("\nNo relevant past experience found for this task.")
        lines.append("This may be new territory - proceed carefully and document learnings.")
    else:
        lines.append(f"\n[{total} relevant items from wisdom index]")

    return "\n".join(lines)


def build_briefing_llm(task: str, wisdom: dict, domains: list[str]) -> str:
    """Build briefing with LLM synthesis using COMPOUND_MIND_LLM_KEY."""
    llm_key = os.environ.get("COMPOUND_MIND_LLM_KEY") or os.environ.get("ANTHROPIC_API_KEY")
    if not llm_key:
        raise RuntimeError("No LLM key available")

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=llm_key)

        # Build wisdom summary for prompt
        sections = []
        if wisdom["lessons"]:
            sections.append("LESSONS:")
            for r in wisdom["lessons"][:6]:
                outcome = r.get("outcome") or r.get("quality") or ""
                sections.append(f"  [{outcome}] {r['text'][:200]} ({r.get('source_date', '')[:7]})")
        if wisdom["decisions"]:
            sections.append("DECISIONS:")
            for r in wisdom["decisions"][:4]:
                sections.append(f"  {r['text'][:200]}")
        if wisdom["facts"]:
            sections.append("KEY FACTS:")
            for r in wisdom["facts"][:5]:
                sections.append(f"  {r['text'][:150]}")
        if wisdom["relationships"]:
            sections.append("RELATIONSHIPS:")
            for r in wisdom["relationships"][:3]:
                sections.append(f"  {r['text'][:150]}")

        wisdom_text = "\n".join(sections) or "No relevant experience found."
        domain_str = ", ".join(domains)

        prompt = f"""You are CompoundMind - a system surfacing relevant past experience before each task.

Task: {task}
Domains: {domain_str}

Relevant accumulated wisdom:
---
{wisdom_text}
---

Generate a sharp pre-session briefing. Format:
1. One sentence framing the task from experience angle
2. TOP LESSONS (max 4 bullets)
3. WATCH OUT (max 3 bullets - past failures to avoid)
4. QUICK FACTS (max 4 bullets - key context)
5. One call-to-action sentence

Rules: Sharp and direct. NEVER use em dash. Max 300 words. Skip empty sections."""

        response = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=800,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text.strip()
    except Exception as e:
        raise RuntimeError(f"LLM call failed: {e}")


def save_brief(task: str, briefing: str) -> Path:
    BRIEFS_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    task_slug = task[:40].replace(" ", "_").replace("/", "-")
    path = BRIEFS_DIR / f"{ts}_{task_slug}.md"
    path.write_text(f"# Brief: {task}\n\n{briefing}\n")
    return path


def brief(task: str, save: bool = True, raw: bool = False, use_llm: bool = False) -> str:
    """Generate and return a pre-session briefing."""
    conn = get_db()
    init_db(conn)
    count = conn.execute("SELECT COUNT(*) FROM entries").fetchone()[0]
    conn.close()

    if count == 0:
        return "Wisdom index is empty. Run: python3 compound_mind.py sync"

    domains = detect_domains(task)
    wisdom = gather_wisdom(task, domains)

    if raw:
        # Raw JSON dump of wisdom
        return json.dumps({k: [{"text": r.get("text"), "category": r.get("category"),
                                 "source_date": r.get("source_date")} for r in v]
                           for k, v in wisdom.items()}, indent=2)

    # Try LLM first if requested, fallback to rule-based
    if use_llm:
        try:
            briefing = build_briefing_llm(task, wisdom, domains)
        except RuntimeError as e:
            print(f"  [warn] LLM unavailable ({e}), using rule-based synthesis", file=sys.stderr)
            briefing = build_briefing_rule_based(task, wisdom, domains)
    else:
        briefing = build_briefing_rule_based(task, wisdom, domains)

    if save:
        path = save_brief(task, briefing)
        briefing += f"\n\n[Saved: {path.name}]"

    return briefing


def main():
    parser = argparse.ArgumentParser(description="CompoundMind Pre-Session Briefing")
    parser.add_argument("task", nargs="+", help="Task description")
    parser.add_argument("--raw", action="store_true", help="Show raw wisdom JSON")
    parser.add_argument("--no-save", action="store_true", help="Don't save brief to file")
    parser.add_argument("--llm", action="store_true", help="Use LLM synthesis (requires COMPOUND_MIND_LLM_KEY)")
    args = parser.parse_args()

    task = " ".join(args.task)
    print(f"Brief for: '{task}'\n")

    result = brief(task, save=not args.no_save, raw=args.raw, use_llm=args.llm)
    print(result)


if __name__ == "__main__":
    main()
