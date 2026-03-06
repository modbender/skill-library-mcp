---
name: github-intel
description: "Analyze any GitHub repository in AI-friendly format. Convert entire repos to single markdown documents, generate architecture diagrams with Mermaid, inspect structure trees, language breakdowns, and recent activity. Includes GitHub URL tricks, API shortcuts, and advanced search techniques. Read-only analysis — never executes code from repositories. Built for AI agents — Python stdlib only, no dependencies. Use for repository analysis, code architecture review, open source research, GitHub intelligence, repo documentation, and codebase understanding."
homepage: https://www.agxntsix.ai
license: MIT
compatibility: Python 3.10+ (stdlib only — no dependencies)
metadata: {"openclaw": {"emoji": "🔍", "requires": {"env": []}, "primaryEnv": "GITHUB_TOKEN", "homepage": "https://www.agxntsix.ai"}}
---

# 🔍 GitHub Intelligence

Analyze any GitHub repository in AI-friendly format. Convert repos to markdown, generate architecture diagrams, understand structure and patterns.

## Features

- **Analyze repo structure** — file tree, README, language breakdown, recent activity
- **Generate architecture diagrams** — Mermaid flowcharts from codebase structure
- **Convert repo to markdown** — entire repository as a single AI-readable document
- **Inspect language breakdown** — percentage by language with file counts
- **Track recent activity** — latest commits, contributors, release history
- **GitHub URL tricks** — hidden features, API shortcuts, search operators
- **Control analysis depth** — configurable directory traversal depth
- **Limit file count** — cap files for large repos
- **Read-only guarantee** — never executes code from repositories
- **Public API access** — no token needed (optional token for higher rate limits)

## Requirements

| Variable | Required | Description |
|----------|----------|-------------|
| `GITHUB_TOKEN` | ❌ | Optional — increases rate limit from 60 to 5000 req/hr. Get from [GitHub Settings](https://github.com/settings/tokens) |

## Quick Start

```bash
PY=~/.openclaw/workspace/.venv/bin/python3

# Analyze a repository
$PY skills/github-intel/scripts/repo_analyzer.py https://github.com/anthropics/claude-code

# Convert repo to single markdown
$PY skills/github-intel/scripts/repo_to_markdown.py https://github.com/openai/openai-python

# Deep analysis
$PY skills/github-intel/scripts/repo_analyzer.py https://github.com/user/repo --depth 3
```

## Commands

### Repo Analyzer
```bash
# Basic analysis
$PY scripts/repo_analyzer.py https://github.com/owner/repo

# Deep directory traversal
$PY scripts/repo_analyzer.py https://github.com/owner/repo --depth 3

# With authentication for higher rate limits
GITHUB_TOKEN=ghp_xxx $PY scripts/repo_analyzer.py https://github.com/owner/repo
```

### Repo to Markdown
```bash
# Convert full repo
$PY scripts/repo_to_markdown.py https://github.com/owner/repo

# Limit files for large repos
$PY scripts/repo_to_markdown.py https://github.com/owner/repo --max-files 50

# Output to file
$PY scripts/repo_to_markdown.py https://github.com/owner/repo > repo.md
```

## Output Format (Analyzer)

```
# Repository: owner/repo

## Structure
├── src/
│   ├── index.ts
│   └── ...
├── README.md
└── package.json

## README
[Full README content]

## Language Breakdown
- TypeScript: 78.2%
- JavaScript: 15.1%
- Shell: 6.7%

## Architecture (Mermaid)
graph TD
  A[CLI Entry] --> B[Command Parser]
  ...

## Recent Activity
- 2 days ago: feat: add streaming support
- 5 days ago: fix: handle timeout errors
```

## References

| File | Description |
|------|-------------|
| `references/github-tricks.md` | URL hacks, API shortcuts, search operators |

## Script Reference

| Script | Description |
|--------|-------------|
| `{baseDir}/scripts/repo_analyzer.py` | Full repository analysis with diagrams |
| `{baseDir}/scripts/repo_to_markdown.py` | Convert repo to single markdown document |

## ⚠️ Security

**This tool is READ-ONLY. It NEVER:**
- Executes code from repositories
- Runs scripts, makefiles, or build commands
- Evaluates any content from repos
- Writes to any repository

All analysis is static file reading only.

## Data Policy

This skill fetches public data from GitHub's API. No data is stored locally beyond the analysis output.

---

Built by [M. Abidi](https://www.agxntsix.ai)

[LinkedIn](https://www.linkedin.com/in/mohammad-ali-abidi) · [YouTube](https://youtube.com/@aiwithabidi) · [GitHub](https://github.com/aiwithabidi) · [Book a Call](https://cal.com/agxntsix/abidi-openclaw)
