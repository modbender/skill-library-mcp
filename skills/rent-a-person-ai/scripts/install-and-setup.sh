#!/usr/bin/env sh
#
# Install RentAPerson skill via ClawHub, then run setup.js in one go.
# Usage:
#   ./install-and-setup.sh [WORKDIR]
#   CLAWHUB_WORKDIR=/path ./install-and-setup.sh
#
# Default WORKDIR: $CLAWHUB_WORKDIR or $HOME/.openclaw/workspace-observer-aligned
# Example:
#   ./install-and-setup.sh ~/.openclaw/workspace-observer-aligned
#
set -e

WORKDIR="${1:-${CLAWHUB_WORKDIR:-$HOME/.openclaw/workspace-observer-aligned}}"
SKILL_NAME="rent-a-person-ai"
SETUP_PATH="$WORKDIR/skills/$SKILL_NAME/scripts/setup.js"

echo "Workdir: $WORKDIR"
echo "Installing $SKILL_NAME via ClawHub..."
npx clawhub install "$SKILL_NAME" --force --workdir "$WORKDIR"

if [ ! -f "$SETUP_PATH" ]; then
  echo "Error: setup.js not found at $SETUP_PATH"
  exit 1
fi

echo ""
echo "Running setup..."
node "$SETUP_PATH"
