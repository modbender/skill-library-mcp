---
name: afrexai-code-reviewer
description: Enterprise-grade code review agent. Reviews PRs, diffs, or code files for security vulnerabilities, performance issues, error handling gaps, architecture smells, and test coverage. Works with any language, any repo, no dependencies required.
auto_trigger: false
---

# Code Review Engine

Enterprise-grade automated code review. Works on GitHub PRs, local diffs, pasted code, or entire files. No dependencies — pure agent intelligence.

## Quick Start

### Review a GitHub PR
```
Review PR #42 in owner/repo
```

### Review a local diff
```
Review the staged changes in this repo
```

### Review a file
```
Review src/auth/login.ts for security issues
```

### Review pasted code
Just paste code and say "review this"

---

## Review Framework: SPEAR

Every review follows the **SPEAR** framework — 5 dimensions, each scored 1-10:

### 🔴 S — Security (Weight: 3x)
| Check | Severity | Example |
|-------|----------|---------|
| Hardcoded secrets | CRITICAL | API keys, passwords, tokens in source |
| SQL injection | CRITICAL | String concatenation in queries |
| XSS vectors | HIGH | Unsanitized user input in HTML/DOM |
| Path traversal | HIGH | User input in file paths without validation |
| Insecure deserialization | HIGH | `eval()`, `pickle.loads()`, `JSON.parse` on untrusted input |
| Auth bypass | CRITICAL | Missing auth checks on endpoints |
| SSRF | HIGH | User-controlled URLs in server requests |
| Timing attacks | MEDIUM | Non-constant-time string comparison for secrets |
| Dependency vulnerabilities | MEDIUM | Known CVEs in imported packages |
| Sensitive data logging | MEDIUM | PII, tokens, passwords in log output |
| Insecure randomness | MEDIUM | `Math.random()` for security-sensitive values |
| Missing rate limiting | MEDIUM | Auth endpoints without throttling |

### 🟡 P — Performance (Weight: 2x)
| Check | Severity | Example |
|-------|----------|---------|
| N+1 queries | HIGH | DB call inside a loop |
| Unbounded queries | HIGH | `SELECT *` without LIMIT on user-facing endpoints |
| Missing indexes (implied) | MEDIUM | Frequent WHERE/ORDER on unindexed columns |
| Memory leaks | HIGH | Event listeners never removed, growing caches |
| Blocking main thread | HIGH | Sync I/O in async context, CPU-heavy in event loop |
| Unnecessary re-renders | MEDIUM | React: missing memo, unstable refs in deps |
| Large bundle imports | MEDIUM | `import _ from 'lodash'` vs `import get from 'lodash/get'` |
| Missing pagination | MEDIUM | Returning all records to client |
| Redundant computation | LOW | Same expensive calc repeated without caching |
| Connection pool exhaustion | HIGH | Not releasing DB/HTTP connections |

### 🟠 E — Error Handling (Weight: 2x)
| Check | Severity | Example |
|-------|----------|---------|
| Swallowed errors | HIGH | Empty catch blocks, Go `_ :=` on error |
| Missing error boundaries | MEDIUM | React components without error boundaries |
| Unchecked null/undefined | HIGH | No null checks before property access |
| Missing finally/cleanup | MEDIUM | Resources opened but not guaranteed closed |
| Generic error messages | LOW | `catch(e) { throw new Error("something went wrong") }` |
| Missing retry logic | MEDIUM | Network calls without retry on transient failures |
| Panic/exit in library code | HIGH | `panic()`, `os.Exit()`, `process.exit()` in non-main |
| Unhandled promise rejections | HIGH | Async calls without `.catch()` or try/catch |
| Error type conflation | MEDIUM | All errors treated the same (4xx vs 5xx, retriable vs fatal) |

