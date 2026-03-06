# Integration: file-search

## Overview

Add fast file search using `fd` and `rg` to the overkill-memory-system.

## Requirements

- `fd` - Fast file finder
- `rg` - Ripgrep content search

## How It Works

```bash
# File name search
fd "pattern" /path

# Content search  
rg "query" /path
```

## Integration with Memory System

### Current File Tier
Currently uses simple Python glob/regex for searching:
- `~/.openclaw/memory/daily/`
- `~/.openclaw/memory/diary/`
- `~/.openclaw/memory/*.md`

### Enhanced with file-search

| Search Type | Current | With file-search |
|-------------|---------|------------------|
| File names | glob() | fd |
| Content | regex | rg |
| Speed | Slow | Fast |
| Features | Basic | Regex, context, filetype |

## Implementation

### 1. Add file_search.py

```python
import subprocess
from pathlib import Path

MEMORY_PATH = Path("~/.openclaw/memory").expanduser()

def search_files_by_name(pattern: str, path: Path = MEMORY_PATH) -> list[str]:
    """Search for files by name using fd"""
    try:
        result = subprocess.run(
            ["fd", pattern, str(path)],
            capture_output=True, text=True, timeout=5
        )
        return result.stdout.strip().split("\n")
    except Exception:
        return []

def search_files_by_content(query: str, path: Path = MEMORY_PATH) -> list[dict]:
    """Search file contents using rg"""
    try:
        result = subprocess.run(
            ["rg", "-n", "--json", query, str(path)],
            capture_output=True, text=True, timeout=10
        ]
        # Parse JSON output
        return parse_rg_json(result.stdout)
    except Exception:
        return []

def fast_file_search(query: str, path: Path = MEMORY_PATH) -> list[dict]:
    """Combined file + content search"""
    # 1. Search file names
    name_results = search_files_by_name(query, path)
    
    # 2. Search content
    content_results = search_files_by_content(query, path)
    
    # Merge and rank
    return merge_results(name_results, content_results)
```

### 2. Update CLI

```bash
# Add to cli.py
# New command: file-search
overkill file search "pattern"    # By name
overkill file content "query"     # By content
overkill file fast "query"        # Combined
```

### 3. Integrate into Search Tiers

```python
def search_file_tier(query: str, use_fast: bool = False):
    """Search file tier with optional fast mode"""
    if use_fast and has_fd_rg():
        return fast_file_search(query)
    else:
        return slow_file_search(query)  # Current method
```

## Speed Comparison

| Method | 100 files | 1000 files |
|--------|-----------|-------------|
| Python glob | ~50ms | ~200ms |
| fd/rg | ~5ms | ~20ms |

**Expected speedup: 10x**

## Fallback Strategy

```python
def has_fd_rg() -> bool:
    """Check if fd and rg are available"""
    return (
        shutil.which("fd") is not None and
        shutil.which("rg") is not None
    )

def search_tier(query):
    if has_fd_rg():
        return fast_search(query)
    return slow_search(query)  # Fallback
```

## CLI Commands

```bash
# File name search (like current file tier)
overkill file search "*.md"

# Content search (new!)
overkill file content "TODO"

# Fast combined search
overkill file fast "pattern"

# Index memory files (optional)
overkill file index
```

## Summary

| Aspect | Value |
|--------|-------|
| Speed gain | 10x |
| Dependencies | fd, rg (optional) |
| Fallback | Yes (slow mode) |
| New commands | 3-4 |
| Integration effort | Low |

*file-search integration analysis*
