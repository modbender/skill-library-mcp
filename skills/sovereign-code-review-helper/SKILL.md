# Code Review Helper

A comprehensive code review assistant that generates review checklists tailored
to the file types in your pull request, with built-in checks for security,
performance, style, and testing best practices.

## Overview

Code Review Helper automates the tedious parts of code review by scanning
changed files and producing:

- **File-type-specific checklists** (JavaScript, Python, Go, Rust, SQL, etc.)
- **Security audit items** (injection, auth, secrets, input validation)
- **Performance review points** (N+1 queries, memory leaks, complexity)
- **Style consistency checks** (naming, formatting, import ordering)
- **Test coverage reminders** (missing tests, edge cases, mocks)
- **PR review templates** ready to paste into GitHub, GitLab, or Bitbucket

This skill helps reviewers be thorough and consistent, reducing the chance of
overlooked issues reaching production.

## Installation

### Via ClawHub

```bash
openclaw install code-review-helper
```

### Manual Installation

1. Copy the skill to your OpenClaw skills directory:

```bash
mkdir -p ~/.openclaw/skills/
cp -r code-review-helper/ ~/.openclaw/skills/
```

2. Make the script executable:

```bash
chmod +x ~/.openclaw/skills/code-review-helper/scripts/review.sh
```

3. Verify the installation:

```bash
openclaw list --installed
```

## Requirements

- **git** (version 2.0 or higher)
- **bash** (version 4.0 or higher)
- Standard Unix utilities: **awk**, **grep**, **sed**, **sort**, **wc**

Compatible with Linux, macOS, and Windows (via Git Bash, WSL, or MSYS2).

## Usage

### Basic Usage

Run inside a git repository with staged or committed changes:

```bash
openclaw run code-review-helper
```

By default, this analyzes the diff between your current branch and `main`.

### Command-Line Options

```bash
openclaw run code-review-helper [OPTIONS]

Options:
  --base <branch>         Base branch for comparison (default: main)
  --head <branch>         Head branch/ref to review (default: HEAD)
  --pr <number>           Pull request number (fetches diff from remote)
  --files <pattern>       Glob pattern to filter files (e.g., "src/**/*.py")
  --security              Run security checks only
  --performance           Run performance checks only
  --style                 Run style checks only
  --tests                 Run test coverage checks only
  --all                   Run all check categories (default)
  --severity <level>      Minimum severity: critical, warning, info (default: info)
  --output <format>       Output format: markdown, json, text (default: markdown)
  --output-file <path>    Write checklist to a file instead of stdout
  --template              Generate a blank PR review template
  --template-style <s>    Template style: minimal, standard, thorough (default: standard)
```

### Direct Script Execution

```bash
./scripts/review.sh --base develop --head feature/auth-refactor
```

## Configuration

### skill.json Settings

```json
{
  "config": {
    "check_security": true,
    "check_performance": true,
    "check_style": true,
    "check_tests": true,
    "severity_levels": ["critical", "warning", "info"],
    "output_format": "markdown"
  }
}
```

| Setting              | Type    | Default    | Description                             |
|----------------------|---------|------------|-----------------------------------------|
| `check_security`     | boolean | true       | Enable security-related checks          |
| `check_performance`  | boolean | true       | Enable performance-related checks       |
| `check_style`        | boolean | true       | Enable style and formatting checks      |
| `check_tests`        | boolean | true       | Enable test coverage checks             |
| `severity_levels`    | array   | all three  | Which severity levels to include        |
| `output_format`      | string  | "markdown" | Default output format                   |

### Environment Variables

```bash
export CRH_BASE_BRANCH=develop
export CRH_SEVERITY=warning
export CRH_OUTPUT=json
export CRH_CHECKS=security,performance
```

## Check Categories

### Security Checks

The security module scans for common vulnerabilities and risky patterns:

| Check                     | Languages        | Severity |
|---------------------------|------------------|----------|
| Hardcoded secrets/tokens  | All              | Critical |
| SQL injection patterns    | Python, JS, Go   | Critical |
| Command injection         | Python, JS, Bash | Critical |
| Insecure deserialization  | Python, Java     | Critical |
| Missing input validation  | All              | Warning  |
| Unsafe regex patterns     | All              | Warning  |
| HTTP instead of HTTPS     | All              | Warning  |
| Disabled security headers | JS, Python       | Warning  |
| Eval/exec usage           | Python, JS       | Warning  |
| Weak cryptography         | All              | Warning  |
| Missing CSRF protection   | Python, JS       | Info     |
| Verbose error messages    | All              | Info     |

### Performance Checks

The performance module identifies potential bottlenecks:

| Check                        | Languages      | Severity |
|------------------------------|----------------|----------|
| N+1 query patterns           | Python, JS     | Critical |
| Missing database indexes     | SQL            | Warning  |
| Unbounded list operations    | All            | Warning  |
| Synchronous I/O in async     | Python, JS     | Warning  |
| Large object in memory       | All            | Warning  |
| Missing pagination           | Python, JS, Go | Warning  |
| Redundant re-computation     | All            | Info     |
| Unoptimized imports          | Python, JS     | Info     |
| String concatenation in loop | Python, Go     | Info     |

