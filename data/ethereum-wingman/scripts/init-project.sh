#!/bin/bash
set -e

# Ethereum Wingman: Initialize Scaffold-ETH 2 Project
# Usage: bash init-project.sh [project-name] [chain]

PROJECT_NAME="${1:-my-dapp}"
CHAIN="${2:-base}"

echo "🏗️  Ethereum Wingman: Initializing Scaffold-ETH 2 Project" >&2
echo "   Project: $PROJECT_NAME" >&2
echo "   Target Chain: $CHAIN" >&2
echo "" >&2

# Check if npx is available
if ! command -v npx &> /dev/null; then
    echo "❌ Error: npx not found. Please install Node.js 18+" >&2
    exit 1
fi

# Check if directory already exists
if [ -d "$PROJECT_NAME" ]; then
    echo "❌ Error: Directory '$PROJECT_NAME' already exists" >&2
    exit 1
fi

# Create Scaffold-ETH 2 project
echo "📦 Creating Scaffold-ETH 2 project..." >&2
npx create-eth@latest --project "$PROJECT_NAME" --skip-install

cd "$PROJECT_NAME"

echo "" >&2
echo "✅ Project created successfully!" >&2
echo "" >&2
echo "📋 Next steps:" >&2
echo "   1. cd $PROJECT_NAME" >&2
echo "   2. yarn install" >&2
echo "   3. yarn chain        # Terminal 1: Start local blockchain" >&2
echo "   4. yarn deploy       # Terminal 2: Deploy contracts" >&2
echo "   5. yarn start        # Terminal 3: Start frontend" >&2
echo "" >&2
echo "🔀 To fork $CHAIN:" >&2
echo "   yarn fork --network $CHAIN" >&2
echo "" >&2
echo "📚 Remember the critical gotchas:" >&2
echo "   • USDC has 6 decimals, not 18!" >&2
echo "   • Always use the approve pattern for ERC-20" >&2
echo "   • Use Chainlink oracles, never DEX spot prices" >&2
echo "   • Design incentives: Who calls your function? Why?" >&2

# Output JSON for machine parsing
echo "{\"status\": \"success\", \"project\": \"$PROJECT_NAME\", \"chain\": \"$CHAIN\", \"path\": \"$(pwd)\"}"
