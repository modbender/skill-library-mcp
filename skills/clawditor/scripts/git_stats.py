#!/usr/bin/env python3
import argparse
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path


def run(cmd, cwd):
    try:
        out = subprocess.check_output(cmd, cwd=cwd, stderr=subprocess.DEVNULL)
        return out.decode().strip()
    except subprocess.CalledProcessError:
        return ""


def main():
    parser = argparse.ArgumentParser(description="Collect basic git stats.")
    parser.add_argument("path", nargs="?", default=".", help="Repo path")
    parser.add_argument("--since", default="30 days", help="Lookback for cadence (git --since)")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    repo = Path(args.path).resolve()
    git_dir = run(["git", "rev-parse", "--git-dir"], cwd=repo)
    if not git_dir:
        print("Not a git repository", file=sys.stderr)
        return 1

    head = run(["git", "rev-parse", "HEAD"], cwd=repo)
    status = run(["git", "status", "--porcelain"], cwd=repo)
    dirty_files = [line for line in status.splitlines() if line.strip()]

    last_commit = run(["git", "log", "-1", "--pretty=%H|%ad|%s", "--date=iso"], cwd=repo)
    shortstat = run(["git", "diff", "--shortstat"], cwd=repo)

    dates = run(["git", "log", f"--since={args.since}", "--pretty=%ad", "--date=short"], cwd=repo)
    counts = Counter(dates.splitlines()) if dates else Counter()

    result = {
        "repo": str(repo),
        "head": head,
        "dirty_count": len(dirty_files),
        "dirty_files": dirty_files[:50],
        "last_commit": last_commit,
        "diff_shortstat": shortstat,
        "commit_cadence": dict(sorted(counts.items())),
    }

    if args.json:
        print(json.dumps(result, indent=2))
        return 0

    print("Git stats")
    print(f"HEAD: {head}")
    print(f"Dirty files: {len(dirty_files)}")
    if shortstat:
        print(f"Working tree diff: {shortstat}")
    if last_commit:
        print(f"Last commit: {last_commit}")
    if counts:
        print("Commit cadence (date: count)")
        for d, c in sorted(counts.items()):
            print(f"  {d}: {c}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
