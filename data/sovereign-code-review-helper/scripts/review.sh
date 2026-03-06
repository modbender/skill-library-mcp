#!/usr/bin/env bash
#
# Code Review Helper - review.sh
# Generates code review checklists and PR review templates based on file types.
#
# Usage: ./review.sh [OPTIONS]
#
# Options:
#   --base <branch>         Base branch for comparison (default: main)
#   --head <branch>         Head branch/ref to review (default: HEAD)
#   --files <pattern>       Glob pattern to filter files
#   --security              Run security checks only
#   --performance           Run performance checks only
#   --style                 Run style checks only
#   --tests                 Run test coverage checks only
#   --all                   Run all check categories (default)
#   --severity <level>      Minimum severity: critical, warning, info
#   --output <format>       Output format: markdown, json, text (default: markdown)
#   --output-file <path>    Write checklist to a file
#   --template              Generate a blank PR review template
#   --template-style <s>    Template style: minimal, standard, thorough
#   --help                  Show this help message
#
# Author: Sovereign AI (Taylor)
# License: MIT
# Version: 1.0.0

set -euo pipefail

# ─── Defaults ───────────────────────────────────────────────────────────────

BASE_BRANCH="${CRH_BASE_BRANCH:-main}"
HEAD_REF="HEAD"
FILE_PATTERN=""
CHECK_SECURITY=true
CHECK_PERFORMANCE=true
CHECK_STYLE=true
CHECK_TESTS=true
MIN_SEVERITY="${CRH_SEVERITY:-info}"
OUTPUT_FORMAT="${CRH_OUTPUT:-markdown}"
OUTPUT_FILE=""
GENERATE_TEMPLATE=false
TEMPLATE_STYLE="standard"
RUN_ALL=true

# ─── Argument Parsing ──────────────────────────────────────────────────────

show_help() {
    sed -n '3,/^$/s/^# \?//p' "$0"
    exit 0
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --base)           BASE_BRANCH="$2"; shift 2 ;;
        --head)           HEAD_REF="$2"; shift 2 ;;
        --files)          FILE_PATTERN="$2"; shift 2 ;;
        --security)       RUN_ALL=false; CHECK_SECURITY=true; CHECK_PERFORMANCE=false; CHECK_STYLE=false; CHECK_TESTS=false; shift ;;
        --performance)    RUN_ALL=false; CHECK_SECURITY=false; CHECK_PERFORMANCE=true; CHECK_STYLE=false; CHECK_TESTS=false; shift ;;
        --style)          RUN_ALL=false; CHECK_SECURITY=false; CHECK_PERFORMANCE=false; CHECK_STYLE=true; CHECK_TESTS=false; shift ;;
        --tests)          RUN_ALL=false; CHECK_SECURITY=false; CHECK_PERFORMANCE=false; CHECK_STYLE=false; CHECK_TESTS=true; shift ;;
        --all)            RUN_ALL=true; CHECK_SECURITY=true; CHECK_PERFORMANCE=true; CHECK_STYLE=true; CHECK_TESTS=true; shift ;;
        --severity)       MIN_SEVERITY="$2"; shift 2 ;;
        --output)         OUTPUT_FORMAT="$2"; shift 2 ;;
        --output-file)    OUTPUT_FILE="$2"; shift 2 ;;
        --template)       GENERATE_TEMPLATE=true; shift ;;
        --template-style) TEMPLATE_STYLE="$2"; shift 2 ;;
        --help|-h)        show_help ;;
        *)                echo "Unknown option: $1" >&2; exit 1 ;;
    esac
done

# ─── Severity Helpers ───────────────────────────────────────────────────────

severity_rank() {
    case "$1" in
        critical) echo 3 ;;
        warning)  echo 2 ;;
        info)     echo 1 ;;
        *)        echo 0 ;;
    esac
}

MIN_SEVERITY_RANK=$(severity_rank "$MIN_SEVERITY")

should_include() {
    local rank
    rank=$(severity_rank "$1")
    [[ $rank -ge $MIN_SEVERITY_RANK ]]
}

