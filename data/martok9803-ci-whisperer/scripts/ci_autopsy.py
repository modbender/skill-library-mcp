#!/usr/bin/env python3
"""CI Autopsy helper for GitHub Actions.

Uses the GitHub CLI (`gh`). Designed to be called by an OpenClaw agent.

Examples:
  python3 ci_autopsy.py view --repo owner/repo --run-id 123
  python3 ci_autopsy.py failed-logs --repo owner/repo --run-id 123

Notes:
- Uses /usr/bin/gh if present to avoid shadowed Node "gh" shims.
- Does not print auth tokens.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys


def gh_bin() -> str:
    if os.path.exists("/usr/bin/gh"):
        return "/usr/bin/gh"
    p = shutil.which("gh")
    if not p:
        raise SystemExit("gh not found. Install GitHub CLI and authenticate: gh auth login")
    return p


def run(cmd: list[str]) -> str:
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if p.returncode != 0:
        raise SystemExit(p.stdout.strip())
    return p.stdout


def cmd_view(args: argparse.Namespace) -> None:
    fields = "status,conclusion,createdAt,updatedAt,event,headBranch,headSha,url,name,workflowDatabaseId"
    out = run([
        gh_bin(), "run", "view", str(args.run_id),
        "--repo", args.repo,
        "--json", fields,
    ])
    print(out)


def cmd_failed_logs(args: argparse.Namespace) -> None:
    out = run([
        gh_bin(), "run", "view", str(args.run_id),
        "--repo", args.repo,
        "--log-failed",
    ])
    print(out)


def cmd_list(args: argparse.Namespace) -> None:
    out = run([
        gh_bin(), "run", "list",
        "--repo", args.repo,
        "--limit", str(args.limit),
        "--json", "databaseId,status,conclusion,createdAt,updatedAt,event,headBranch,headSha,workflowName,displayTitle,url",
    ])
    # Pretty-print a compact view
    data = json.loads(out)
    for r in data:
        print(f"{r['databaseId']} {r['conclusion'] or r['status']} {r['workflowName']} :: {r['displayTitle']} ({r['url']})")


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_list = sub.add_parser("list")
    p_list.add_argument("--repo", required=True, help="owner/repo")
    p_list.add_argument("--limit", type=int, default=10)
    p_list.set_defaults(func=cmd_list)

    p_view = sub.add_parser("view")
    p_view.add_argument("--repo", required=True, help="owner/repo")
    p_view.add_argument("--run-id", type=int, required=True)
    p_view.set_defaults(func=cmd_view)

    p_logs = sub.add_parser("failed-logs")
    p_logs.add_argument("--repo", required=True, help="owner/repo")
    p_logs.add_argument("--run-id", type=int, required=True)
    p_logs.set_defaults(func=cmd_failed_logs)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
