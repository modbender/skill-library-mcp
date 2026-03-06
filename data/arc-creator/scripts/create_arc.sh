#!/bin/bash
# Create ARC directory structure
# Usage: create_arc.sh <path> <investigation_id>

set -euo pipefail

ARC_PATH="${1:?Usage: create_arc.sh <path> <investigation_id>}"
INV_ID="${2:?Usage: create_arc.sh <path> <investigation_id>}"

mkdir -p "$ARC_PATH"
cd "$ARC_PATH"

# Check if arc commander is available
if command -v arc &>/dev/null || [ -x "$HOME/bin/arc" ]; then
    ARC_CMD="${HOME}/bin/arc"
    [ -x "$ARC_CMD" ] || ARC_CMD="arc"
    $ARC_CMD init
    echo "ARC initialized with arc commander at $ARC_PATH"
else
    # Manual init
    git init
    mkdir -p .arc studies assays workflows runs
    touch .arc/.gitkeep studies/.gitkeep assays/.gitkeep workflows/.gitkeep runs/.gitkeep
    echo "ARC manually initialized at $ARC_PATH (arc commander not found — isa.investigation.xlsx must be created manually)"
fi

echo "ARC_PATH=$ARC_PATH"
echo "INV_ID=$INV_ID"
