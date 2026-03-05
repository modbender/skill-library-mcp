#!/usr/bin/env bash
#
# ClawBrain Integration Test Suite
# Tests ClawBrain in a Docker container simulating OpenClaw environment
#
# Usage:
#   ./run_integration_tests.sh          # Run all tests
#   ./run_integration_tests.sh --build  # Force rebuild container
#   ./run_integration_tests.sh --shell  # Open shell in container for debugging
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
IMAGE_NAME="clawbrain-test"
CONTAINER_NAME="clawbrain-test-runner"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

# Parse arguments
FORCE_BUILD=false
OPEN_SHELL=false
while [[ $# -gt 0 ]]; do
    case $1 in
        --build|-b)
            FORCE_BUILD=true
            shift
            ;;
        --shell|-s)
            OPEN_SHELL=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Check Docker is available
if ! command -v docker &> /dev/null; then
    log_error "Docker is not installed or not in PATH"
    exit 1
fi

# Build the test image
build_image() {
    log_info "Building test container..."
    docker build -t "$IMAGE_NAME" -f "$SCRIPT_DIR/Dockerfile.test" "$PROJECT_DIR"
    log_success "Container built successfully"
}

# Check if image exists or force rebuild
if $FORCE_BUILD || ! docker image inspect "$IMAGE_NAME" &> /dev/null; then
    build_image
else
    log_info "Using existing image (use --build to rebuild)"
fi

# Cleanup function
cleanup() {
    log_info "Cleaning up..."
    docker rm -f "$CONTAINER_NAME" 2>/dev/null || true
}
trap cleanup EXIT

# Open shell for debugging
if $OPEN_SHELL; then
    log_info "Opening shell in test container..."
    docker run -it --rm \
        --name "$CONTAINER_NAME" \
        -v "$PROJECT_DIR:/home/openclaw/.openclaw/skills/clawbrain:ro" \
        "$IMAGE_NAME" \
        /bin/bash
    exit 0
fi

echo ""
echo "========================================"
echo "  ClawBrain Integration Test Suite"
echo "========================================"
echo ""

# Run the test container with the integration test script
log_info "Starting test container..."

# Run basic integration tests first
docker run --rm \
    --name "$CONTAINER_NAME" \
    -v "$PROJECT_DIR:/home/openclaw/.openclaw/skills/clawbrain:ro" \
    -e PYTHONPATH="/home/openclaw/.openclaw/skills/clawbrain" \
    "$IMAGE_NAME" \
    python /home/openclaw/.openclaw/skills/clawbrain/tests/integration_test.py

TEST_EXIT_CODE=$?

if [ $TEST_EXIT_CODE -ne 0 ]; then
    log_error "Basic integration tests failed!"
    exit $TEST_EXIT_CODE
fi

echo ""
log_info "Running OpenClaw container integration test..."

# Run OpenClaw-specific integration test
docker run --rm \
    --name "${CONTAINER_NAME}-openclaw" \
    -v "$PROJECT_DIR:/home/openclaw/.openclaw/skills/clawbrain:ro" \
    -e PYTHONPATH="/home/openclaw/.openclaw/skills/clawbrain" \
    "$IMAGE_NAME" \
    python /home/openclaw/.openclaw/skills/clawbrain/tests/test_openclaw_container.py

OPENCLAW_EXIT_CODE=$?

echo ""
if [ $OPENCLAW_EXIT_CODE -eq 0 ]; then
    log_success "All integration tests passed!"
else
    log_error "OpenClaw integration tests failed (exit code: $OPENCLAW_EXIT_CODE)"
fi

exit $OPENCLAW_EXIT_CODE