# ─── Issue Tracking ────────────────────────────────────────────────────────

ISSUES=()
CRITICAL_COUNT=0
WARNING_COUNT=0
INFO_COUNT=0

add_issue() {
    local severity="$1"
    local category="$2"
    local check_id="$3"
    local message="$4"
    local file="${5:-}"
    local line="${6:-}"

    if ! should_include "$severity"; then
        return
    fi

    ISSUES+=("${severity}|${category}|${check_id}|${message}|${file}|${line}")

    case "$severity" in
        critical) CRITICAL_COUNT=$((CRITICAL_COUNT + 1)) ;;
        warning)  WARNING_COUNT=$((WARNING_COUNT + 1)) ;;
        info)     INFO_COUNT=$((INFO_COUNT + 1)) ;;
    esac
}

# ─── Template Generation ───────────────────────────────────────────────────

generate_template() {
    case "$TEMPLATE_STYLE" in
        minimal)
            cat <<'TEMPLATE_MINIMAL'
## Review

- [ ] Changes look correct
- [ ] No obvious security issues
- [ ] Tests pass

**Verdict:** Approve / Request Changes / Comment
TEMPLATE_MINIMAL
            ;;
        standard)
            cat <<'TEMPLATE_STANDARD'
## Review Summary

**Reviewer:** ___
**Date:** ___
**PR:** #___

### Correctness
- [ ] Logic is correct and handles edge cases
- [ ] Error handling is appropriate and consistent
- [ ] No regressions introduced

### Security
- [ ] No hardcoded secrets or credentials
- [ ] Input is validated and sanitized
- [ ] Authentication/authorization is properly enforced
- [ ] No SQL injection or XSS vulnerabilities

### Performance
- [ ] No obvious performance regressions
- [ ] Database queries are optimized
- [ ] No unnecessary network calls or I/O

### Code Quality
- [ ] Code is readable and well-structured
- [ ] Naming is clear and consistent
- [ ] No unnecessary duplication
- [ ] Comments explain "why", not "what"

### Tests
- [ ] New code has adequate test coverage
- [ ] Edge cases are tested
- [ ] Existing tests still pass

### Documentation
- [ ] Public APIs are documented
- [ ] README updated if needed
- [ ] Changelog entry added if needed

### Notes
_Additional comments here_

**Verdict:** Approve / Request Changes / Comment
TEMPLATE_STANDARD
            ;;
        thorough)
            cat <<'TEMPLATE_THOROUGH'
## Review Summary

**Reviewer:** ___
**Date:** ___
**PR:** #___
**Time Spent:** ___ minutes

### Overview
_Brief summary of the changes and their purpose_

### Correctness
- [ ] Logic is correct and handles edge cases
- [ ] Error handling is appropriate and consistent
- [ ] No regressions introduced
- [ ] Concurrency/race conditions considered
- [ ] State management is correct
- [ ] Boundary conditions handled

### Security
- [ ] No hardcoded secrets, tokens, or credentials
- [ ] Input is validated and sanitized at all entry points
- [ ] Authentication and authorization properly enforced
- [ ] No SQL injection, XSS, or CSRF vulnerabilities
- [ ] Sensitive data is encrypted at rest and in transit
- [ ] No information leakage in error messages or logs
- [ ] Dependencies checked for known vulnerabilities
- [ ] CORS and security headers configured properly

### Performance
- [ ] No obvious performance regressions
- [ ] Database queries are optimized (no N+1 queries)
- [ ] Proper indexing on queried fields
- [ ] No unnecessary network calls or blocking I/O
- [ ] Memory usage is reasonable (no leaks)
- [ ] Pagination used for large data sets
- [ ] Caching strategy is appropriate
- [ ] No unbounded loops or recursion

### Architecture
- [ ] Changes align with the existing architecture
- [ ] Separation of concerns maintained
- [ ] Interfaces and abstractions are appropriate
- [ ] No circular dependencies introduced
- [ ] Configuration is externalized properly
- [ ] Feature flags used for incomplete features

