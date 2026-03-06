#!/usr/bin/env python3
"""
CompoundMind v0.1 - Growth Tracker
Measures intelligence growth over time.
Tracks decision quality, lesson retention, skill progression.
LLM report generation is optional (set COMPOUND_MIND_LLM_KEY for enhanced reports).
"""

import os
import sys
import json
import argparse
import difflib
from datetime import datetime, date, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
EXP_DIR = DATA_DIR / "experiences"
GROWTH_FILE = DATA_DIR / "growth.json"

sys.path.insert(0, str(BASE_DIR))


def load_growth() -> dict:
    if GROWTH_FILE.exists():
        return json.loads(GROWTH_FILE.read_text())
    return {
        "sessions": [],
        "skill_scores": {},
        "growth_snapshots": [],
        "baseline_date": None
    }


def save_growth(data: dict):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    GROWTH_FILE.write_text(json.dumps(data, indent=2))


def analyze_experience_quality(exp_dir: Path) -> dict:
    """Analyze all experience files for quality signals."""
    exp_files = sorted(exp_dir.glob("*.json"))
    if not exp_files:
        return {}

    stats = {
        "total_lessons": 0,
        "positive_lessons": 0,
        "negative_lessons": 0,
        "mixed_lessons": 0,
        "neutral_lessons": 0,
        "total_decisions": 0,
        "good_decisions": 0,
        "bad_decisions": 0,
        "neutral_decisions": 0,
        "total_skills": 0,
        "total_facts": 0,
        "total_relationships": 0,
        "by_domain": {},
        "by_month": {},
        "high_importance_lessons": [],
        "all_negative_lessons": [],
        "domain_skill_count": {}
    }

    for f in exp_files:
        try:
            exp = json.loads(f.read_text())
        except Exception:
            continue

        source_date = exp.get("source_date", "unknown")
        month = source_date[:7] if len(source_date) >= 7 else "unknown"

        lessons = exp.get("lessons", [])
        decisions = exp.get("decisions", [])
        skills = exp.get("skill_updates", [])
        facts = exp.get("facts", [])
        relationships = exp.get("relationships", [])

        stats["total_lessons"] += len(lessons)
        stats["total_decisions"] += len(decisions)
        stats["total_skills"] += len(skills)
        stats["total_facts"] += len(facts)
        stats["total_relationships"] += len(relationships)

        stats["by_month"].setdefault(month, {
            "lessons": 0, "decisions": 0, "skills": 0,
            "positive": 0, "negative": 0, "good": 0, "bad": 0
        })
        stats["by_month"][month]["lessons"] += len(lessons)
        stats["by_month"][month]["decisions"] += len(decisions)
        stats["by_month"][month]["skills"] += len(skills)

        for l in lessons:
            outcome = l.get("outcome", "neutral")
            domain = l.get("domain", "general")
            importance = l.get("importance", 3)

            if outcome == "positive":
                stats["positive_lessons"] += 1
                stats["by_month"][month]["positive"] += 1
            elif outcome == "negative":
                stats["negative_lessons"] += 1
                stats["by_month"][month]["negative"] += 1
                stats["all_negative_lessons"].append({
                    "text": l.get("text", ""),
                    "domain": domain,
                    "date": source_date
                })
            elif outcome == "mixed":
                stats["mixed_lessons"] += 1
            else:
                stats["neutral_lessons"] += 1

            # Domain tracking
            stats["by_domain"].setdefault(domain, {
                "lessons": 0, "positive": 0, "negative": 0,
                "decisions": 0, "good": 0, "bad": 0, "skills": 0
            })
            stats["by_domain"][domain]["lessons"] += 1
            if outcome in ("positive",):
                stats["by_domain"][domain]["positive"] += 1
            elif outcome in ("negative",):
                stats["by_domain"][domain]["negative"] += 1

            if importance >= 4:
                stats["high_importance_lessons"].append({
                    "text": l.get("text", ""),
                    "domain": domain,
                    "date": source_date,
                    "importance": importance
                })

        for d in decisions:
            quality = d.get("quality", "neutral")
            domain = d.get("domain", "general")

            stats["by_domain"].setdefault(domain, {
                "lessons": 0, "positive": 0, "negative": 0,
                "decisions": 0, "good": 0, "bad": 0, "skills": 0
            })
            stats["by_domain"][domain]["decisions"] += 1

            if quality == "good":
                stats["good_decisions"] += 1
                stats["by_domain"][domain]["good"] += 1
                stats["by_month"][month]["good"] += 1
            elif quality == "bad":
                stats["bad_decisions"] += 1
                stats["by_domain"][domain]["bad"] += 1
                stats["by_month"][month]["bad"] += 1
            else:
                stats["neutral_decisions"] += 1

        for s in skills:
            domain = s.get("domain", "general")
            stats["by_domain"].setdefault(domain, {
                "lessons": 0, "positive": 0, "negative": 0,
                "decisions": 0, "good": 0, "bad": 0, "skills": 0
            })
            stats["by_domain"][domain]["skills"] += 1

    # Sort high importance by importance desc
    stats["high_importance_lessons"].sort(key=lambda x: x.get("importance", 3), reverse=True)

    return stats


