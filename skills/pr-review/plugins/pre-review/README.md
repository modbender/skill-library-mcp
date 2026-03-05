# Pre-Review Skill

A Claude Code skill that performs comprehensive code review and audit using specialized agents and **automatically fixes issues**.

## Why This Exists

The official `code-review` plugin from Claude Code marketplace posts comments on GitHub PRs **after** publication. This creates an inefficient workflow:

```
PR published → review → issues found → comments posted → you fix → update PR
```

This skill inverts the workflow:

```
Code ready → /pre-review → issues found AND fixed → PR published clean
```

## Features

- **6 Parallel Agents**: 5 Sonnet agents for deep analysis + Haiku agents for coordination
- **Auto-Fix**: Issues are fixed directly in your code, not just reported
- **Confidence Scoring**: 0-100 scale filters out false positives (threshold: 70)
- **Guidelines Aware**: Reads CLAUDE.md, eslint, prettier configs
- **Git Context**: Analyzes git history to understand code evolution

## Agent Specializations

### `/pre-review` Agents

| Agent | Focus |
|-------|-------|
| #1 | CLAUDE.md & project guidelines compliance |
| #2 | Bug scanning (logic errors, null handling, etc.) |
| #3 | Git history context (regressions, breaking changes) |
| #4 | Security & performance issues |
| #5 | Code quality & test coverage |
| Haiku | Coordination, eligibility checks, confidence scoring |

### `/code-audit` Agents

| Agent | Focus |
|-------|-------|
| #1 | Security audit (injection, XSS, auth, secrets) |
| #2 | Bug detection (null handling, race conditions, leaks) |
| #3 | Data flow analysis (input validation, trust boundaries) |
| #4 | Performance & resources (N+1, memory, algorithms) |
| #5 | Code quality & maintainability |
| Haiku | Scope discovery, file categorization, deduplication |

## Installation

### Option 1: Install from Local Path

```bash
claude /plugin install /path/to/pre-review-skill
```

### Option 2: Add to Your Plugin Directory

Copy this folder to your Claude Code plugins directory:
- macOS/Linux: `~/.claude/plugins/pre-review-skill/`
- Windows: `%USERPROFILE%\.claude\plugins\pre-review-skill\`

### Option 3: Register as Local Marketplace

```bash
claude /plugin marketplace add /path/to/pre-review-skill
```

## Commands

### `/pre-review` - Review Changes Before PR

```bash
# In any git repository with uncommitted or committed changes on a branch
/pre-review
```

Best for: Feature branches, before opening a PR.

The skill will:
1. Check for changes compared to main/master
2. Discover project guidelines
3. Launch 5 parallel analysis agents
4. Score each issue for confidence
5. **Fix issues directly in your code**
6. Provide a summary report
7. Offer next steps (run tests, review diff, commit)

### `/code-audit` - Audit Existing Code

```bash
# Audit specific paths
/code-audit src/api/

# Audit with file pattern
/code-audit **/*.ts

# Audit entire codebase (will prompt for scope)
/code-audit
```

Best for: Personal repos, reviewing existing code, security audits.

The skill will:
1. Determine audit scope (specific paths or full codebase)
2. Categorize files by risk (auth, payments, data access = high priority)
3. Launch 5 parallel analysis agents
4. Score and deduplicate issues
5. **Auto-fix high-confidence issues (score >= 80)**
6. Generate comprehensive audit report
7. Offer next steps

**Key differences from `/pre-review`:**
- Does NOT require a branch or changes
- Audits code as it exists
- Prioritizes security-sensitive code
- Higher fix threshold (80 vs 70) for more conservative auto-fixing

## Output Examples

### `/pre-review` Output

```
## Pre-Review Complete

### Issues Found and Fixed: 3

1. **src/api/handler.ts:45** - Missing null check before accessing user.email
   - Severity: critical
   - Category: bug
   - Fix applied: Added optional chaining operator

2. **src/utils/parser.js:112** - SQL injection vulnerability in query builder
   - Severity: critical
   - Category: security
   - Fix applied: Used parameterized query

3. **src/components/List.tsx:78** - useEffect missing dependency
   - Severity: important
   - Category: bug
   - Fix applied: Added 'items' to dependency array

### Files Modified: 3
- src/api/handler.ts
- src/utils/parser.js
- src/components/List.tsx

### Recommendations
- Run `npm test` to verify fixes
- Review changes with `git diff`
```

### `/code-audit` Output

```
## Code Audit Report

### Summary
- Files Audited: 24
- Issues Found: 8
- Issues Fixed: 5
- Issues Requiring Manual Review: 3

### Critical Issues (Fixed)

1. **src/auth/login.ts:89** - SQL injection in user lookup
   - Category: security
   - Fix applied: Used parameterized query

2. **src/api/upload.ts:34** - Path traversal vulnerability
   - Category: security
   - Fix applied: Sanitized file path input

### Critical Issues (Manual Review Required)

1. **src/db/migrations.ts:156** - Potential race condition in schema update
   - Category: bug
   - Reason: Requires architectural decision on locking strategy
   - Recommended: Add database-level locking

### Security Summary
- [x] No hardcoded credentials found
- [x] No XSS vulnerabilities found
- [ ] 2 SQL injection risks found and fixed
- [ ] 1 path traversal fixed

### Files Modified: 3
- src/auth/login.ts
- src/api/upload.ts
- src/utils/validate.ts

### Recommendations
- Review manual issues before deploy
- Add integration tests for auth flow
- Consider security audit of remaining modules
```

## Configuration

The skill respects your project's existing configuration:
- `CLAUDE.md` - Project-specific Claude guidelines
- `.eslintrc.*` - ESLint rules
- `.prettierrc` - Prettier configuration
- `tsconfig.json` - TypeScript settings
- `CONTRIBUTING.md` - Contribution guidelines

## Command Comparison

| Aspect | `/pre-review` | `/code-audit` |
|--------|---------------|---------------|
| Requires changes | Yes (branch diff) | No |
| Scope | Changed files only | Any files/paths |
| Auto-fix threshold | 70 | 80 (more conservative) |
| Best for | Before PR | Personal repos, audits |
| Git history analysis | Yes | No |

## Comparison with code-review Plugin

| Aspect | code-review (plugin) | pre-review (this skill) |
|--------|---------------------|------------------------|
| When to run | After PR published | Before PR published |
| Output | GitHub comment | Direct code fixes |
| Workflow | Report issues | Fix issues |
| False positive handling | Threshold 80 | Threshold 70 |
| Use case | Team review bot | Solo dev workflow |

## License

MIT
