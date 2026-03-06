#!/bin/sh
# Nanobot: Mulch flow. Same tasks as baseline; outputs metrics for token comparison.
set -e
BENCH_DIR="${1:-/tmp/bench-mulch}"
METRICS_OUT="${2:-$BENCH_DIR/metrics-mulch.json}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MULCH="npx --yes mulch-cli"
mkdir -p "$BENCH_DIR"
cd "$BENCH_DIR"

# Init Mulch and seed with same prior knowledge as baseline
$MULCH init
$MULCH add config
$MULCH add infra
$MULCH record config --type convention "Use pnpm not npm for this repo. Lock file is pnpm-lock.yaml."
$MULCH record infra --type failure --description "Docker build failed on M1: platform mismatch" --resolution "Use --platform linux/amd64 or FROM --platform=linux/amd64 in Dockerfile"

# Session start: reminder + mulch prime (optimized context only)
REMINDER=$(cat "$SCRIPT_DIR/mulch-reminder.txt")
PRIME_OUT=$($MULCH prime 2>/dev/null)
MULCH_REMINDER_CHARS=$(printf '%s' "$REMINDER" | wc -c | tr -d ' ')
MULCH_CONTEXT_CHARS=$(printf '%s\n%s' "$REMINDER" "$PRIME_OUT" | wc -c | tr -d ' ')

# Task: record new failure
$MULCH record config --type failure --description "pnpm command not found in CI" --resolution "Install: npm install -g pnpm"

# Task: record new convention
$MULCH record config --type convention "Use pnpm not npm. Always run pnpm install."

# Retrieve: "What is our package manager convention?" (targeted: mulch search)
RETRIEVAL_CONVENTION=$($MULCH search "package manager" 2>/dev/null || $MULCH query config 2>/dev/null)
RETRIEVAL_CONVENTION_CHARS=$(printf '%s' "$RETRIEVAL_CONVENTION" | wc -c | tr -d ' ')

# Retrieve: "List known failures" (targeted: query or search failure)
RETRIEVAL_FAILURES=$($MULCH query config 2>/dev/null | head -40)
RETRIEVAL_FAILURES_CHARS=$(printf '%s' "$RETRIEVAL_FAILURES" | wc -c | tr -d ' ')

MULCH_RETRIEVAL_CHARS=$((RETRIEVAL_CONVENTION_CHARS + RETRIEVAL_FAILURES_CHARS))

# Output metrics JSON
printf '%s' "{
  \"reminder_chars\": $MULCH_REMINDER_CHARS,
  \"context_chars\": $MULCH_CONTEXT_CHARS,
  \"retrieval_convention_chars\": $RETRIEVAL_CONVENTION_CHARS,
  \"retrieval_failures_chars\": $RETRIEVAL_FAILURES_CHARS,
  \"retrieval_total_chars\": $MULCH_RETRIEVAL_CHARS
}" > "$METRICS_OUT"
echo "MULCH_METRICS=$METRICS_OUT" >> "$BENCH_DIR/env"
echo "reminder_chars=$MULCH_REMINDER_CHARS context_chars=$MULCH_CONTEXT_CHARS retrieval_total_chars=$MULCH_RETRIEVAL_CHARS"
