---
name: requesting-code-review
description: Review diffs with structured checklist — spec compliance, security, tests, breaking changes, code quality
---

# Requesting Code Review — Structured Diff Review

## When to Use

- After each task completion
- Before merging any MR/PR
- After a subagent reports task completion

## Process

### Step 1: Get the Diff

Read the full diff. EVERY line. Do not skim.

```bash
git diff main..feature-branch
# or
gh pr diff [number]
```

### Step 2: Review Checklist

**Spec Compliance:**
- [ ] Implements what was requested (nothing missing)
- [ ] No extra/unrequested work (YAGNI)
- [ ] Matches the plan specification

**Code Quality:**
- [ ] Follows existing patterns in the codebase
- [ ] No duplicated logic
- [ ] Error handling present
- [ ] Types/interfaces correct

**Security:**
- [ ] No hardcoded secrets, tokens, passwords
- [ ] No credentials in comments or logs
- [ ] Input validation on API routes
- [ ] Authorization checks present
- [ ] No SQL injection or XSS vectors

**Critical Files:**
- [ ] No changes to critical infrastructure without coordination
- [ ] No breaking API response shape changes
- [ ] No queue/job config changes without impact analysis
- [ ] Schema changes coordinated across dependent services

**Testing:**
- [ ] Tests exist for new functionality
- [ ] Tests actually test behavior (not mock behavior)
- [ ] Edge cases covered

**Production Readiness:**
- [ ] No console.log debugging left
- [ ] No TODO/FIXME for critical paths
- [ ] No commented-out code

### Step 3: Post Verdict

**Approved:**
```
APPROVED

Strengths:
- [what's good]

No issues found. Ready to merge.
```

**Changes Requested:**
```
CHANGES REQUESTED

Issues:
1. [CRITICAL] file.ts:42 — [description and why]
2. [IMPORTANT] file.ts:87 — [description and why]
3. [MINOR] file.ts:12 — [suggestion]

Fix critical and important issues before merge.
```

### Step 4: Re-review After Fixes

When fixes are pushed, get the diff again and verify each issue is resolved. Do NOT skip re-review.
