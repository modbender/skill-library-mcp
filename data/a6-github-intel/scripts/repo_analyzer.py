#!/usr/bin/env python3
"""
GitHub Repository Analyzer — Analyze any public GitHub repo.

Usage:
    python3 repo_analyzer.py https://github.com/owner/repo
    python3 repo_analyzer.py owner/repo --depth 3 --json

⚠️ SECURITY: Read-only analysis. NEVER executes code from repositories.
"""

import argparse
import json
import os
import re
import sys
from urllib.parse import quote
import requests

GITHUB_API = "https://api.github.com"
GITHUB_RAW = "https://raw.githubusercontent.com"
TOKEN = os.environ.get("GITHUB_TOKEN", "")
HEADERS = {"Accept": "application/vnd.github.v3+json"}
if TOKEN:
    HEADERS["Authorization"] = f"token {TOKEN}"


def parse_github_url(url: str) -> tuple[str, str]:
    """Extract owner/repo from GitHub URL or 'owner/repo' string."""
    url = url.rstrip("/")
    m = re.match(r"(?:https?://github\.com/)?([^/]+)/([^/]+?)(?:\.git)?$", url)
    if not m:
        raise ValueError(f"Invalid GitHub URL: {url}")
    return m.group(1), m.group(2)


def get_repo_info(owner: str, repo: str) -> dict:
    """Get repository metadata."""
    r = requests.get(f"{GITHUB_API}/repos/{owner}/{repo}", headers=HEADERS, timeout=15)
    r.raise_for_status()
    return r.json()


def get_tree(owner: str, repo: str, branch: str, depth: int = 2) -> list[dict]:
    """Get repository file tree."""
    r = requests.get(
        f"{GITHUB_API}/repos/{owner}/{repo}/git/trees/{branch}?recursive=1",
        headers=HEADERS, timeout=15,
    )
    r.raise_for_status()
    tree = r.json().get("tree", [])
    if depth > 0:
        tree = [t for t in tree if t["path"].count("/") < depth]
    return tree


def get_readme(owner: str, repo: str) -> str:
    """Get README content."""
    r = requests.get(
        f"{GITHUB_API}/repos/{owner}/{repo}/readme",
        headers={**HEADERS, "Accept": "application/vnd.github.raw"},
        timeout=15,
    )
    if r.status_code == 200:
        return r.text
    return "(No README found)"


def get_languages(owner: str, repo: str) -> dict:
    """Get language breakdown."""
    r = requests.get(f"{GITHUB_API}/repos/{owner}/{repo}/languages", headers=HEADERS, timeout=15)
    r.raise_for_status()
    return r.json()


def get_recent_commits(owner: str, repo: str, count: int = 10) -> list[dict]:
    """Get recent commits."""
    r = requests.get(
        f"{GITHUB_API}/repos/{owner}/{repo}/commits?per_page={count}",
        headers=HEADERS, timeout=15,
    )
    r.raise_for_status()
    return r.json()


def format_tree(tree_items: list[dict]) -> str:
    """Format tree items into a visual tree."""
    lines = []
    paths = sorted([t["path"] for t in tree_items])
    for path in paths:
        depth = path.count("/")
        name = path.split("/")[-1]
        is_dir = any(t["path"] == path and t["type"] == "tree" for t in tree_items)
        prefix = "│   " * depth
        connector = "├── "
        suffix = "/" if is_dir else ""
        lines.append(f"{prefix}{connector}{name}{suffix}")
    return "\n".join(lines)


def format_languages(langs: dict) -> str:
    """Format language breakdown as percentages."""
    total = sum(langs.values())
    if total == 0:
        return "(No language data)"
    lines = []
    for lang, bytes_ in sorted(langs.items(), key=lambda x: -x[1]):
        pct = (bytes_ / total) * 100
        lines.append(f"- {lang}: {pct:.1f}%")
    return "\n".join(lines)


def generate_mermaid(tree_items: list[dict], repo_info: dict) -> str:
    """Generate a basic Mermaid architecture diagram from file structure."""
    dirs = set()
    for t in tree_items:
        if t["type"] == "tree" and t["path"].count("/") == 0:
            dirs.add(t["path"])

    if not dirs:
        return "(Repository too flat for architecture diagram)"

    lines = ["graph TD"]
    lines.append(f'  ROOT["{repo_info.get("name", "repo")}"]')
    for d in sorted(dirs):
        safe = d.replace("-", "_").replace(".", "_")
        lines.append(f'  ROOT --> {safe}["{d}/"]')
        # Find subdirs
        subdirs = [t["path"].split("/")[1] for t in tree_items
                    if t["type"] == "tree" and t["path"].startswith(d + "/") and t["path"].count("/") == 1]
        for sd in sorted(set(subdirs))[:8]:
            sd_safe = f"{safe}_{sd.replace('-', '_').replace('.', '_')}"
            lines.append(f'  {safe} --> {sd_safe}["{sd}/"]')

    return "\n".join(lines)


def format_commits(commits: list[dict]) -> str:
    """Format recent commits."""
    lines = []
    for c in commits[:10]:
        date = c.get("commit", {}).get("author", {}).get("date", "")[:10]
        msg = c.get("commit", {}).get("message", "").split("\n")[0][:80]
        author = c.get("commit", {}).get("author", {}).get("name", "unknown")
        lines.append(f"- {date}: {msg} ({author})")
    return "\n".join(lines)


def analyze(owner: str, repo: str, depth: int = 2) -> str:
    """Full repository analysis."""
    info = get_repo_info(owner, repo)
    branch = info.get("default_branch", "main")
    tree = get_tree(owner, repo, branch, depth)
    readme = get_readme(owner, repo)
    langs = get_languages(owner, repo)
    commits = get_recent_commits(owner, repo)

    output = []
    output.append(f"# Repository: {owner}/{repo}")
    output.append("")
    output.append(f"**{info.get('description', 'No description')}**")
    output.append(f"- ⭐ {info.get('stargazers_count', 0):,} stars | 🍴 {info.get('forks_count', 0):,} forks")
    output.append(f"- License: {info.get('license', {}).get('spdx_id', 'Unknown') if info.get('license') else 'None'}")
    output.append(f"- Default branch: {branch}")
    output.append(f"- Last push: {info.get('pushed_at', 'Unknown')}")
    output.append("")

    output.append("## Structure")
    output.append("```")
    output.append(format_tree(tree))
    output.append("```")
    output.append("")

    output.append("## README")
    # Truncate very long READMEs
    if len(readme) > 3000:
        readme = readme[:3000] + "\n\n... (truncated)"
    output.append(readme)
    output.append("")

    output.append("## Language Breakdown")
    output.append(format_languages(langs))
    output.append("")

    output.append("## Architecture (Mermaid)")
    output.append("```mermaid")
    output.append(generate_mermaid(tree, info))
    output.append("```")
    output.append("")

    output.append("## Recent Activity")
    output.append(format_commits(commits))

    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(description="Analyze a GitHub repository")
    parser.add_argument("url", help="GitHub URL or owner/repo")
    parser.add_argument("--depth", "-d", type=int, default=2, help="Tree depth (default: 2)")
    parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    owner, repo = parse_github_url(args.url)

    if args.json:
        info = get_repo_info(owner, repo)
        branch = info.get("default_branch", "main")
        print(json.dumps({
            "info": info,
            "tree": get_tree(owner, repo, branch, args.depth),
            "languages": get_languages(owner, repo),
            "commits": get_recent_commits(owner, repo),
        }, indent=2))
    else:
        print(analyze(owner, repo, args.depth))


if __name__ == "__main__":
    main()
