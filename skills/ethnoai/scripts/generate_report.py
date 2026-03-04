#!/usr/bin/env python3
"""
UXR Observer v2.0 - Daily Report Generator
Reads today's observations and surveys, produces a comprehensive Markdown report
with ethnographic analysis, cost tracking, verbatim galleries, and super summary references.
"""

import json
import os
import sys
import zipfile
from datetime import datetime
from pathlib import Path
from collections import Counter, defaultdict

BASE_DIR = Path.home() / ".uxr-observer"
SESSIONS_DIR = BASE_DIR / "sessions"
REPORTS_DIR = BASE_DIR / "reports"


def load_jsonl(filepath: Path) -> list:
    """Load a JSONL file into a list of dicts."""
    records = []
    if filepath.exists():
        with open(filepath) as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        records.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
    return records


def format_cost(amount) -> str:
    """Format a cost amount as a dollar string."""
    if amount is None:
        return "N/A"
    return f"${amount:.4f}" if amount < 0.01 else f"${amount:.2f}"


def generate_report(date_str: str = None) -> str:
    """Generate the daily report for a given date (default: today)."""
    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")

    today_dir = SESSIONS_DIR / date_str
    if not today_dir.exists():
        return f"No data found for {date_str}."

    observations = load_jsonl(today_dir / "observations.jsonl")
    surveys = load_jsonl(today_dir / "surveys.jsonl")

    if not observations and not surveys:
        return f"No observations or surveys recorded for {date_str}."

    # Separate survey types
    post_task_surveys = [s for s in surveys if s.get("survey_type") == "post_task"]
    eod_surveys = [s for s in surveys if s.get("survey_type") == "end_of_day"]

    # --- Metrics ---
    total_tasks = len(observations)
    outcomes = Counter(obs.get("outcome", "unknown") for obs in observations)
    categories = Counter(obs.get("task_category", "other") for obs in observations)

    # Friction
    all_friction = []
    for obs in observations:
        signals = obs.get("friction_signals", [])
        if isinstance(signals, list):
            all_friction.extend([s for s in signals if s != "none"])
    friction_types = Counter(all_friction)
    tasks_with_friction = sum(
        1 for obs in observations
        if any(s != "none" for s in (obs.get("friction_signals", []) if isinstance(obs.get("friction_signals"), list) else []))
    )

    # Sentiment
    tasks_with_delight = sum(
        1 for obs in observations
        if "delighted" in (obs.get("sentiment_signals", []) if isinstance(obs.get("sentiment_signals"), list) else [])
    )

    # Satisfaction scores from post-task surveys
    ratings = []
    for survey in post_task_surveys:
        r = survey.get("responses", {}).get("quality_rating")
        if r is None:
            r = survey.get("responses", {}).get("experience_rating")
        if isinstance(r, (int, float)) and 1 <= r <= 5:
            ratings.append(r)
    avg_rating = sum(ratings) / len(ratings) if ratings else None

    # End-of-day rating
    eod_rating = None
    if eod_surveys:
        eod_rating = eod_surveys[-1].get("responses", {}).get("overall_rating")

    # Cost tracking
    total_cost = 0.0
    cost_source = "estimated"
    cost_by_category = defaultdict(lambda: {"cost": 0.0, "count": 0, "ratings": []})
    cost_by_model = defaultdict(lambda: {"cost": 0.0, "count": 0})
    most_expensive_task = None
    max_cost = 0.0

    for i, obs in enumerate(observations):
        cost = obs.get("cost", {})
        task_cost = cost.get("task_total_cost_usd") or cost.get("actual_cost_usd") or cost.get("estimated_cost_usd") or 0
        if cost.get("cost_source") == "actual":
            cost_source = "actual"
        total_cost += task_cost

        cat = obs.get("task_category", "other")
        cost_by_category[cat]["cost"] += task_cost
        cost_by_category[cat]["count"] += 1

        model = cost.get("model_used", "unknown")
        cost_by_model[model]["cost"] += task_cost
        cost_by_model[model]["count"] += 1

        if task_cost > max_cost:
            max_cost = task_cost
            most_expensive_task = (obs.get("user_intent", f"Task {i+1}"), task_cost, cost)

    avg_cost = total_cost / total_tasks if total_tasks > 0 else 0

    # PII redaction summary
    pii_tasks = 0
    pii_categories = Counter()
    for obs in observations:
        pii = obs.get("pii_redacted", {})
        if pii.get("count", 0) > 0:
            pii_tasks += 1
            for cat in pii.get("categories", []):
                pii_categories[cat] += 1

    # Use cases
    use_cases = defaultdict(lambda: {"tasks": [], "ratings": [], "cost": 0.0, "pattern": None})
    for i, obs in enumerate(observations):
        uc_id = obs.get("use_case_id", f"uc-{i+1}")
        uc_label = obs.get("use_case_label", obs.get("user_intent", "Unnamed task"))
        use_cases[uc_id]["label"] = uc_label
        use_cases[uc_id]["tasks"].append(i + 1)
        use_cases[uc_id]["pattern"] = obs.get("workflow_pattern", use_cases[uc_id]["pattern"])
        cost = obs.get("cost", {})
        use_cases[uc_id]["cost"] += cost.get("task_total_cost_usd", 0)

    # Match ratings to use cases via related_observation_id or index
    for survey in post_task_surveys:
        r = survey.get("responses", {}).get("quality_rating")
        if r is None:
            r = survey.get("responses", {}).get("experience_rating")
        ea = survey.get("ethnographic_analysis", {})
        uc_id = ea.get("use_case_id")
        if uc_id and isinstance(r, (int, float)):
            use_cases[uc_id]["ratings"].append(r)

    # Verbatims collection
    verbatims_positive = []
    verbatims_pain = []
    verbatims_expectations = []
    verbatims_suggestions = []
    verbatims_workflow = []

    for obs in observations:
        for v in obs.get("verbatims", []):
            header = v.get("header", "").lower()
            entry = f'**[{v.get("header", "Notable quote")}]**\n> "{v.get("quote", "")}"'
            if any(w in header for w in ["delight", "positive", "praise", "great", "impress"]):
                verbatims_positive.append(entry)
            elif any(w in header for w in ["frustrat", "pain", "error", "wrong", "fail"]):
                verbatims_pain.append(entry)
            elif any(w in header for w in ["expect", "mental model", "thought", "assumed"]):
                verbatims_expectations.append(entry)
            elif any(w in header for w in ["suggest", "wish", "improve", "better", "could"]):
                verbatims_suggestions.append(entry)
            else:
                verbatims_workflow.append(entry)

    # Also collect from survey responses
    for survey in post_task_surveys:
        responses = survey.get("responses", {})
        if responses.get("improvement_suggestion"):
            verbatims_suggestions.append(
                f'**[Improvement suggestion (post-task survey)]**\n> "{responses["improvement_suggestion"]}"'
            )
        if responses.get("friction_description"):
            verbatims_pain.append(
                f'**[Friction described in survey]**\n> "{responses["friction_description"]}"'
            )

    # Super summary files
    supersummary_dir = today_dir / "supersummary"
    supersummary_files = sorted(supersummary_dir.glob("*.md")) if supersummary_dir.exists() else []
    supersummary_zip = supersummary_dir / "supersummary.zip" if supersummary_dir.exists() else None

    # --- Build Report ---
    report = f"# UXR Daily Report — {date_str}\n\n"

    # Executive Summary
    report += "## Executive Summary\n"
    report += f"Observed {total_tasks} tasks across the day. "
    if avg_rating:
        report += f"Average post-task satisfaction was {avg_rating:.1f}/5. "
    if eod_rating:
        report += f"Overall day rating: {eod_rating}/5. "
    report += f"Total cost: {format_cost(total_cost)} ({cost_source}). "
    if tasks_with_friction:
        report += f"Friction was reported in {tasks_with_friction} tasks ({tasks_with_friction/total_tasks*100:.0f}%)."
    report += "\n\n"

    # By the Numbers
    report += "## By the Numbers\n"
    report += f"- **Tasks completed:** {total_tasks}\n"
    report += f"- **Post-task surveys completed:** {len(post_task_surveys)} / {total_tasks} possible ({len(post_task_surveys)/total_tasks*100:.0f}%)\n" if total_tasks > 0 else ""
    report += f"- **Average post-task satisfaction:** {avg_rating:.1f} / 5\n" if avg_rating else "- **Average post-task satisfaction:** N/A\n"
    report += f"- **Overall day rating:** {eod_rating} / 5\n" if eod_rating else "- **Overall day rating:** N/A\n"
    report += f"- **Tasks with reported friction:** {tasks_with_friction} ({tasks_with_friction/total_tasks*100:.0f}%)\n" if total_tasks > 0 else ""
    report += f"- **Tasks with reported delight:** {tasks_with_delight} ({tasks_with_delight/total_tasks*100:.0f}%)\n" if total_tasks > 0 else ""
    report += f"- **Total daily cost:** {format_cost(total_cost)} ({cost_source})\n"
    report += f"- **Average cost per task:** {format_cost(avg_cost)}\n"
    report += f"- **PII redaction events:** {sum(pii_categories.values())} across {pii_tasks} tasks\n\n"

    # Cost Summary
    report += "## Cost Summary\n\n"
    report += f"### Daily Total\n"
    report += f"- **Total:** {format_cost(total_cost)} ({cost_source})\n"
    if cost_by_model:
        model_parts = [f"{m}: {format_cost(d['cost'])} ({d['count']} tasks)" for m, d in cost_by_model.items()]
        report += f"- **Model breakdown:** {', '.join(model_parts)}\n"
    report += "\n"

    if cost_by_category:
        report += "### By Task Category\n"
        report += "| Category | Tasks | Total Cost | Avg Cost |\n"
        report += "|----------|-------|-----------|----------|\n"
        for cat, data in sorted(cost_by_category.items(), key=lambda x: x[1]["cost"], reverse=True):
            avg_cat = data["cost"] / data["count"] if data["count"] > 0 else 0
            report += f"| {cat} | {data['count']} | {format_cost(data['cost'])} | {format_cost(avg_cat)} |\n"
        report += "\n"

    if most_expensive_task:
        name, cost_val, cost_data = most_expensive_task
        report += f"### Most Expensive Task\n"
        report += f"**{name}** — {format_cost(cost_val)}"
        if cost_data.get("tokens_input"):
            report += f" ({cost_data['tokens_input']} in / {cost_data.get('tokens_output', 0)} out)"
        report += "\n\n"

    # Use Case Analysis
    if use_cases:
        report += "## Use Case Analysis\n\n"
        for uc_id, uc_data in use_cases.items():
            label = uc_data.get("label", "Unknown")
            task_list = ", ".join(str(t) for t in uc_data["tasks"])
            avg_uc_rating = sum(uc_data["ratings"]) / len(uc_data["ratings"]) if uc_data["ratings"] else None
            report += f"### {uc_id}: {label}\n"
            report += f"- **Tasks involved:** {task_list}\n"
            report += f"- **Workflow pattern:** {uc_data.get('pattern', 'N/A')}\n"
            if avg_uc_rating:
                report += f"- **Average satisfaction:** {avg_uc_rating:.1f}/5\n"
            report += f"- **Total cost:** {format_cost(uc_data['cost'])}\n\n"

    # Task-by-Task Breakdown
    report += "## Task-by-Task Breakdown\n\n"
    for i, obs in enumerate(observations):
        intent = obs.get("user_intent", f"Task {i+1}")
        report += f"### Task {i+1}: {intent}\n"
        report += f"**What happened:** {obs.get('task_context_summary', 'N/A')}\n"
        report += f"**Use case:** {obs.get('use_case_label', 'N/A')}\n"
        cost = obs.get("cost", {})
        task_cost = cost.get("task_total_cost_usd", 0)
        report += f"**Cost:** {format_cost(task_cost)} ({cost.get('cost_source', 'N/A')})\n"

        # Find matching survey
        matched_survey = None
        for survey in post_task_surveys:
            if survey.get("related_observation_id") == obs.get("observation_id"):
                matched_survey = survey
                break

        if matched_survey:
            responses = matched_survey.get("responses", {})
            rating = responses.get("quality_rating") or responses.get("experience_rating")
            report += f"**Rating:** {rating}/5\n" if rating else ""
            if responses.get("rating_factors"):
                report += f'\n**[User\'s rationale for their rating]**\n> "{responses["rating_factors"]}"\n'
            if responses.get("experienced_friction") in ("yes", "Yes", True):
                report += f"**Friction reported:** Yes\n"
                if responses.get("friction_description"):
                    report += f'\n**[What frustrated the user]**\n> "{responses["friction_description"]}"\n'
            else:
                report += f"**Friction reported:** No\n"
            if responses.get("improvement_suggestion"):
                report += f'\n**[What the user would improve]**\n> "{responses["improvement_suggestion"]}"\n'

        friction_str = ", ".join(obs.get("friction_signals", ["none"])) if isinstance(obs.get("friction_signals"), list) else "none"
        sentiment_str = ", ".join(obs.get("sentiment_signals", ["neutral"])) if isinstance(obs.get("sentiment_signals"), list) else "neutral"
        report += f"\n**Observed friction signals:** {friction_str}\n"
        report += f"**Observed sentiment signals:** {sentiment_str}\n"

        needs = obs.get("inferred_needs", [])
        if needs:
            report += f"**Inferred needs:** {', '.join(needs)}\n"
        report += "\n---\n\n"

    # Verbatim Gallery
    report += "## Verbatim Gallery\n\n"

    if verbatims_positive:
        report += "### Positive Experiences\n"
        report += "\n\n".join(verbatims_positive) + "\n\n"
    if verbatims_pain:
        report += "### Pain Points & Frustrations\n"
        report += "\n\n".join(verbatims_pain) + "\n\n"
    if verbatims_expectations:
        report += "### Expectations & Mental Models\n"
        report += "\n\n".join(verbatims_expectations) + "\n\n"
    if verbatims_suggestions:
        report += "### Suggestions & Wishes\n"
        report += "\n\n".join(verbatims_suggestions) + "\n\n"
    if verbatims_workflow:
        report += "### Workflow & Context\n"
        report += "\n\n".join(verbatims_workflow) + "\n\n"

    # End-of-Day Reflection
    if eod_surveys:
        eod = eod_surveys[-1]
        responses = eod.get("responses", {})
        report += "## End-of-Day Reflection\n\n"
        report += f"**Overall day rating:** {responses.get('overall_rating', 'N/A')}/5\n\n"
        if responses.get("highlights"):
            report += f'**[Highlights the user recalled]**\n> "{responses["highlights"]}"\n\n'
        if responses.get("lowlights"):
            report += f'**[Lowlights the user recalled]**\n> "{responses["lowlights"]}"\n\n'
        if responses.get("improvement_suggestion"):
            report += f'**[What the user would change]**\n> "{responses["improvement_suggestion"]}"\n\n'

    # PII Summary
    if pii_tasks > 0:
        report += "## PII & Sensitive Work Summary\n"
        report += f"- **Tasks involving sensitive data:** {pii_tasks}\n"
        report += f"- **PII categories encountered:** {', '.join(f'{cat}: {count}' for cat, count in pii_categories.most_common())}\n\n"

    # Patterns & Insights (placeholder for LLM-generated insights)
    report += "## Patterns & Insights\n\n"
    report += "### What's Working Well\n"
    report += "- *(To be filled by Distiller Agent with specific insights grounded in verbatims)*\n\n"
    report += "### Recurring Pain Points\n"
    report += "- *(To be filled by Distiller Agent)*\n\n"
    report += "### Unmet Needs (from Ethnographic Analysis)\n"
    report += "- *(To be filled by Distiller Agent)*\n\n"
    report += "### Emerging Themes\n"
    report += "- *(To be filled by Distiller Agent)*\n\n"

    report += "## Recommendations\n"
    report += "*(To be generated by Distiller Agent based on today's evidence)*\n\n"

    # Attachments
    if supersummary_files:
        report += "## Attachments\n"
        report += f"- **Super Summary:** {len(supersummary_files)} notable task case studies attached\n"
        if supersummary_zip and supersummary_zip.exists():
            report += f"  - See: `{supersummary_zip}`\n"
        report += "  - Files:\n"
        for f in supersummary_files:
            report += f"    - {f.name}\n"
        report += "\n"

    # Footer
    report += "---\n"
    report += f"*This report was generated locally by UXR Observer v2.0. No data has been transmitted externally.*\n"
    report += f"*Report file: ~/.uxr-observer/reports/{date_str}-daily-report.md*\n"
    report += f"*Super summary: ~/.uxr-observer/sessions/{date_str}/supersummary/supersummary.zip*\n"
    report += f"*To share: review and edit this file, then ask OpenClaw to email it to whoever you'd like.*\n"

    # Save report
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORTS_DIR / f"{date_str}-daily-report.md"
    report_path.write_text(report)

    print(f"[UXR Observer] Report saved to {report_path}")
    return report


def zip_supersummary(date_str: str = None):
    """Zip all super summary case studies for the given date."""
    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")

    ss_dir = SESSIONS_DIR / date_str / "supersummary"
    if not ss_dir.exists():
        return None

    md_files = sorted(ss_dir.glob("*.md"))
    if not md_files:
        return None

    zip_path = ss_dir / "supersummary.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for md_file in md_files:
            zf.write(md_file, md_file.name)

    print(f"[UXR Observer] Super summary zipped to {zip_path}")
    return str(zip_path)


if __name__ == "__main__":
    date = sys.argv[1] if len(sys.argv) > 1 else None
    if len(sys.argv) > 2 and sys.argv[2] == "--zip-supersummary":
        zip_supersummary(date)
    else:
        print(generate_report(date))
