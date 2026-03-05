#!/usr/bin/env python3
"""
Batch prospect research — research multiple prospects from today's cluster rotation.

Reads cluster-rotation.json, picks businesses from KLW directory, runs research_prospect.py
on each, generates a rollup summary.

Usage:
    batch_research.py --run run_1|run_2|run_3     # Research today's Nth scheduled cluster
    batch_research.py --cluster "Restaurants" --limit 5  # Research specific cluster
    batch_research.py --input prospects.json       # Research from JSON file
"""

import argparse
import csv
import json
import subprocess
import sys
from datetime import date
from pathlib import Path
from difflib import SequenceMatcher

WORKSPACE = Path.home() / ".openclaw" / "workspace"
SCRIPTS_DIR = WORKSPACE / "scripts"
SKILL_SCRIPTS = Path(__file__).parent
KLW_CSV = WORKSPACE / "leads" / "data" / "klw-directory.csv"
ROTATION_PATH = WORKSPACE / "leads" / "data" / "cluster-rotation.json"
PROSPECTS_DIR = WORKSPACE / "leads" / "prospects"
REPORTS_DIR = WORKSPACE / "leads" / "reports"


def load_klw_directory() -> list[dict]:
    """Load KLW directory CSV into list of dicts."""
    if not KLW_CSV.exists():
        print(f"Error: KLW directory not found at {KLW_CSV}", file=sys.stderr)
        return []
    rows = []
    with open(KLW_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def get_today_clusters() -> dict:
    """Get today's scheduled clusters from rotation."""
    cmd = ["python3", str(SCRIPTS_DIR / "prospect_tracker.py"), "today-clusters"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {}


def check_duplicate(business_name: str) -> bool:
    """Return True if already researched recently."""
    cmd = [
        "python3", str(SCRIPTS_DIR / "prospect_tracker.py"),
        "check", "--business", business_name, "--days", "14"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    try:
        data = json.loads(result.stdout)
        return data.get("found", False)
    except json.JSONDecodeError:
        return False


def fuzzy_match(text: str, patterns: list[str]) -> bool:
    """Check if text fuzzy-matches any pattern."""
    text_lower = text.lower()
    for p in patterns:
        if p.lower() in text_lower or SequenceMatcher(None, text_lower, p.lower()).ratio() > 0.6:
            return True
    return False


def select_prospects(cluster: dict, directory: list[dict], limit: int = 5) -> list[dict]:
    """Select prospects from KLW directory for a cluster, filtering out duplicates."""
    klw_filter = cluster.get("klw_filter", [])
    industries = cluster.get("industries", [])
    filter_terms = klw_filter or industries

    candidates = []
    for biz in directory:
        industry = biz.get("industry", "")
        if fuzzy_match(industry, filter_terms):
            # Must have a website to audit
            website = biz.get("website", "").strip()
            if website and website.startswith("http"):
                candidates.append(biz)

    # Filter out already-researched
    fresh = []
    for c in candidates:
        name = c.get("name", "")
        if not check_duplicate(name):
            fresh.append(c)

    # Take up to limit
    return fresh[:limit]


def research_one(biz: dict, cluster_name: str, priority: str = "MEDIUM") -> dict:
    """Run research_prospect.py for one business."""
    domain = biz.get("website", "").replace("http://", "").replace("https://", "").rstrip("/")
    cmd = [
        "python3", str(SKILL_SCRIPTS / "research_prospect.py"),
        "--business", biz.get("name", "Unknown"),
        "--domain", domain,
        "--industry", biz.get("industry", "Unknown"),
        "--priority", priority,
        "--cluster", cluster_name,
        "--output-json"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"status": "error", "business": biz.get("name"), "stderr": result.stderr[:500]}


def generate_rollup(cluster_name: str, results: list[dict], tier: str) -> str:
    """Generate a markdown rollup of all prospects in this batch."""
    today = date.today()
    success = [r for r in results if r.get("status") == "success"]
    errors = [r for r in results if r.get("status") != "success"]

    lines = [
        f"# {cluster_name} Cluster — Prospect Rollup\n",
        f"**Date:** {today.strftime('%B %d, %Y')}",
        f"**Cluster:** {cluster_name} (Tier {tier})",
        f"**Prospects Researched:** {len(success)}",
        f"**Errors:** {len(errors)}\n",
        "---\n",
        "## Prospects\n",
    ]

    for i, r in enumerate(success, 1):
        biz = r.get("business", "Unknown")
        path = r.get("report_path", "")
        lines.append(f"### {i}. {biz}")
        lines.append(f"- Report: `{path}`")
        summary = r.get("research_summary", "")
        if summary:
            lines.append(f"- Summary: {summary[:200]}")
        lines.append("")

    if errors:
        lines.append("## Errors\n")
        for e in errors:
            lines.append(f"- {e.get('business', 'Unknown')}: {e.get('stderr', e.get('error', 'unknown'))[:200]}")
        lines.append("")

    lines.append("---\n")
    lines.append(f"*Generated by SEO Prospector Skill on {today.isoformat()}*\n")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Batch SEO prospect research")
    parser.add_argument("--run", choices=["run_1", "run_2", "run_3", "morning", "afternoon", "evening"],
                        help="Run today's Nth scheduled cluster (morning=run_1, afternoon=run_2, evening=run_3)")
    parser.add_argument("--cluster", help="Research a specific cluster by name")
    parser.add_argument("--input", type=Path, help="JSON file with prospect list")
    parser.add_argument("--limit", type=int, default=5, help="Max prospects per cluster")
    parser.add_argument("--priority", default="MEDIUM", help="Default priority for batch")
    args = parser.parse_args()

    # Map friendly names to run keys
    run_map = {"morning": "run_1", "afternoon": "run_2", "evening": "run_3"}
    run_key = run_map.get(args.run, args.run)

    if args.input:
        # Research from JSON file
        prospects = json.loads(args.input.read_text())
        cluster_name = "manual"
        tier = "N/A"
        for p in prospects[:args.limit]:
            biz = {
                "name": p.get("business", ""),
                "website": p.get("domain", ""),
                "industry": p.get("industry", "Unknown")
            }
            result = research_one(biz, cluster_name, p.get("priority", args.priority))
            print(json.dumps(result))
        return

    if args.cluster:
        # Find cluster by name in rotation
        rotation = json.loads(ROTATION_PATH.read_text())
        cluster_data = None
        for c in rotation.get("clusters", []):
            if c["name"].lower() == args.cluster.lower():
                cluster_data = c
                break
        if not cluster_data:
            print(f"Error: Cluster '{args.cluster}' not found in rotation", file=sys.stderr)
            sys.exit(1)
        cluster_name = cluster_data["name"]
        tier = cluster_data.get("tier", "B")
    elif run_key:
        # Get today's scheduled cluster for this run
        today_data = get_today_clusters()
        runs = today_data.get("runs", {})
        if run_key not in runs:
            print(f"No cluster scheduled for {run_key} today ({today_data.get('weekday', 'unknown')})", file=sys.stderr)
            print(f"Available runs: {list(runs.keys())}", file=sys.stderr)
            sys.exit(1)
        run_info = runs[run_key]
        cluster_name = run_info["cluster_name"]
        tier = run_info.get("tier", "B")

        # Build cluster_data from run_info
        cluster_data = {
            "name": cluster_name,
            "industries": run_info.get("industries", []),
            "klw_filter": run_info.get("klw_filter", []),
            "tier": tier
        }
    else:
        parser.print_help()
        sys.exit(1)

    # Load directory and select prospects
    print(f"📂 Loading KLW directory...", file=sys.stderr)
    directory = load_klw_directory()
    if not directory:
        sys.exit(1)

    print(f"🔍 Selecting prospects for {cluster_name}...", file=sys.stderr)
    prospects = select_prospects(cluster_data, directory, limit=args.limit)

    if not prospects:
        print(f"⚠️  No fresh prospects found for {cluster_name} (all researched or no matches)", file=sys.stderr)
        sys.exit(0)

    print(f"📋 Researching {len(prospects)} prospects for {cluster_name}...\n", file=sys.stderr)

    # Research each
    results = []
    for i, biz in enumerate(prospects, 1):
        print(f"[{i}/{len(prospects)}] {biz['name']}...", file=sys.stderr)
        result = research_one(biz, cluster_name, args.priority)
        results.append(result)
        status = result.get("status", "unknown")
        if status == "success":
            print(f"  ✅ Done → {result.get('report_path', 'saved')}", file=sys.stderr)
        else:
            print(f"  ❌ {status}: {result.get('error', result.get('stderr', ''))[:100]}", file=sys.stderr)

    # Generate rollup
    rollup_md = generate_rollup(cluster_name, results, tier)
    slug = cluster_name.lower().replace(" ", "-").replace("/", "-")
    rollup_path = REPORTS_DIR / f"{date.today().isoformat()}-{slug}-rollup.md"
    rollup_path.parent.mkdir(parents=True, exist_ok=True)
    rollup_path.write_text(rollup_md)

    print(f"\n📊 Rollup saved: {rollup_path}", file=sys.stderr)
    print(f"✅ Batch complete: {len([r for r in results if r.get('status') == 'success'])} / {len(results)} successful", file=sys.stderr)

    # Output JSON summary
    summary = {
        "cluster": cluster_name,
        "tier": tier,
        "total": len(results),
        "success": len([r for r in results if r.get("status") == "success"]),
        "errors": len([r for r in results if r.get("status") != "success"]),
        "rollup_path": str(rollup_path),
        "results": results
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
