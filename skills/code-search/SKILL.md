---
name: Code Search Skill
description: Fast code search toolkit for exploring codebases. Provides
  structured grep (content search), glob (filename search), and tree (directory
  structure) via ripgrep, fd, and tree CLI tools.
---

# Code Search Skill

Fast code search toolkit for exploring codebases. Provides structured grep (content search), glob (filename search), and tree (directory structure) via ripgrep, fd, and tree CLI tools.

## When to Use

- Searching for function/class/variable definitions or usages in code
- Finding files by name or extension pattern
- Understanding project directory structure
- Exploring unfamiliar codebases
- Looking for configuration files, imports, error messages

## Prerequisites

Run dependency check first:
```bash
bash /root/.openclaw/workspace/skills/code-search/scripts/search.sh check
```

## Commands

All commands go through a single entry point:
```bash
bash /root/.openclaw/workspace/skills/code-search/scripts/search.sh <command> [options]
```

### grep — Search file contents

```bash
# Basic search
bash /root/.openclaw/workspace/skills/code-search/scripts/search.sh grep "func main" --path /some/project

# Literal text (no regex interpretation)
bash /root/.openclaw/workspace/skills/code-search/scripts/search.sh grep "fmt.Println(" --literal --path /some/project

# Filter by file type
bash /root/.openclaw/workspace/skills/code-search/scripts/search.sh grep "import" --type go --path /some/project

# With context lines
bash /root/.openclaw/workspace/skills/code-search/scripts/search.sh grep "TODO" --context 2 --path /some/project

# Limit results
bash /root/.openclaw/workspace/skills/code-search/scripts/search.sh grep "error" --max 20 --path /some/project
```

Options:
- `--path <dir>` — Search directory (default: current dir)
- `--type <ext>` — File type filter: go, py, ts, js, etc. (repeatable)
- `--literal` — Treat pattern as literal text, not regex
- `--max <n>` — Max results (default: 100)
- `--context <n>` — Show N lines of context around matches (default: 0)

### glob — Search filenames

```bash
# Find all Go files
bash /root/.openclaw/workspace/skills/code-search/scripts/search.sh glob "*.go" --path /some/project

# Find test files
bash /root/.openclaw/workspace/skills/code-search/scripts/search.sh glob "*_test.go" --path /some/project

# Find config files
bash /root/.openclaw/workspace/skills/code-search/scripts/search.sh glob "*.{json,yaml,yml,toml}" --path /some/project

# Filter by type
bash /root/.openclaw/workspace/skills/code-search/scripts/search.sh glob "config" --type f --path /some/project
```

Options:
- `--path <dir>` — Search directory (default: current dir)
- `--type <f|d>` — f=files only, d=directories only
- `--max <n>` — Max results (default: 200)

### tree — Directory structure

```bash
# Default (3 levels deep)
bash /root/.openclaw/workspace/skills/code-search/scripts/search.sh tree --path /some/project

# Shallow view
bash /root/.openclaw/workspace/skills/code-search/scripts/search.sh tree --path /some/project --depth 1

# With file sizes
bash /root/.openclaw/workspace/skills/code-search/scripts/search.sh tree --path /some/project --depth 2 --size
```

Options:
- `--path <dir>` — Target directory (default: current dir)
- `--depth <n>` — Max depth (default: 3)
- `--size` — Show file sizes

### check — Verify dependencies

```bash
bash /root/.openclaw/workspace/skills/code-search/scripts/search.sh check
```

## Output Format

All commands output structured text with clear delimiters:
- `[SEARCH RESULTS: grep]` / `[SEARCH RESULTS: glob]` / `[DIRECTORY TREE]`
- `[END RESULTS]` / `[END TREE]`
- `[TRUNCATED: ...]` when results exceed the limit
- `[ERROR] ...` on failures

## Notes

- All operations are read-only — no files are modified
- Automatically ignores .git, node_modules, __pycache__, vendor, build artifacts
- Respects .gitignore rules
- Results sorted by modification time (newest first) for grep and glob
