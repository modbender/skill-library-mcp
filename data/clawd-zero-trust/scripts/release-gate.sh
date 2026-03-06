#!/bin/bash
set -euo pipefail

SCRIPT_PATH="$(readlink -f "$0")"
SCRIPT_DIR="$(cd "$(dirname "$SCRIPT_PATH")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
SKILL_NAME="$(basename "$SKILL_DIR")"
WORKSPACE_DIR="$(cd "$SKILL_DIR/../.." && pwd)"
DIST_DIR="$WORKSPACE_DIR/skills/dist"
OUT_FILE="$DIST_DIR/${SKILL_NAME}.skill"

info() { echo "[release-gate] $*"; }
fail() { echo "[release-gate][ERROR] $*" >&2; exit 1; }

info "Running quick validate"
python3 "$SCRIPT_DIR/quick_validate.py" "$SKILL_DIR" || fail "quick_validate.py failed"

if ! command -v shellcheck >/dev/null 2>&1; then
  fail "shellcheck is required but not installed. Install with: sudo apt install shellcheck"
fi

info "Running shellcheck"
while IFS= read -r -d '' shf; do
  shellcheck "$shf"
done < <(find "$SCRIPT_DIR" -maxdepth 1 -type f -name "*.sh" -print0)

mkdir -p "$DIST_DIR"
info "Packaging skill"
python3 "$SCRIPT_DIR/package_skill.py" "$SKILL_DIR" "$OUT_FILE" || fail "package_skill.py failed"

info "Running endpoint verification"
bash "$SCRIPT_DIR/egress-filter.sh" --verify || fail "endpoint verification failed"

info "Release gate passed: $OUT_FILE"
