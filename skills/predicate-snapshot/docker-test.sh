#!/bin/bash
# Docker test script for predicate-snapshot skill
# Usage: ./docker-test.sh [skill|openclaw|demo:login|demo|demo:llm]
#
# Options:
#   skill       Test skill MCP tools and browser integration (default)
#   openclaw    Test with OpenClaw's full runtime (CLI commands)
#   demo:login  Run the login demo directly
#   demo        Run basic comparison demo
#   demo:llm    Run LLM action demo

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Predicate Snapshot Skill - Docker Test${NC}"
echo -e "${GREEN}========================================${NC}"
echo
echo -e "Test site: ${YELLOW}https://www.localllamaland.com/login${NC}"
echo -e "This is a fake login site with intentional challenges:"
echo -e "  - Delayed hydration (~600ms)"
echo -e "  - Button disabled until form filled"
echo -e "  - Late-loading profile content"
echo

# Check for environment variables
if [ -z "$PREDICATE_API_KEY" ]; then
    echo -e "${YELLOW}Note: PREDICATE_API_KEY not set. Using local heuristic mode.${NC}"
fi

# Check for LLM API keys (need at least one for the login demo)
if [ -z "$OPENAI_API_KEY" ] && [ -z "$ANTHROPIC_API_KEY" ]; then
    echo -e "${YELLOW}Note: No LLM API key set (OPENAI_API_KEY or ANTHROPIC_API_KEY).${NC}"
    echo -e "${YELLOW}      The login demo requires an LLM to select elements.${NC}"
fi

# Create output directory
mkdir -p test-output

# Default test to run
TEST_MODE="${1:-skill}"

echo
echo -e "${CYAN}Building Docker image...${NC}"
docker build -t predicate-snapshot-test .

echo
case "$TEST_MODE" in
    skill)
        echo -e "${GREEN}Running: Skill MCP tools test${NC}"
        echo -e "${CYAN}This tests the skill's MCP tools and browser integration.${NC}"
        echo
        # Use -t only if TTY is available
        TTY_FLAG=""
        if [ -t 0 ]; then TTY_FLAG="-t"; fi
        # PredicateBrowser uses headless: false + --headless=new for extension support
        # This works without xvfb
        docker run --rm $TTY_FLAG \
            -e PREDICATE_API_KEY="${PREDICATE_API_KEY:-}" \
            -e OPENAI_API_KEY="${OPENAI_API_KEY:-}" \
            -e ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY:-}" \
            -v "$(pwd)/test-output:/app/test-output" \
            predicate-snapshot-test \
            npx ts-node test-skill.ts
        ;;
    openclaw)
        echo -e "${GREEN}Running: OpenClaw full runtime integration test${NC}"
        echo -e "${CYAN}This tests the skill through OpenClaw's CLI commands.${NC}"
        echo
        TTY_FLAG=""
        if [ -t 0 ]; then TTY_FLAG="-t"; fi
        docker run --rm $TTY_FLAG \
            -e PREDICATE_API_KEY="${PREDICATE_API_KEY:-}" \
            -e OPENAI_API_KEY="${OPENAI_API_KEY:-}" \
            -e ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY:-}" \
            -v "$(pwd)/test-output:/app/test-output" \
            predicate-snapshot-test \
            bash /app/test-openclaw-integration.sh
        ;;
    demo:login|demo|demo:llm)
        echo -e "${GREEN}Running: npm run ${TEST_MODE}${NC}"
        echo -e "${CYAN}This runs the demo script directly (SDK-level test).${NC}"
        echo
        TTY_FLAG=""
        if [ -t 0 ]; then TTY_FLAG="-t"; fi
        docker run --rm $TTY_FLAG \
            -e PREDICATE_API_KEY="${PREDICATE_API_KEY:-}" \
            -e OPENAI_API_KEY="${OPENAI_API_KEY:-}" \
            -e ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY:-}" \
            -e HEADLESS=true \
            -v "$(pwd)/test-output:/app/test-output" \
            predicate-snapshot-test \
            npm run "$TEST_MODE"
        ;;
    *)
        echo -e "${RED}Unknown test mode: ${TEST_MODE}${NC}"
        echo "Usage: ./docker-test.sh [skill|openclaw|demo:login|demo|demo:llm]"
        exit 1
        ;;
esac

echo
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Test complete!${NC}"
echo -e "${GREEN}========================================${NC}"

# Check for trace files
if [ -d "test-output" ] && [ "$(ls -A test-output 2>/dev/null)" ]; then
    echo -e "${GREEN}Trace files saved to: ./test-output/${NC}"
    ls -la test-output/
fi
