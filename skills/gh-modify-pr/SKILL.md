---
name: gh-modify-pr
description: Modify code based on GitHub PR review comments and create a local commit using gh + git. Use when the user asks to "follow PR comments", "fix review comments", "update this PR", or provides a PR URL and asks for edits/commit.
metadata:
  openclaw:
    requires:
      bins: ["gh", "git"]
---

# gh-modify-pr

Use this workflow for PR-comment-driven changes.

## Inputs

- PR URL (preferred), e.g. `https://github.com/owner/repo/pull/123`
- Optional scope from user (e.g. only one comment, all unresolved comments)

## Workflow

1. Parse owner/repo and PR number from URL.
2. Inspect PR summary:
   - `gh pr view <url> --json number,title,headRefName,baseRefName,files,reviews,reviewDecision`
3. Fetch inline review comments:
   - `gh api repos/<owner>/<repo>/pulls/<number>/comments`
4. Extract actionable items from comment bodies.
5. Ensure local repo exists in workspace:
   - If missing: `git clone git@github.com:<owner>/<repo>.git`
6. Checkout PR branch in local repo:
   - `gh pr checkout <number>`
7. Open affected files and implement requested changes exactly.
8. Validate changed files quickly (lint/test only if needed or requested).
9. Commit:
   - `git add <files>`
   - `git commit -m "<clear message>"`
10. Report back with:
   - What changed
   - Commit hash
   - Branch name
11. Push only if user asks/approves:
   - `git push`

## Rules

- Prefer minimal diffs that address reviewer intent directly.
- Do not silently alter unrelated code.
- If a comment is ambiguous, ask one focused clarification question.
- If no local repo exists, clone first instead of failing.
- Include failed attempts in the final operation log when user asks for traceability.

## Handy commands

```bash
# PR meta
gh pr view <url> --json number,title,headRefName,baseRefName,files,reviews,reviewDecision

# Inline review comments
gh api repos/<owner>/<repo>/pulls/<number>/comments

# Checkout PR branch (inside repo)
gh pr checkout <number>

# Status and commit
git status --short
git add <files>
git commit -m "chore: address PR review comments"
```

## Output template

- PR: `<url>`
- Addressed comments: `<n>`
- Changed files:
  - `<path>`: `<summary>`
- Commit: `<hash>`
- Branch: `<branch>`
- Pushed: `yes/no`
