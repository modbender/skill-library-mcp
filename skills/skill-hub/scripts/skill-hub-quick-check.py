#!/usr/bin/env python3
"""Skill Hub — quick-check for new skills via GitHub API.

Uses `gh` CLI to check if awesome-openclaw-skills has updates since last sync.
If new commits found, fetches README diff and reports new/removed skills.
Much faster than full re-sync — ideal for daily checks.

Usage:
  python3 skill-hub-quick-check.py              # check for updates
  python3 skill-hub-quick-check.py --sync        # auto-sync if updates found
  python3 skill-hub-quick-check.py --query "ai"  # check + search new skills
"""

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

CATALOG_PATH = Path(__file__).parent.parent / "references" / "awesome-catalog.json"
REPO = "VoltAgent/awesome-openclaw-skills"
SYNC_SCRIPT = Path(__file__).parent / "skill-hub-sync.py"


def run_gh(args):
    """Run gh CLI command, return stdout."""
    try:
        result = subprocess.run(
            ["gh"] + args,
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode != 0:
            print(f"  gh error: {result.stderr.strip()}", file=sys.stderr)
            return None
        return result.stdout.strip()
    except FileNotFoundError:
        print("Error: `gh` CLI not found. Install GitHub CLI first.", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error running gh: {e}", file=sys.stderr)
        return None


def get_last_sync_date():
    """Get synced_at from catalog."""
    if not CATALOG_PATH.exists():
        return None
    try:
        with open(CATALOG_PATH) as f:
            catalog = json.load(f)
        return catalog.get("synced_at", "")[:19]  # trim microseconds
    except Exception:
        return None


def get_repo_latest_commit():
    """Get latest commit info from GitHub API via gh."""
    output = run_gh([
        "api", f"repos/{REPO}/commits?per_page=1",
        "--jq", ".[0] | .sha + \"|\" + .commit.committer.date + \"|\" + .commit.message",
    ])
    if not output:
        return None, None, None
    parts = output.split("|", 2)
    if len(parts) < 3:
        return None, None, None
    return parts[0][:8], parts[1][:19], parts[2].split("\n")[0][:80]


def get_commits_since(since_date):
    """Get commits since a date."""
    output = run_gh([
        "api", f"repos/{REPO}/commits?since={since_date}&per_page=20",
        "--jq", '.[] | .sha[:8] + " " + .commit.committer.date[:10] + " " + (.commit.message | split("\n") | .[0])[:60]',
    ])
    if not output:
        return []
    return output.strip().split("\n")


def get_readme_skill_count():
    """Quick check: get skill count from repo description or README badge."""
    output = run_gh([
        "api", f"repos/{REPO}",
        "--jq", ".description",
    ])
    if output:
        # Try to extract count from description
        m = re.search(r"(\d{3,})\s*(?:community|skills)", output, re.IGNORECASE)
        if m:
            return int(m.group(1))
    return None


def load_catalog_stats():
    """Load basic stats from current catalog."""
    if not CATALOG_PATH.exists():
        return 0, 0, []
    try:
        with open(CATALOG_PATH) as f:
            catalog = json.load(f)
        skills = catalog.get("skills", [])
        return catalog.get("total", len(skills)), catalog.get("categories", 0), skills
    except Exception:
        return 0, 0, []


def main():
    parser = argparse.ArgumentParser(description="Skill Hub — quick check for new skills")
    parser.add_argument("--sync", "-s", action="store_true", help="Auto-sync if updates found")
    parser.add_argument("--query", "-q", help="Search new skills by keyword after check")
    args = parser.parse_args()

    print("=" * 55)
    print("  SKILL HUB — QUICK CHECK")
    print("=" * 55)

    # Current state
    sync_date = get_last_sync_date()
    total, cats, skills = load_catalog_stats()
    print(f"  Local catalog: {total} skills | {cats} categories")
    print(f"  Last synced:   {sync_date or 'never'}")
    print()

    # Check GitHub
    print("  Checking GitHub...")
    sha, commit_date, message = get_repo_latest_commit()
    if not sha:
        print("  Could not reach GitHub API. Check `gh auth status`.")
        sys.exit(1)

    print(f"  Latest commit: {sha} ({commit_date})")
    print(f"  Message:       {message}")

    # Compare dates
    has_updates = False
    if sync_date and commit_date:
        # Parse dates for comparison
        try:
            sync_dt = datetime.fromisoformat(sync_date.replace("Z", "+00:00").replace("T", "T"))
            commit_dt = datetime.fromisoformat(commit_date.replace("Z", "+00:00").replace("T", "T"))
            has_updates = commit_dt > sync_dt
        except Exception:
            # Fallback to string comparison
            has_updates = commit_date > sync_date
    else:
        has_updates = True  # No sync date = always update

    if not has_updates:
        print(f"\n  Up to date! No changes since last sync.")
        # Check remote skill count vs local
        remote_count = get_readme_skill_count()
        if remote_count and remote_count != total:
            print(f"  Note: Remote reports {remote_count} skills vs local {total}")
            print(f"  Run: python3 scripts/skill-hub-sync.py  to reconcile")
        sys.exit(0)

    # Has updates — show what changed
    print(f"\n  Updates available!")
    if sync_date:
        commits = get_commits_since(sync_date)
        if commits:
            print(f"  {len(commits)} commit(s) since last sync:")
            for c in commits[:10]:
                print(f"    {c}")
            if len(commits) > 10:
                print(f"    ... and {len(commits) - 10} more")

    # Check remote count
    remote_count = get_readme_skill_count()
    if remote_count:
        diff = remote_count - total
        if diff > 0:
            print(f"\n  ~{diff} new skills estimated (remote: {remote_count}, local: {total})")
        elif diff < 0:
            print(f"\n  ~{abs(diff)} skills removed (remote: {remote_count}, local: {total})")

    # Auto-sync if requested
    if args.sync:
        print(f"\n  Auto-syncing...")
        result = subprocess.run(
            [sys.executable, str(SYNC_SCRIPT)],
            cwd=str(SYNC_SCRIPT.parent.parent),
        )
        if result.returncode == 0 and args.query:
            # Search after sync
            search_script = Path(__file__).parent / "skill-hub-search.py"
            subprocess.run(
                [sys.executable, str(search_script), "--query", args.query, "--limit", "20"],
                cwd=str(search_script.parent.parent),
            )
    else:
        print(f"\n  To sync:   python3 scripts/skill-hub-sync.py")
        print(f"  Auto-sync: python3 scripts/skill-hub-quick-check.py --sync")

    print()


if __name__ == "__main__":
    main()
