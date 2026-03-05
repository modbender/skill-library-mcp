#!/usr/bin/env bash
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TMP_DIR="$(mktemp -d)"
CLEAN_DIR="$TMP_DIR/tempest-weather"

cleanup() {
  rm -rf "$TMP_DIR"
}
trap cleanup EXIT

mkdir -p "$CLEAN_DIR"

# Copy only clean files into temp folder
rsync -a \
  --exclude '.git/' \
  --exclude '**/.git/' \
  --exclude '__pycache__/' \
  --exclude '**/__pycache__/' \
  --exclude '*.pyc' \
  --exclude '*.pyo' \
  --exclude '*.skill' \
  --exclude '.DS_Store' \
  "$SKILL_DIR/" "$CLEAN_DIR/"

PACKAGE_SKILL_PY="${OPENCLAW_PACKAGE_SKILL_PY:-$HOME/.npm-global/lib/node_modules/openclaw/skills/skill-creator/scripts/package_skill.py}"

if [[ ! -f "$PACKAGE_SKILL_PY" ]]; then
  echo "ERROR: package_skill.py not found at: $PACKAGE_SKILL_PY" >&2
  echo "Set OPENCLAW_PACKAGE_SKILL_PY to your package_skill.py path." >&2
  exit 1
fi

python3 "$PACKAGE_SKILL_PY" "$CLEAN_DIR" "$SKILL_DIR"

echo "Built clean package: $SKILL_DIR/tempest-weather.skill"