### Code Quality
- [ ] Code is readable and well-structured
- [ ] Naming is clear, consistent, and descriptive
- [ ] No unnecessary duplication (DRY)
- [ ] Functions are focused (single responsibility)
- [ ] Comments explain "why", not "what"
- [ ] No dead code or commented-out code
- [ ] Magic numbers replaced with named constants
- [ ] Error messages are helpful and actionable

### Tests
- [ ] New code has adequate test coverage (>80%)
- [ ] Edge cases and error paths are tested
- [ ] Unit tests are isolated (proper mocking)
- [ ] Integration tests cover critical paths
- [ ] Test names clearly describe the scenario
- [ ] Existing tests still pass
- [ ] No flaky tests introduced

### Documentation
- [ ] Public APIs are documented
- [ ] Complex algorithms have explanatory comments
- [ ] README updated if needed
- [ ] API documentation updated if needed
- [ ] Changelog entry added
- [ ] Migration guide provided if breaking changes

### Deployment
- [ ] Database migrations are backwards-compatible
- [ ] Feature can be rolled back safely
- [ ] Environment variables documented
- [ ] Monitoring and alerting updated
- [ ] Load testing considered for high-traffic paths

### Checklist for Author
- [ ] Self-reviewed the code
- [ ] Ran tests locally
- [ ] Updated documentation
- [ ] Addressed all review comments

### Detailed Findings

| # | Severity | File | Line | Finding | Suggestion |
|---|----------|------|------|---------|------------|
| 1 |          |      |      |         |            |

### Notes
_Additional comments, questions, or concerns_

**Verdict:** Approve / Request Changes / Comment
TEMPLATE_THOROUGH
            ;;
        *)
            echo "Unknown template style: $TEMPLATE_STYLE" >&2
            echo "Available styles: minimal, standard, thorough" >&2
            exit 1
            ;;
    esac
}

if [[ "$GENERATE_TEMPLATE" == "true" ]]; then
    output=$(generate_template)
    if [[ -n "$OUTPUT_FILE" ]]; then
        echo "$output" > "$OUTPUT_FILE"
        echo "Template written to $OUTPUT_FILE"
    else
        echo "$output"
    fi
    exit 0
fi

# ─── Validation ─────────────────────────────────────────────────────────────

if ! git rev-parse --is-inside-work-tree &>/dev/null; then
    echo "Error: Not inside a git repository." >&2
    exit 1
fi

# ─── Collect Changed Files ──────────────────────────────────────────────────

CHANGED_FILES=$(git diff --name-only "${BASE_BRANCH}...${HEAD_REF}" 2>/dev/null || \
                git diff --name-only "${BASE_BRANCH}" "${HEAD_REF}" 2>/dev/null || true)

if [[ -n "$FILE_PATTERN" ]]; then
    CHANGED_FILES=$(echo "$CHANGED_FILES" | grep -E "$FILE_PATTERN" 2>/dev/null || true)
fi

if [[ -z "$CHANGED_FILES" ]]; then
    echo "No changed files found between $BASE_BRANCH and $HEAD_REF." >&2
    exit 0
fi

FILE_COUNT=$(echo "$CHANGED_FILES" | wc -l | tr -d ' ')
DIFF_CONTENT=$(git diff "${BASE_BRANCH}...${HEAD_REF}" 2>/dev/null || \
               git diff "${BASE_BRANCH}" "${HEAD_REF}" 2>/dev/null || true)

# ─── Detect File Types ─────────────────────────────────────────────────────

declare -A FILE_TYPES
HAS_PYTHON=false
HAS_JS=false
HAS_TS=false
HAS_GO=false
HAS_RUST=false
HAS_JAVA=false
HAS_SQL=false
HAS_BASH=false
HAS_RUBY=false

