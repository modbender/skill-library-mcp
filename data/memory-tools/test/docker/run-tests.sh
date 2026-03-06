#!/bin/bash
# Run migration tests in Docker
#
# Usage: ./run-tests.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "Building and running migration tests..."
echo ""

cd "$PROJECT_ROOT"

# Build the Docker image
docker build -t memory-tools-test -f test/docker/Dockerfile .

# Run the tests
docker run --rm memory-tools-test

echo ""
echo "Done!"
