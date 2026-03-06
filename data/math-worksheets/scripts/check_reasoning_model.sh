#!/usr/bin/env bash
# check_reasoning_model.sh — Detect the best available reasoning model for math
#
# Reads the active OpenClaw model config (if present) and checks whether a
# reasoning model or strong fallback is configured. All logic is local — no
# network requests are made.
#
# Outputs one line: "<STATUS> <alias> <full-model-id>"
#   FOUND_REASONING — a dedicated reasoning model is active (o3, DeepThink, R1, etc.)
#   FOUND_STRONG    — a strong non-reasoning model is active (Opus, etc.)
#   NONE            — only standard models found; recommend switching
#
# Exit 0 = usable model found
# Exit 1 = only standard models available

set -uo pipefail

# ── Reasoning model patterns (in priority order) ──────────────────────────────
# Format: "alias|substring-to-match-in-model-id"
REASONING_PATTERNS=(
  "o3|/o3"
  "o1|/o1"
  "deepthink|deepthink"
  "deepseek|deepseek-r1"
  "deepseek|deepseek/r1"
)

# ── Strong non-reasoning models (excellent for math, not pure reasoning) ──────
STRONG_PATTERNS=(
  "opus|claude-opus-4"
  "opus|claude-opus-3"
)

# ── Try to read configured models from OpenClaw config (optional) ─────────────
# The config file is only read if it exists. Nothing fails if it doesn't.
CONFIGURED_MODELS=""
CONFIG_PATHS=(
  "${HOME}/.openclaw/config.json"
  "${HOME}/.openclaw/openclaw.json"
)

for config_path in "${CONFIG_PATHS[@]}"; do
  if [[ -f "$config_path" ]]; then
    CONFIGURED_MODELS=$(python3 -c "
import json, sys
try:
    with open('$config_path') as f:
        cfg = json.load(f)
    models = set()
    defaults = cfg.get('agents', {}).get('defaults', {})
    for key in defaults.get('models', {}).keys():
        models.add(key.lower())
    model_cfg = defaults.get('model', {})
    primary = model_cfg.get('primary', '')
    if primary:
        models.add(primary.lower())
    for m in model_cfg.get('fallbacks', []):
        if m: models.add(m.lower())
    for m in sorted(models):
        print(m)
except Exception:
    sys.exit(0)
" 2>/dev/null || true)
    break
  fi
done

# ── Match against a pattern list ──────────────────────────────────────────────
check_patterns() {
  local -n patterns=$1
  for entry in "${patterns[@]}"; do
    local alias="${entry%%|*}"
    local substr="${entry##*|}"
    local match
    match=$(echo "$CONFIGURED_MODELS" | grep -i "$substr" | head -1 || true)
    if [[ -n "$match" ]]; then
      echo "$alias $match"
      return 0
    fi
  done
  return 1
}

# ── Check Tier 1: Reasoning models ───────────────────────────────────────────
if result=$(check_patterns REASONING_PATTERNS 2>/dev/null); then
  echo "FOUND_REASONING $result"
  exit 0
fi

# ── Check Tier 2: Strong non-reasoning ───────────────────────────────────────
if result=$(check_patterns STRONG_PATTERNS 2>/dev/null); then
  echo "FOUND_STRONG $result"
  exit 0
fi

# ── Nothing useful found ──────────────────────────────────────────────────────
echo "NONE"
exit 1
