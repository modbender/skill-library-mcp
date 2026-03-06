#!/usr/bin/env python3
"""Safely finish a development branch with merge summary and cleanup.

Usage:
    python finish_branch.py                    # analyze current branch
    python finish_branch.py --squash-msg       # generate squash commit message
    python finish_branch.py --cleanup          # delete branch after merge
    python finish_branch.py --dry-run          # preview only
"""

import argparse
import os
import re
import subprocess
import sys
from datetime import datetime


def run_git(*args, check=True, capture=True):
    """Run a git command and return stripped stdout."""
    cmd = ["git"] + list(args)
    result = subprocess.run(
        cmd,
        capture_output=capture,
        text=True,
        check=check,
    )
    return result.stdout.strip() if capture else ""


def run_git_rc(*args):
    """Run a git command and return (return_code, stdout, stderr)."""
    cmd = ["git"] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def get_current_branch():
    return run_git("rev-parse", "--abbrev-ref", "HEAD")


def get_main_branch():
    """Detect whether the repo uses 'main' or 'master'."""
    for candidate in ("main", "master"):
        rc, _, _ = run_git_rc("rev-parse", "--verify", candidate)
        if rc == 0:
            return candidate
    print("Error: Could not find a 'main' or 'master' branch.")
    sys.exit(1)


def check_not_main(branch, main_branch):
    if branch in (main_branch, "HEAD"):
        print(f"Error: You are on '{branch}'. Switch to a feature branch first.")
        sys.exit(1)


def check_clean_worktree():
    """Abort if the working tree has uncommitted changes."""
    rc, out, _ = run_git_rc("status", "--porcelain")
    if rc != 0:
        print("Error: Could not determine worktree status.")
        sys.exit(1)
    if out:
        print("Error: Working tree is dirty. Commit or stash changes first.")
        print(out)
        sys.exit(1)


def detect_test_runner():
    """Return a shell command to run tests, or None."""
    markers = {
        "Makefile": "make test",
        "package.json": "npm test",
        "Cargo.toml": "cargo test",
        "pyproject.toml": "python -m pytest",
        "setup.py": "python -m pytest",
        "pytest.ini": "python -m pytest",
        "tox.ini": "tox",
    }
    for filename, cmd in markers.items():
        if os.path.isfile(filename):
            return cmd
    return None


def run_tests(dry_run=False):
    """Run tests if a test runner is detected. Return True on success."""
    runner = detect_test_runner()
    if runner is None:
        print("  No test runner detected — skipping tests.")
        return True
    print(f"  Detected test runner: {runner}")
    if dry_run:
        print("  [dry-run] Would run tests.")
        return True
    rc = subprocess.run(runner, shell=True).returncode
    if rc != 0:
        print(f"  Tests failed (exit {rc}). Fix before finishing the branch.")
        return False
    print("  Tests passed.")
    return True


def check_up_to_date(branch, main_branch):
    """Check if the branch is up to date with main."""
    run_git("fetch", "origin", main_branch, check=False)
    behind = run_git(
        "rev-list", "--count", f"{branch}..origin/{main_branch}"
    )
    behind_count = int(behind) if behind.isdigit() else 0
    if behind_count > 0:
        print(f"  Warning: Branch is {behind_count} commit(s) behind origin/{main_branch}.")
        print(f"  Consider rebasing: git rebase origin/{main_branch}")
    else:
        print(f"  Branch is up to date with origin/{main_branch}.")
    return behind_count


def get_merge_base(branch, main_branch):
    return run_git("merge-base", branch, main_branch)


def get_commit_log(base, branch):
    """Return list of (hash, subject) tuples."""
    log = run_git(
        "log", "--oneline", "--no-decorate", f"{base}..{branch}"
    )
    if not log:
        return []
    commits = []
    for line in log.splitlines():
        parts = line.split(" ", 1)
        commits.append((parts[0], parts[1] if len(parts) > 1 else ""))
    return commits


def get_files_changed(base, branch):
    diff = run_git("diff", "--stat", f"{base}..{branch}")
    return diff


def find_todos_completed(base, branch):
    """Look for TODO/FIXME removals in the diff."""
    diff = run_git("diff", f"{base}..{branch}")
    pattern = re.compile(r"^-.*\b(TODO|FIXME|HACK|XXX)\b", re.IGNORECASE)
    return [line[1:].strip() for line in diff.splitlines() if pattern.match(line)]


