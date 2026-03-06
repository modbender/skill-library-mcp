#!/bin/bash
#
# Webhook Router Test Suite
# Tests the webhook routing system with mock payloads
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROUTER="${SCRIPT_DIR}/router.sh"
LOG_FILE="/Users/gregborden/.openclaw/workspace/memory/webhooks.jsonl"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
TESTS_PASSED=0
TESTS_FAILED=0

# Helper functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_section() {
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    echo "  $1"
    echo "═══════════════════════════════════════════════════════════════"
}

run_test() {
    local test_name="$1"
    local payload="$2"
    local source="$3"
    local event="$4"
    local expected_handler="$5"
    
    echo ""
    echo "Testing: $test_name"
    echo "─────────────────────────────────────────────────────────────"
    
    # Run router
    RESULT=$(echo "$payload" | "$ROUTER" --source "$source" --event "$event" 2>&1) || true
    
    # Check result
    if echo "$RESULT" | grep -q "\"status\": \"success\""; then
        HANDLER=$(echo "$RESULT" | jq -r '.handler // "unknown"' 2>/dev/null || echo "unknown")
        if [[ "$HANDLER" == *"$expected_handler"* ]]; then
            log_info "✓ PASSED - Routed to correct handler: $HANDLER"
            ((TESTS_PASSED++))
            return 0
        else
            log_error "✗ FAILED - Wrong handler: $HANDLER (expected: $expected_handler)"
            ((TESTS_FAILED++))
            return 1
        fi
    else
        log_error "✗ FAILED - Router returned error"
        echo "$RESULT"
        ((TESTS_FAILED++))
        return 1
    fi
}

# Check dependencies
log_section "Pre-flight Checks"

if [[ ! -x "$ROUTER" ]]; then
    log_error "Router script not found or not executable: $ROUTER"
    exit 1
fi

if ! command -v jq &> /dev/null; then
    log_error "jq is required but not installed"
    exit 1
fi

log_info "Dependencies OK"
log_info "Router: $ROUTER"
log_info "Log file: $LOG_FILE"

# Test 1: GitHub Push Event
log_section "Test 1: GitHub Push Event"

GITHUB_PUSH_PAYLOAD=$(jq -n \
    --arg repo "test-user/demo-repo" \
    --arg branch "main" \
    --arg pusher "testuser" \
    '{
        ref: "refs/heads/\($branch)",
        repository: {
            full_name: $repo,
            name: "demo-repo",
            html_url: "https://github.com/\($repo)"
        },
        pusher: {
            name: $pusher,
            email: "test@example.com"
        },
        sender: {
            login: $pusher,
            html_url: "https://github.com/\($pusher)"
        },
        commits: [
            {
                id: "abc123",
                message: "Update README.md",
                author: { name: $pusher }
            },
            {
                id: "def456",
                message: "Fix bug in auth",
                author: { name: $pusher }
            }
        ]
    }')

run_test "GitHub Push" "$GITHUB_PUSH_PAYLOAD" "github-test-repo" "push" "github.sh"

# Test 2: GitHub Pull Request Event
log_section "Test 2: GitHub Pull Request Opened"

GITHUB_PR_PAYLOAD=$(jq -n \
    --arg repo "test-user/demo-repo" \
    --arg user "contributor" \
    '{
        action: "opened",
        number: 42,
        pull_request: {
            title: "Add new feature",
            html_url: "https://github.com/test-user/demo-repo/pull/42",
            state: "open",
            merged: false,
            user: {
                login: $user
            },
            base: {
                ref: "main"
            },
            head: {
                ref: "feature-branch"
            }
        },
        repository: {
            full_name: $repo,
            name: "demo-repo",
            html_url: "https://github.com/\($repo)"
        },
        sender: {
            login: $user,
            html_url: "https://github.com/\($user)"
        }
    }')

run_test "GitHub PR Opened" "$GITHUB_PR_PAYLOAD" "github-test-repo" "pull_request" "github.sh"

# Test 3: GitHub PR Merged
log_section "Test 3: GitHub Pull Request Merged"

GITHUB_PR_MERGED_PAYLOAD=$(jq -n \
    --arg repo "test-user/demo-repo" \
    --arg user "maintainer" \
    '{
        action: "closed",
        number: 42,
        pull_request: {
            title: "Critical bug fix",
            html_url: "https://github.com/test-user/demo-repo/pull/42",
            state: "closed",
            merged: true,
            user: {
                login: "contributor"
            },
            merged_by: {
                login: $user
            },
            base: {
                ref: "main"
            },
            head: {
                ref: "hotfix-branch"
            }
        },
        repository: {
            full_name: $repo,
            name: "demo-repo"
        },
        sender: {
            login: $user
        }
    }')

run_test "GitHub PR Merged" "$GITHUB_PR_MERGED_PAYLOAD" "github-test-repo" "pull_request" "github.sh"

# Test 4: GitHub Issue Assigned
log_section "Test 4: GitHub Issue Assigned"

