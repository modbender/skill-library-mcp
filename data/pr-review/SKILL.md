---
name: pr-review
description: Find and fix code issues before publishing a PR. Single-pass review with auto-fix. Use when reviewing code changes before submission or auditing existing code for bugs/security. Don't use when running a coding agent to write code (use coding-agent) or checking GitHub CI status (use github).
metadata: {"openclaw": {"requires": {"bins": ["git"]}}}
---

# Pre-Review

Find and fix issues **before** publishing your PR — not after.

Single-pass review using one capable model. No orchestration overhead, no agent swarm. Fast, cheap, thorough.

## When to use
- Reviewing code changes before publishing a PR
- Auditing existing code for bugs, security, or quality issues
- Finding and fixing issues in specific files or directories

## When NOT to use
- Running a coding agent to write new code → use `coding-agent`
- Checking GitHub CI status → use `github`
- Managing forks or rebasing branches → use `fork-manager`

## Usage

```
/pr-review                    # Review changes on current branch vs main/master
/pr-review src/api/ src/auth/ # Audit specific directories
/pr-review **/*.ts            # Audit files matching a pattern
/pr-review --audit            # Audit entire codebase with smart prioritization
```

Two modes:

| Mode | Trigger | Scope | Fix threshold |
|------|---------|-------|---------------|
| **Diff** | No args, on branch with changes | Changed files only | >= 70 |
| **Audit** | Paths, patterns, or `--audit` | Specified files or full codebase | >= 80 |

## Instructions

### Step 1: Detect Mode and Scope

**No arguments provided:**
```bash
git diff main...HEAD --name-only 2>/dev/null || git diff master...HEAD --name-only
```
- If changes exist → **Diff mode**
- If no changes → inform user, stop

**Paths/patterns provided or `--audit`:**
- Resolve to actual files (exclude node_modules, dist, build, vendor, .git, coverage)
- If > 50 files, ask user to narrow scope or confirm
- **Audit mode**

### Step 2: Gather Context

Read project guidelines (quick scan, don't overthink):
```bash
# Check for project conventions
cat CLAUDE.md .claude/settings.json CONTRIBUTING.md 2>/dev/null | head -100
cat .eslintrc* .prettierrc* biome.json tsconfig.json 2>/dev/null | head -50
cat package.json 2>/dev/null | head -20  # tech stack
```

Get the diff or file contents:
```bash
# Diff mode
git diff main...HEAD  # or master

# Audit mode
cat <files>  # read target files
```

### Step 3: Review (Single Pass)

Analyze all code in one pass. Cover these areas in priority order:

**1. Correctness** (highest priority)
- Logic errors, edge cases, null/undefined handling
- Off-by-one, pagination boundaries, numeric precision
- Async/await mistakes, race conditions, resource leaks
- Data consistency, idempotency

**2. Security**
- Injection vulnerabilities (SQL, XSS, command, path traversal)
- Auth/authz gaps, IDOR risks, exposed secrets
- Unvalidated input reaching sensitive operations
- Logging sensitive data, insecure defaults

**3. Reliability**
- Error handling gaps, silent failures, swallowed exceptions
- Missing timeouts, retries without backoff
- Unbounded operations on user-controlled data

**4. Performance**
- N+1 queries, unnecessary loops, memory bloat
- Missing pagination, inefficient algorithms
- Blocking operations in async context

**5. Quality** (lowest priority — skip if trivial)
- Missing tests for new functionality
- Dead code, duplicated logic
- Stale comments, unclear naming
- Style issues **only** if they violate project guidelines

### Step 4: Score and Classify

For each issue found, assign:

| Score | Meaning | Action |
|-------|---------|--------|
| 90-100 | Critical bug or vulnerability | Must fix |
| 70-89 | Real issue, will cause problems | Should fix |
| 50-69 | Code smell, needs human judgment | Report only |
| < 50 | Minor, likely false positive | Discard |

**Discard thresholds:**
- Diff mode: discard below 50
- Audit mode: discard below 40

**Classify each issue:**
- `blocker` — security, data corruption, crash risk
- `important` — likely bug, perf regression, missing validation
- `minor` — edge case, maintainability, style

### Step 5: Auto-Fix

Apply fixes directly for issues meeting the threshold:
- **Diff mode:** fix issues scoring **>= 70**
- **Audit mode:** fix issues scoring **>= 80**

For each fix: read file → apply edit → verify surrounding code preserved.

**Never auto-fix:**
- Issues requiring architectural changes
- Ambiguous fixes with multiple valid approaches
- Issues in test files (report only)

After fixing, if any files were modified:
```bash
git diff --stat  # show what changed
```

### Step 6: Report

**Format:**

```
## Pre-Review Complete

**Risk:** Low / Medium / High
**Verdict:** ✅ Clean | ⚠️ Issues found | 🔴 Blockers

### 🔴 Blockers (must fix)
1. **file:line** — Description
   - Impact: what goes wrong
   - Fix: applied ✅ | manual required (reason)

### ⚠️ Important (should fix)
1. **file:line** — Description (score: XX)
   - Fix: applied ✅ | suggestion

### 💡 Minor
1. **file:line** — Description

### Tests to Add
- description of test

### Files Modified: N
- path/to/file.ts
```

If zero issues found: `## Pre-Review Complete — ✅ Clean. No issues found.`

## Guidelines

**DO:**
- Fix issues directly, not just report them
- Match existing code patterns and style
- Be specific: file, line, concrete fix
- Prioritize impact over thoroughness

**DON'T:**
- Fix pre-existing issues in diff mode — only what changed
- Bikeshed on style unless it violates project guidelines
- Report what a linter or type checker would catch (assume CI handles these)
- Make architectural changes or large refactors
- Spend tokens on obvious non-issues

## False Positives to Avoid

- Pre-existing code not touched by the current change (diff mode)
- Intentional patterns that look unusual but are correct
- Issues a type checker or linter would flag
- Style opinions not grounded in project guidelines
- General nitpicks a senior engineer would skip
