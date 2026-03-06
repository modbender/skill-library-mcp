#!/bin/sh
# Nanobot: baseline (Self Improving Agent — Rank #2 on ClawHub / legacy .learnings) flow.
# Simulates session start + record + retrieve; outputs metrics for token comparison.
set -e
BENCH_DIR="${1:-/tmp/bench-baseline}"
METRICS_OUT="${2:-$BENCH_DIR/metrics-baseline.json}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$BENCH_DIR"
cd "$BENCH_DIR"

# Simulated .learnings from prior sessions (realistic size)
mkdir -p .learnings
cat > .learnings/LEARNINGS.md << 'LEARN'
# Learnings

## [LRN-20250101-001] correction
**Logged**: 2025-01-01T10:00:00Z
**Priority**: medium
**Status**: pending
**Area**: config
### Summary
Use pnpm not npm for this repo.
### Details
Lock file is pnpm-lock.yaml. npm install fails.
### Metadata
- Source: user_feedback
- Tags: pnpm, package-manager
---
LEARN

cat > .learnings/ERRORS.md << 'ERR'
# Errors

## [ERR-20250101-001] docker_build
**Logged**: 2025-01-01T11:00:00Z
**Priority**: high
**Status**: pending
**Area**: infra
### Summary
Docker build failed on M1: platform mismatch.
### Error
```
no matching manifest for linux/arm64
```
### Suggested Fix
Use --platform linux/amd64 or FROM --platform=linux/amd64 in Dockerfile.
### Metadata
- Reproducible: yes
---
ERR

# Session start: reminder + full .learnings context (what agent would load)
REMINDER=$(cat "$SCRIPT_DIR/legacy-reminder.txt")
LEARNINGS_CONTENT=$(cat .learnings/LEARNINGS.md)
ERRORS_CONTENT=$(cat .learnings/ERRORS.md)
BASELINE_REMINDER_CHARS=$(printf '%s' "$REMINDER" | wc -c | tr -d ' ')
BASELINE_CONTEXT_CHARS=$(printf '%s\n%s\n%s' "$REMINDER" "$LEARNINGS_CONTENT" "$ERRORS_CONTENT" | wc -c | tr -d ' ')

# Task: record a new failure (append to ERRORS.md)
cat >> .learnings/ERRORS.md << 'NEWERR'

## [ERR-20250115-002] pnpm_not_found
**Logged**: 2025-01-15T12:00:00Z
**Priority**: medium
**Status**: pending
**Area**: config
### Summary
pnpm command not found in CI.
### Error
```
pnpm: command not found
```
### Suggested Fix
Install: npm install -g pnpm
### Metadata
- Reproducible: yes
---
NEWERR

# Task: record a new convention (append to LEARNINGS.md)
cat >> .learnings/LEARNINGS.md << 'NEWLRN'

## [LRN-20250115-002] convention
**Logged**: 2025-01-15T12:01:00Z
**Priority**: medium
**Status**: pending
**Area**: config
### Summary
Use pnpm not npm. Always run pnpm install.
### Metadata
- Source: conversation
- Tags: pnpm
---
NEWLRN

# Retrieve: "What is our package manager convention?" (grep LEARNINGS)
RETRIEVAL_CONVENTION=$(grep -A 2 "pnpm\|package" .learnings/LEARNINGS.md | head -20)
RETRIEVAL_CONVENTION_CHARS=$(printf '%s' "$RETRIEVAL_CONVENTION" | wc -c | tr -d ' ')

# Retrieve: "List known failures" (full ERRORS.md - agent often loads full file)
RETRIEVAL_FAILURES=$(cat .learnings/ERRORS.md)
RETRIEVAL_FAILURES_CHARS=$(printf '%s' "$RETRIEVAL_FAILURES" | wc -c | tr -d ' ')

# Total "retrieval" for two queries (simulate agent reading both)
BASELINE_RETRIEVAL_CHARS=$((RETRIEVAL_CONVENTION_CHARS + RETRIEVAL_FAILURES_CHARS))

# Output metrics JSON
printf '%s' "{
  \"reminder_chars\": $BASELINE_REMINDER_CHARS,
  \"context_chars\": $BASELINE_CONTEXT_CHARS,
  \"retrieval_convention_chars\": $RETRIEVAL_CONVENTION_CHARS,
  \"retrieval_failures_chars\": $RETRIEVAL_FAILURES_CHARS,
  \"retrieval_total_chars\": $BASELINE_RETRIEVAL_CHARS
}" > "$METRICS_OUT"
echo "BASELINE_METRICS=$METRICS_OUT" >> "$BENCH_DIR/env"
echo "reminder_chars=$BASELINE_REMINDER_CHARS context_chars=$BASELINE_CONTEXT_CHARS retrieval_total_chars=$BASELINE_RETRIEVAL_CHARS"