while IFS= read -r file; do
    ext="${file##*.}"
    case "$ext" in
        py)    HAS_PYTHON=true; FILE_TYPES["$file"]="python" ;;
        js)    HAS_JS=true; FILE_TYPES["$file"]="javascript" ;;
        jsx)   HAS_JS=true; FILE_TYPES["$file"]="javascript" ;;
        ts)    HAS_TS=true; FILE_TYPES["$file"]="typescript" ;;
        tsx)   HAS_TS=true; FILE_TYPES["$file"]="typescript" ;;
        go)    HAS_GO=true; FILE_TYPES["$file"]="go" ;;
        rs)    HAS_RUST=true; FILE_TYPES["$file"]="rust" ;;
        java)  HAS_JAVA=true; FILE_TYPES["$file"]="java" ;;
        sql)   HAS_SQL=true; FILE_TYPES["$file"]="sql" ;;
        sh)    HAS_BASH=true; FILE_TYPES["$file"]="bash" ;;
        bash)  HAS_BASH=true; FILE_TYPES["$file"]="bash" ;;
        rb)    HAS_RUBY=true; FILE_TYPES["$file"]="ruby" ;;
    esac
done <<< "$CHANGED_FILES"

# ─── Security Checks ───────────────────────────────────────────────────────

run_security_checks() {
    # SEC-001: Hardcoded secrets
    while IFS= read -r file; do
        if grep -nEi '(api[_-]?key|secret|password|token|credential)\s*[=:]\s*["\x27][^"\x27]{8,}' "$file" 2>/dev/null | head -5 | while IFS=: read -r line_num content; do
            add_issue "critical" "security" "SEC-001" "Possible hardcoded secret detected" "$file" "$line_num"
        done; then true; fi
    done <<< "$CHANGED_FILES"

    # SEC-002: SQL injection patterns
    if [[ "$HAS_PYTHON" == "true" ]] || [[ "$HAS_JS" == "true" ]]; then
        while IFS= read -r file; do
            if grep -nE '(execute|query)\s*\(\s*["\x27].*(%s|\$\{|" *\+)' "$file" 2>/dev/null | head -5 | while IFS=: read -r line_num content; do
                add_issue "critical" "security" "SEC-002" "Possible SQL injection via string interpolation" "$file" "$line_num"
            done; then true; fi
        done <<< "$CHANGED_FILES"
    fi

    # SEC-003: eval/exec usage
    while IFS= read -r file; do
        if grep -nE '\b(eval|exec)\s*\(' "$file" 2>/dev/null | head -5 | while IFS=: read -r line_num content; do
            add_issue "warning" "security" "SEC-003" "Use of eval/exec detected" "$file" "$line_num"
        done; then true; fi
    done <<< "$CHANGED_FILES"

    # SEC-004: HTTP URLs (should be HTTPS)
    while IFS= read -r file; do
        if grep -nE 'http://[^l][^o][^c]' "$file" 2>/dev/null | grep -v 'localhost\|127\.0\.0\.1\|0\.0\.0\.0' | head -5 | while IFS=: read -r line_num content; do
            add_issue "warning" "security" "SEC-004" "HTTP URL detected (should use HTTPS)" "$file" "$line_num"
        done; then true; fi
    done <<< "$CHANGED_FILES"

    # SEC-005: Disabled TLS verification
    while IFS= read -r file; do
        if grep -nEi '(verify\s*=\s*False|NODE_TLS_REJECT_UNAUTHORIZED.*0|InsecureSkipVerify.*true)' "$file" 2>/dev/null | head -5 | while IFS=: read -r line_num content; do
            add_issue "critical" "security" "SEC-005" "TLS verification disabled" "$file" "$line_num"
        done; then true; fi
    done <<< "$CHANGED_FILES"

    # SEC-006: Command injection
    if [[ "$HAS_PYTHON" == "true" ]]; then
        while IFS= read -r file; do
            if grep -nE '(os\.system|subprocess.*shell\s*=\s*True|os\.popen)' "$file" 2>/dev/null | head -5 | while IFS=: read -r line_num content; do
                add_issue "critical" "security" "SEC-006" "Possible command injection risk" "$file" "$line_num"
            done; then true; fi
        done <<< "$(echo "$CHANGED_FILES" | grep '\.py$')"
    fi
}

