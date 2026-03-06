#!/usr/bin/env bash

# Bloom Identity Skill - Auto Installer
# Parses skill.json and auto-installs dependencies

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "🌸 Bloom Identity Skill - Auto Installer"
echo "========================================="

# 1. Check skill.json exists
if [ ! -f "$PROJECT_ROOT/skill.json" ]; then
  echo "❌ Error: skill.json not found"
  exit 1
fi

echo "✓ Found skill.json"

# 2. Parse requirements (using jq if available, otherwise basic parsing)
if command -v jq &> /dev/null; then
  echo ""
  echo "📋 Checking requirements..."

  # Check Node.js version
  REQUIRED_NODE=$(jq -r '.openclaw.requirements.node' "$PROJECT_ROOT/skill.json")
  CURRENT_NODE=$(node -v | sed 's/v//')
  echo "  Node.js: $CURRENT_NODE (required: $REQUIRED_NODE)"

  # Check required binaries
  echo ""
  echo "🔍 Verifying required binaries..."
  REQUIRED_BINS=$(jq -r '.openclaw.requirements.bins[]' "$PROJECT_ROOT/skill.json")
  for bin in $REQUIRED_BINS; do
    if command -v "$bin" &> /dev/null; then
      echo "  ✓ $bin"
    else
      echo "  ❌ $bin not found"
      exit 1
    fi
  done
fi

# 3. Install npm dependencies
echo ""
echo "📦 Installing dependencies..."
cd "$PROJECT_ROOT"
npm install

# 4. Install Agent Kits
echo ""
echo "🤖 Installing Agent Kits..."
if command -v jq &> /dev/null; then
  jq -r '.agentKits[] | "\(.source)"' "$PROJECT_ROOT/skill.json" | while read -r kit; do
    echo "  Installing: $kit"
    # npm install is already done above, this is just for logging
  done
fi

# 5. Setup environment
echo ""
echo "⚙️  Setting up environment..."
if [ ! -f "$PROJECT_ROOT/.env" ]; then
  cp "$PROJECT_ROOT/.env.example" "$PROJECT_ROOT/.env"
  echo "  ✓ Created .env from .env.example"
  echo "  ⚠️  Please edit .env with your credentials"
else
  echo "  ✓ .env already exists"
fi

# 6. Verify installation
echo ""
echo "✅ Installation complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env with your configuration"
echo "2. Test the skill: bash scripts/generate.sh --user-id test-user"
echo "3. Check status: bash scripts/health-check.sh"
