"""
project_tracker.py — OpenClaw Ecosystem GitHub Metadata Tracker

Tracks stars, forks, PRs, releases, and commit activity for core OpenClaw repos.
Uses GitHub API via GITHUB_TOKEN from .env.
Called from hourly_heartbeat.py.
"""

import json
import os
import subprocess
from datetime import datetime, timezone

import storage

# Core OpenClaw ecosystem repos to track
REPOS = [
    "openclaw/openclaw",    # Main framework (245K+ stars)
    "openclaw/clawhub",     # Skill registry CLI (3.5K stars)
    "openclaw/skills",      # Archived skill versions
]


def _gh_api(endpoint: str) -> dict | list | None:
    """Call GitHub API via gh CLI. Returns parsed JSON or None on error."""
    try:
        result = subprocess.run(
            ["gh", "api", endpoint],
            capture_output=True, text=True, timeout=15, encoding="utf-8",
        )
        if result.returncode != 0:
            print(f"  [WARN] gh api {endpoint}: {(result.stderr or '').strip()[:100]}")
            return None
        if not result.stdout:
            return None
        return json.loads(result.stdout)
    except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError) as e:
        print(f"  [WARN] gh api {endpoint}: {e}")
        return None


def snapshot_repos() -> list[dict]:
    """Fetch metadata for all tracked repos. Returns list of dicts for storage."""
    results = []

    for repo in REPOS:
        print(f"  [PROJECT] {repo}...")
        data = _gh_api(f"repos/{repo}")
        if not data:
            continue

        entry = {
            "repo": repo,
            "stars": data.get("stargazers_count", 0),
            "forks": data.get("forks_count", 0),
            "open_issues": data.get("open_issues_count", 0),
            "watchers": data.get("subscribers_count", 0),
        }

        # Open PRs count
        prs = _gh_api(f"search/issues?q=repo:{repo}+type:pr+state:open")
        entry["open_prs"] = prs.get("total_count", 0) if prs else 0

        # Latest release
        releases = _gh_api(f"repos/{repo}/releases?per_page=1")
        if releases and len(releases) > 0:
            entry["latest_release"] = releases[0].get("tag_name", "")
            entry["latest_release_date"] = releases[0].get("published_at", "")[:10]
        else:
            entry["latest_release"] = ""
            entry["latest_release_date"] = ""

        # Weekly commit count (from commit_activity stats)
        stats = _gh_api(f"repos/{repo}/stats/commit_activity")
        if stats and len(stats) > 0:
            entry["weekly_commits"] = stats[-1].get("total", 0)
        else:
            entry["weekly_commits"] = 0

        results.append(entry)

    return results


def capture() -> int:
    """Full capture: snapshot repos and store to DB."""
    storage.init_project_metadata()
    entries = snapshot_repos()
    if not entries:
        print("[PROJECT] No repo data captured")
        return 0
    return storage.record_project_metadata(entries)


if __name__ == "__main__":
    capture()
