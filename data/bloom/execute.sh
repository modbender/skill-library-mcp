#!/usr/bin/env bash

# Bloom Identity OpenClaw Wrapper
#
# Auto-installs bloom-identity-skill on first run
# Uses the last ~120 messages for accurate personality detection

set -e

# Get the directory of this script
WRAPPER_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Determine workspace location
WORKSPACE_DIR="${HOME}/.openclaw/workspace"
BLOOM_SKILL_DIR="${WORKSPACE_DIR}/bloom-identity-skill"

# Auto-install bloom-identity-skill if not present
if [ ! -d "$BLOOM_SKILL_DIR" ] || [ ! -d "$BLOOM_SKILL_DIR/src" ]; then
  echo "📦 First-time setup: Installing Bloom Identity Skill..."
  echo ""

  # Create workspace directory if needed
  mkdir -p "$WORKSPACE_DIR"

  # Clone the repo
  echo "⬇️  Downloading from GitHub..."
  if ! git clone --depth 1 https://github.com/unicornbloom/bloom-identity-skill.git "$BLOOM_SKILL_DIR" 2>/dev/null; then
    echo "❌ Error: Failed to download Bloom Identity Skill"
    echo "   Please check your internet connection and try again"
    exit 1
  fi

  # Install dependencies
  echo "📦 Installing dependencies..."
  cd "$BLOOM_SKILL_DIR"
  if ! npm install --silent 2>/dev/null; then
    echo "⚠️  Warning: npm install had issues, but continuing..."
  fi

  echo "✅ Installation complete!"
  echo ""
fi

# Check for required environment variables
if [ ! -f "$BLOOM_SKILL_DIR/.env" ]; then
  echo "⚙️  Setting up configuration..."

  # Copy .env.example if it exists
  if [ -f "$BLOOM_SKILL_DIR/.env.example" ]; then
    cp "$BLOOM_SKILL_DIR/.env.example" "$BLOOM_SKILL_DIR/.env"
    echo "📝 Created .env file from template"
    echo "   Edit $BLOOM_SKILL_DIR/.env to customize settings"
  else
    # Create minimal .env
    cat > "$BLOOM_SKILL_DIR/.env" << 'EOF'
# Bloom Identity Configuration
JWT_SECRET=default_secret_change_me
DASHBOARD_URL=https://bloomprotocol.ai
BLOOM_API_URL=https://api.bloomprotocol.ai
NETWORK=base-mainnet
EOF
    echo "📝 Created default .env file"
  fi
  echo ""
fi

# Parse arguments
SESSION_FILE=""
USER_ID=""

# Check for --session-file or positional argument
if [ "$1" = "--session-file" ]; then
  SESSION_FILE="$2"
  USER_ID="${3:-$OPENCLAW_USER_ID}"
elif [ -f "$1" ]; then
  SESSION_FILE="$1"
  USER_ID="${2:-$OPENCLAW_USER_ID}"
else
  USER_ID="${1:-$OPENCLAW_USER_ID}"
fi

# If no session file provided, try to find it
if [ -z "$SESSION_FILE" ]; then
  # Try to locate session file from OpenClaw directory
  OPENCLAW_SESSIONS="$HOME/.openclaw/agents/main/sessions"

  if [ -d "$OPENCLAW_SESSIONS" ]; then
    # Find most recent .jsonl file
    SESSION_FILE=$(ls -t "$OPENCLAW_SESSIONS"/*.jsonl 2>/dev/null | head -1)

    if [ -n "$SESSION_FILE" ]; then
      echo "📁 Using session file: $(basename "$SESSION_FILE")"
    fi
  fi
fi

# Validate inputs
if [ -z "$USER_ID" ]; then
  echo "❌ Error: USER_ID required"
  echo ""
  echo "Usage:"
  echo "  /bloom                  # Auto-detects session and user"
  echo "  /bloom <user-id>        # With specific user ID"
  echo ""
  echo "Or set OPENCLAW_USER_ID environment variable"
  exit 1
fi

if [ -z "$SESSION_FILE" ] || [ ! -f "$SESSION_FILE" ]; then
  echo "❌ Error: Session file not found"
  echo ""
  echo "Please ensure you have an active OpenClaw conversation"
  echo "Session files are stored at: ~/.openclaw/agents/main/sessions/"
  exit 1
fi

echo "🌸 Bloom Identity - Analyzing your conversation..."
echo ""

# Run analyzer with session file
cd "$BLOOM_SKILL_DIR"
npx tsx scripts/run-from-session.ts "$SESSION_FILE" "$USER_ID"
