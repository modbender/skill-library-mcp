#!/usr/bin/env python3
"""Skill Hub — export full catalog as browsable table.

Outputs catalog in terminal table or markdown format, grouped by category.
Useful for quick browsing and reference.

Usage:
  python3 skill-hub-table-export.py                           # terminal table
  python3 skill-hub-table-export.py --format markdown          # markdown table
  python3 skill-hub-table-export.py --category "AI"            # filter category
  python3 skill-hub-table-export.py --format markdown > skills.md  # save to file
"""

import argparse
import json
import sys
from pathlib import Path

CATALOG_PATH = Path(__file__).parent.parent / "references" / "awesome-catalog.json"


def load_catalog():
    """Load catalog."""
    if not CATALOG_PATH.exists():
        print(f"Error: Catalog not found. Run skill-hub-sync.py first.", file=sys.stderr)
        sys.exit(1)
    with open(CATALOG_PATH) as f:
        return json.load(f)


def score_tier(score):
    """Credibility tier."""
    if score >= 85:
        return "Trusted"
    if score >= 60:
        return "Good"
    if score >= 30:
        return "Unvetted"
    return "Caution"


def print_terminal_table(skills, category_filter=None):
    """Print formatted terminal table grouped by category."""
    # Group by category
    by_cat = {}
    for s in skills:
        cat = s.get("category", "Uncategorized")
        if category_filter and category_filter.lower() not in cat.lower():
            continue
        by_cat.setdefault(cat, []).append(s)

    if not by_cat:
        print("  No skills found.")
        return

    total_shown = sum(len(v) for v in by_cat.values())
    print(f"Total: {total_shown} skills in {len(by_cat)} categories\n")

    for cat in sorted(by_cat.keys()):
        cat_skills = sorted(by_cat[cat], key=lambda s: s["name"])
        print(f"  [{cat}] ({len(cat_skills)} skills)")
        print(f"  {'Name':<32} {'Score':>5} {'Tier':<9} {'Vet':<5} Description")
        print(f"  {'-'*32} {'-'*5} {'-'*9} {'-'*5} {'-'*45}")
        for s in cat_skills:
            name = s["name"][:31]
            score = s.get("credibility", 0)
            tier = score_tier(score)
            vet = s.get("vet_status") or "—"
            desc = s.get("description", "")[:45]
            print(f"  {name:<32} {score:>5} {tier:<9} {vet:<5} {desc}")
        print()


def print_markdown_table(skills, category_filter=None):
    """Print markdown-formatted table grouped by category."""
    by_cat = {}
    for s in skills:
        cat = s.get("category", "Uncategorized")
        if category_filter and category_filter.lower() not in cat.lower():
            continue
        by_cat.setdefault(cat, []).append(s)

    if not by_cat:
        print("No skills found.")
        return

    total_shown = sum(len(v) for v in by_cat.values())
    print(f"# OpenClaw Skills Catalog ({total_shown} skills)\n")

    for cat in sorted(by_cat.keys()):
        cat_skills = sorted(by_cat[cat], key=lambda s: s["name"])
        print(f"## {cat} ({len(cat_skills)})\n")
        print("| Name | Score | Tier | Vet | Description |")
        print("|------|------:|------|-----|-------------|")
        for s in cat_skills:
            name = s["name"]
            link = s.get("link", "")
            if link:
                name_col = f"[{name}]({link})"
            else:
                name_col = name
            score = s.get("credibility", 0)
            tier = score_tier(score)
            vet = s.get("vet_status") or "—"
            desc = s.get("description", "")[:60].replace("|", "\\|")
            print(f"| {name_col} | {score} | {tier} | {vet} | {desc} |")
        print()


def main():
    parser = argparse.ArgumentParser(description="Skill Hub — export catalog table")
    parser.add_argument("--format", "-f", choices=["terminal", "markdown"], default="terminal",
                        help="Output format (default: terminal)")
    parser.add_argument("--category", "-c", help="Filter by category (partial match)")
    args = parser.parse_args()

    catalog = load_catalog()
    skills = catalog["skills"]

    if args.format == "markdown":
        print_markdown_table(skills, args.category)
    else:
        print_terminal_table(skills, args.category)


if __name__ == "__main__":
    main()
