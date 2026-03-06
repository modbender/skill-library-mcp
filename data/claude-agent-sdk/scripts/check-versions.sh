#!/bin/bash

# Check package versions for Claude Agent SDK skill
# Usage: ./scripts/check-versions.sh

set -e

echo "🔍 Checking Claude Agent SDK package versions..."
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if npm is available
if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ npm not found. Please install Node.js.${NC}"
    exit 1
fi

# Function to check package version
check_package() {
    local package=$1
    local current_version=$2

    echo -n "Checking $package... "

    # Get latest version from npm
    latest_version=$(npm view $package version 2>/dev/null)

    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Not found in npm registry${NC}"
        return 1
    fi

    if [ "$current_version" = "$latest_version" ]; then
        echo -e "${GREEN}✅ Up to date ($current_version)${NC}"
    else
        echo -e "${YELLOW}⚠️  Update available: $current_version → $latest_version${NC}"
    fi
}

echo "📦 Dependencies:"
check_package "@anthropic-ai/claude-agent-sdk" "0.1.0"
check_package "zod" "3.23.0"

echo ""
echo "🛠️  Dev Dependencies:"
check_package "@types/node" "20.0.0"
check_package "typescript" "5.3.0"

echo ""
echo "✨ Check complete!"
