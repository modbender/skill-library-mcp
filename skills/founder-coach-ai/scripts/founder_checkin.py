#!/usr/bin/env python3
"""Founder Coach — Daily check-in and accountability tracker."""

import argparse
import json
import os
import sys
import random
from datetime import datetime, timedelta
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

JOURNAL_DIR = os.environ.get("FOUNDER_JOURNAL_DIR",
    os.path.join(os.path.expanduser("~"), ".openclaw", "workspace", "memory", "founder-journal"))

AI_QUESTIONS = [
    "What manual process am I doing that AI could handle?",
    "Where is my moat — data, workflow, distribution, or brand?",
    "What's my cost-per-serve and how do I halve it?",
    "Am I building a product or a feature that GPT will add next quarter?",
    "What would a 10-person AI-native company do differently?",
    "What proprietary data or feedback loops am I creating?",
    "If OpenAI built my feature tomorrow, what would still be mine?",
    "Can I charge for outcomes instead of access?",
    "What am I uniquely positioned to build that AI can't replicate?",
    "Am I spending time on $10/hr tasks or $1000/hr tasks?",
    "What can a 3-person AI-native startup build in 3 months that competes with me?",
    "What switching costs have I built?",
]

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


def ensure_dirs():
    """Create journal directories if needed."""
    for sub in ["", "weekly", "decisions"]:
        Path(os.path.join(JOURNAL_DIR, sub)).mkdir(parents=True, exist_ok=True)


def today_str():
    return datetime.now().strftime("%Y-%m-%d")


def get_entry_path(date_str=None):
    if not date_str:
        date_str = today_str()
    return os.path.join(JOURNAL_DIR, f"{date_str}.md")


def read_entry(date_str):
    path = get_entry_path(date_str)
    if os.path.isfile(path):
        with open(path) as f:
            return f.read()
    return None


def append_entry(content, date_str=None):
    """Append to today's journal entry."""
    if not date_str:
        date_str = today_str()
    path = get_entry_path(date_str)
    mode = "a" if os.path.isfile(path) else "w"
    with open(path, mode) as f:
        if mode == "w":
            f.write(f"# Founder Journal — {date_str}\n\n")
        f.write(content + "\n\n")
    return path


def call_llm(prompt, system="You are a concise, actionable founder coach. Be direct, no fluff."):
    """Call LLM via OpenRouter for personalized coaching."""
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        return None

    payload = json.dumps({
        "model": "anthropic/claude-haiku-4.5",
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": 500,
        "temperature": 0.7,
    }).encode()

    req = Request(OPENROUTER_URL, data=payload, headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://agxntsix.ai",
        "X-Title": "Founder Coach",
    })

    try:
        with urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
            return data["choices"][0]["message"]["content"]
    except Exception:
        return None


def get_recent_entries(days=7):
    """Read recent journal entries."""
    entries = {}
    for i in range(days):
        date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        content = read_entry(date)
        if content:
            entries[date] = content
    return entries


def get_commitments(content):
    """Extract commitments from entry content."""
    commitments = []
    in_priorities = False
    for line in content.split("\n"):
        stripped = line.strip()
        if "priorities" in stripped.lower() or "commitments" in stripped.lower():
            in_priorities = True
            continue
        if in_priorities and stripped.startswith(("1.", "2.", "3.", "- [", "- ")):
            done = "[x]" in stripped.lower() or "✅" in stripped
            text = stripped.lstrip("123.-[] x✅").strip()
            if text:
                commitments.append({"text": text, "done": done})
        if in_priorities and stripped == "" and commitments:
            in_priorities = False
    return commitments


def cmd_morning(args):
    """Generate morning brief."""
    ensure_dirs()
    now = datetime.now()
    question = random.choice(AI_QUESTIONS)

    # Check yesterday
    yesterday = (now - timedelta(days=1)).strftime("%Y-%m-%d")
    yesterday_entry = read_entry(yesterday)
    yesterday_recap = ""
    if yesterday_entry:
        commitments = get_commitments(yesterday_entry)
        if commitments:
            done = sum(1 for c in commitments if c["done"])
            total = len(commitments)
            yesterday_recap = f"Yesterday: {done}/{total} commitments completed ({done/total*100:.0f}%)\n"
            for c in commitments:
                status = "✅" if c["done"] else "❌"
                yesterday_recap += f"  {status} {c['text']}\n"

    # Generate personalized prompt if LLM available
    ai_insight = ""
    if yesterday_entry:
        ai_response = call_llm(
            f"Based on this founder's yesterday journal, give ONE sharp insight or challenge for today (2-3 sentences max):\n\n{yesterday_entry[:1000]}"
        )
        if ai_response:
            ai_insight = f"\n### 🤖 AI Coach Says\n{ai_response}\n"

    brief = f"""## 🌅 Morning Brief — {now.strftime('%A, %B %d, %Y')}

{yesterday_recap}
### Today's Top 3 Priorities
1. [ ] 
2. [ ] 
3. [ ] 

### 🎯 AI Founder Question
> {question}

{ai_insight}---
*Fill in your priorities above, then get to work.*
"""

    path = append_entry(brief)
    print(brief)
    print(f"\n📝 Saved to: {path}")


