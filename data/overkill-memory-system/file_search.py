#!/usr/bin/env python3
"""
Fast File Search Module using fd and ripgrep
Optional tier for overkill-memory-system

Provides 10x speedup over Python glob/regex for file searching.
Falls back gracefully if fd/rg are not available.
"""

import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional

# Memory path
MEMORY_PATH = Path.home() / ".openclaw" / "memory"


def has_fd_rg() -> bool:
    """Check if fd and ripgrep are available on the system."""
    return shutil.which("fd") is not None and shutil.which("rg") is not None


def search_by_name(pattern: str, path: Optional[Path] = None) -> list[dict]:
    """
    Search for files by name using fd (fast alternative to glob).
    
    Args:
        pattern: Search pattern (supports fd's regex/glob syntax)
        path: Directory to search in (defaults to memory path)
    
    Returns:
        List of dicts with file info: {"path": str, "name": str}
    """
    if path is None:
        path = MEMORY_PATH
    
    if not has_fd_rg():
        return _fallback_search_by_name(pattern, path)
    
    try:
        result = subprocess.run(
            ["fd", "--type", "f", "-t", "f", pattern, str(path)],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            return []
        
        files = []
        for line in result.stdout.strip().split("\n"):
            if line:
                file_path = Path(line)
                files.append({
                    "path": str(file_path),
                    "name": file_path.name,
                    "type": "filename"
                })
        return files
    except Exception as e:
        print(f"fd search error: {e}", file=__import__('sys').stderr)
        return _fallback_search_by_name(pattern, path)


def search_by_content(query: str, path: Optional[Path] = None, limit: int = 50) -> list[dict]:
    """
    Search file contents using ripgrep (rg).
    
    Args:
        query: Search query string
        path: Directory to search in (defaults to memory path)
        limit: Maximum number of results
    
    Returns:
        List of dicts with match info: {"path", "line", "content", "matches"}
    """
    if path is None:
        path = MEMORY_PATH
    
    if not has_fd_rg():
        return _fallback_search_by_content(query, path, limit)
    
    try:
        # Use rg with JSON output for structured results
        result = subprocess.run(
            ["rg", "--json", "-n", "--max-count", str(limit), query, str(path)],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode not in (0, 1):  # 0=found, 1=no match
            return []
        
        matches = []
        for line in result.stdout.strip().split("\n"):
            if not line:
                continue
            try:
                data = json.loads(line)
                if data.get("type") == "match":
                    match_data = data.get("data", {})
                    matches.append({
                        "path": match_data.get("path", {}).get("text", ""),
                        "line": match_data.get("line_number", 0),
                        "content": match_data.get("lines", {}).get("text", "").strip(),
                        "type": "content"
                    })
            except json.JSONDecodeError:
                continue
        
        return matches
    except Exception as e:
        print(f"rg search error: {e}", file=__import__('sys').stderr)
        return _fallback_search_by_content(query, path, limit)


def fast_file_search(query: str, path: Optional[Path] = None, limit: int = 30) -> list[dict]:
    """
    Combined file name + content search.
    
    Searches both file names and contents, then merges and ranks results.
    Uses fd for names (fast) and rg for content.
    
    Args:
        query: Search query
        path: Directory to search in
        limit: Max results per category
    
    Returns:
        Merged, ranked list of results
    """
    if path is None:
        path = MEMORY_PATH
    
    results = []
    
    # 1. Search file names with fd
    name_results = search_by_name(query, path)
    for r in name_results[:limit]:
        r["source"] = "name"
        r["score"] = 1.0  # High score for exact name matches
        results.append(r)
    
    # 2. Search content with rg
    content_results = search_by_content(query, path, limit)
    for r in content_results:
        r["source"] = "content"
        r["score"] = 0.8  # Slightly lower for content matches
        results.append(r)
    
    # 3. Deduplicate by path, keeping highest score
    seen = {}
    for r in results:
        path_key = r["path"]
        if path_key not in seen or r["score"] > seen[path_key]["score"]:
            seen[path_key] = r
    
    # 4. Sort by score descending
    final = sorted(seen.values(), key=lambda x: x["score"], reverse=True)
    
    return final[:limit * 2]


# Fallback implementations using Python stdlib
def _fallback_search_by_name(pattern: str, path: Path) -> list[dict]:
    """Fallback using Python glob/regex if fd not available."""
    import re
    
    results = []
    # Convert glob-like pattern to regex
    regex_pattern = pattern.replace(".", r"\.").replace("*", ".*").replace("?", ".")
    
    try:
        regex = re.compile(regex_pattern)
    except re.error:
        regex = re.compile(re.escape(pattern))
    
    for file_path in path.rglob("*"):
        if file_path.is_file() and regex.search(file_path.name):
            results.append({
                "path": str(file_path),
                "name": file_path.name,
                "type": "filename"
            })
    
    return results


def _fallback_search_by_content(query: str, path: Path, limit: int) -> list[dict]:
    """Fallback using Python file reading if rg not available."""
    import re
    
    results = []
    try:
        regex = re.compile(query, re.IGNORECASE)
    except re.error:
        return []
    
    count = 0
    for file_path in path.rglob("*"):
        if not file_path.is_file() or count >= limit:
            continue
        
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                for line_num, line in enumerate(f, 1):
                    if regex.search(line):
                        results.append({
                            "path": str(file_path),
                            "line": line_num,
                            "content": line.strip(),
                            "type": "content"
                        })
                        count += 1
                        break  # One match per file enough for fallback
        except Exception:
            continue
    
    return results


# CLI helper functions
def format_search_results(results: list[dict]) -> str:
    """Format search results for CLI output."""
    if not results:
        return "No results found."
    
    output = []
    for i, r in enumerate(results, 1):
        path = r.get("path", "")
        # Make path relative to home
        try:
            path = str(Path(path).relative_to(Path.home()))
        except ValueError:
            pass
        
        if r.get("type") == "filename":
            output.append(f"{i}. 📄 {path}")
        else:
            line = r.get("line", "?")
            content = r.get("content", "")[:80]
            output.append(f"{i}. 📄 {path}:{line}\n   {content}")
    
    return "\n".join(output)


if __name__ == "__main__":
    # Simple CLI for testing
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python file_search.py <query>")
        sys.exit(1)
    
    query = sys.argv[1]
    results = fast_file_search(query)
    print(format_search_results(results))
