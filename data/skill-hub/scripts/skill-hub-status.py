#!/usr/bin/env python3
"""Skill Hub — status dashboard.

Shows installed vs catalog coverage, unvetted warnings, recommendations.

Usage:
  python3 skill-hub-status.py
"""

import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

CATALOG_PATH = Path(__file__).parent.parent / "references" / "awesome-catalog.json"
WORKSPACE = Path.home() / ".openclaw" / "workspace"


def load_catalog():
    """Load cached catalog."""
    if not CATALOG_PATH.exists():
        print(f"Error: Catalog not found at {CATALOG_PATH}", file=sys.stderr)
        print("Run skill-hub-sync.py first.", file=sys.stderr)
        sys.exit(1)
    with open(CATALOG_PATH) as f:
        return json.load(f)


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


def score_tier(score):
    """Credibility tier label."""
    if score >= 85:
        return "Trusted"
    if score >= 60:
        return "Good"
    if score >= 30:
        return "Unvetted"
    return "Caution"


def main():
    catalog = load_catalog()
    installed = get_installed_skills()
    skills = catalog["skills"]

    # Mark installed
    for s in skills:
        s["installed"] = s["name"] in installed

    installed_skills = [s for s in skills if s["installed"]]
    not_installed = [s for s in skills if not s["installed"]]

    # --- Header ---
    print("=" * 60)
    print("  SKILL HUB STATUS DASHBOARD")
    print("=" * 60)
    print(f"  Catalog:   {catalog['total']} skills | {catalog['categories']} categories")
    print(f"  Source:    {catalog.get('source', 'unknown')}")
    print(f"  Synced:    {catalog.get('synced_at', 'never')[:19]}")
    print(f"  Installed: {len(installed)} skills")
    print(f"  Coverage:  {len(installed)}/{catalog['total']} ({100*len(installed)//max(1,catalog['total'])}%)")
    print()

    # --- Vet status breakdown ---
    vet_counts = Counter(s.get("vet_status") for s in skills)
    print("  Vet Status (all catalog):")
    print(f"    PASS: {vet_counts.get('PASS', 0)}  WARN: {vet_counts.get('WARN', 0)}  FAIL: {vet_counts.get('FAIL', 0)}  Unscanned: {vet_counts.get(None, 0)}")
    print()

    # --- Category breakdown ---
    cat_counts = Counter(s["category"] for s in skills)
    cat_installed = Counter(s["category"] for s in installed_skills)
    print("  Category Breakdown:")
    print(f"  {'Category':<35} {'Total':>5} {'Installed':>9}")
    print(f"  {'-'*35} {'-'*5} {'-'*9}")
    for cat, count in cat_counts.most_common():
        inst = cat_installed.get(cat, 0)
        marker = " *" if inst > 0 else ""
        print(f"  {cat:<35} {count:>5} {inst:>9}{marker}")
    print()

    # --- Unvetted installed skills (action items) ---
    unvetted_installed = [s for s in installed_skills if s.get("vet_status") is None]
    if unvetted_installed:
        print(f"  ACTION: {len(unvetted_installed)} installed skill(s) not yet vetted:")
        for s in unvetted_installed:
            print(f"    ! {s['name']}")
        print(f"\n  Run: python3 scripts/skill-hub-vet.py --all-installed")
        print()

    # --- Installed skills with FAIL ---
    failed_installed = [s for s in installed_skills if s.get("vet_status") == "FAIL"]
    if failed_installed:
        print(f"  WARNING: {len(failed_installed)} installed skill(s) FAILED security vet:")
        for s in failed_installed:
            print(f"    !! {s['name']} (score: {s.get('credibility', '?')})")
        print()

    # --- Recommendations ---
    # High-credibility skills user doesn't have
    recs = sorted(
        [s for s in not_installed if s.get("credibility", 0) >= 55],
        key=lambda s: s.get("credibility", 0),
        reverse=True,
    )[:10]

    if recs:
        print("  Recommended (high credibility, not installed):")
        print(f"  {'Name':<35} {'Score':>5} {'Tier':<9} Description")
        print(f"  {'-'*35} {'-'*5} {'-'*9} {'-'*40}")
        for s in recs:
            tier = score_tier(s.get("credibility", 0))
            desc = s.get("description", "")[:40]
            print(f"  {s['name']:<35} {s.get('credibility',0):>5} {tier:<9} {desc}")
        print(f"\n  Install: npx clawhub@latest install <skill-name>")

    print()


if __name__ == "__main__":
    main()
