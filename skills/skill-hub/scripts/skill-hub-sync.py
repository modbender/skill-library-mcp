#!/usr/bin/env python3
"""Skill Hub — sync catalog from VoltAgent/awesome-openclaw-skills GitHub repo.

Fetches README.md, parses skill entries, computes initial credibility scores,
preserves existing vet results, shows diff of changes.

Usage:
  python3 skill-hub-sync.py
"""

import json
import re
import sys
import urllib.request
from datetime import datetime
from pathlib import Path

CATALOG_PATH = Path(__file__).parent.parent / "references" / "awesome-catalog.json"
RAW_URL = "https://raw.githubusercontent.com/VoltAgent/awesome-openclaw-skills/master/README.md"


def fetch_readme():
    """Fetch README.md from GitHub raw URL."""
    print(f"Fetching from {RAW_URL} ...")
    try:
        req = urllib.request.Request(RAW_URL, headers={"User-Agent": "skill-hub/1.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            content = resp.read().decode("utf-8")
        print(f"  Fetched {len(content)} bytes")
        return content
    except Exception as e:
        print(f"Error fetching README: {e}", file=sys.stderr)
        sys.exit(1)


def parse_skills(readme_text):
    """Parse skill entries from awesome-list README markdown.

    Supports two category header formats:
      1. Markdown: ## Category Name / ### Category Name
      2. HTML details/summary: <summary><h3>Category Name</h3></summary>

    Skill entry format: - [skill-name](link) - Description text
    """
    skills = []
    current_category = ""
    categories = set()

    skip_headers = {
        "table of contents", "contents", "contributing",
        "license", "acknowledgments", "about",
        "awesome openclaw skills", "installation",
        "clawhub cli", "manual installation", "alternative",
        "why this list exists", "why this list exists?",
    }

    for line in readme_text.split("\n"):
        line = line.strip()

        # Detect HTML category headers: <summary><h3>Category Name</h3></summary>
        html_cat = re.search(r"<h[23][^>]*>([^<]+)</h[23]>", line)
        if html_cat:
            candidate = html_cat.group(1).strip()
            # Remove emoji prefixes
            candidate = re.sub(r"^[\U0001f300-\U0001faff\u2600-\u27bf]+\s*", "", candidate).strip()
            if candidate and candidate.lower() not in skip_headers:
                current_category = candidate
                categories.add(current_category)
            continue

        # Detect markdown category headers (## or ###)
        cat_match = re.match(r"^#{2,3}\s+(.+)$", line)
        if cat_match:
            candidate = cat_match.group(1).strip()
            # Remove emoji prefixes
            candidate = re.sub(r"^[\U0001f300-\U0001faff\u2600-\u27bf]+\s*", "", candidate).strip()
            if candidate.lower() not in skip_headers:
                current_category = candidate
                categories.add(current_category)
            else:
                current_category = ""  # Reset to avoid capturing entries under skipped sections
            continue

        # Parse skill entry: - [name](url) - description
        entry_match = re.match(
            r"^[-*]\s+\[([^\]]+)\]\(([^)]+)\)\s*[-\u2013\u2014]?\s*(.*)",
            line,
        )
        if entry_match and current_category:
            name = entry_match.group(1).strip()
            link = entry_match.group(2).strip()
            desc = entry_match.group(3).strip()
            # Only include actual skill entries (linked to openclaw/skills repo)
            if "openclaw/skills" not in link and "clawhub" not in link:
                continue
            skills.append({
                "name": name,
                "category": current_category,
                "link": link,
                "description": desc,
            })

    return skills, len(categories)


def compute_owner_counts(skills):
    """Count skills per owner from GitHub links."""
    owner_counts = {}
    for s in skills:
        link = s.get("link", "")
        parts = link.split("/skills/")
        if len(parts) > 1:
            owner = parts[1].split("/")[0]
            owner_counts[owner] = owner_counts.get(owner, 0) + 1
    return owner_counts


def compute_credibility(skill, prolific_owners):
    """Compute initial credibility score for a skill."""
    score = 30  # curated in awesome-list
    if skill.get("description", "").strip():
        score += 10
    if skill.get("category", "").strip():
        score += 5
    # Check if owner is prolific
    link = skill.get("link", "")
    parts = link.split("/skills/")
    if len(parts) > 1:
        owner = parts[1].split("/")[0]
        if owner in prolific_owners:
            score += 10
    return score


def load_existing_catalog():
    """Load existing catalog to preserve vet results."""
    if not CATALOG_PATH.exists():
        return {}
    try:
        with open(CATALOG_PATH) as f:
            catalog = json.load(f)
        # Index by name for fast lookup
        return {s["name"]: s for s in catalog.get("skills", [])}
    except Exception:
        return {}


def main():
    readme = fetch_readme()
    new_skills, cat_count = parse_skills(readme)

    if not new_skills:
        print("Warning: No skills parsed from README. Check format.", file=sys.stderr)
        sys.exit(1)

    print(f"  Parsed {len(new_skills)} skills in {cat_count} categories")

    # Load existing catalog for vet preservation & diff
    existing = load_existing_catalog()

    # Compute prolific owners
    owner_counts = compute_owner_counts(new_skills)
    prolific = {o for o, c in owner_counts.items() if c >= 3}

    # Build updated catalog, preserving vet results
    added, removed, updated = [], [], []
    seen_names = set()

    for s in new_skills:
        name = s["name"]
        seen_names.add(name)

        s["credibility"] = compute_credibility(s, prolific)
        s["source"] = "awesome-list"
        s["installed"] = False

        if name in existing:
            # Preserve vet results
            old = existing[name]
            s["vet_status"] = old.get("vet_status")
            s["vet_date"] = old.get("vet_date")
            s["installed"] = old.get("installed", False)

            # Recalculate credibility with vet bonus
            if s["vet_status"] == "PASS":
                s["credibility"] += 25
            elif s["vet_status"] == "WARN":
                s["credibility"] += 10
            elif s["vet_status"] == "FAIL":
                s["credibility"] -= 20

            # Preserve prolific owner bonus from existing
            if old.get("credibility", 0) != s["credibility"] or old.get("description") != s.get("description"):
                updated.append(name)
        else:
            s["vet_status"] = None
            s["vet_date"] = None
            added.append(name)

    # Detect removed skills
    for name in existing:
        if name not in seen_names:
            removed.append(name)

    # Build final catalog
    catalog = {
        "total": len(new_skills),
        "categories": cat_count,
        "synced_at": datetime.now().isoformat(),
        "source": "VoltAgent/awesome-openclaw-skills",
        "skills": new_skills,
    }

    # Save
    CATALOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CATALOG_PATH, "w") as f:
        json.dump(catalog, f, indent=2)

    # Report diff
    print(f"\nSync complete: {len(new_skills)} skills, {cat_count} categories")
    print(f"  Added:   {len(added)}")
    print(f"  Removed: {len(removed)}")
    print(f"  Changed: {len(updated)}")

    if added:
        print(f"\n  New skills:")
        for n in added[:20]:
            print(f"    + {n}")
        if len(added) > 20:
            print(f"    ... and {len(added) - 20} more")

    if removed:
        print(f"\n  Removed skills:")
        for n in removed[:20]:
            print(f"    - {n}")
        if len(removed) > 20:
            print(f"    ... and {len(removed) - 20} more")

    print(f"\nCatalog saved to {CATALOG_PATH}")


if __name__ == "__main__":
    main()
