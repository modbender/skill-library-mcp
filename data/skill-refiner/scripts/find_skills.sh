#!/bin/bash
# Find all skill directories in the workspace.
# Searches for SKILL.md files anywhere in the workspace tree.
# Usage: find_skills.sh [workspace_dir]
# Output: one skill directory path per line

WORKSPACE="${1:-$HOME/.openclaw/workspace}"

find "$WORKSPACE" \
  -name "SKILL.md" \
  -not -path "*/node_modules/*" \
  -not -path "*/.git/*" \
  | while read -r skill_md; do
      dirname "$skill_md"
    done \
  | sort -u