# ─── Performance Checks ────────────────────────────────────────────────────

run_performance_checks() {
    # PERF-001: N+1 query patterns (loop with query inside)
    while IFS= read -r file; do
        if grep -nE 'for .* in .*:' "$file" 2>/dev/null | head -3 | while IFS=: read -r line_num _; do
            # Check if there is a query call within the next 10 lines
            local next_lines
            next_lines=$(tail -n "+$line_num" "$file" 2>/dev/null | head -10)
            if echo "$next_lines" | grep -qEi '(\.query|\.execute|\.find|\.get|fetch)' 2>/dev/null; then
                add_issue "critical" "performance" "PERF-001" "Possible N+1 query pattern detected" "$file" "$line_num"
            fi
        done; then true; fi
    done <<< "$CHANGED_FILES"

    # PERF-002: Missing pagination indicators
    if echo "$DIFF_CONTENT" | grep -qE '\.find\(\)|\.all\(\)|SELECT.*FROM.*[^L]$' 2>/dev/null; then
        add_issue "warning" "performance" "PERF-002" "Query without pagination detected (consider LIMIT/OFFSET)" "" ""
    fi

    # PERF-003: String concatenation in loops
    while IFS= read -r file; do
        local ext="${file##*.}"
        if [[ "$ext" == "py" ]]; then
            if grep -nE 'for .* in .*:' "$file" 2>/dev/null | head -3 | while IFS=: read -r line_num _; do
                local next_lines
                next_lines=$(tail -n "+$line_num" "$file" 2>/dev/null | head -10)
                if echo "$next_lines" | grep -qE '\+=' 2>/dev/null; then
                    add_issue "info" "performance" "PERF-003" "String concatenation in loop (consider join())" "$file" "$line_num"
                fi
            done; then true; fi
        fi
    done <<< "$CHANGED_FILES"

    # PERF-004: Synchronous I/O in async context
    while IFS= read -r file; do
        if grep -nE 'async\s+(def|function)' "$file" 2>/dev/null | head -3 | while IFS=: read -r line_num _; do
            local next_lines
            next_lines=$(tail -n "+$line_num" "$file" 2>/dev/null | head -20)
            if echo "$next_lines" | grep -qE '(open\(|\.read\(\)|\.write\(\)|time\.sleep)' 2>/dev/null; then
                add_issue "warning" "performance" "PERF-004" "Synchronous I/O in async function" "$file" "$line_num"
            fi
        done; then true; fi
    done <<< "$CHANGED_FILES"
}

# ─── Style Checks ──────────────────────────────────────────────────────────

