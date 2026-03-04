#!/usr/bin/env bash
#
# ClawBrain Local Test Runner
# Runs tests without Docker - requires Python and dependencies installed locally
#
# Usage:
#   ./run_local_tests.sh
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

echo ""
echo "========================================"
echo "  ClawBrain Local Test Suite"
echo "========================================"
echo ""

cd "$PROJECT_DIR"

# Check Python
if ! command -v python3 &> /dev/null; then
    log_error "Python 3 is required"
    exit 1
fi

log_info "Python: $(python3 --version)"

# Check if clawbrain is importable
log_info "Checking ClawBrain import..."
if python3 -c "import clawbrain" 2>/dev/null; then
    log_success "ClawBrain is installed"
else
    log_warning "ClawBrain not installed globally, using local path"
    export PYTHONPATH="$PROJECT_DIR:$PYTHONPATH"
fi

# Check cryptography
log_info "Checking cryptography library..."
if python3 -c "from cryptography.fernet import Fernet" 2>/dev/null; then
    log_success "cryptography is available"
else
    log_warning "cryptography not installed - encryption tests will fail"
    log_info "Install with: pip install cryptography"
fi

# Create temp directory for test data
export CLAWBRAIN_TEST_DIR=$(mktemp -d)
log_info "Test data directory: $CLAWBRAIN_TEST_DIR"

# Cleanup function
cleanup() {
    log_info "Cleaning up test data..."
    rm -rf "$CLAWBRAIN_TEST_DIR"
}
trap cleanup EXIT

# Run integration tests
echo ""
log_info "Running integration tests..."
python3 "$SCRIPT_DIR/integration_test.py"
TEST_EXIT_CODE=$?

echo ""
if [ $TEST_EXIT_CODE -eq 0 ]; then
    log_success "All tests passed!"
else
    log_error "Some tests failed (exit code: $TEST_EXIT_CODE)"
fi

exit $TEST_EXIT_CODE
