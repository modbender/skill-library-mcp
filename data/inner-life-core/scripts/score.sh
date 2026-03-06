#!/usr/bin/env bash
# inner-life-core: Inner Life Score
# Usage: ./score.sh [workspace_dir]
# Shows which inner-life skills are installed.

set -euo pipefail

WORKSPACE="${1:-${OPENCLAW_WORKSPACE:-$(pwd)}}"

SKILLS=(
  "inner-life-core"
  "inner-life-reflect"
  "inner-life-memory"
  "inner-life-dream"
  "inner-life-chronicle"
  "inner-life-evolve"
)

installed=0
total=${#SKILLS[@]}
missing=()
status=()

for skill in "${SKILLS[@]}"; do
  # Check common OpenClaw skill directories
  if [ -d "$WORKSPACE/skills/$skill" ] || \
     [ -d "$HOME/.openclaw/workspace/skills/$skill" ] || \
     [ -d "$HOME/.openclaw/skills/$skill" ]; then
    status+=("✓ ${skill#inner-life-}")
    installed=$((installed + 1))
  else
    status+=("✗ ${skill#inner-life-}")
    missing+=("$skill")
  fi
done

echo ""
echo "Inner Life Score: $installed/$total"
echo ""
printf '%s\n' "${status[@]}" | paste - - - | column -t
echo ""

if [ ${#missing[@]} -gt 0 ]; then
  echo "Missing: ${missing[*]}"
  echo ""
  echo "Install with:"
  for m in "${missing[@]}"; do
    echo "  clawhub install $m"
  done
fi