### 🔵 A — Architecture (Weight: 1.5x)
| Check | Severity | Example |
|-------|----------|---------|
| God functions (>50 lines) | MEDIUM | Single function doing too many things |
| God files (>300 lines) | MEDIUM | Monolithic module |
| Tight coupling | MEDIUM | Direct DB calls in request handlers |
| Missing abstraction | LOW | Repeated patterns that should be extracted |
| Circular dependencies | HIGH | A imports B imports A |
| Wrong layer | MEDIUM | Business logic in controllers, SQL in UI |
| Magic numbers/strings | LOW | Hardcoded values without named constants |
| Missing types | MEDIUM | `any` in TypeScript, missing type hints in Python |
| Dead code | LOW | Unreachable branches, unused imports/variables |
| Inconsistent patterns | LOW | Different error handling styles in same codebase |

### 📊 R — Reliability (Weight: 1.5x)
| Check | Severity | Example |
|-------|----------|---------|
| Missing tests for changes | HIGH | New logic without corresponding test |
| Test quality | MEDIUM | Tests that only check happy path |
| Missing edge cases | MEDIUM | No handling for empty arrays, null, boundary values |
| Race conditions | HIGH | Shared mutable state without synchronization |
| Non-idempotent operations | MEDIUM | Retrying could cause duplicates |
| Missing validation | HIGH | User input accepted without schema validation |
| Brittle tests | LOW | Tests depending on execution order or timing |
| Missing logging | MEDIUM | Error paths with no observability |
| Configuration drift | MEDIUM | Hardcoded env-specific values |
| Missing migrations | HIGH | Schema changes without migration files |

---

## Scoring System

### Per-Finding Severity
```
CRITICAL  → -3 points from dimension score
HIGH      → -2 points
MEDIUM    → -1 point
LOW       → -0.5 points
INFO      → 0 (suggestion only)
```

### Overall SPEAR Score Calculation
```
Raw Score = (S×3 + P×2 + E×2 + A×1.5 + R×1.5) / 10
Final Score = Raw Score × 10  (scale 0-100)
```

### Verdict Thresholds
| Score | Verdict | Action |
|-------|---------|--------|
| 90-100 | ✅ EXCELLENT | Ship it |
| 75-89 | 🟢 GOOD | Minor suggestions, approve |
| 60-74 | 🟡 NEEDS WORK | Address findings before merge |
| 40-59 | 🟠 SIGNIFICANT ISSUES | Major rework needed |
| 0-39 | 🔴 BLOCK | Critical issues, do not merge |

---

## Review Output Template

Use this structure for every review:

```markdown
# Code Review: [PR title or file name]

## Summary
[1-2 sentence overview of what this code does and overall quality]

## SPEAR Score: [X]/100 — [VERDICT]

| Dimension | Score | Key Finding |
|-----------|-------|-------------|
| 🔴 Security | X/10 | [worst finding or "Clean"] |
| 🟡 Performance | X/10 | [worst finding or "Clean"] |
| 🟠 Error Handling | X/10 | [worst finding or "Clean"] |
| 🔵 Architecture | X/10 | [worst finding or "Clean"] |
| 📊 Reliability | X/10 | [worst finding or "Clean"] |

## Findings

### [CRITICAL/HIGH] 🔴 [Title]
**File:** `path/to/file.ts:42`
**Category:** Security
**Issue:** [What's wrong]
**Impact:** [What could happen]
**Fix:**
```[lang]
// suggested fix
```

### [MEDIUM] 🟡 [Title]
...

## What's Done Well
- [Genuinely good patterns worth calling out]

## Recommendations
1. [Prioritized action items]
```

---

## Language-Specific Patterns

### TypeScript / JavaScript
- `any` type usage → Architecture finding
- `as` type assertions → potential runtime error
- `console.log` in production code → Style
- `==` instead of `===` → Reliability
- Missing `async/await` error handling
- `useEffect` missing cleanup return
- Index signatures without validation

