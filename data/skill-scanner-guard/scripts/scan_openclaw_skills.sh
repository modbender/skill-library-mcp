#!/usr/bin/env bash
set -euo pipefail

STATE_DIR="${OPENCLAW_STATE_DIR:-$HOME/.openclaw}"
WORKSPACE_DIR="${OPENCLAW_WORKSPACE_DIR:-$STATE_DIR/workspace}"
SCANNER_DIR="$WORKSPACE_DIR/skill-scanner"

if command -v uv >/dev/null 2>&1; then
  UV_BIN="$(command -v uv)"
elif [[ -x "/home/linuxbrew/.linuxbrew/bin/uv" ]]; then
  UV_BIN="/home/linuxbrew/.linuxbrew/bin/uv"
else
  echo "ERROR: uv not found in PATH. Install uv: https://astral.sh/uv" >&2
  exit 2
fi

SCANNER_CMD=("$UV_BIN" run skill-scanner)

OUT_DIR="$WORKSPACE_DIR/skill_scans"
mkdir -p "$OUT_DIR"
TS="$(date +%Y%m%d-%H%M%S)"

if [[ ! -d "$SCANNER_DIR" ]]; then
  echo "ERROR: skill-scanner repo not found at $SCANNER_DIR" >&2
  echo "Clone it first: git clone https://github.com/cisco-ai-defense/skill-scanner $SCANNER_DIR" >&2
  exit 2
fi

cd "$SCANNER_DIR"

USER_SKILLS="$STATE_DIR/skills"
BUILTIN_SKILLS="/usr/local/lib/node_modules/openclaw/skills"

USER_REPORT="$OUT_DIR/openclaw_user_skills_$TS.md"
BUILTIN_REPORT="$OUT_DIR/openclaw_builtin_skills_$TS.md"

if [[ -d "$USER_SKILLS" ]]; then
  "${SCANNER_CMD[@]}" scan-all "$USER_SKILLS" --format markdown --detailed --output "$USER_REPORT"
  echo "User skills report: $USER_REPORT"
else
  echo "No user skills dir at $USER_SKILLS"
fi

if [[ -d "$BUILTIN_SKILLS" ]]; then
  # Built-in skills may include a few legacy manifests that don't parse; the scanner will log failures.
  "${SCANNER_CMD[@]}" scan-all "$BUILTIN_SKILLS" --format markdown --detailed --output "$BUILTIN_REPORT" || true
  echo "Built-in skills report: $BUILTIN_REPORT"
else
  echo "No built-in skills dir at $BUILTIN_SKILLS"
fi
