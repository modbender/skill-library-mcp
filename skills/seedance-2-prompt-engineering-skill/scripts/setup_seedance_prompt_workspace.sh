#!/usr/bin/env bash
# Seedance 2.0 JiMeng — local workspace scaffold
# Usage:
#   bash scripts/setup_seedance_prompt_workspace.sh [dir]

set -euo pipefail

OUT_DIR="${1:-seedance2-workspace}"
mkdir -p "$OUT_DIR"/{prompts,assets,outputs}

cat > "$OUT_DIR/README.txt" <<'EOF'
Seedance prompt workspace

folders:
- prompts/ : saved prompt drafts
- assets/  : reference media names for @asset mapping
- outputs/ : generated results notes
EOF

echo "Created: $OUT_DIR"