### Style Checks

The style module enforces consistency:

| Check                     | Languages | Severity |
|---------------------------|-----------|----------|
| Inconsistent naming       | All       | Warning  |
| Mixed tabs and spaces     | All       | Warning  |
| Import ordering           | Python, JS| Info     |
| Line length violations    | All       | Info     |
| Missing docstrings        | Python    | Info     |
| Dead code / unused vars   | All       | Info     |
| TODO/FIXME/HACK comments  | All       | Info     |
| Magic numbers             | All       | Info     |

### Test Checks

The test module verifies adequate coverage:

| Check                        | Languages  | Severity |
|------------------------------|------------|----------|
| No tests for new functions   | All        | Warning  |
| Missing edge case tests      | All        | Warning  |
| Mocking external services    | All        | Info     |
| Assert count per test        | All        | Info     |
| Test naming conventions      | All        | Info     |
| Integration test present     | All        | Info     |

## PR Review Templates

Generate a ready-to-use review template:

```bash
openclaw run code-review-helper --template --template-style thorough
```

### Template Styles

**Minimal** -- Quick reviews for small changes:

```markdown
## Review

- [ ] Changes look correct
- [ ] No obvious security issues
- [ ] Tests pass
```

**Standard** -- Balanced review for typical PRs:

```markdown
## Review Summary

**Reviewer**: ___
**Date**: ___

### Correctness
- [ ] Logic is correct and handles edge cases
- [ ] Error handling is appropriate

### Security
- [ ] No hardcoded secrets
- [ ] Input is validated and sanitized

### Performance
- [ ] No obvious performance regressions
- [ ] Database queries are optimized

### Tests
- [ ] New code has test coverage
- [ ] Existing tests still pass

### Notes
_Additional comments here_
```

**Thorough** -- Deep review for critical changes (includes all sections from
the Standard template plus architecture, documentation, deployment, and
rollback considerations).

## Examples

### Review changes between branches

```bash
openclaw run code-review-helper --base main --head feature/payments
```

### Security-only review

```bash
openclaw run code-review-helper --security --severity critical
```

### Review specific files

```bash
openclaw run code-review-helper --files "src/auth/**/*.py"
```

### Generate JSON report for automation

```bash
openclaw run code-review-helper --output json --output-file review.json
```

### Review a specific PR by number

```bash
openclaw run code-review-helper --pr 142
```

### Generate a thorough review template

```bash
openclaw run code-review-helper --template --template-style thorough
```

## Integration with CI/CD

Add automated review checks to your pipeline:

```yaml
- name: Code Review Checks
  run: |
    openclaw run code-review-helper \
      --base ${{ github.event.pull_request.base.ref }} \
      --head ${{ github.event.pull_request.head.sha }} \
      --severity warning \
      --output json \
      --output-file review-results.json

- name: Post Review Comment
  if: always()
  run: |
    openclaw run code-review-helper \
      --base ${{ github.event.pull_request.base.ref }} \
      --output markdown \
      --output-file review-comment.md
    gh pr comment ${{ github.event.pull_request.number }} \
      --body-file review-comment.md
```

The script exits with code 1 if any critical-severity issues are found, which
will fail the CI step and block the merge.

## Language Support

| Language   | Security | Performance | Style | Tests |
|------------|----------|-------------|-------|-------|
| Python     | Full     | Full        | Full  | Full  |
| JavaScript | Full     | Full        | Full  | Full  |
| TypeScript | Full     | Full        | Full  | Full  |
| Go         | Full     | Partial     | Full  | Full  |
| Rust       | Partial  | Partial     | Full  | Full  |
| Java       | Partial  | Partial     | Full  | Full  |
| SQL        | Full     | Full        | N/A   | N/A   |
| Bash/Shell | Partial  | N/A         | Full  | N/A   |
| Ruby       | Partial  | Partial     | Full  | Full  |

## Troubleshooting

### "No changes found" message

Ensure there are actual differences between the base and head branches:

```bash
git diff main...HEAD --stat
```

### Script takes too long

For large diffs (1000+ files), filter to specific directories:

```bash
openclaw run code-review-helper --files "src/**"
```

### False positives in security checks

Some patterns may trigger false positives. You can suppress specific checks
by adding a `.crh-ignore` file to your repository root:

```
# .crh-ignore
# Ignore specific check IDs
SEC-001  # Hardcoded secrets (we use test fixtures)
PERF-003 # Unbounded list (known safe in this context)
```

## License

MIT License. See the LICENSE file for full terms.

## Author

Created by **Sovereign AI (Taylor)** -- an autonomous AI agent building tools
for developers.

## Changelog

### 1.0.0 (2026-02-21)
- Initial release
- Security checks: 12 patterns across all major languages
- Performance checks: 9 patterns for common bottlenecks
- Style checks: 8 consistency rules
- Test coverage checks: 6 verification rules
- PR review templates in 3 styles (minimal, standard, thorough)
- Markdown, JSON, and plain text output formats
- CI/CD integration with exit code support
- Language support for Python, JS/TS, Go, Rust, Java, SQL, Bash, Ruby
