#!/usr/bin/env python3
"""
Generate daily prospect summary combining all research from today.

Outputs a Discord-friendly summary with key stats, top leads, and pipeline health.

Usage:
    daily_summary.py                    # Today's summary
    daily_summary.py --date 2026-02-09  # Specific date
    daily_summary.py --format discord   # Discord-friendly (no tables)
    daily_summary.py --format markdown  # Full markdown
"""

import argparse
import json
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

WORKSPACE = Path.home() / ".openclaw" / "workspace"
SCRIPTS_DIR = WORKSPACE / "scripts"
PROSPECTS_DIR = WORKSPACE / "leads" / "prospects"
REPORTS_DIR = WORKSPACE / "leads" / "reports"


def count_reports_for_date(target_date: str) -> dict:
    """Count reports and extract key info for a date."""
    clusters = {}
    total = 0
    high_priority = []

    for d in PROSPECTS_DIR.iterdir():
        if d.is_dir() and d.name.startswith(target_date):
            cluster_name = d.name.replace(f"{target_date}-", "").replace("-", " ").title()
            reports = list(d.glob("*.md"))
            count = len(reports)
            clusters[cluster_name] = count
            total += count

            # Check for HIGH priority in report content
            for r in reports:
                try:
                    content = r.read_text()[:1000]
                    if "**Priority:** HIGH" in content or "**Priority Level:** HIGH" in content:
                        # Extract business name from first line
                        first_line = content.split("\n")[0]
                        biz_name = first_line.replace("#", "").replace("—", "-").strip()
                        if " - " in biz_name:
                            biz_name = biz_name.split(" - ")[0].strip()
                        if "Prospect" in biz_name:
                            biz_name = biz_name.replace("Prospect Report", "").replace("Prospect Research:", "").strip()
                        high_priority.append({"name": biz_name, "cluster": cluster_name, "file": str(r)})
                except Exception:
                    pass

    return {
        "total": total,
        "clusters": clusters,
        "high_priority": high_priority
    }


def get_pipeline_stats() -> dict:
    """Get overall pipeline stats."""
    cmd = ["python3", str(SCRIPTS_DIR / "prospect_tracker.py"), "stats"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {}


def format_discord(target_date: str, day_stats: dict, pipeline_stats: dict) -> str:
    """Format summary for Discord (no tables, no markdown tables)."""
    lines = [
        f"📊 **Prospect Pipeline Summary — {target_date}**\n",
    ]

    total = day_stats["total"]
    lines.append(f"**Today:** {total} prospects researched\n")

    # Clusters
    if day_stats["clusters"]:
        lines.append("**Clusters Covered:**")
        for cluster, count in day_stats["clusters"].items():
            lines.append(f"  • {cluster}: {count} prospects")
        lines.append("")

    # Hot leads
    if day_stats["high_priority"]:
        lines.append("🔥 **High-Priority Leads:**")
        for lead in day_stats["high_priority"]:
            lines.append(f"  • **{lead['name']}** ({lead['cluster']})")
        lines.append("")

    # Pipeline health
    if pipeline_stats:
        lines.append("📈 **Pipeline Health:**")
        lines.append(f"  • Total prospects: {pipeline_stats.get('total_prospects', 0)}")
        lines.append(f"  • Duplicates prevented: {pipeline_stats.get('duplicates_prevented', 0)}")
        lines.append(f"  • Industries covered: {pipeline_stats.get('industries_covered', 0)}")
        lines.append(f"  • Last 7 days: {pipeline_stats.get('recent_7_days', 0)}")

        # Priority breakdown
        pb = pipeline_stats.get("priority_breakdown", {})
        if pb:
            lines.append(f"  • Priority: HIGH={pb.get('HIGH', 0)} / MED={pb.get('MEDIUM', 0)} / LOW={pb.get('LOW', 0)}")

    lines.append("")
    return "\n".join(lines)


def format_markdown(target_date: str, day_stats: dict, pipeline_stats: dict) -> str:
    """Format full markdown summary."""
    lines = [
        f"# Daily Prospect Summary — {target_date}\n",
        f"## Today's Results\n",
        f"- **Prospects Researched:** {day_stats['total']}",
        f"- **Clusters Covered:** {len(day_stats['clusters'])}",
        f"- **High-Priority Leads:** {len(day_stats['high_priority'])}\n",
    ]

    if day_stats["clusters"]:
        lines.append("### Clusters\n")
        for cluster, count in day_stats["clusters"].items():
            lines.append(f"- {cluster}: {count} prospects")
        lines.append("")

    if day_stats["high_priority"]:
        lines.append("### 🔥 High-Priority Leads\n")
        for lead in day_stats["high_priority"]:
            lines.append(f"1. **{lead['name']}** ({lead['cluster']})")
            lines.append(f"   - Report: `{lead['file']}`")
        lines.append("")

    if pipeline_stats:
        lines.append("## Pipeline Health\n")
        lines.append(f"- Total prospects: {pipeline_stats.get('total_prospects', 0)}")
        lines.append(f"- Duplicates prevented: {pipeline_stats.get('duplicates_prevented', 0)}")
        lines.append(f"- Industries covered: {pipeline_stats.get('industries_covered', 0)}")
        lines.append(f"- Recent 7 days: {pipeline_stats.get('recent_7_days', 0)}")
        lines.append(f"- Date range: {pipeline_stats.get('date_range', 'N/A')}\n")

    lines.append(f"---\n*Generated by SEO Prospector Skill*")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Daily prospect summary")
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--format", choices=["discord", "markdown"], default="discord")
    parser.add_argument("--out", type=Path, help="Save to file")
    args = parser.parse_args()

    target_date = date.today().isoformat() if args.date == "today" else args.date

    day_stats = count_reports_for_date(target_date)
    pipeline_stats = get_pipeline_stats()

    if args.format == "discord":
        output = format_discord(target_date, day_stats, pipeline_stats)
    else:
        output = format_markdown(target_date, day_stats, pipeline_stats)

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(output)
        print(f"Saved to {args.out}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
