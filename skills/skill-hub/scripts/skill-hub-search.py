#!/usr/bin/env python3
"""Skill Hub — search curated catalog + optional live ClawHub registry.

Fuzzy matches name & description, shows credibility score & vet status.

Usage:
  python3 skill-hub-search.py --query "spreadsheet"
  python3 skill-hub-search.py --category "DevOps" --min-score 60
  python3 skill-hub-search.py --query "auth" --live
  python3 skill-hub-search.py --installed
  python3 skill-hub-search.py --not-installed --limit 20
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

CATALOG_PATH = Path(__file__).parent.parent / "references" / "awesome-catalog.json"
WORKSPACE = Path.home() / ".openclaw" / "workspace"


def load_catalog():
    """Load cached catalog from references/."""
    if not CATALOG_PATH.exists():
        print(f"Error: Catalog not found at {CATALOG_PATH}", file=sys.stderr)
        print("Run skill-hub-sync.py first.", file=sys.stderr)
        sys.exit(1)
    with open(CATALOG_PATH) as f:
        return json.load(f)


def fuzzy_match(skill, query):
    """Check if query tokens all appear in name+description (case-insensitive)."""
    tokens = query.lower().split()
    text = f"{skill['name']} {skill.get('description', '')}".lower()
    return all(t in text for t in tokens)


def get_installed_skills():
    """Get installed skill names from ClawHub."""
    try:
        result = subprocess.run(
            ["npx", "clawhub@latest", "list"],
            capture_output=True, text=True, timeout=30,
            cwd=str(WORKSPACE),
        )
        names = set()
        for line in result.stdout.strip().split("\n"):
            parts = line.strip().split()
            if parts:
                names.add(parts[0])
        return names
    except Exception:
        return set()


def search_clawhub_live(query):
    """Search ClawHub registry live via npx."""
    try:
        result = subprocess.run(
            ["npx", "clawhub@latest", "search", query],
            capture_output=True, text=True, timeout=30,
            cwd=str(WORKSPACE),
        )
        skills = []
        for line in result.stdout.strip().split("\n"):
            line = line.strip()
            if not line or line.startswith("Install") or line.startswith("└"):
                continue
            # Lines like: owner/skill-name  description text
            parts = line.split(None, 1)
            if parts:
                name = parts[0].split("/")[-1] if "/" in parts[0] else parts[0]
                desc = parts[1] if len(parts) > 1 else ""
                skills.append({
                    "name": name,
                    "category": "ClawHub Live",
                    "description": desc,
                    "credibility": 30,
                    "vet_status": None,
                    "source": "clawhub-live",
                })
        return skills
    except Exception:
        return []


def vet_label(status):
    """Human-readable vet status."""
    if status == "PASS":
        return "PASS"
    if status == "WARN":
        return "WARN"
    if status == "FAIL":
        return "FAIL"
    return "—"


def score_tier(score):
    """Credibility tier label."""
    if score >= 85:
        return "Trusted"
    if score >= 60:
        return "Good"
    if score >= 30:
        return "Unvetted"
    return "Caution"


def print_table(skills, installed_set):
    """Print skills as formatted table."""
    if not skills:
        print("  No results found.")
        return

    # Header
    print(f"{'Name':<35} {'Cat':<25} {'Score':>5} {'Tier':<9} {'Vet':<5} {'Status':<9} Description")
    print("-" * 130)

    for s in skills:
        name = s["name"][:34]
        cat = s.get("category", "")[:24]
        score = s.get("credibility", 0)
        tier = score_tier(score)
        vet = vet_label(s.get("vet_status"))
        is_installed = name in installed_set or s.get("installed")
        status = "INSTALLED" if is_installed else ""
        desc = s.get("description", "")[:50]
        print(f"{name:<35} {cat:<25} {score:>5} {tier:<9} {vet:<5} {status:<9} {desc}")


def main():
    parser = argparse.ArgumentParser(description="Skill Hub — search skills")
    parser.add_argument("--query", "-q", help="Search by keyword(s)")
    parser.add_argument("--category", "-c", help="Filter by category (partial match)")
    parser.add_argument("--live", "-l", action="store_true", help="Include live ClawHub results")
    parser.add_argument("--installed", "-i", action="store_true", help="Show only installed")
    parser.add_argument("--not-installed", "-n", action="store_true", help="Show only not installed")
    parser.add_argument("--min-score", type=int, default=0, help="Minimum credibility score")
    parser.add_argument("--limit", type=int, default=50, help="Max results (default 50)")
    args = parser.parse_args()

    catalog = load_catalog()
    installed = get_installed_skills()

    # Mark installed in catalog
    for s in catalog["skills"]:
        s["installed"] = s["name"] in installed

    skills = catalog["skills"]

    # Apply filters
    if args.query:
        skills = [s for s in skills if fuzzy_match(s, args.query)]
    if args.category:
        cat_lower = args.category.lower()
        skills = [s for s in skills if cat_lower in s.get("category", "").lower()]
    if args.installed:
        skills = [s for s in skills if s.get("installed")]
    if args.not_installed:
        skills = [s for s in skills if not s.get("installed")]
    if args.min_score > 0:
        skills = [s for s in skills if s.get("credibility", 0) >= args.min_score]

    # Sort by credibility desc
    skills.sort(key=lambda s: s.get("credibility", 0), reverse=True)

    # Live search merge
    if args.live and args.query:
        live = search_clawhub_live(args.query)
        existing_names = {s["name"] for s in skills}
        for ls in live:
            if ls["name"] not in existing_names:
                skills.append(ls)

    # Apply limit
    skills = skills[: args.limit]

    # Print header
    print(f"Catalog: {catalog['total']} skills | {catalog['categories']} categories | Installed: {len(installed)}")
    if args.query:
        print(f"Search: \"{args.query}\"", end="")
    if args.category:
        print(f" | Category: \"{args.category}\"", end="")
    if args.min_score > 0:
        print(f" | Min score: {args.min_score}", end="")
    print(f" | Showing {len(skills)} results\n")

    print_table(skills, installed)

    # Install hint
    if skills and not args.installed:
        print(f"\nInstall: npx clawhub@latest install <skill-name>")
        print(f"Vet:     python3 scripts/skill-hub-vet.py --slug <skill-name>")


if __name__ == "__main__":
    main()
