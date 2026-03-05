#!/bin/bash
# batch-review.sh — Fetch skill sources for a batch and output combined review input
# Usage: bash batch-review.sh author1/skill1 author2/skill2 ...
# Output: Combined skill sources to stdout for review agent

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

for SKILL_PATH in "$@"; do
    bash "$SCRIPT_DIR/fetch-skill.sh" "$SKILL_PATH" 2>/dev/null
    echo ""
    echo ""
done