### Python
- Bare `except:` or `except Exception:` → Error Handling
- `eval()` / `exec()` → Security CRITICAL
- Mutable default arguments → Reliability
- `import *` → Architecture
- Missing `__init__.py` type hints
- f-strings with user input → potential injection

### Go
- `_ :=` discarding errors → Error Handling HIGH
- `panic()` in library code → Reliability HIGH
- Missing `defer` for resource cleanup
- Exported functions without doc comments
- `interface{}` / `any` overuse

### Java
- Catching `Exception` or `Throwable` → Error Handling
- Missing `@Override` annotations
- Mutable static fields → thread safety
- `System.out.println` in production
- Missing null checks (pre-Optional code)

### SQL
- String concatenation in queries → Security CRITICAL
- `SELECT *` → Performance
- Missing WHERE on UPDATE/DELETE → Security CRITICAL
- No LIMIT on user-facing queries → Performance
- Missing indexes for JOIN columns

---

## Advanced Techniques

### Reviewing for Business Logic
Beyond code quality, check:
- Does the code match the PR description / ticket requirements?
- Are there edge cases the spec didn't mention?
- Could this break existing functionality?
- Is there a simpler way to achieve the same result?

### Reviewing for Operability
- Can this be debugged in production? (logging, error messages)
- Can this be rolled back safely?
- Are feature flags needed?
- What monitoring should accompany this change?

### Reviewing Database Changes
- Is the migration reversible?
- Will it lock tables during migration?
- Are there indexes for new query patterns?
- Is there a data backfill needed?

### Security Review Depth Levels
| Level | When | What |
|-------|------|------|
| Quick | Internal tool, trusted input | OWASP Top 10 patterns only |
| Standard | User-facing feature | + auth, input validation, output encoding |
| Deep | Payment, auth, PII handling | + crypto review, session management, audit logging |
| Threat Model | New service/API surface | + attack surface mapping, trust boundaries |

---

## Integration Patterns

### GitHub PR Review
```bash
# Get PR diff
gh pr diff 42 --repo owner/repo

# Get PR details
gh pr view 42 --repo owner/repo --json title,body,files,commits

# Post review comment
gh pr review 42 --repo owner/repo --comment --body "review content"
```

### Local Git Review
```bash
# Review staged changes
git diff --cached

# Review branch vs main
git diff main..HEAD

# Review last N commits
git log -5 --oneline && git diff HEAD~5..HEAD
```

### Heartbeat / Cron Integration
```
Check for open PRs in [repo] that I haven't reviewed yet.
For each, run a SPEAR review and post the results as a PR comment.
```

---

## Edge Cases & Gotchas

- **Large PRs (>500 lines):** Break into logical chunks. Review file-by-file. Flag the PR size itself as a finding (Architecture: "PR too large — consider splitting").
- **Generated code:** Skip generated files (proto, swagger, migrations from ORMs). Note that you skipped them.
- **Dependency updates:** Focus on breaking changes in changelogs, not the lockfile diff.
- **Merge conflicts markers:** Flag immediately as CRITICAL — `<<<<<<<` in code means broken merge.
- **Binary files:** Note presence, can't review content.
- **Config changes:** Extra scrutiny — wrong env var = production outage.
- **Refactors:** Verify behavior preservation. Check if tests still pass conceptually.

---

## Review Checklist (Quick Mode)

For fast reviews when full SPEAR isn't needed:

- [ ] No hardcoded secrets or credentials
- [ ] No SQL injection / XSS / path traversal
- [ ] All errors handled (no empty catch, no discarded errors)
- [ ] No N+1 queries or unbounded operations
- [ ] Tests exist for new/changed logic
- [ ] No `console.log` / `print` / `fmt.Print` left in
- [ ] Functions under 50 lines, files under 300 lines
- [ ] Types are specific (no `any` / `interface{}`)
- [ ] PR description matches the actual changes
- [ ] No TODOs without linked issues
