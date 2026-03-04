---
name: gitlab-code-reviewer
description: "Senior-level code review for GitLab merge requests. Use when: reviewing MRs, providing feedback on code quality, security, performance, maintainability, or preparing review comments for GitLab MRs."
---

# GitLab Code Reviewer

## Overview

Automated code review tool for GitLab merge requests. Analyzes code for security vulnerabilities, code quality issues, and best practices violations.

## ⚠️ Important: GitLab Access

**This tool uses GitLab API, NOT web pages.**

When reviewing a GitLab MR:
1. **DO NOT** try to fetch the MR URL as a web page (will fail - redirects to login)
2. **DO** use the CLI tool with credentials from `~/.openclaw/credentials/gitlab.json`
3. The tool automatically authenticates via `PRIVATE-TOKEN` header

Example workflow:
```
User: "Review MR !2223 in project kks/backend/bpm-platform"

✅ Correct: Run CLI tool with token authentication
❌ Wrong: Try to fetch https://git.company.com/... as web page
```

## When to Use

- Review merge requests automatically
- Find security vulnerabilities (SQL injection, XSS, hardcoded secrets, etc.)
- Detect code quality issues
- Generate review comments for GitLab

## Usage

### Via OpenClaw

```
"Review MR !42 in project group/project"
```

### Via CLI

```bash
# Using GitLab URL (recommended)
python scripts/gitlab_code_review.py --url "https://gitlab.com/group/project/-/merge_requests/42"

# Using project and MR IID
python scripts/gitlab_code_review.py --project group/project --mr 42

# Post comments to GitLab
python scripts/gitlab_code_review.py --project group/project --mr 42 --post-comments

# Save report to file
python scripts/gitlab_code_review.py --project group/project --mr 42 --output review.md

# From diff file (offline)
python scripts/gitlab_code_review.py --diff-file changes.json
```

## Configuration

### Credentials

Create `~/.openclaw/credentials/gitlab.json`:

```json
{
  "token": "glpat-xxx",
  "host": "https://gitlab.com",
  "ignore_patterns": [
    "*.min.js",
    "*.lock",
    "forms/*.json"
  ]
}
```

**Get token:** GitLab → Settings → Access Tokens → Create token with `read_api`, `write_repository` scopes.

**Priority:** `--token` arg > `GITLAB_TOKEN` env > credentials file

## Security Checks

| Category | Severity | Examples |
|----------|----------|----------|
| SQL Injection | HIGH | String concatenation in queries |
| XSS | HIGH | innerHTML, document.write |
| Command Injection | CRITICAL | os.system, subprocess with user input |
| Hardcoded Secrets | CRITICAL | Passwords, API keys, tokens |
| Weak Crypto | MEDIUM | MD5, SHA1, DES |
| Path Traversal | MEDIUM | User input in file paths |
| Auth Bypass | CRITICAL | Hardcoded admin checks |

## Review Priorities

- **🔴 Critical** — Block merge (security vulns, data loss)
- **🟡 Major** — Fix before merge (error handling, missing tests)
- **🟢 Minor** — Recommendations (style, documentation)

## Supported Languages

Python, JavaScript/TypeScript, Java, Go, Ruby, PHP, YAML, JSON

## File Ignoring

Default ignores: `*.min.js`, `*.min.css`, `*.lock`, `package-lock.json`, `pnpm-lock.yaml`, `forms/*.json`

Override with `--ignore "*.json" "*.lock"` or `--no-default-ignores`

## Troubleshooting

### "GitLab redirects to login page"

**Problem:** Trying to fetch GitLab URL as web page instead of using API.

**Solution:** Use the CLI tool with token authentication:
```bash
python scripts/gitlab_code_review.py --url "https://gitlab.com/group/project/-/merge_requests/123"
```

### "401 Unauthorized"

**Problem:** Token is invalid or expired.

**Solution:** 
1. Check token in `~/.openclaw/credentials/gitlab.json`
2. Generate new token: GitLab → Settings → Access Tokens
3. Required scopes: `read_api`, `write_repository`

### "404 Not Found"

**Problem:** Project path or MR IID is incorrect.

**Solution:** Verify the URL format:
- ✅ `https://gitlab.com/group/project/-/merge_requests/123`
- ❌ `https://gitlab.com/group/project/merge_requests/123` (old format may not work)

---

**Note:** This tool assists human review but doesn't replace it.
