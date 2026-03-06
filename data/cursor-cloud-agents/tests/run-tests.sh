#!/usr/bin/env bash
#
# Test runner for cursor-api.sh
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Options
RUN_INTEGRATION=false
SHOW_COVERAGE=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --integration)
            RUN_INTEGRATION=true
            shift
            ;;
        --coverage)
            SHOW_COVERAGE=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --integration    Run integration tests (requires CURSOR_API_KEY)"
            echo "  --coverage       Show test coverage report"
            echo "  --help           Show this help"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Check dependencies
check_deps() {
    local missing=()
    
    if ! command -v bats >/dev/null 2>&1; then
        missing+=("bats-core")
    fi
    
    if ! command -v jq >/dev/null 2>&1; then
        missing+=("jq")
    fi
    
    if ! command -v shellcheck >/dev/null 2>&1; then
        echo -e "${YELLOW}Warning: shellcheck not installed (skipping lint check)${NC}"
    fi
    
    if [[ ${#missing[@]} -gt 0 ]]; then
        echo -e "${RED}Missing dependencies: ${missing[*]}${NC}"
        echo "Install with:"
        echo "  brew install bats-core jq shellcheck  # macOS"
        echo "  apt-get install bats jq shellcheck    # Debian/Ubuntu"
        exit 1
    fi
}

# Run shellcheck
run_shellcheck() {
    if command -v shellcheck >/dev/null 2>&1; then
        echo "Running shellcheck..."
        if shellcheck "$PROJECT_ROOT/scripts/cursor-api.sh"; then
            echo -e "${GREEN}✓ shellcheck passed${NC}"
        else
            echo -e "${RED}✗ shellcheck failed${NC}"
            exit 1
        fi
        echo ""
    fi
}

# Run unit tests
run_unit_tests() {
    echo "Running unit tests..."
    if bats "$SCRIPT_DIR/test_cursor_api.bats"; then
        echo -e "${GREEN}✓ Unit tests passed${NC}"
    else
        echo -e "${RED}✗ Unit tests failed${NC}"
        exit 1
    fi
    echo ""
}

# Run integration tests
run_integration_tests() {
    if [[ "$RUN_INTEGRATION" == "true" ]]; then
        echo "Running integration tests..."
        if bats "$SCRIPT_DIR/integration.bats"; then
            echo -e "${GREEN}✓ Integration tests passed${NC}"
        else
            echo -e "${RED}✗ Integration tests failed${NC}"
            exit 1
        fi
        echo ""
    else
        echo -e "${YELLOW}Skipping integration tests (use --integration to run)${NC}"
        echo ""
    fi
}

# Calculate coverage
calculate_coverage() {
    if [[ "$SHOW_COVERAGE" == "true" ]]; then
        echo "Test coverage:"
        echo "=============="
        
        # Count test cases
        local total_tests
        total_tests=$(grep -c "^@test" "$SCRIPT_DIR"/*.bats 2>/dev/null || echo 0)
        
        # List functions in script
        local functions
        functions=$(grep "^cmd_" "$PROJECT_ROOT/scripts/cursor-api.sh" | sed 's/cmd_\([a-z_]*\).*/\1/' | sort -u)
        
        echo ""
        echo "Functions tested:"
        for func in $functions; do
            # Check if function has a corresponding test
            if grep -q "test.*$func" "$SCRIPT_DIR"/*.bats 2>/dev/null; then
                echo -e "  ${GREEN}✓${NC} $func"
            else
                echo -e "  ${RED}✗${NC} $func (no test)"
            fi
        done
        
        echo ""
        echo "Total test cases: $total_tests"
        echo ""
    fi
}

# Main
main() {
    echo "Cursor API Test Runner"
    echo "======================"
    echo ""
    
    check_deps
    run_shellcheck
    run_unit_tests
    run_integration_tests
    calculate_coverage
    
    echo -e "${GREEN}All tests passed!${NC}"
}

main "$@"
