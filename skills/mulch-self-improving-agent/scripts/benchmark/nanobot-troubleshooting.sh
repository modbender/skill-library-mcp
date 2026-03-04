#!/bin/sh
# Troubleshooting benchmark: given recurring errors, how many chars to find the fix?
# Simulates "agent hits error → looks for resolution". Quantifies token efficiency and find-rate.
set -e
ROOT="${1:-/skill}"
BENCH_ROOT="${2:-/tmp/bench}"
BASELINE_DIR="$BENCH_ROOT/baseline"
MULCH_DIR="$BENCH_ROOT/mulch"
MULCH="npx --yes mulch-cli"

# Scenario definitions: error query → expected resolution string (must appear in result)
SCENARIO_1_QUERY="pnpm not found"
SCENARIO_1_NEEDLE="npm install"   # resolution: install pnpm
SCENARIO_2_QUERY="docker M1"
SCENARIO_2_NEEDLE="amd64"         # resolution: platform linux/amd64
SCENARIO_3_QUERY="package manager"
SCENARIO_3_NEEDLE="pnpm"

# --- Baseline: agent loads full .learnings to troubleshoot (realistic: read both files)
BASELINE_ERRORS=$(cat "$BASELINE_DIR/.learnings/ERRORS.md" 2>/dev/null || echo "")
BASELINE_LEARNINGS=$(cat "$BASELINE_DIR/.learnings/LEARNINGS.md" 2>/dev/null || echo "")
BASELINE_TROUBLESHOOT_CHARS=$(printf '%s\n%s' "$BASELINE_ERRORS" "$BASELINE_LEARNINGS" | wc -c | tr -d ' ')

# Check each resolution is in the loaded context (agent can find it)
BASELINE_FOUND_1=0; echo "$BASELINE_ERRORS" | grep -q "$SCENARIO_1_NEEDLE" && BASELINE_FOUND_1=1
BASELINE_FOUND_2=0; echo "$BASELINE_ERRORS" | grep -q "$SCENARIO_2_NEEDLE" && BASELINE_FOUND_2=1
BASELINE_FOUND_3=0; echo "$BASELINE_LEARNINGS" | grep -q "$SCENARIO_3_NEEDLE" && BASELINE_FOUND_3=1
BASELINE_FOUND_TOTAL=$((BASELINE_FOUND_1 + BASELINE_FOUND_2 + BASELINE_FOUND_3))

# --- Mulch: targeted search per error (agent runs mulch search "error")
cd "$MULCH_DIR"
MULCH_OUT_1=$($MULCH search "$SCENARIO_1_QUERY" 2>/dev/null || echo "")
MULCH_OUT_2=$($MULCH search "$SCENARIO_2_QUERY" 2>/dev/null || echo "")
MULCH_OUT_3=$($MULCH search "$SCENARIO_3_QUERY" 2>/dev/null || echo "")
MULCH_CHARS_1=$(printf '%s' "$MULCH_OUT_1" | wc -c | tr -d ' ')
MULCH_CHARS_2=$(printf '%s' "$MULCH_OUT_2" | wc -c | tr -d ' ')
MULCH_CHARS_3=$(printf '%s' "$MULCH_OUT_3" | wc -c | tr -d ' ')
MULCH_TROUBLESHOOT_CHARS=$((MULCH_CHARS_1 + MULCH_CHARS_2 + MULCH_CHARS_3))

MULCH_FOUND_1=0; echo "$MULCH_OUT_1" | grep -q "$SCENARIO_1_NEEDLE" && MULCH_FOUND_1=1
MULCH_FOUND_2=0; echo "$MULCH_OUT_2" | grep -q "$SCENARIO_2_NEEDLE" && MULCH_FOUND_2=1
MULCH_FOUND_3=0; echo "$MULCH_OUT_3" | grep -q "$SCENARIO_3_NEEDLE" && MULCH_FOUND_3=1
MULCH_FOUND_TOTAL=$((MULCH_FOUND_1 + MULCH_FOUND_2 + MULCH_FOUND_3))

# Output JSON for runner
printf '%s' "{
  \"baseline\": { \"troubleshoot_chars\": $BASELINE_TROUBLESHOOT_CHARS, \"resolutions_found\": $BASELINE_FOUND_TOTAL, \"scenarios\": 3 },
  \"mulch\": { \"troubleshoot_chars\": $MULCH_TROUBLESHOOT_CHARS, \"resolutions_found\": $MULCH_FOUND_TOTAL, \"scenarios\": 3 }
}" > "$BENCH_ROOT/metrics-troubleshooting.json"

echo "baseline_troubleshoot_chars=$BASELINE_TROUBLESHOOT_CHARS baseline_found=$BASELINE_FOUND_TOTAL/3 mulch_troubleshoot_chars=$MULCH_TROUBLESHOOT_CHARS mulch_found=$MULCH_FOUND_TOTAL/3"