def cmd_evening(args):
    """Generate evening reflection prompt."""
    ensure_dirs()
    now = datetime.now()

    # Check today's entry for commitments
    today_entry = read_entry(today_str())
    commitment_review = ""
    if today_entry:
        commitments = get_commitments(today_entry)
        if commitments:
            commitment_review = "### Commitment Review\n"
            for i, c in enumerate(commitments, 1):
                commitment_review += f"{i}. [ ] {c['text']} — completed? notes:\n"
            commitment_review += "\n"

    reflection = f"""## 🌙 Evening Reflection — {now.strftime('%A, %B %d, %Y')}

{commitment_review}### Wins
- 

### Losses / Lessons
- 

### Tomorrow's Top 3
1. [ ] 
2. [ ] 
3. [ ] 

### Energy Check (1-5)
- Energy: [ ]
- Focus: [ ]
- Motivation: [ ]

### One Thing
- Stop doing: 
- Start doing: 

---
*Be honest. Growth comes from truth, not comfort.*
"""

    path = append_entry(reflection)
    print(reflection)
    print(f"\n📝 Saved to: {path}")


def cmd_weekly(args):
    """Generate weekly review."""
    ensure_dirs()
    now = datetime.now()
    week_num = now.isocalendar()[1]

    # Gather week's data
    entries = get_recent_entries(7)
    total_commitments = 0
    total_done = 0
    for date, content in entries.items():
        comms = get_commitments(content)
        total_commitments += len(comms)
        total_done += sum(1 for c in comms if c["done"])

    rate = (total_done / total_commitments * 100) if total_commitments > 0 else 0

    # AI summary if available
    ai_summary = ""
    if entries:
        combined = "\n---\n".join(f"## {d}\n{c[:500]}" for d, c in sorted(entries.items()))
        ai_response = call_llm(
            f"Summarize this founder's week in 3-4 bullet points. Identify patterns, wins, and one area to improve:\n\n{combined[:3000]}"
        )
        if ai_response:
            ai_summary = f"\n### 🤖 AI Weekly Analysis\n{ai_response}\n"

    review = f"""## 📊 Weekly Review — Week {week_num} ({now.strftime('%Y')})

### Performance
- Commitments made: {total_commitments}
- Commitments kept: {total_done} ({rate:.0f}%)
- Journal entries: {len(entries)}/7 days

{ai_summary}
### Key Metrics
| Metric | Last Week | This Week | Target |
|--------|-----------|-----------|--------|
| Revenue | | | |
| Users | | | |
| Key Progress | | | |

### Moat Check
- Data moat: 
- Workflow moat: 
- Distribution moat: 

### Decisions Made
| Decision | Outcome | Lesson |
|----------|---------|--------|
| | | |

### Next Week #1 Priority


---
"""

    weekly_path = os.path.join(JOURNAL_DIR, "weekly", f"{now.strftime('%Y')}-W{week_num:02d}.md")
    with open(weekly_path, "w") as f:
        f.write(review)

    print(review)
    print(f"\n📝 Saved to: {weekly_path}")


def cmd_stats(args):
    """Show accountability stats."""
    entries = get_recent_entries(30)

    total_entries = len(entries)
    total_commitments = 0
    total_done = 0
    weekly = {}

    for date, content in sorted(entries.items()):
        comms = get_commitments(content)
        total_commitments += len(comms)
        total_done += sum(1 for c in comms if c["done"])

        # Group by week
        dt = datetime.strptime(date, "%Y-%m-%d")
        week = dt.strftime("%Y-W%W")
        if week not in weekly:
            weekly[week] = {"commitments": 0, "done": 0, "entries": 0}
        weekly[week]["commitments"] += len(comms)
        weekly[week]["done"] += sum(1 for c in comms if c["done"])
        weekly[week]["entries"] += 1

    rate = (total_done / total_commitments * 100) if total_commitments > 0 else 0

    print("\n═══ Founder Coach Stats (30 days) ═══")
    print(f"Journal entries: {total_entries}")
    print(f"Total commitments: {total_commitments}")
    print(f"Completed: {total_done} ({rate:.0f}%)")
    print(f"Consistency: {total_entries}/30 days ({total_entries/30*100:.0f}%)")

    if rate >= 90:
        print("Rating: 🟢 Crushing it (or setting easy goals?)")
    elif rate >= 70:
        print("Rating: 🟡 Healthy stretch zone")
    elif rate >= 50:
        print("Rating: 🟠 Overcommitting — focus on fewer things")
    else:
        print("Rating: 🔴 Reset — commit to 1-2 things only")

    if weekly:
        print("\nWeekly Breakdown:")
        for week, data in sorted(weekly.items()):
            w_rate = (data["done"] / data["commitments"] * 100) if data["commitments"] > 0 else 0
            bar = "█" * int(w_rate / 10) + "░" * (10 - int(w_rate / 10))
            print(f"  {week}: {bar} {w_rate:.0f}% ({data['done']}/{data['commitments']})")

    print("═════════════════════════════════════")


def cmd_history(args):
    """Show recent entries."""
    days = args.days if hasattr(args, 'days') else 7
    entries = get_recent_entries(days)

    if not entries:
        print(f"No entries in the last {days} days.")
        return

    for date in sorted(entries.keys(), reverse=True):
        print(f"\n{'─' * 40}")
        print(entries[date][:500])
        if len(entries[date]) > 500:
            print(f"  ... ({len(entries[date])} chars total)")


def main():
    parser = argparse.ArgumentParser(description="Founder Coach — Daily accountability")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("morning", help="Morning brief")
    sub.add_parser("evening", help="Evening reflection")
    sub.add_parser("weekly", help="Weekly review")
    sub.add_parser("stats", help="View accountability stats")

    hist = sub.add_parser("history", help="View recent entries")
    hist.add_argument("--days", type=int, default=7)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    cmds = {
        "morning": cmd_morning,
        "evening": cmd_evening,
        "weekly": cmd_weekly,
        "stats": cmd_stats,
        "history": cmd_history,
    }
    cmds[args.command](args)


if __name__ == "__main__":
    main()
