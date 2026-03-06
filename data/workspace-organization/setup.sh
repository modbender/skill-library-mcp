#!/bin/bash
# Workspace Organization Setup
# Initializes standard OpenClaw workspace structure
# Usage: ./setup.sh [workspace_path]
# Example: ./setup.sh ~/.openclaw/workspace

set -e

# Auto-detect workspace or use provided path
if [ -n "$1" ]; then
    WS="$1"
elif [ -n "$OPENCLAW_WORKSPACE" ]; then
    WS="$OPENCLAW_WORKSPACE"
elif [ -d "${HOME}/.openclaw/workspace" ]; then
    WS="${HOME}/.openclaw/workspace"
else
    echo "Error: Could not detect workspace. Usage: ./setup.sh [workspace_path]"
    exit 1
fi

echo "Setting up OpenClaw workspace structure at: $WS"
echo ""

# Create standard directories
mkdir -p "$WS/projects/writing"
mkdir -p "$WS/projects/code"
mkdir -p "$WS/notes/daily-reviews"
mkdir -p "$WS/notes/decisions"
mkdir -p "$WS/memory/owner"
mkdir -p "$WS/memory/sessions"
mkdir -p "$WS/skills"
mkdir -p "$WS/subagents/_archived"
mkdir -p "$WS/docs"
mkdir -p "$WS/scripts"

# Create placeholder files
cat > "$WS/notes/cost-tracking.md" << 'EOF'
# Cost Tracking Log

## Multipliers
- Creative: 7.5x
- Research: 3x
- Technical: 2x
- Simple: 1.5x

| Date | Task | Model | Est. | Actual | Ratio | Notes |
|------|------|-------|------|--------|-------|-------|
EOF

cat > "$WS/notes/README.md" << 'EOF'
# Notes Directory

Organized notes and tracking files.

- `daily-reviews/` — Daily review logs
- `decisions/` — Important decisions made
- `cost-tracking.md` — Subagent cost tracking
EOF

cat > "$WS/docs/README.md" << 'EOF'
# Documentation

Project documentation, guides, and references.
EOF

cat > "$WS/scripts/README.md" << 'EOF'
# Scripts

Utility scripts for workspace maintenance and automation.
EOF

echo "✓ Directory structure created"
echo "✓ Placeholder files added"
echo ""
echo "Workspace structure:"
echo "  projects/     - Active work (writing, code)"
echo "  notes/        - Organized notes and tracking"
echo "  memory/       - Long-term memory storage"
echo "  skills/       - Custom skills"
echo "  subagents/    - Permanent specialists"
echo "  docs/         - Documentation"
echo "  scripts/      - Utility scripts"
echo ""
echo "Run ./maintenance-audit.sh for health check."
