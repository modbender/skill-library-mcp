#!/bin/bash
# Install ClawMeter as an OpenClaw skill
set -e

SKILL_DIR="${HOME}/.openclaw/skills/clawmeter"
CLAWMETER_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "🔥 Installing ClawMeter skill..."

# Create skill directory
mkdir -p "$SKILL_DIR"

# Copy SKILL.md from source
if [ -f "$CLAWMETER_DIR/SKILL.md" ]; then
  cp "$CLAWMETER_DIR/SKILL.md" "$SKILL_DIR/SKILL.md"
  echo "✅ Copied SKILL.md to $SKILL_DIR"
else
  echo "⚠️  SKILL.md not found in source directory"
  exit 1
fi

# Create symlink to source directory (optional, for easy access)
if [ ! -L "$SKILL_DIR/source" ]; then
  ln -s "$CLAWMETER_DIR" "$SKILL_DIR/source"
  echo "✅ Created symlink: $SKILL_DIR/source -> $CLAWMETER_DIR"
fi

# Check if dependencies are installed
if [ ! -d "$CLAWMETER_DIR/node_modules" ]; then
  echo ""
  echo "⚠️  Dependencies not installed. Running npm install..."
  cd "$CLAWMETER_DIR"
  npm install
fi

# Check if .env exists
if [ ! -f "$CLAWMETER_DIR/.env" ]; then
  echo ""
  echo "⚠️  .env not found. Creating from template..."
  cp "$CLAWMETER_DIR/.env.example" "$CLAWMETER_DIR/.env"
  echo "✅ Created .env (please review and customize)"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ ClawMeter skill installed successfully!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📂 Skill location: $SKILL_DIR"
echo "📂 Source code:    $CLAWMETER_DIR"
echo ""
echo "🚀 Next steps:"
echo ""
echo "  1. Review configuration:"
echo "     nano $CLAWMETER_DIR/.env"
echo ""
echo "  2. Ingest existing logs:"
echo "     cd $CLAWMETER_DIR && npm run ingest"
echo ""
echo "  3. Start the dashboard:"
echo "     cd $CLAWMETER_DIR && npm start"
echo ""
echo "  4. Open in browser:"
echo "     http://localhost:3377"
echo ""
echo "📚 Documentation: $CLAWMETER_DIR/README.md"
echo ""