run_style_checks() {
    # STYLE-001: TODO/FIXME/HACK comments
    while IFS= read -r file; do
        if grep -nEi '\b(TODO|FIXME|HACK|XXX|TEMP)\b' "$file" 2>/dev/null | head -5 | while IFS=: read -r line_num content; do
            add_issue "info" "style" "STYLE-001" "TODO/FIXME comment found" "$file" "$line_num"
        done; then true; fi
    done <<< "$CHANGED_FILES"

    # STYLE-002: Long lines (>120 characters)
    while IFS= read -r file; do
        if awk 'length > 120 {print NR": "substr($0,1,80)"..."}' "$file" 2>/dev/null | head -3 | while IFS=: read -r line_num _; do
            add_issue "info" "style" "STYLE-002" "Line exceeds 120 characters" "$file" "$line_num"
        done; then true; fi
    done <<< "$CHANGED_FILES"

    # STYLE-003: Mixed tabs and spaces
    while IFS= read -r file; do
        if grep -nP '^\t+ ' "$file" 2>/dev/null | head -3 | while IFS=: read -r line_num _; do
            add_issue "warning" "style" "STYLE-003" "Mixed tabs and spaces in indentation" "$file" "$line_num"
        done; then true; fi
        if grep -nP '^ +\t' "$file" 2>/dev/null | head -3 | while IFS=: read -r line_num _; do
            add_issue "warning" "style" "STYLE-003" "Mixed tabs and spaces in indentation" "$file" "$line_num"
        done; then true; fi
    done <<< "$CHANGED_FILES"

    # STYLE-004: Trailing whitespace
    while IFS= read -r file; do
        if grep -nE ' +$' "$file" 2>/dev/null | head -3 | while IFS=: read -r line_num _; do
            add_issue "info" "style" "STYLE-004" "Trailing whitespace" "$file" "$line_num"
        done; then true; fi
    done <<< "$CHANGED_FILES"

    # STYLE-005: Missing docstrings (Python)
    if [[ "$HAS_PYTHON" == "true" ]]; then
        while IFS= read -r file; do
            if grep -nE '^\s*(def |class )' "$file" 2>/dev/null | head -5 | while IFS=: read -r line_num _; do
                local next_line
                next_line=$(awk "NR==$((line_num+1))" "$file" 2>/dev/null)
                if ! echo "$next_line" | grep -qE '^\s*("""|\x27\x27\x27)' 2>/dev/null; then
                    add_issue "info" "style" "STYLE-005" "Missing docstring" "$file" "$line_num"
                fi
            done; then true; fi
        done <<< "$(echo "$CHANGED_FILES" | grep '\.py$')"
    fi

    # STYLE-006: Console.log / print left in code
    while IFS= read -r file; do
        if grep -nE '(console\.(log|debug|info)|print\(|fmt\.Print)' "$file" 2>/dev/null | head -5 | while IFS=: read -r line_num content; do
            add_issue "info" "style" "STYLE-006" "Debug output statement found" "$file" "$line_num"
        done; then true; fi
    done <<< "$CHANGED_FILES"
}

# ─── Test Checks ────────────────────────────────────────────────────────────

run_test_checks() {
    # TEST-001: New source files without corresponding test files
    while IFS= read -r file; do
        # Skip test files and non-source files
        if echo "$file" | grep -qEi '(test|spec|__test__|_test\.)' 2>/dev/null; then
            continue
        fi

        local ext="${file##*.}"
        local base="${file%.*}"
        local dir
        dir="$(dirname "$file")"
        local filename
        filename="$(basename "$base")"

        local test_found=false
        case "$ext" in
            py)
                for pattern in "test_${filename}.py" "${filename}_test.py" "tests/test_${filename}.py"; do
                    if [[ -f "$pattern" ]] || echo "$CHANGED_FILES" | grep -q "$pattern" 2>/dev/null; then
                        test_found=true; break
                    fi
                done
                ;;
            js|ts|jsx|tsx)
                for pattern in "${filename}.test.${ext}" "${filename}.spec.${ext}" "__tests__/${filename}.${ext}"; do
                    if [[ -f "${dir}/${pattern}" ]] || echo "$CHANGED_FILES" | grep -q "$pattern" 2>/dev/null; then
                        test_found=true; break
                    fi
                done
                ;;
            go)
                if [[ -f "${base}_test.go" ]] || echo "$CHANGED_FILES" | grep -q "${filename}_test.go" 2>/dev/null; then
                    test_found=true
                fi
                ;;
        esac

        if [[ "$test_found" == "false" ]]; then
            add_issue "warning" "tests" "TEST-001" "No test file found for this source file" "$file" ""
        fi
    done <<< "$CHANGED_FILES"

    # TEST-002: Test files with no assertions
    while IFS= read -r file; do
        if echo "$file" | grep -qEi '(test|spec)' 2>/dev/null; then
            if ! grep -qE '(assert|expect|should|must|require\.)' "$file" 2>/dev/null; then
                add_issue "warning" "tests" "TEST-002" "Test file appears to have no assertions" "$file" ""
            fi
        fi
    done <<< "$CHANGED_FILES"
}

# ─── Run Checks ────────────────────────────────────────────────────────────

