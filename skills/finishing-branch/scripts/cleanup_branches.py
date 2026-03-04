#!/usr/bin/env python3
"""Clean up stale and merged branches.

Usage:
    python cleanup_branches.py                 # list stale branches
    python cleanup_branches.py --delete        # delete merged branches
    python cleanup_branches.py --days 14       # custom stale threshold
    python cleanup_branches.py --dry-run       # preview only
"""

import argparse
import subprocess
import sys
from datetime import datetime, timezone


def run_git(*args, check=True):
    """Run a git command and return stripped stdout."""
    cmd = ["git"] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True, check=check)
    return result.stdout.strip()


def run_git_rc(*args):
    """Run a git command and return (return_code, stdout, stderr)."""
    cmd = ["git"] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def get_main_branch():
    """Detect whether the repo uses 'main' or 'master'."""
    for candidate in ("main", "master"):
        rc, _, _ = run_git_rc("rev-parse", "--verify", candidate)
        if rc == 0:
            return candidate
    print("Error: Could not find a 'main' or 'master' branch.")
    sys.exit(1)


def get_merged_branches(main_branch):
    """Return list of local branches already merged into main."""
    output = run_git("branch", "--merged", main_branch)
    branches = []
    for line in output.splitlines():
        name = line.strip().lstrip("* ")
        if name and name not in (main_branch, "HEAD"):
            branches.append(name)
    return branches


def get_all_local_branches():
    """Return list of all local branch names."""
    output = run_git("branch", "--format=%(refname:short)")
    return [b.strip() for b in output.splitlines() if b.strip()]


def get_branch_last_commit_date(branch):
    """Return the datetime of the last commit on the branch."""
    iso = run_git("log", "-1", "--format=%cI", branch, check=False)
    if not iso:
        return None
    try:
        return datetime.fromisoformat(iso)
    except ValueError:
        return None


def get_branch_last_commit_subject(branch):
    """Return the subject of the last commit on the branch."""
    return run_git("log", "-1", "--format=%s", branch, check=False)


def days_ago(dt):
    """Return how many days ago a datetime was."""
    if dt is None:
        return float("inf")
    now = datetime.now(timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    delta = now - dt
    return delta.days


def find_stale_branches(main_branch, threshold_days):
    """Return list of (branch, days_stale, last_subject) for stale branches."""
    all_branches = get_all_local_branches()
    stale = []
    for branch in all_branches:
        if branch in (main_branch, "HEAD"):
            continue
        last_date = get_branch_last_commit_date(branch)
        age = days_ago(last_date)
        if age >= threshold_days:
            subject = get_branch_last_commit_subject(branch)
            stale.append((branch, age, subject))
    stale.sort(key=lambda x: x[1], reverse=True)
    return stale


def delete_branch(branch, dry_run=False):
    """Delete a branch locally and attempt remote deletion."""
    if dry_run:
        print(f"  [dry-run] Would delete local branch: {branch}")
        print(f"  [dry-run] Would delete remote branch: origin/{branch}")
        return

    rc, _, err = run_git_rc("branch", "-d", branch)
    if rc == 0:
        print(f"  Deleted local branch: {branch}")
    else:
        print(f"  Failed to delete local '{branch}': {err}")
        print(f"  Tip: use 'git branch -D {branch}' to force-delete.")
        return

    rc, _, err = run_git_rc("push", "origin", "--delete", branch)
    if rc == 0:
        print(f"  Deleted remote branch: origin/{branch}")
    else:
        # Remote branch may not exist — not an error
        pass


def main():
    parser = argparse.ArgumentParser(
        description="Clean up stale and merged git branches."
    )
    parser.add_argument(
        "--delete",
        action="store_true",
        help="Delete branches that have been merged into main.",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="Threshold in days for considering a branch stale (default: 30).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview actions without making changes.",
    )
    args = parser.parse_args()

    main_branch = get_main_branch()
    print(f"Main branch: {main_branch}")
    print(f"Stale threshold: {args.days} days")
    print()

    # --- Merged branches ---
    merged = get_merged_branches(main_branch)
    print(f"Branches merged into {main_branch} ({len(merged)}):")
    if merged:
        for b in merged:
            subject = get_branch_last_commit_subject(b)
            print(f"  - {b:30s}  {subject}")
    else:
        print("  (none)")
    print()

    # --- Stale branches ---
    stale = find_stale_branches(main_branch, args.days)
    # Exclude already-merged from stale list to avoid duplicate reporting
    merged_set = set(merged)
    stale_unmerged = [(b, d, s) for b, d, s in stale if b not in merged_set]

    print(f"Stale branches (no commits in {args.days}+ days, not merged) ({len(stale_unmerged)}):")
    if stale_unmerged:
        for branch, age, subject in stale_unmerged:
            print(f"  - {branch:30s}  {age:>4d} days  {subject}")
    else:
        print("  (none)")
    print()

    # --- Deletion ---
    if args.delete:
        targets = merged  # only delete branches confirmed merged
        if not targets:
            print("Nothing to delete — no merged branches found.")
            return

        print(f"Deleting {len(targets)} merged branch(es)...")
        for branch in targets:
            delete_branch(branch, dry_run=args.dry_run)
        print("\nDone.")
    else:
        if merged:
            print("To delete merged branches, run with --delete.")
        if stale_unmerged:
            print("Stale unmerged branches require manual review before deletion.")


if __name__ == "__main__":
    main()
