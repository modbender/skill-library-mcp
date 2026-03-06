#!/usr/bin/env python3
"""
Scan local GitHub directory and generate repository summaries.
"""
import json
import sys
from pathlib import Path


def get_repo_summary(repo_path):
    """Extract summary from README or repo description."""
    readme_files = ["README.md", "README.MD", "readme.md", "README", "README.txt"]
    for readme in readme_files:
        readme_path = repo_path / readme
        if readme_path.exists():
            try:
                with open(readme_path, "r", encoding="utf-8") as file:
                    content = file.read()
                    lines = [line.strip() for line in content.split("\n") if line.strip()]
                    if not lines:
                        continue
                    for line in lines:
                        if not line.startswith("#"):
                            return line[:200]
                    return lines[0].lstrip("#").strip()[:200]
            except Exception:
                pass
    return "No description available"


def scan_github_directory(github_dir):
    """Scan GitHub directory and return repo information."""
    github_path = Path(github_dir)
    if not github_path.exists():
        return {"error": "Directory does not exist", "path": str(github_path)}

    repos = []
    for item in github_path.iterdir():
        if item.is_dir() and not item.name.startswith(".") and (item / ".git").exists():
            repos.append(
                {
                    "name": item.name,
                    "path": str(item),
                    "summary": get_repo_summary(item),
                }
            )

    return {"repos": repos, "path": str(github_path)}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: scan_repos.py <github_directory>")
        raise SystemExit(1)

    result = scan_github_directory(sys.argv[1])
    print(json.dumps(result, indent=2, ensure_ascii=False))
