#!/usr/bin/env bash
set -euo pipefail

# Agent Pulse — Multi-Agent Monitor
# Check liveness for multiple agents. Supports address args, file input, and JSON output.
#
# Usage:
#   monitor.sh <addr1> [addr2] ...
#   monitor.sh -f agents.txt
#   monitor.sh --feed
#   monitor.sh --json <addr1> ...

API_BASE="${API_BASE:-https://x402pulse.xyz}"

usage() {
  cat >&2 <<EOF
Usage:
  $0 <address> [address ...]     Check specific agents
  $0 -f <file>                   Read addresses from file (one per line, # = comment)
  $0 --feed                      Show global pulse feed
  $0 --json <address> [...]      Output results as JSON array

Options:
  --json        Machine-readable JSON output
  --feed        Show the global pulse feed
  -f, --file    Read addresses from file
  -h, --help    Show this help
EOF
}

ADDRESSES=()
OUTPUT_JSON=false
SHOW_FEED=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    -f|--file)
      shift
      [[ $# -eq 0 ]] && { echo "Error: -f requires a file path" >&2; exit 2; }
      [[ ! -f "$1" ]] && { echo "Error: File '$1' not found" >&2; exit 1; }
      while IFS= read -r line || [[ -n "$line" ]]; do
        line="${line%%#*}"        # strip comments
        line="${line//[[:space:]]/}"  # strip whitespace
        [[ -n "$line" ]] && ADDRESSES+=("$line")
      done < "$1"
      shift
      ;;
    --json)
      OUTPUT_JSON=true
      shift
      ;;
    --feed)
      SHOW_FEED=true
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    0x*)
      ADDRESSES+=("$1")
      shift
      ;;
    *)
      echo "Error: Unknown argument '$1'" >&2
      usage
      exit 2
      ;;
  esac
done

# ── Feed mode ─────────────────────────────────────────────────────
if [[ "$SHOW_FEED" == "true" ]]; then
  FEED=$(curl -sS --connect-timeout 10 --max-time 30 \
    "$API_BASE/api/pulse-feed" 2>/dev/null) || {
    echo "Error: Could not fetch pulse feed" >&2
    exit 1
  }
  if $OUTPUT_JSON; then
    echo "$FEED"
  else
    echo "=== Agent Pulse Feed ==="
    echo "$FEED" | jq '.' 2>/dev/null || echo "$FEED"
  fi
  exit 0
fi

# ── Monitor mode ──────────────────────────────────────────────────
if [[ ${#ADDRESSES[@]} -eq 0 ]]; then
  echo "Error: No addresses specified" >&2
  usage
  exit 2
fi

# Validate addresses
for addr in "${ADDRESSES[@]}"; do
  if [[ ! "$addr" =~ ^0x[a-fA-F0-9]{40}$ ]]; then
    echo "Error: Invalid address: $addr" >&2
    exit 1
  fi
done

ALIVE_COUNT=0
DEAD_COUNT=0
ERROR_COUNT=0
JSON_ITEMS=()

$OUTPUT_JSON || echo "=== Agent Pulse Monitor (${#ADDRESSES[@]} agents) ==="
$OUTPUT_JSON || echo ""

for addr in "${ADDRESSES[@]}"; do
  # Fetch v1 status
  STATUS=$(curl -sS --connect-timeout 10 --max-time 15 \
    "$API_BASE/api/status/$addr" 2>/dev/null) || STATUS=""

  if [[ -n "$STATUS" ]] && echo "$STATUS" | jq -e '.isAlive // .alive' &>/dev/null 2>&1; then
    IS_ALIVE=$(echo "$STATUS" | jq -r '.isAlive // .alive')
    STREAK=$(echo "$STATUS" | jq -r '.streak // 0')
    HAZARD=$(echo "$STATUS" | jq -r '.hazardScore // "N/A"')
    LAST=$(echo "$STATUS" | jq -r '.lastPulse // .lastPulseAt // "never"')

    if [[ "$IS_ALIVE" == "true" ]]; then
      ICON="🟢"; ALIVE_COUNT=$((ALIVE_COUNT + 1))
    else
      ICON="🔴"; DEAD_COUNT=$((DEAD_COUNT + 1))
    fi

    $OUTPUT_JSON || echo "$ICON $addr"
    $OUTPUT_JSON || echo "   Alive: $IS_ALIVE | Streak: $STREAK | Hazard: $HAZARD | Last: $LAST"

    JSON_ITEMS+=("$(jq -n \
      --arg a "$addr" --argjson alive "$IS_ALIVE" \
      --argjson streak "$STREAK" --arg hazard "$HAZARD" --arg last "$LAST" \
      '{address:$a, alive:$alive, streak:$streak, hazard:$hazard, lastPulse:$last}')")
  else
    ERROR_COUNT=$((ERROR_COUNT + 1))
    $OUTPUT_JSON || echo "⚪ $addr"
    $OUTPUT_JSON || echo "   Status: unknown (API error or unregistered)"

    JSON_ITEMS+=("$(jq -n --arg a "$addr" '{address:$a, alive:null, error:"could not fetch status"}')")
  fi
done

# ── Summary ───────────────────────────────────────────────────────
if $OUTPUT_JSON; then
  printf '%s\n' "${JSON_ITEMS[@]}" | jq -s '.'
else
  echo ""
  echo "=== Summary ==="
  echo "  🟢 Alive: $ALIVE_COUNT"
  echo "  🔴 Dead:  $DEAD_COUNT"
  echo "  ⚪ Error: $ERROR_COUNT"
  echo "  Total:   ${#ADDRESSES[@]}"
fi