def detect_repeated_mistakes(stats: dict) -> list[dict]:
    """Find negative lessons that appear in multiple files - failure to learn."""
    from collections import defaultdict

    negative_by_domain = defaultdict(list)
    for lesson in stats.get("all_negative_lessons", []):
        domain = lesson.get("domain", "general")
        negative_by_domain[domain].append(lesson)

    repeated = []
    for domain, lessons in negative_by_domain.items():
        if len(lessons) < 2:
            continue
        grouped = []
        used = set()
        for i, l in enumerate(lessons):
            if i in used:
                continue
            group = [l]
            for j, l2 in enumerate(lessons):
                if j <= i or j in used:
                    continue
                ratio = difflib.SequenceMatcher(None, l["text"].lower()[:100], l2["text"].lower()[:100]).ratio()
                if ratio > 0.35:
                    group.append(l2)
                    used.add(j)
            if len(group) >= 2:
                grouped.append({
                    "domain": domain,
                    "occurrences": group,
                    "count": len(group),
                    "representative": group[0]["text"][:200]
                })
            used.add(i)
        repeated.extend(grouped)

    return sorted(repeated, key=lambda x: x["count"], reverse=True)[:10]


def calculate_growth_score(stats: dict) -> dict:
    """Composite growth score 0-100."""
    total = max(stats.get("total_lessons", 0), 1)
    positive = stats.get("positive_lessons", 0)
    negative = stats.get("negative_lessons", 0)
    total_dec = max(stats.get("total_decisions", 0), 1)
    good_dec = stats.get("good_decisions", 0)
    bad_dec = stats.get("bad_decisions", 0)

    lesson_positive_rate = positive / total
    lesson_negative_rate = negative / total
    decision_quality_rate = good_dec / total_dec if stats.get("total_decisions", 0) > 0 else 0.5

    # Volume score - more data = better intelligence base (caps at 20pts)
    volume_score = min(total / 50.0 * 20, 20)

    # Quality score - positive lesson rate
    quality_score = lesson_positive_rate * 40

    # Decision score
    decision_score = decision_quality_rate * 30

    # Penalty for negative rate
    penalty = lesson_negative_rate * 10

    composite = max(0, int(quality_score + decision_score + volume_score - penalty))

    # Month-over-month trend (if we have 2+ months)
    by_month = stats.get("by_month", {})
    months = sorted(by_month.keys())
    trend = "stable"
    if len(months) >= 2:
        recent = by_month[months[-1]]
        older = by_month[months[-2]]
        recent_pos = recent.get("positive", 0)
        older_pos = older.get("positive", 0)
        if recent_pos > older_pos + 1:
            trend = "improving"
        elif older_pos > recent_pos + 1:
            trend = "declining"

    return {
        "score": composite,
        "lesson_positive_rate": round(lesson_positive_rate, 3),
        "lesson_negative_rate": round(lesson_negative_rate, 3),
        "decision_quality_rate": round(decision_quality_rate, 3),
        "total_lessons": stats.get("total_lessons", 0),
        "total_decisions": stats.get("total_decisions", 0),
        "trend": trend
    }


