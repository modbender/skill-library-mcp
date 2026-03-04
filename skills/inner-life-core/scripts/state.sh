#!/usr/bin/env bash
# inner-life-core: State file utilities
# Usage: source this file, then call functions
#   state_read <file> <path>        — read a value from state
#   state_write <file> <path> <val> — write a value to state
#   state_update_timestamp <file>   — update lastUpdate
#   state_decay <file>              — apply half-life decay

set -euo pipefail

WORKSPACE="${OPENCLAW_WORKSPACE:-$(pwd)}"
MEMORY_DIR="$WORKSPACE/memory"

# Validate jq path to prevent injection.
# Allows: .foo, .foo.bar, .foo[0], .["key"], .foo | .bar
_validate_jq_path() {
  if [[ ! "$1" =~ ^\.[][a-zA-Z0-9_.\"\ \|]+$ ]]; then
    echo "error: invalid jq path: $1" >&2
    return 1
  fi
}

state_read() {
  local file="$MEMORY_DIR/$1"
  local path="$2"
  _validate_jq_path "$path" || { echo "null"; return 1; }
  jq -r "$path" "$file" 2>/dev/null || echo "null"
}

state_write() {
  local file="$MEMORY_DIR/$1"
  local path="$2"
  local value="$3"
  _validate_jq_path "$path" || return 1
  local tmp
  tmp=$(jq --argjson val "$value" "$path = \$val" "$file")
  echo "$tmp" > "$file"
}

state_update_timestamp() {
  local file="$MEMORY_DIR/$1"
  local now
  now=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  local tmp
  tmp=$(jq --arg now "$now" '.lastUpdate = $now' "$file")
  echo "$tmp" > "$file"
}

state_decay() {
  # Apply half-life decay to inner-state.json
  local file="$MEMORY_DIR/inner-state.json"
  local last_update
  last_update=$(jq -r '.lastUpdate // empty' "$file" 2>/dev/null)

  if [ -z "$last_update" ]; then
    state_update_timestamp "inner-state.json"
    return
  fi

  local now_epoch last_epoch hours_elapsed periods
  now_epoch=$(date -u +%s)
  last_epoch=$(date -u -d "$last_update" +%s 2>/dev/null || date -u -j -f "%Y-%m-%dT%H:%M:%SZ" "$last_update" +%s 2>/dev/null || echo "$now_epoch")
  hours_elapsed=$(( (now_epoch - last_epoch) / 3600 ))
  periods=$(( hours_elapsed / 6 ))

  if [ "$periods" -gt 0 ]; then
    local conn curi conf
    conn=$(jq -r '.connection.value' "$file")
    curi=$(jq -r '.curiosity.value' "$file")
    conf=$(jq -r '.confidence.value' "$file")

    # connection: -0.05 per 6h period
    conn=$(echo "$conn - ($periods * 0.05)" | bc -l)
    [ "$(echo "$conn < 0" | bc -l)" -eq 1 ] && conn="0"

    # curiosity: -0.03 per 6h period
    curi=$(echo "$curi - ($periods * 0.03)" | bc -l)
    [ "$(echo "$curi < 0" | bc -l)" -eq 1 ] && curi="0"

    # confidence: +0.02 per 6h period (recovery)
    conf=$(echo "$conf + ($periods * 0.02)" | bc -l)
    [ "$(echo "$conf > 1" | bc -l)" -eq 1 ] && conf="1"

    local tmp
    tmp=$(jq --argjson c "$conn" --argjson cu "$curi" --argjson co "$conf" \
      '.connection.value = $c | .curiosity.value = $cu | .confidence.value = $co' "$file")
    echo "$tmp" > "$file"
  fi

  state_update_timestamp "inner-state.json"
}
