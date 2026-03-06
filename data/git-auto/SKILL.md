---
name: git-auto
description: Git workspace automation (status/commit/push/log/diff)
version: 1.0.0
author: 무펭이 🐧
---

# git-auto

**Git Workspace Automation** — Streamline daily Git operations with intelligent defaults. Status checks, smart commits, safe pushes, and diff analysis in one skill.

## When to Use

- Check workspace status across multiple repos
- Generate meaningful commit messages from staged changes
- Push with safety checks (branch protection, conflict detection)
- View formatted logs and diffs
- Batch operations across monorepo subdirectories

## Commands

### status
```bash
# Show concise workspace status
git-auto status
# Multi-repo status scan
git-auto status --all
```
Returns: modified files, untracked files, branch info, ahead/behind count.

### commit
```bash
# Auto-generate commit message from diff
git-auto commit
# With explicit message
git-auto commit -m "feat: add user auth"
# Commit specific files
git-auto commit -f "src/auth.ts,src/types.ts"
```
Behavior:
1. Runs `git diff --staged` to analyze changes
2. Generates conventional commit message (feat/fix/refactor/docs/chore)
3. Validates message format before committing
4. Shows commit hash and summary

### push
```bash
# Push current branch with safety checks
git-auto push
# Force push (with confirmation)
git-auto push --force
```
Safety checks:
- Warns if pushing to main/master directly
- Checks for upstream conflicts
- Verifies remote exists

### log
```bash
# Last 10 commits, formatted
git-auto log
# Last N commits
git-auto log -n 20
# Filter by author
git-auto log --author "name"
```

### diff
```bash
# Staged changes
git-auto diff
# Working directory changes
git-auto diff --unstaged
# Between branches
git-auto diff main..feature-branch
```

## Smart Commit Message Format

Uses [Conventional Commits](https://www.conventionalcommits.org/):
- `feat:` — New feature
- `fix:` — Bug fix
- `refactor:` — Code restructuring
- `docs:` — Documentation only
- `chore:` — Maintenance tasks
- `test:` — Adding/updating tests

## Integration

Works with any Git repository. No configuration needed — auto-detects `.git` directory and current branch. Pairs well with `code-review` skill for pre-commit analysis.

## Error Handling

| Situation | Behavior |
|-----------|----------|
| Not a git repo | Clear error message with suggestion |
| Merge conflicts | Shows conflict files, suggests resolution |
| No staged changes | Prompts to stage or shows unstaged changes |
| Auth failure | Suggests credential refresh |
| Detached HEAD | Warns and suggests creating branch |