if [[ "$RUN_ALL" == "true" ]] || [[ "$CHECK_SECURITY" == "true" ]]; then
    run_security_checks
fi

if [[ "$RUN_ALL" == "true" ]] || [[ "$CHECK_PERFORMANCE" == "true" ]]; then
    run_performance_checks
fi

if [[ "$RUN_ALL" == "true" ]] || [[ "$CHECK_STYLE" == "true" ]]; then
    run_style_checks
fi

if [[ "$RUN_ALL" == "true" ]] || [[ "$CHECK_TESTS" == "true" ]]; then
    run_test_checks
fi

# ─── Report Generation ─────────────────────────────────────────────────────

generate_markdown_output() {
    echo "# Code Review Report"
    echo ""
    echo "**Base:** $BASE_BRANCH"
    echo "**Head:** $HEAD_REF"
    echo "**Files Changed:** $FILE_COUNT"
    echo "**Generated:** $(date -u +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date +%Y-%m-%d)"
    echo ""

    echo "## Summary"
    echo ""
    echo "| Severity | Count |"
    echo "|----------|-------|"
    echo "| Critical | $CRITICAL_COUNT |"
    echo "| Warning  | $WARNING_COUNT |"
    echo "| Info     | $INFO_COUNT |"
    echo "| **Total**| **$((CRITICAL_COUNT + WARNING_COUNT + INFO_COUNT))** |"
    echo ""

    if [[ ${#ISSUES[@]} -eq 0 ]]; then
        echo "No issues found. The code looks good!"
        echo ""
        return
    fi

    echo "## Findings"
    echo ""
    echo "| Severity | Category | ID | Message | File | Line |"
    echo "|----------|----------|----|---------|------|------|"

    for issue in "${ISSUES[@]}"; do
        IFS='|' read -r severity category check_id message file line <<< "$issue"
        local sev_icon
        case "$severity" in
            critical) sev_icon="CRITICAL" ;;
            warning)  sev_icon="WARNING" ;;
            info)     sev_icon="INFO" ;;
        esac
        echo "| $sev_icon | $category | $check_id | $message | $file | $line |"
    done
    echo ""

    # Checklist based on detected file types
    echo "## Review Checklist"
    echo ""

    if [[ "$HAS_PYTHON" == "true" ]]; then
        echo "### Python"
        echo "- [ ] Type hints used for function signatures"
        echo "- [ ] Docstrings present for public functions and classes"
        echo "- [ ] No bare except clauses"
        echo "- [ ] Context managers used for resource handling"
        echo "- [ ] f-strings preferred over % or .format()"
        echo ""
    fi

    if [[ "$HAS_JS" == "true" ]] || [[ "$HAS_TS" == "true" ]]; then
        echo "### JavaScript/TypeScript"
        echo "- [ ] const/let used instead of var"
        echo "- [ ] Async/await used instead of raw promises where appropriate"
        echo "- [ ] Error boundaries in React components (if applicable)"
        echo "- [ ] No unused imports"
        echo "- [ ] Proper null/undefined checking"
        echo ""
    fi

    if [[ "$HAS_GO" == "true" ]]; then
        echo "### Go"
        echo "- [ ] Errors are checked and not discarded"
        echo "- [ ] defer used for cleanup"
        echo "- [ ] Goroutine leaks prevented"
        echo "- [ ] Interfaces kept minimal"
        echo "- [ ] Context propagation correct"
        echo ""
    fi

    if [[ "$HAS_RUST" == "true" ]]; then
        echo "### Rust"
        echo "- [ ] unwrap() not used in production code"
        echo "- [ ] Proper error types with thiserror/anyhow"
        echo "- [ ] No unnecessary clones"
        echo "- [ ] Lifetimes are correct"
        echo "- [ ] unsafe blocks justified and documented"
        echo ""
    fi

    if [[ "$HAS_SQL" == "true" ]]; then
        echo "### SQL"
        echo "- [ ] Parameterized queries used (no string interpolation)"
        echo "- [ ] Migrations are reversible"
        echo "- [ ] Indexes added for foreign keys and frequent queries"
        echo "- [ ] No SELECT * in production queries"
        echo ""
    fi

    if [[ "$HAS_BASH" == "true" ]]; then
        echo "### Bash"
        echo "- [ ] set -euo pipefail at the top"
        echo "- [ ] Variables quoted properly"
        echo "- [ ] Shellcheck passes"
        echo "- [ ] No hardcoded paths"
        echo ""
    fi

    echo "## General Checklist"
    echo ""
    echo "- [ ] Code is readable and self-documenting"
    echo "- [ ] No sensitive data committed (keys, passwords, tokens)"
    echo "- [ ] Error handling is comprehensive"
    echo "- [ ] Logging is appropriate (not too verbose, not too sparse)"
    echo "- [ ] Breaking changes are documented"
    echo ""
}

