---
name: GitHub Issue Manager
description: Fetch GitHub issues, spawn sub-agents to implement fixes, open PRs,
  and monitor review comments.
---

# GitHub Issue Manager

Fetch GitHub issues, spawn sub-agents to implement fixes, open PRs, and monitor review comments.

## Overview

This skill enables autonomous issue management on GitHub repositories. It can:
- List and filter issues by labels, milestones, assignees
- Spawn sub-agents to work on fixes
- Create PRs with automated descriptions
- Track PR review status and respond to comments

## Prerequisites

- `gh` CLI must be authenticated (`gh auth status`)
- Repository must be accessible via HTTPS or SSH

## Configuration

```bash
# Optional: Set default repo
export GITHUB_REPO="owner/repo"
export GITHUB_TOKEN="ghp_xxx"  # Or use gh auth
```

## Commands

### List Issues

```bash
# All open issues
gh issue list

# With labels
gh issue list --label "bug" --label "priority"

# Assigned to you
gh issue list --assignee "@me"
```

### Create Issue

```bash
gh issue create --title "Fix login bug" --body "Description..." --label bug
```

### View Issue Details

```bash
gh issue view 123
```

## Usage in Agents

```python
# Spawn agent to fix issue
spawn_subagent(
  task=f"Fix GitHub issue #{issue_number}: {title}. {description}"
)
```

## Notes

- Requires `gh` CLI installed
- Authentication handled via `gh auth`
- Rate limits apply (5000 requests/hour for authenticated users)
