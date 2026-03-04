#!/bin/bash
# Install ACC (Anterior Cingulate Memory) skill
#
# Usage:
#   ./install.sh              # Basic install
#   ./install.sh --with-cron  # Install + set up cron jobs

set -e

WORKSPACE="${WORKSPACE:-$HOME/.openclaw/workspace}"
SKILL_DIR="$(cd "$(dirname "$0")" && pwd)"
STATE_FILE="$WORKSPACE/memory/acc-state.json"
WATERMARK_FILE="$WORKSPACE/memory/acc-watcher-watermark.json"
STATE_MD="$WORKSPACE/ACC_STATE.md"

WITH_CRON=false
while [[ $# -gt 0 ]]; do
    case $1 in
        --with-cron) WITH_CRON=true; shift ;;
        *) shift ;;
    esac
done

echo "⚡ Installing ACC (Anterior Cingulate Memory)"
echo "============================================="
echo ""

# Create memory directory
mkdir -p "$WORKSPACE/memory"

# Initialize state file if not exists
if [ ! -f "$STATE_FILE" ]; then
    echo "Creating acc-state.json..."
    cat > "$STATE_FILE" << 'EOF'
{
  "version": "2.0",
  "lastUpdated": null,
  "activePatterns": {},
  "resolved": {},
  "stats": {
    "totalErrorsLogged": 0,
    "totalScreened": 0,
    "totalAnalyzed": 0
  }
}
EOF
fi

# Initialize watermark if not exists
if [ ! -f "$WATERMARK_FILE" ]; then
    echo "Creating watermark file..."
    cat > "$WATERMARK_FILE" << EOF
{
  "session": null,
  "line": 0,
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
}
EOF
fi

# Generate initial state markdown
echo "Generating ACC_STATE.md..."
"$SKILL_DIR/scripts/sync-state.sh" 2>/dev/null || true

# Make scripts executable
chmod +x "$SKILL_DIR/scripts/"*.sh 2>/dev/null || true

echo ""
echo "✅ ACC installed!"
echo ""
echo "Files created:"
echo "  - $STATE_FILE"
echo "  - $WATERMARK_FILE"
echo "  - $STATE_MD"
echo ""

if [ "$WITH_CRON" = true ]; then
    echo "Setting up cron jobs..."
    echo ""
    echo "Add this cron job (runs 3x daily at 4 AM, 12 PM, 8 PM):"
    echo ""
    echo "  openclaw cron add --name acc-analysis \\"
    echo "    --cron '0 4,12,20 * * *' \\"
    echo "    --session isolated \\"
    echo "    --agent-turn 'Run ACC error analysis: encode-pipeline.sh, analyze exchanges, log errors, update watermark'"
    echo ""
fi

echo "┌─────────────────────────────────────────────┐"
echo "│  Load at session start:                     │"
echo "│  $SKILL_DIR/scripts/load-state.sh           │"
echo "└─────────────────────────────────────────────┘"