def build_report_rule_based(stats: dict, repeated: list, growth_score: dict) -> str:
    """Build growth report without LLM."""
    lines = []
    score = growth_score.get("score", 0)
    trend = growth_score.get("trend", "stable")

    trend_emoji = {"improving": "^ IMPROVING", "declining": "v DECLINING", "stable": "= STABLE"}.get(trend, "= STABLE")

    lines.append("COMPOUND MIND - GROWTH REPORT")
    lines.append("=" * 50)
    lines.append(f"Growth Score: {score}/100  [{trend_emoji}]")
    lines.append(f"Lesson positive rate: {growth_score.get('lesson_positive_rate', 0):.0%}")
    lines.append(f"Lesson negative rate: {growth_score.get('lesson_negative_rate', 0):.0%}")
    lines.append(f"Decision quality rate: {growth_score.get('decision_quality_rate', 0):.0%}")
    lines.append(f"Total lessons: {stats.get('total_lessons', 0)} | Skills: {stats.get('total_skills', 0)} | Facts: {stats.get('total_facts', 0)}")
    lines.append("")

    # Domain breakdown
    by_domain = stats.get("by_domain", {})
    if by_domain:
        lines.append("BY DOMAIN:")
        for domain, d in sorted(by_domain.items(), key=lambda x: x[1]["lessons"], reverse=True):
            pos_rate = f"{d['positive']/max(d['lessons'],1):.0%}" if d["lessons"] else "n/a"
            dec_qual = f"{d['good']}/{d['decisions']}d" if d["decisions"] else "no decisions"
            lines.append(f"  {domain:15} {d['lessons']:3} lessons ({pos_rate} positive) | {dec_qual}")
        lines.append("")

    # High importance lessons
    hi = stats.get("high_importance_lessons", [])[:5]
    if hi:
        lines.append("HIGH-VALUE LESSONS:")
        for l in hi:
            lines.append(f"  [{l['domain']}] {l['text'][:150]} ({l['date'][:7]})")
        lines.append("")

    # Repeated mistakes
    if repeated:
        lines.append(f"REPEATED MISTAKES ({len(repeated)} patterns found):")
        for m in repeated[:5]:
            lines.append(f"  [{m['domain']}] x{m['count']}: {m['representative'][:120]}")
        lines.append("")
        lines.append("ACTION: These patterns repeat. Address them directly.")
    else:
        lines.append("REPEATED MISTAKES: None detected. Clean learning record.")
        lines.append("")

    # Monthly trend
    by_month = stats.get("by_month", {})
    if by_month:
        lines.append("MONTHLY ACTIVITY:")
        for month in sorted(by_month.keys())[-6:]:  # Last 6 months
            d = by_month[month]
            lines.append(f"  {month}: {d['lessons']}L {d['decisions']}D {d['skills']}S (+{d.get('positive',0)}/-{d.get('negative',0)})")

    return "\n".join(lines)


