#!/usr/bin/env python3
"""
Repo to Markdown — Convert a GitHub repository into a single AI-readable markdown document.

Usage:
    python3 repo_to_markdown.py https://github.com/owner/repo
    python3 repo_to_markdown.py owner/repo --max-files 100 --max-size 50000

⚠️ SECURITY: Read-only. NEVER executes code from repositories.
"""

import argparse
import json
import os
import re
import sys
import requests

GITHUB_API = "https://api.github.com"
GITHUB_RAW = "https://raw.githubusercontent.com"
TOKEN = os.environ.get("GITHUB_TOKEN", "")
HEADERS = {"Accept": "application/vnd.github.v3+json"}
if TOKEN:
    HEADERS["Authorization"] = f"token {TOKEN}"

# File extensions to include (text-readable code/docs)
TEXT_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".go", ".rs", ".rb", ".java", ".kt",
    ".c", ".cpp", ".h", ".hpp", ".cs", ".swift", ".php", ".lua", ".r", ".jl",
    ".sh", ".bash", ".zsh", ".fish", ".ps1", ".bat", ".cmd",
    ".md", ".txt", ".rst", ".adoc", ".org",
    ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".conf", ".env.example",
    ".xml", ".html", ".css", ".scss", ".less", ".svg",
    ".sql", ".graphql", ".proto", ".tf", ".hcl",
    ".dockerfile", ".gitignore", ".editorconfig",
    ".makefile", ".cmake",
}

# Files to always include regardless of extension
IMPORTANT_FILES = {
    "README.md", "readme.md", "README", "LICENSE", "LICENSE.md",
    "Makefile", "CMakeLists.txt", "Dockerfile", "docker-compose.yml",
    "package.json", "Cargo.toml", "go.mod", "pyproject.toml", "setup.py",
    "requirements.txt", "Gemfile", "pom.xml", "build.gradle",
    ".gitignore", ".env.example",
}

# Skip these directories
SKIP_DIRS = {
    "node_modules", "vendor", "dist", "build", "__pycache__", ".git",
    ".next", ".nuxt", "target", "bin", "obj", ".cache", "coverage",
}


def parse_github_url(url: str) -> tuple[str, str]:
    url = url.rstrip("/")
    m = re.match(r"(?:https?://github\.com/)?([^/]+)/([^/]+?)(?:\.git)?$", url)
    if not m:
        raise ValueError(f"Invalid GitHub URL: {url}")
    return m.group(1), m.group(2)


def should_include(path: str) -> bool:
    """Decide if a file should be included."""
    name = path.split("/")[-1]
    # Skip hidden dirs and known junk
    parts = path.split("/")
    for part in parts[:-1]:
        if part in SKIP_DIRS or (part.startswith(".") and part not in {".github"}):
            return False
    # Always include important files
    if name in IMPORTANT_FILES:
        return True
    # Check extension
    _, ext = os.path.splitext(name.lower())
    if ext in TEXT_EXTENSIONS:
        return True
    # Include extensionless files in root (like Makefile, Dockerfile)
    if "/" not in path and not ext:
        return True
    return False


def get_file_content(owner: str, repo: str, branch: str, path: str, max_size: int) -> str:
    """Fetch a single file's content."""
    url = f"{GITHUB_RAW}/{owner}/{repo}/{branch}/{path}"
    try:
        r = requests.get(url, timeout=10, headers={"Authorization": f"token {TOKEN}"} if TOKEN else {})
        if r.status_code != 200:
            return f"(Failed to fetch: HTTP {r.status_code})"
        if len(r.content) > max_size:
            return r.text[:max_size] + f"\n\n... (truncated, {len(r.content)} bytes total)"
        return r.text
    except Exception as e:
        return f"(Error fetching: {e})"


def get_language_comment(path: str) -> str:
    """Get appropriate code fence language from file extension."""
    ext_map = {
        ".py": "python", ".js": "javascript", ".ts": "typescript",
        ".jsx": "jsx", ".tsx": "tsx", ".go": "go", ".rs": "rust",
        ".rb": "ruby", ".java": "java", ".kt": "kotlin",
        ".c": "c", ".cpp": "cpp", ".h": "c", ".hpp": "cpp",
        ".cs": "csharp", ".swift": "swift", ".php": "php",
        ".sh": "bash", ".bash": "bash", ".zsh": "zsh",
        ".json": "json", ".yaml": "yaml", ".yml": "yaml",
        ".toml": "toml", ".xml": "xml", ".html": "html",
        ".css": "css", ".scss": "scss", ".sql": "sql",
        ".md": "markdown", ".dockerfile": "dockerfile",
        ".tf": "hcl", ".graphql": "graphql", ".proto": "protobuf",
    }
    _, ext = os.path.splitext(path.lower())
    return ext_map.get(ext, "")


def convert(owner: str, repo: str, max_files: int = 75, max_size: int = 30000) -> str:
    """Convert repo to a single markdown document."""
    # Get repo info
    r = requests.get(f"{GITHUB_API}/repos/{owner}/{repo}", headers=HEADERS, timeout=15)
    r.raise_for_status()
    info = r.json()
    branch = info.get("default_branch", "main")

    # Get full tree
    r = requests.get(
        f"{GITHUB_API}/repos/{owner}/{repo}/git/trees/{branch}?recursive=1",
        headers=HEADERS, timeout=15,
    )
    r.raise_for_status()
    all_items = r.json().get("tree", [])

    # Filter to includable files
    files = [t for t in all_items if t["type"] == "blob" and should_include(t["path"])]
    # Sort: important files first, then by path
    files.sort(key=lambda t: (t["path"].split("/")[-1] not in IMPORTANT_FILES, t["path"]))
    files = files[:max_files]

    output = []
    output.append(f"# {owner}/{repo}")
    output.append(f"\n> {info.get('description', 'No description')}")
    output.append(f"\n⭐ {info.get('stargazers_count', 0):,} stars | License: {info.get('license', {}).get('spdx_id', 'None') if info.get('license') else 'None'}")
    output.append(f"\nFiles included: {len(files)} of {len([t for t in all_items if t['type'] == 'blob'])}")
    output.append("\n---\n")

    # Tree overview
    output.append("## File Structure\n```")
    for t in sorted(all_items, key=lambda x: x["path"]):
        if t["path"].count("/") < 2:
            prefix = "  " * t["path"].count("/")
            suffix = "/" if t["type"] == "tree" else ""
            output.append(f"{prefix}{t['path'].split('/')[-1]}{suffix}")
    output.append("```\n\n---\n")

    # File contents
    for i, f in enumerate(files):
        path = f["path"]
        print(f"[repo2md] ({i+1}/{len(files)}) {path}", file=sys.stderr)
        lang = get_language_comment(path)
        content = get_file_content(owner, repo, branch, path, max_size)
        output.append(f"## `{path}`\n")
        output.append(f"```{lang}")
        output.append(content)
        output.append("```\n")

    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(description="Convert GitHub repo to markdown")
    parser.add_argument("url", help="GitHub URL or owner/repo")
    parser.add_argument("--max-files", type=int, default=75, help="Max files to include (default: 75)")
    parser.add_argument("--max-size", type=int, default=30000, help="Max bytes per file (default: 30000)")
    args = parser.parse_args()

    owner, repo = parse_github_url(args.url)
    print(convert(owner, repo, args.max_files, args.max_size))


if __name__ == "__main__":
    main()