GITHUB_ISSUE_PAYLOAD=$(jq -n \
    --arg repo "test-user/demo-repo" \
    --arg user "developer" \
    '{
        action: "assigned",
        issue: {
            number: 123,
            title: "Fix authentication bug",
            html_url: "https://github.com/test-user/demo-repo/issues/123",
            state: "open",
            user: {
                login: "reporter"
            },
            assignees: [
                { login: $user }
            ],
            labels: [
                { name: "bug" },
                { name: "high-priority" }
            ]
        },
        repository: {
            full_name: $repo,
            name: "demo-repo"
        },
        sender: {
            login: "maintainer"
        },
        assignee: {
            login: $user
        }
    }')

run_test "GitHub Issue Assigned" "$GITHUB_ISSUE_PAYLOAD" "github-test-repo" "issues" "github.sh"

# Test 5: GitHub Release Published
log_section "Test 5: GitHub Release Published"

GITHUB_RELEASE_PAYLOAD=$(jq -n \
    --arg repo "test-user/demo-repo" \
    '{
        action: "published",
        release: {
            tag_name: "v1.0.0",
            name: "Version 1.0.0",
            html_url: "https://github.com/test-user/demo-repo/releases/tag/v1.0.0",
            body: "Initial stable release with all core features",
            prerelease: false
        },
        repository: {
            full_name: $repo,
            name: "demo-repo"
        },
        sender: {
            login: "maintainer"
        }
    }')

run_test "GitHub Release" "$GITHUB_RELEASE_PAYLOAD" "github-test-repo" "release" "github.sh"

# Test 6: Generic/Unknown Source
log_section "Test 6: Generic Unknown Source"

GENERIC_PAYLOAD=$(jq -n \
    --arg service "custom-app" \
    --arg event "data.updated" \
    '{
        service: $service,
        event: $event,
        timestamp: "2026-02-07T20:00:00Z",
        data: {
            id: "12345",
            status: "completed",
            user: "testuser"
        }
    }')

run_test "Generic Webhook" "$GENERIC_PAYLOAD" "unknown-service" "data.updated" "generic.sh"

# Test 7: Generic Webhook with Error Status
log_section "Test 7: Generic Webhook with Error"

ERROR_PAYLOAD=$(jq -n \
    --arg service "monitoring" \
    '{
        service: $service,
        event: "alert.triggered",
        status: "critical",
        error: {
            code: "DB_CONNECTION_FAILED",
            message: "Unable to connect to database"
        },
        timestamp: "2026-02-07T20:00:00Z"
    }')

run_test "Generic Error Webhook" "$ERROR_PAYLOAD" "monitoring-system" "alert.triggered" "generic.sh"

# Test 8: GitHub Ping Event
log_section "Test 8: GitHub Ping (Webhook Test)"

GITHUB_PING_PAYLOAD=$(jq -n \
    --arg repo "test-user/demo-repo" \
    '{
        zen: "Keep it logically awesome.",
        hook_id: 12345678,
        hook: {
            type: "Repository",
            id: 12345678,
            name: "web"
        },
        repository: {
            full_name: $repo,
            name: "demo-repo"
        },
        sender: {
            login: "testuser"
        }
    }')

run_test "GitHub Ping" "$GITHUB_PING_PAYLOAD" "github-test-repo" "ping" "github.sh"

# Test 9: Invalid JSON (should fail gracefully)
log_section "Test 9: Invalid JSON Handling"

echo ""
echo "Testing: Invalid JSON payload"
echo "─────────────────────────────────────────────────────────────"

RESULT=$(echo "{invalid json here" | "$ROUTER" --source "test" --event "test" 2>&1) || true

if echo "$RESULT" | grep -q "Invalid JSON"; then
    log_info "✓ PASSED - Correctly rejected invalid JSON"
    ((TESTS_PASSED++))
else
    log_error "✗ FAILED - Did not handle invalid JSON properly"
    echo "$RESULT"
    ((TESTS_FAILED++))
fi

# Test 10: Source Auto-Detection
log_section "Test 10: Source Auto-Detection"

echo ""
echo "Testing: Auto-detect GitHub from payload structure"
echo "─────────────────────────────────────────────────────────────"

AUTO_PAYLOAD=$(jq -n \
    --arg repo "auto-detect/repo" \
    '{
        repository: {
            full_name: $repo
        },
        sender: {
            login: "testuser"
        },
        action: "test"
    }')

export HTTP_X_GITHUB_EVENT="push"
RESULT=$(echo "$AUTO_PAYLOAD" | "$ROUTER" --event "push" 2>&1) || true
unset HTTP_X_GITHUB_EVENT

if echo "$RESULT" | grep -q "success"; then
    log_info "✓ PASSED - Auto-detection works"
    ((TESTS_PASSED++))
else
    log_error "✗ FAILED - Auto-detection failed"
    echo "$RESULT"
    ((TESTS_FAILED++))
fi

# Summary
log_section "Test Summary"

echo ""
echo "Tests Passed: $TESTS_PASSED"
echo "Tests Failed: $TESTS_FAILED"
echo ""

if [[ $TESTS_FAILED -eq 0 ]]; then
    log_info "🎉 All tests passed!"
    echo ""
    echo "You can view the webhook log at:"
    echo "  tail -10 $LOG_FILE | jq ."
    exit 0
else
    log_error "❌ Some tests failed. Check output above."
    exit 1
fi
