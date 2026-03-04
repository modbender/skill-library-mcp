"""
Git activity collector — reads commit history from project repos.
Extracts what actually changed: files modified, messages, authors.
No interpretation — pure structured extraction.

Env vars:
  GIT_REPOS   Comma-separated list of repo paths to collect from
              (defaults to current directory)
"""
from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path
from typing import Optional


def _get_repos() -> list[str]:
    repos_env = os.environ.get('GIT_REPOS', '')
    if repos_env:
        return [r.strip() for r in repos_env.split(',') if r.strip()]
    # Default: current directory
    return [str(Path.cwd())]


def get_commits(repo_path: str, since: str = '1 day ago', until: str = 'now') -> list[dict]:
    """Return commits from a git repo in the given window."""
    path = Path(repo_path)
    if not (path / '.git').exists():
        return []

    try:
        hashes = subprocess.check_output(
            ['git', 'log', f'--since={since}', f'--until={until}',
             '--format=%H', '--no-merges'],
            cwd=repo_path, stderr=subprocess.DEVNULL, text=True
        ).strip().splitlines()
    except subprocess.CalledProcessError:
        return []

    commits = []
    for h in hashes:
        try:
            msg = subprocess.check_output(
                ['git', 'show', '--no-patch', '--format=%s%n%b', h],
                cwd=repo_path, stderr=subprocess.DEVNULL, text=True
            ).strip()
            lines = msg.splitlines()
            subject = lines[0] if lines else ''
            body = '\n'.join(lines[1:]).strip() if len(lines) > 1 else ''

            meta = subprocess.check_output(
                ['git', 'show', '--no-patch', '--format=%aI|%an', h],
                cwd=repo_path, stderr=subprocess.DEVNULL, text=True
            ).strip().splitlines()[0]
            timestamp, author = meta.split('|', 1) if '|' in meta else (meta, 'unknown')

            stat = subprocess.check_output(
                ['git', 'show', '--stat', '--format=', h],
                cwd=repo_path, stderr=subprocess.DEVNULL, text=True
            ).strip()

            files_changed = []
            insertions = deletions = 0
            for line in stat.splitlines():
                if 'changed' in line:
                    if m := re.search(r'(\d+) insertion', line):
                        insertions = int(m.group(1))
                    if m := re.search(r'(\d+) deletion', line):
                        deletions = int(m.group(1))
                elif '|' in line:
                    fname = line.split('|')[0].strip()
                    if fname:
                        files_changed.append(fname)

            commits.append({
                'hash': h[:8],
                'subject': subject,
                'body': body[:400] if body else '',
                'author': author,
                'timestamp': timestamp,
                'files_changed': files_changed[:15],
                'insertions': insertions,
                'deletions': deletions,
                'repo': Path(repo_path).name,
            })
        except Exception:
            continue

    return commits


def build_git_summary(since: str = '1 day ago', repos: Optional[list[str]] = None) -> dict:
    """Aggregate git activity across tracked repos."""
    if repos is None:
        repos = _get_repos()

    all_commits = []
    per_repo = {}

    for repo in repos:
        commits = get_commits(repo, since=since)
        repo_name = Path(repo).name
        per_repo[repo_name] = {
            'commits': len(commits),
            'insertions': sum(c['insertions'] for c in commits),
            'deletions': sum(c['deletions'] for c in commits),
            'subjects': [c['subject'] for c in commits],
        }
        all_commits.extend(commits)

    all_commits.sort(key=lambda c: c.get('timestamp', ''), reverse=True)

    return {
        'total_commits': len(all_commits),
        'total_insertions': sum(c['insertions'] for c in all_commits),
        'total_deletions': sum(c['deletions'] for c in all_commits),
        'per_repo': per_repo,
        'commits': all_commits[:30],
    }
