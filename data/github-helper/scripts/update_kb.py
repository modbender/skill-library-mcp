#!/usr/bin/env python3
"""
Update CLAUDE.md knowledge base file with repository information.
"""
import json
import sys
from datetime import datetime
from pathlib import Path


def update_claude_md(github_dir, repos_data):
    """Update or create CLAUDE.md with repository summaries."""
    claude_md_path = Path(github_dir) / "CLAUDE.md"
    content = f"""# GitHub Knowledge Base

Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

This file contains summaries of all repositories in this directory.

## Repositories

"""
    if repos_data:
        for repo in sorted(repos_data, key=lambda item: item["name"].lower()):
            content += f"### {repo['name']}\n\n"
            content += f"**Path**: `{repo['path']}`\n\n"
            content += f"**Summary**: {repo['summary']}\n\n"
            content += "---\n\n"
    else:
        content += "*No repositories found.*\n"

    with open(claude_md_path, "w", encoding="utf-8") as file:
        file.write(content)
    return str(claude_md_path)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: update_kb.py <github_directory> <repos_json>")
        raise SystemExit(1)

    github_dir = sys.argv[1]
    repos_data = json.loads(sys.argv[2])
    result_path = update_claude_md(github_dir, repos_data)
    print(f"Updated: {result_path}")