def build_report_llm(stats: dict, repeated: list, growth_score: dict) -> str:
    """Build report with LLM synthesis."""
    llm_key = os.environ.get("COMPOUND_MIND_LLM_KEY")
    if not llm_key:
        raise RuntimeError("COMPOUND_MIND_LLM_KEY not set")

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=llm_key)

        domain_summary = []
        for domain, d in stats.get("by_domain", {}).items():
            domain_summary.append(
                f"  {domain}: {d['lessons']} lessons ({d['positive']} positive, {d['negative']} negative), "
                f"{d['good']} good decisions, {d['bad']} bad decisions"
            )

        mistake_summary = [f"  [{m['domain']}] x{m['count']}: '{m['representative'][:100]}'" for m in repeated[:5]]
        hi_lessons = [f"  [{l['domain']}] {l['text'][:120]} ({l['date'][:7]})" for l in stats.get("high_importance_lessons", [])[:5]]

        data_block = f"""Score: {growth_score['score']}/100 ({growth_score['trend']})
Lesson positive rate: {growth_score['lesson_positive_rate']:.0%}
Decision quality rate: {growth_score['decision_quality_rate']:.0%}
Total: {stats['total_lessons']} lessons, {stats['total_decisions']} decisions, {stats['total_skills']} skills

By domain:
{chr(10).join(domain_summary)}

High-importance lessons:
{chr(10).join(hi_lessons) or '  None'}

Repeated mistakes:
{chr(10).join(mistake_summary) or '  None'}"""

        response = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=800,
            messages=[{"role": "user", "content": f"""Generate a sharp, honest AI agent growth report.

{data_block}

Format: verdict sentence, strongest domains, weakest domains, repeated mistakes callout, top lessons, ONE improvement focus.
Rules: Direct and honest. Numbers matter. NEVER em dash. Max 400 words."""}]
        )
        return response.content[0].text.strip()
    except Exception as e:
        raise RuntimeError(f"LLM call failed: {e}")


def record_session(task: str, quality_score: int, domain: str, notes: str = ""):
    """Record a manual session quality score."""
    growth = load_growth()
    growth["sessions"].append({
        "date": datetime.now().isoformat(),
        "task": task,
        "domain": domain,
        "quality_score": quality_score,
        "notes": notes
    })
    growth["skill_scores"].setdefault(domain, [])
    growth["skill_scores"][domain].append(quality_score)
    save_growth(growth)
    print(f"Recorded: {task} [{domain}] score={quality_score}/10")


def main():
    parser = argparse.ArgumentParser(description="CompoundMind Growth Tracker")
    sub = parser.add_subparsers(dest="cmd")

    r = sub.add_parser("report", help="Generate growth report")
    r.add_argument("--llm", action="store_true", help="Use LLM synthesis (requires COMPOUND_MIND_LLM_KEY)")

    rec = sub.add_parser("record", help="Record a session quality score")
    rec.add_argument("task", help="Task description")
    rec.add_argument("score", type=int, help="Quality score 1-10")
    rec.add_argument("--domain", default="general")
    rec.add_argument("--notes", default="")

    sub.add_parser("mistakes", help="Show repeated mistake patterns")

    args = parser.parse_args()

    if args.cmd == "report":
        print("Analyzing experience database...")
        stats = analyze_experience_quality(EXP_DIR)
        if not stats.get("total_lessons"):
            print("No experience data found. Run: python3 compound_mind.py sync")
            return

        repeated = detect_repeated_mistakes(stats)
        growth_score = calculate_growth_score(stats)

        if args.llm:
            try:
                report = build_report_llm(stats, repeated, growth_score)
            except RuntimeError as e:
                print(f"[warn] {e}, using rule-based report", file=sys.stderr)
                report = build_report_rule_based(stats, repeated, growth_score)
        else:
            report = build_report_rule_based(stats, repeated, growth_score)

        print(report)

        # Save snapshot
        growth = load_growth()
        if not growth["baseline_date"]:
            growth["baseline_date"] = date.today().isoformat()
        growth["growth_snapshots"].append({
            "date": date.today().isoformat(),
            "score": growth_score["score"],
            "total_lessons": stats.get("total_lessons", 0),
            "trend": growth_score["trend"]
        })
        save_growth(growth)

    elif args.cmd == "record":
        record_session(args.task, args.score, args.domain, getattr(args, "notes", ""))

    elif args.cmd == "mistakes":
        stats = analyze_experience_quality(EXP_DIR)
        if not stats:
            print("No data. Run: python3 compound_mind.py sync")
            return
        repeated = detect_repeated_mistakes(stats)
        if not repeated:
            print("No repeated mistakes detected. Clean learning record.")
        else:
            print(f"Found {len(repeated)} repeated mistake patterns:\n")
            for i, m in enumerate(repeated, 1):
                print(f"{i}. [{m['domain']}] Repeated {m['count']}x")
                for occ in m["occurrences"][:3]:
                    print(f"   {occ['date'][:7]}: {occ['text'][:120]}")
                print()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