def generate_merge_summary(branch, main_branch):
    """Print a human-readable merge summary."""
    base = get_merge_base(branch, main_branch)
    commits = get_commit_log(base, branch)
    files = get_files_changed(base, branch)
    todos = find_todos_completed(base, branch)

    print(f"\n{'=' * 60}")
    print(f"  MERGE SUMMARY: {branch} → {main_branch}")
    print(f"{'=' * 60}")

    print(f"\n  Commits ({len(commits)}):")
    for sha, msg in commits:
        print(f"    {sha} {msg}")

    print(f"\n  Files changed:")
    for line in files.splitlines():
        print(f"    {line}")

    if todos:
        print(f"\n  TODOs resolved ({len(todos)}):")
        for t in todos:
            print(f"    - {t}")
    else:
        print("\n  No TODOs resolved in this branch.")

    print(f"\n{'=' * 60}\n")
    return commits


def generate_squash_message(branch, main_branch):
    """Generate a squash commit message from the branch history."""
    base = get_merge_base(branch, main_branch)
    commits = get_commit_log(base, branch)

    title = branch.replace("-", " ").replace("_", " ").title()
    lines = [f"{title}\n"]
    lines.append(f"Squash merge of branch '{branch}' into {main_branch}.\n")

    if commits:
        lines.append("Included commits:")
        for sha, msg in commits:
            lines.append(f"  - {msg} ({sha})")
        lines.append("")

    message = "\n".join(lines)
    print("Generated squash commit message:\n")
    print(message)
    return message


def cleanup_branch(branch, dry_run=False):
    """Delete the branch locally and from origin."""
    print(f"\nCleanup: deleting branch '{branch}'")

    if dry_run:
        print(f"  [dry-run] Would run: git branch -d {branch}")
        print(f"  [dry-run] Would run: git push origin --delete {branch}")
        return

    # Delete local branch — must not be on it
    current = get_current_branch()
    if current == branch:
        main = get_main_branch()
        print(f"  Switching to {main} first...")
        run_git("checkout", main)

    rc, _, err = run_git_rc("branch", "-d", branch)
    if rc == 0:
        print(f"  Deleted local branch '{branch}'.")
    else:
        print(f"  Could not delete local branch: {err}")
        print(f"  If unmerged, use: git branch -D {branch}")

    # Delete remote branch
    rc, _, err = run_git_rc("push", "origin", "--delete", branch)
    if rc == 0:
        print(f"  Deleted remote branch 'origin/{branch}'.")
    else:
        print(f"  Could not delete remote branch (may not exist): {err}")


def main():
    parser = argparse.ArgumentParser(
        description="Safely finish a development branch."
    )
    parser.add_argument(
        "--squash-msg",
        action="store_true",
        help="Generate a squash commit message from the branch history.",
    )
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Delete the branch locally and from origin after merge.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview actions without making changes.",
    )
    args = parser.parse_args()

    branch = get_current_branch()
    main_branch = get_main_branch()

    print(f"Branch : {branch}")
    print(f"Target : {main_branch}")
    print(f"Date   : {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print()

    # --- Step 1: verify not on main ---
    check_not_main(branch, main_branch)

    # --- Step 2: check for uncommitted changes ---
    print("[1/5] Checking working tree...")
    check_clean_worktree()
    print("  Working tree is clean.")

    # --- Step 3: run tests ---
    print("[2/5] Running tests...")
    if not run_tests(dry_run=args.dry_run):
        sys.exit(1)

    # --- Step 4: check up-to-date with main ---
    print("[3/5] Checking sync with main...")
    check_up_to_date(branch, main_branch)

    # --- Step 5: merge summary ---
    print("[4/5] Generating merge summary...")
    generate_merge_summary(branch, main_branch)

    # --- Step 6: squash message ---
    if args.squash_msg:
        print("[5/5] Generating squash commit message...")
        generate_squash_message(branch, main_branch)
    else:
        print("[5/5] Skipping squash message (use --squash-msg to generate).")

    # --- Step 7: cleanup ---
    if args.cleanup:
        cleanup_branch(branch, dry_run=args.dry_run)
    else:
        print("\nCleanup commands (run manually after merging):")
        print(f"  git checkout {main_branch}")
        print(f"  git branch -d {branch}")
        print(f"  git push origin --delete {branch}")


if __name__ == "__main__":
    main()
