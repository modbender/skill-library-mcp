---
name: github-helper
description: Local GitHub repository helper for search, clone, sync, and issue/PR inspection workflows. Use when users mention github/repo/repository, ask to download or track repositories, or need structured local knowledge at /Users/liuchen/Documents/github with gh CLI and GitHub MCP integration.
---

# GitHub Helper

## Overview

管理本地 GitHub 仓库目录，维护可检索知识库，并为仓库检索、克隆、Issue/PR 跟踪提供统一流程。

## Local Repository Directory

**Default path**: `/Users/liuchen/Documents/github`

This path is referenced in the knowledge base file: `@/Users/liuchen/Documents/github/CLAUDE.md`

## Core Workflows

### 1. Initialize or Update Knowledge Base

When first using this skill or when user requests an update:

1. Check if the github directory exists.
2. If not found, ask user for the correct path.
3. Scan the directory using `scripts/scan_repos.py`.
4. Update CLAUDE.md using `scripts/update_kb.py`.

Example:
```bash
# Scan repositories
python3 scripts/scan_repos.py /Users/liuchen/Documents/github

# Update knowledge base (pass repos as JSON)
python3 scripts/update_kb.py /Users/liuchen/Documents/github '[{"name":"repo1","path":"/path","summary":"desc"}]'
```

### 2. Search for Repository

When user mentions a repository name:

1. **Check local first**: Read `@/Users/liuchen/Documents/github/CLAUDE.md`.
2. **If found locally**: Use local path to analyze and answer.
3. **If not found**: Search GitHub using `gh` or GitHub MCP tools.
4. **Offer to download**: Ask user whether to clone.

### 3. Download Repository

When user requests to download/clone:

1. Clone to the github directory:
   ```bash
   cd /Users/liuchen/Documents/github
   git clone <repo-url>
   ```
2. After successful clone, update knowledge base:
   - Run `scripts/scan_repos.py` to get repo info.
   - Run `scripts/update_kb.py` to update CLAUDE.md.

### 4. GitHub Search Integration

Use `gh` CLI first, then fall back to GitHub MCP:

**Search repositories**
```bash
gh search repos <query> --limit 10
```

**Search issues**
```bash
gh issue list --repo <owner/repo> --state all --limit 20
```

**Search PRs**
```bash
gh pr list --repo <owner/repo> --state all --limit 20
```

## Answering Repository Questions

1. Check whether repository exists in local knowledge base.
2. If local, prioritize local code inspection.
3. If information is insufficient, query GitHub issues/PRs/releases.

## Directory Validation

If `/Users/liuchen/Documents/github` does not exist:

1. Ask user for the correct repository root path.
2. Update this SKILL.md path if needed.
3. Initialize knowledge base at the new location.

## Scripts

- `scan_repos.py`: Scan local repositories and extract summaries.
- `update_kb.py`: Update `CLAUDE.md` with repository metadata.