generate_json_output() {
    echo "{"
    echo "  \"base\": \"$BASE_BRANCH\","
    echo "  \"head\": \"$HEAD_REF\","
    echo "  \"files_changed\": $FILE_COUNT,"
    echo "  \"summary\": {"
    echo "    \"critical\": $CRITICAL_COUNT,"
    echo "    \"warning\": $WARNING_COUNT,"
    echo "    \"info\": $INFO_COUNT,"
    echo "    \"total\": $((CRITICAL_COUNT + WARNING_COUNT + INFO_COUNT))"
    echo "  },"
    echo "  \"issues\": ["

    local first=true
    for issue in "${ISSUES[@]}"; do
        IFS='|' read -r severity category check_id message file line <<< "$issue"
        if [[ "$first" == "true" ]]; then first=false; else echo ","; fi
        printf '    {"severity": "%s", "category": "%s", "id": "%s", "message": "%s", "file": "%s", "line": "%s"}' \
            "$severity" "$category" "$check_id" "$message" "$file" "$line"
    done

    echo ""
    echo "  ],"
    echo "  \"generated\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date +%Y-%m-%d)\""
    echo "}"
}

generate_text_output() {
    echo "============================================"
    echo "  CODE REVIEW REPORT"
    echo "============================================"
    echo ""
    echo "Base:          $BASE_BRANCH"
    echo "Head:          $HEAD_REF"
    echo "Files Changed: $FILE_COUNT"
    echo ""
    echo "Summary:"
    echo "  Critical: $CRITICAL_COUNT"
    echo "  Warning:  $WARNING_COUNT"
    echo "  Info:     $INFO_COUNT"
    echo "  Total:    $((CRITICAL_COUNT + WARNING_COUNT + INFO_COUNT))"
    echo ""

    if [[ ${#ISSUES[@]} -eq 0 ]]; then
        echo "No issues found."
        return
    fi

    echo "Findings:"
    echo ""
    for issue in "${ISSUES[@]}"; do
        IFS='|' read -r severity category check_id message file line <<< "$issue"
        printf "[%-8s] %-8s %-10s %s" "$severity" "$category" "$check_id" "$message"
        if [[ -n "$file" ]]; then
            printf " (%s" "$file"
            if [[ -n "$line" ]]; then printf ":%s" "$line"; fi
            printf ")"
        fi
        echo ""
    done
}

# ─── Output ─────────────────────────────────────────────────────────────────

output=""
case "$OUTPUT_FORMAT" in
    markdown|md)  output=$(generate_markdown_output) ;;
    json)         output=$(generate_json_output) ;;
    text|txt)     output=$(generate_text_output) ;;
    *)
        echo "Error: Unknown output format '$OUTPUT_FORMAT'." >&2
        exit 1
        ;;
esac

if [[ -n "$OUTPUT_FILE" ]]; then
    echo "$output" > "$OUTPUT_FILE"
    echo "Report written to $OUTPUT_FILE"
else
    echo "$output"
fi

# Exit with failure if any critical issues found
if [[ $CRITICAL_COUNT -gt 0 ]]; then
    exit 1
fi
