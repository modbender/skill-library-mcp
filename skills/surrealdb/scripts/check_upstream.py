# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "rich>=13.0.0",
# ]
# ///
"""Check upstream SurrealDB repos for changes since the last skill snapshot.

Compares current HEAD SHAs and release tags against the baselines recorded
in SOURCES.json.  Prints a Rich table on stderr and structured JSON on stdout
so both humans and agents can consume the output.

Usage:
    uv run scripts/check_upstream.py            # full diff report
    uv run scripts/check_upstream.py --json     # stdout JSON only (no Rich)
    uv run scripts/check_upstream.py --stale    # only repos that changed
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.table import Table

stderr = Console(stderr=True)
SOURCES_PATH = Path(__file__).resolve().parent.parent / "SOURCES.json"


def _gh_api(endpoint: str) -> Any:
    """Call gh api and return parsed JSON."""
    result = subprocess.run(
        ["gh", "api", endpoint],
        capture_output=True,
        text=True,
        timeout=15,
    )
    if result.returncode != 0:
        return None
    return json.loads(result.stdout)


def load_sources() -> dict[str, Any]:
    if not SOURCES_PATH.exists():
        stderr.print(f"[red]SOURCES.json not found at {SOURCES_PATH}[/red]")
        sys.exit(1)
    return json.loads(SOURCES_PATH.read_text())


def check_repo(name: str, baseline: dict[str, Any]) -> dict[str, Any]:
    """Compare a single repo against its baseline."""
    commits = _gh_api(f"repos/{name}/commits?per_page=1")
    if not commits or not isinstance(commits, list):
        return {"repo": name, "status": "error", "message": "Failed to fetch commits"}

    current_sha = commits[0]["sha"]
    current_date = commits[0]["commit"]["committer"]["date"]

    release_data = _gh_api(f"repos/{name}/releases/latest")
    current_release = None
    if isinstance(release_data, dict) and "tag_name" in release_data:
        current_release = release_data["tag_name"]

    baseline_sha = baseline["sha"]
    baseline_release = baseline.get("release")

    sha_changed = current_sha != baseline_sha
    release_changed = current_release != baseline_release and current_release is not None

    # Count commits since baseline
    commits_behind = 0
    if sha_changed:
        compare = _gh_api(f"repos/{name}/compare/{baseline_sha[:12]}...{current_sha[:12]}")
        if isinstance(compare, dict):
            commits_behind = compare.get("ahead_by", 0)

    return {
        "repo": name,
        "status": "changed" if (sha_changed or release_changed) else "current",
        "baseline_sha": baseline_sha[:12],
        "current_sha": current_sha[:12],
        "sha_changed": sha_changed,
        "commits_behind": commits_behind,
        "baseline_release": baseline_release,
        "current_release": current_release,
        "release_changed": release_changed,
        "current_date": current_date,
        "rules_affected": baseline.get("rules_affected", []),
    }


def render_table(results: list[dict[str, Any]]) -> None:
    """Print a Rich table to stderr."""
    table = Table(title="Upstream Source Status", show_lines=True)
    table.add_column("Repository", style="bold")
    table.add_column("Status")
    table.add_column("Baseline SHA")
    table.add_column("Current SHA")
    table.add_column("Commits")
    table.add_column("Release")
    table.add_column("Rules Affected")

    for r in results:
        if r["status"] == "error":
            table.add_row(r["repo"], "[red]ERROR[/red]", "-", "-", "-", "-", r.get("message", ""))
            continue

        status = "[green]CURRENT[/green]" if r["status"] == "current" else "[yellow]CHANGED[/yellow]"
        sha_display = r["current_sha"]
        if r["sha_changed"]:
            sha_display = f"[yellow]{r['current_sha']}[/yellow]"

        commits = str(r["commits_behind"]) if r["commits_behind"] else "-"

        release_display = r.get("current_release") or "-"
        if r["release_changed"]:
            release_display = f"[yellow]{r['baseline_release']} -> {r['current_release']}[/yellow]"

        rules = ", ".join(Path(p).name for p in r["rules_affected"])

        table.add_row(r["repo"], status, r["baseline_sha"], sha_display, commits, release_display, rules)

    stderr.print(table)

    changed = [r for r in results if r["status"] == "changed"]
    if changed:
        all_rules = sorted({rule for r in changed for rule in r["rules_affected"]})
        stderr.print(f"\n[yellow]{len(changed)} repo(s) changed.[/yellow] Rules to review:")
        for rule in all_rules:
            stderr.print(f"  - {rule}")
    else:
        stderr.print("\n[green]All sources are current. No updates needed.[/green]")


def main() -> None:
    parser = argparse.ArgumentParser(description="Check upstream repos for changes since last snapshot.")
    parser.add_argument("--json", action="store_true", help="JSON-only output (no Rich table)")
    parser.add_argument("--stale", action="store_true", help="Only show repos that changed")
    args = parser.parse_args()

    sources = load_sources()
    results: list[dict[str, Any]] = []

    for name, baseline in sources.get("repos", {}).items():
        if not args.json:
            stderr.print(f"Checking {name}...", end=" ")
        result = check_repo(name, baseline)
        results.append(result)
        if not args.json:
            mark = "[green]OK[/green]" if result["status"] == "current" else "[yellow]CHANGED[/yellow]"
            stderr.print(mark)

    if args.stale:
        results = [r for r in results if r["status"] == "changed"]

    if not args.json:
        stderr.print()
        render_table(results)

    report = {
        "skill_version": sources.get("skill_version"),
        "snapshot_date": sources.get("snapshot_date"),
        "check_date": __import__("datetime").date.today().isoformat(),
        "repos": results,
        "stale_count": sum(1 for r in results if r["status"] == "changed"),
        "rules_to_update": sorted({rule for r in results if r["status"] == "changed" for rule in r["rules_affected"]}),
    }
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
