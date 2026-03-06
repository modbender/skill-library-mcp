#!/usr/bin/env bash
# ╔══════════════════════════════════════════════════════╗
# ║  RUNE Skill — Prompt Amplification via WAND          ║
# ║  NeuraByte Labs | OpenClaw Skill                     ║
# ╚══════════════════════════════════════════════════════╝
#
# Usage:
#   echo "Write a blog post about AI" | bash main.sh
#   bash main.sh "Write a blog post about AI"
#   bash main.sh                  # prompts interactively

set -euo pipefail

RUNE_DIR="${RUNE_DIR:-/Users/mustafa/Documents/GitHub/rune}"
WAND="$RUNE_DIR/wand.py"

# ── Load secrets for API key ──────────────────────────────
if [[ -f "$HOME/.secrets" ]]; then
  # shellcheck disable=SC1091
  source "$HOME/.secrets"
fi

# ── Validate wand.py ──────────────────────────────────────
if [[ ! -f "$WAND" ]]; then
  echo "ERROR: wand.py not found at $WAND" >&2
  echo "Set RUNE_DIR env var to the RUNE repo path." >&2
  exit 1
fi

# ── Validate RUNE_API_KEY ─────────────────────────────────
if [[ -z "${RUNE_API_KEY:-}" ]]; then
  echo "ERROR: RUNE_API_KEY is not set." >&2
  echo "Add it to ~/.secrets or export RUNE_API_KEY=your_key" >&2
  exit 1
fi

# ── Read prompt from arg, stdin, or interactively ─────────
if [[ $# -ge 1 ]]; then
  PROMPT="$*"
elif ! [ -t 0 ]; then
  # stdin has data (pipe or redirect)
  PROMPT="$(cat)"
else
  echo "Enter prompt (Ctrl+D when done):" >&2
  PROMPT="$(cat)"
fi

if [[ -z "$PROMPT" ]]; then
  echo "ERROR: No prompt provided." >&2
  exit 1
fi

# ── Invoke RUNE wand inscribe ─────────────────────────────
cd "$RUNE_DIR"

# Strip ANSI colors from output for clean piping
python3 "$WAND" inscribe "$PROMPT" \
  | sed $'s/\033\[[0-9;]*m//g'
