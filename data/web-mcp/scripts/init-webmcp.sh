#!/bin/bash
# init-webmcp.sh - Inizializza WebMCP in un progetto Next.js

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
TARGET_DIR="${1:-.}"
EXAMPLE_TYPE=""

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --example)
      EXAMPLE_TYPE="$2"
      shift 2
      ;;
    --help)
      echo "Usage: init-webmcp.sh [target-dir] [--example <type>]"
      echo ""
      echo "Examples:"
      echo "  init-webmcp.sh                    # Initialize in current directory"
      echo "  init-webmcp.sh ./my-app           # Initialize in ./my-app"
      echo "  init-webmcp.sh --example e-commerce # Create e-commerce example"
      exit 0
      ;;
    *)
      TARGET_DIR="$1"
      shift
      ;;
  esac
done

TARGET_DIR="$(cd "$TARGET_DIR" && pwd)"

echo "🚀 Initializing WebMCP in $TARGET_DIR"

# Check if target is a Next.js project
if [ ! -f "$TARGET_DIR/package.json" ]; then
  echo "❌ No package.json found. Are you in a Next.js project?"
  exit 1
fi

# Create directories
mkdir -p "$TARGET_DIR/lib"
mkdir -p "$TARGET_DIR/hooks"
mkdir -p "$TARGET_DIR/components"
mkdir -p "$TARGET_DIR/types"

# Copy core files
echo "📦 Copying WebMCP core files..."
cp "$SKILL_DIR/templates/nextjs/lib/webmcp.ts" "$TARGET_DIR/lib/webmcp.ts"
cp "$SKILL_DIR/templates/nextjs/hooks/useWebMCP.ts" "$TARGET_DIR/hooks/useWebMCP.ts"
cp "$SKILL_DIR/templates/nextjs/components/WebMCPProvider.tsx" "$TARGET_DIR/components/WebMCPProvider.tsx"

# Copy bridge asset
mkdir -p "$TARGET_DIR/public"
cp "$SKILL_DIR/assets/webmcp-bridge.js" "$TARGET_DIR/public/webmcp-bridge.js"

# Copy example tools if requested
if [ -n "$EXAMPLE_TYPE" ]; then
  echo "📚 Copying $EXAMPLE_TYPE example..."
  if [ -d "$SKILL_DIR/templates/examples/$EXAMPLE_TYPE" ]; then
    cp -r "$SKILL_DIR/templates/examples/$EXAMPLE_TYPE" "$TARGET_DIR/examples/"
  else
    echo "⚠️ Example '$EXAMPLE_TYPE' not found. Available: e-commerce, dashboard, blog"
  fi
fi

# Update package.json if needed
if ! grep -q "webmcp" "$TARGET_DIR/package.json" 2>/dev/null; then
  echo "📝 Adding webmcp scripts to package.json..."
  # This is a simple approach - in production use jq
  echo ""
  echo "Add these scripts to your package.json:"
  echo '  "webmcp:types": "tsc --noEmit lib/webmcp.ts"'
fi

# Create webmcp.config.js if it doesn't exist
if [ ! -f "$TARGET_DIR/webmcp.config.js" ]; then
  cat > "$TARGET_DIR/webmcp.config.js" << 'EOF'
/** @type {import('webmcp').WebMCPConfig} */
module.exports = {
  name: 'My WebMCP App',
  version: '1.0.0',
  tools: {
    // Tool configurations
  },
  bridge: {
    enabled: true,
    scriptPath: '/webmcp-bridge.js'
  }
};
EOF
fi

echo ""
echo "✅ WebMCP initialized successfully!"
echo ""
echo "Next steps:"
echo "  1. Wrap your app with WebMCPProvider in layout.tsx"
echo "  2. Import and use the useWebMCP hook in your components"
echo "  3. Register your first tool with registerTool()"
echo ""
echo "Documentation:"
echo "  - lib/webmcp.ts - Core implementation"
echo "  - hooks/useWebMCP.ts - React hook"
echo "  - components/WebMCPProvider.tsx - Provider component"
