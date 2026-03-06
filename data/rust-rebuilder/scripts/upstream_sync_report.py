#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

DEFAULT_BRANCH = "main"
DEFAULT_MAX_COMMITS = 20
REQUIRED_REMOTES = ("upstream", "origin")


class GitCommandError(RuntimeError):
    pass


@dataclass(frozen=True)
class SyncReport:
    repository: str
    branch: str
    upstream_only_commits: int
    origin_only_commits: int
    upstream_new_commits: list[str]


def run_git(repo_path: Path, args: list[str]) -> str:
    command = ["git", *args]
    result = subprocess.run(
        command,
        cwd=repo_path,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        error_message = result.stderr.strip() or result.stdout.strip()
        raise GitCommandError(f"命令失败: {' '.join(command)}\n{error_message}")
    return result.stdout.strip()


def ensure_git_repo(repo_path: Path) -> None:
    run_git(repo_path, ["rev-parse", "--is-inside-work-tree"])


def get_remotes(repo_path: Path) -> set[str]:
    remotes_raw = run_git(repo_path, ["remote"])
    if not remotes_raw:
        return set()
    return {remote.strip() for remote in remotes_raw.splitlines() if remote.strip()}


def ensure_required_remotes(repo_path: Path) -> None:
    remotes = get_remotes(repo_path)
    missing = [name for name in REQUIRED_REMOTES if name not in remotes]
    if missing:
        missing_value = ", ".join(missing)
        raise GitCommandError(f"缺少远程仓库: {missing_value}")


def fetch_remotes(repo_path: Path) -> None:
    for remote_name in REQUIRED_REMOTES:
        run_git(repo_path, ["fetch", "--prune", remote_name])


def read_ahead_behind(
    repo_path: Path,
    branch: str,
) -> tuple[int, int]:
    comparison = run_git(
        repo_path,
        [
            "rev-list",
            "--left-right",
            "--count",
            f"upstream/{branch}...origin/{branch}",
        ],
    )
    counts = comparison.split()
    if len(counts) != 2:
        raise GitCommandError(f"无法解析分支差异统计: {comparison}")
    upstream_only = int(counts[0])
    origin_only = int(counts[1])
    return upstream_only, origin_only


def read_upstream_new_commits(
    repo_path: Path,
    branch: str,
    max_commits: int,
) -> list[str]:
    log_output = run_git(
        repo_path,
        [
            "log",
            "--oneline",
            f"--max-count={max_commits}",
            f"origin/{branch}..upstream/{branch}",
        ],
    )
    if not log_output:
        return []
    return [line for line in log_output.splitlines() if line.strip()]


def build_report(repo_path: Path, branch: str, max_commits: int) -> SyncReport:
    upstream_only, origin_only = read_ahead_behind(repo_path, branch)
    commits = read_upstream_new_commits(repo_path, branch, max_commits)
    return SyncReport(
        repository=str(repo_path),
        branch=branch,
        upstream_only_commits=upstream_only,
        origin_only_commits=origin_only,
        upstream_new_commits=commits,
    )


def to_markdown(report: SyncReport) -> str:
    lines = [
        "# Upstream Sync Report",
        "",
        f"- repository: {report.repository}",
        f"- branch: {report.branch}",
        f"- upstream_only_commits: {report.upstream_only_commits}",
        f"- origin_only_commits: {report.origin_only_commits}",
        "",
        "## upstream_new_commits",
    ]
    if report.upstream_new_commits:
        for commit_line in report.upstream_new_commits:
            lines.append(f"- {commit_line}")
    else:
        lines.append("- none")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="生成 upstream 与 origin 的 commit 差异报告。",
    )
    parser.add_argument(
        "--repo",
        default=".",
        help="目标仓库路径，默认当前目录。",
    )
    parser.add_argument(
        "--branch",
        default=DEFAULT_BRANCH,
        help=f"比较分支名，默认 {DEFAULT_BRANCH}。",
    )
    parser.add_argument(
        "--max-commits",
        type=int,
        default=DEFAULT_MAX_COMMITS,
        help=f"最多输出上游新增 commit 数，默认 {DEFAULT_MAX_COMMITS}。",
    )
    parser.add_argument(
        "--skip-fetch",
        action="store_true",
        help="跳过 fetch。",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="输出 JSON 格式。",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_path = Path(args.repo).expanduser().resolve()

    try:
        ensure_git_repo(repo_path)
        ensure_required_remotes(repo_path)
        if not args.skip_fetch:
            fetch_remotes(repo_path)
        report = build_report(repo_path, args.branch, args.max_commits)
    except (GitCommandError, FileNotFoundError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(asdict(report), ensure_ascii=False, indent=2))
    else:
        print(to_markdown(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
