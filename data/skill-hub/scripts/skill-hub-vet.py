#!/usr/bin/env python3
"""Skill Hub — security vetting scanner (NLP antivirus).

Scans skills for malicious code patterns, prompt injection, and logic weaknesses.
Updates catalog with vet results. Patterns defined in skill-hub-security-patterns.py.

Usage:
  python3 skill-hub-vet.py --slug google-sheets
  python3 skill-hub-vet.py --all-installed
  python3 skill-hub-vet.py --category "DevOps"
  python3 skill-hub-vet.py --top 10
"""

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

# Import scanner from sibling module
sys.path.insert(0, str(Path(__file__).parent))
from importlib import import_module
patterns_mod = import_module("skill-hub-security-patterns")
scan_skill_dir = patterns_mod.scan_skill_dir
compute_verdict = patterns_mod.compute_verdict

CATALOG_PATH = Path(__file__).parent.parent / "references" / "awesome-catalog.json"
WORKSPACE = Path.home() / ".openclaw" / "workspace"


def get_skill_path(slug):
    """Get path to installed skill, or inspect via clawhub to temp dir."""
    local = WORKSPACE / "skills" / slug
    if local.exists():
        return local, False

    # Try to inspect via clawhub
    tmpdir = tempfile.mkdtemp(prefix=f"skill-vet-{slug}-")
    try:
        result = subprocess.run(
            ["npx", "clawhub@latest", "inspect", slug, "--output", tmpdir],
            capture_output=True, text=True, timeout=60,
            cwd=str(WORKSPACE),
        )
        if result.returncode == 0 and any(Path(tmpdir).iterdir()):
            return Path(tmpdir), True
    except Exception:
        pass

    return None, False


def update_catalog(slug, verdict, score_delta):
    """Update catalog with vet results for a skill."""
    if not CATALOG_PATH.exists():
        return
    try:
        with open(CATALOG_PATH) as f:
            catalog = json.load(f)
    except Exception:
        return

    now = datetime.now().strftime("%Y-%m-%d")
    for s in catalog["skills"]:
        if s["name"] == slug:
            # Remove old vet score contribution
            old_status = s.get("vet_status")
            if old_status == "PASS":
                s["credibility"] = s.get("credibility", 0) - 25
            elif old_status == "WARN":
                s["credibility"] = s.get("credibility", 0) - 10
            elif old_status == "FAIL":
                s["credibility"] = s.get("credibility", 0) + 20

            # Apply new vet score
            s["vet_status"] = verdict
            s["vet_date"] = now
            s["credibility"] = max(0, min(100, s.get("credibility", 0) + score_delta))
            break

    with open(CATALOG_PATH, "w") as f:
        json.dump(catalog, f, indent=2)


def vet_single(slug, quiet=False):
    """Vet a single skill by slug. Returns (verdict, findings)."""
    if not quiet:
        print(f"\nVetting: {slug}")

    skill_path, is_temp = get_skill_path(slug)
    if skill_path is None:
        if not quiet:
            print(f"  Could not find or download skill '{slug}'")
        return None, []

    findings = scan_skill_dir(skill_path)
    verdict, score_delta = compute_verdict(findings)
    update_catalog(slug, verdict, score_delta)

    if not quiet:
        if not findings:
            print(f"  Status: PASS — no security issues detected")
        else:
            print(f"  Status: {verdict} — {len(findings)} finding(s)")
            by_sev = {}
            for f in findings:
                by_sev.setdefault(f["severity"], []).append(f)
            for sev in ("CRITICAL", "HIGH", "MEDIUM", "LOW"):
                items = by_sev.get(sev, [])
                if items:
                    print(f"    [{sev}]")
                    for item in items:
                        print(f"      {item['file']}:{item['line']} — {item['description']}")
                        print(f"        match: {item['match']}")

    # Cleanup temp dir
    if is_temp and skill_path:
        shutil.rmtree(skill_path, ignore_errors=True)

    return verdict, findings


def get_installed_skill_names():
    """Get installed skill slugs from ClawHub."""
    try:
        result = subprocess.run(
            ["npx", "clawhub@latest", "list"],
            capture_output=True, text=True, timeout=30,
            cwd=str(WORKSPACE),
        )
        names = []
        for line in result.stdout.strip().split("\n"):
            parts = line.strip().split()
            if parts:
                names.append(parts[0])
        return names
    except Exception:
        return []


def load_catalog():
    """Load catalog for batch operations."""
    if not CATALOG_PATH.exists():
        return {"skills": []}
    with open(CATALOG_PATH) as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser(description="Skill Hub — security vetting")
    parser.add_argument("--slug", "-s", help="Vet a single skill by name")
    parser.add_argument("--all-installed", "-a", action="store_true", help="Vet all installed skills")
    parser.add_argument("--category", "-c", help="Vet all skills in a category")
    parser.add_argument("--top", "-t", type=int, help="Vet top N unvetted skills")
    args = parser.parse_args()

    if not any([args.slug, args.all_installed, args.category, args.top]):
        parser.print_help()
        sys.exit(1)

    slugs = []
    if args.slug:
        slugs = [args.slug]
    elif args.all_installed:
        slugs = get_installed_skill_names()
        print(f"Found {len(slugs)} installed skills to vet")
    elif args.category:
        catalog = load_catalog()
        cat_lower = args.category.lower()
        slugs = [s["name"] for s in catalog["skills"] if cat_lower in s.get("category", "").lower()]
        print(f"Found {len(slugs)} skills in category '{args.category}'")
    elif args.top:
        catalog = load_catalog()
        unvetted = [s["name"] for s in catalog["skills"] if s.get("vet_status") is None]
        slugs = unvetted[: args.top]
        print(f"Vetting top {len(slugs)} unvetted skills")

    if not slugs:
        print("No skills to vet.")
        sys.exit(0)

    # Vet each skill
    results = {"PASS": 0, "WARN": 0, "FAIL": 0, "ERROR": 0}
    for slug in slugs:
        verdict, _ = vet_single(slug)
        if verdict:
            results[verdict] += 1
        else:
            results["ERROR"] += 1

    # Summary for batch runs
    if len(slugs) > 1:
        print(f"\n{'=' * 50}")
        print(f"Vet Summary: {len(slugs)} skills scanned")
        print(f"  PASS: {results['PASS']}  WARN: {results['WARN']}  FAIL: {results['FAIL']}  ERROR: {results['ERROR']}")


if __name__ == "__main__":
    main()
