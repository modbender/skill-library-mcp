| allowed-tools | description |
|---|---|
| Bash(git *), Read, Edit, Write, Glob, Grep, Task | Audit existing code for bugs, security issues, and quality problems |

# Code Audit: Deep Analysis of Existing Code

Analyze existing code in the repository (or specific paths) for bugs, security issues, and quality problems. Unlike pre-review, this does NOT require a branch or changes - it audits code as it exists.

## Usage

The user may specify:
- Specific files or directories to audit: `/code-audit src/api/`
- File patterns: `/code-audit **/*.ts`
- Nothing (audits entire codebase, with smart prioritization)

## Instructions

Follow these steps precisely:

### Step 0: Initialize Progress Tracking

Create a todo list to track progress through all steps. This provides visibility to the user as the audit progresses.

### Step 1: Scope Discovery (Haiku Agent)

Use a Haiku agent to determine audit scope:

**If user specified paths/patterns:**
- Resolve the paths/patterns to actual files
- Count files and estimate scope
- If > 50 files, ask user to narrow scope or confirm full audit

**If no paths specified:**
- List top-level directories
- Identify main source directories (src/, lib/, app/, etc.)
- Exclude obvious non-code: node_modules, dist, build, vendor, .git
- Propose a reasonable scope to the user

Return the list of files to audit.

### Step 2: Discover Project Guidelines (Haiku Agent)

Use a Haiku agent to find and read:
- Root CLAUDE.md file (if exists)
- Any CLAUDE.md files in directories being audited
- .eslintrc, .prettierrc, tsconfig.json, or similar config files
- Any CONTRIBUTING.md or code style guides
- Package.json or similar to understand the tech stack

Return a summary of:
- Tech stack and framework
- Coding guidelines found
- Key patterns to look for

### Step 3: File Categorization (Haiku Agent)

Use a Haiku agent to categorize files by risk/priority:

**High Priority (audit first):**
- Authentication/authorization code
- Payment/financial logic
- Database queries and data access
- API endpoints and controllers
- Input validation and sanitization
- File upload/download handlers
- Encryption/security utilities

**Medium Priority:**
- Business logic
- Service layers
- Utility functions
- State management

**Low Priority:**
- Tests (unless specifically requested)
- Configuration
- Types/interfaces only
- Constants

Return categorized file list.

### Step 4: Parallel Deep Analysis (5 Sonnet Agents)

Launch 5 parallel Sonnet agents to analyze the high and medium priority files. Each agent should return:
- List of specific issues found
- File path and line numbers
- Severity (critical, important, minor)
- Suggested fix
- Confidence score (0-100)

**Agent #1 - Security Audit:**
Scan for security vulnerabilities:
- SQL/NoSQL injection
- XSS vulnerabilities
- Command injection
- Path traversal
- Insecure deserialization
- Hardcoded secrets/credentials
- Weak cryptography
- Authentication bypasses
- Authorization flaws
- SSRF vulnerabilities

**Agent #2 - Bug Detection:**
Scan for bugs and logic errors:
- Null/undefined handling issues
- Off-by-one errors
- Race conditions
- Resource leaks (memory, file handles, connections)
- Infinite loops or recursion
- Dead code paths
- Unreachable code
- Type coercion issues
- Async/await mistakes
- Error swallowing

**Agent #3 - Data Flow Analysis:**
Trace data through the application:
- Unvalidated user input reaching sensitive operations
- Data leaks (logging sensitive data, exposing in errors)
- Missing input sanitization
- Inconsistent data validation
- Trust boundary violations

**Agent #4 - Performance & Resources:**
Identify performance issues:
- N+1 query patterns
- Missing pagination
- Unbounded loops over user data
- Memory accumulation
- Blocking operations in async context
- Missing caching opportunities
- Inefficient algorithms (O(n^2) when O(n) possible)
- Large payload handling

**Agent #5 - Code Quality & Maintainability:**
Check code health:
- Functions/methods too long (> 50 lines)
- High cyclomatic complexity
- Deep nesting (> 4 levels)
- Duplicated logic
- Missing error handling
- Inconsistent patterns
- Outdated patterns (callbacks vs promises vs async/await)
- Dead code
- TODOs and FIXMEs that look critical

### Step 5: Issue Deduplication & Scoring (Haiku Agent)

Use a Haiku agent to:
- Remove duplicate issues found by multiple agents
- Merge related issues
- Re-score based on full context

Scoring criteria:
- **90-100:** Critical security or data loss risk. Must fix.
- **70-89:** Real bug that will cause problems. Should fix.
- **50-69:** Code smell or potential issue. Consider fixing.
- **Below 50:** Minor or stylistic. Note but don't fix automatically.

### Step 6: Fix High-Confidence Issues

For issues scoring >= 80, **fix directly**:

1. Read the file containing the issue
2. Apply the fix using Edit tool
3. Verify the fix doesn't break surrounding code

**DO NOT auto-fix:**
- Issues that require architectural changes
- Issues where the fix is ambiguous
- Issues in test files (report only)
- Issues scoring below 80

### Step 7: Audit Report

Generate a comprehensive report:

```
## Code Audit Report

### Summary
- Files Audited: X
- Issues Found: Y
- Issues Fixed: Z
- Issues Requiring Manual Review: W

### Critical Issues (Fixed)

1. **[file:line]** - Description
   - Category: security/bug/performance/quality/guidelines
   - Fix applied: Description of fix

### Critical Issues (Manual Review Required)

1. **[file:line]** - Description
   - Category: security/bug/performance/quality/guidelines
   - Reason not auto-fixed: Requires architectural decision
   - Recommended fix: Description

### Important Issues

1. **[file:line]** - Description
   - Confidence: XX%
   - Suggested fix: Description

### Minor Issues & Code Smells

1. **[file:line]** - Brief description

### Security Summary
- [ ] No hardcoded credentials found / X instances found
- [ ] No SQL injection risks / X potential risks
- [ ] No XSS vulnerabilities / X potential vulnerabilities
- [ ] Input validation adequate / X gaps found

### Files Modified
- path/to/file1.js
- path/to/file2.ts

### Recommendations
- Priority items for manual review
- Suggested refactoring opportunities
- Tests to add
```

### Step 8: Offer Next Steps

Ask the user:
- "Review specific issues in detail?"
- "Run tests to verify fixes?"
- "Audit additional directories?"
- "Generate a TODO list for manual fixes?"

## Important Guidelines

- **DO fix clear bugs and security issues** with high confidence
- **DON'T make sweeping changes** - focus on real problems
- **DON'T refactor working code** unless it has actual bugs
- **DO preserve existing patterns** - match the codebase style
- **DO be conservative** - when in doubt, report instead of fix
- **DON'T audit node_modules, vendor, or generated code**

## Confidence Scoring Guide

- **100:** Definite bug/vulnerability with clear evidence
- **90:** Very likely real issue, straightforward fix
- **80:** Real issue, fix is clear but verify
- **70:** Probably real, but context might change assessment
- **60:** Possible issue, needs human judgment
- **50:** Code smell, not necessarily wrong
- **Below 50:** Stylistic or very minor

## Notes

- For large codebases, suggest auditing one module at a time
- Prioritize security-sensitive code (auth, payments, data access)
- Update todo list as you complete each step
- If no issues found, confirm the code looks healthy
- Always provide actionable recommendations
