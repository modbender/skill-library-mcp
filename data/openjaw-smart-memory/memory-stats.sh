#!/usr/bin/env bash
# smart-memory: memory-stats.sh
# Analytics and reporting for the smart-memory skill
# Shows memory health, usage patterns, token savings, and ROI

set -euo pipefail

MEMORY_DIR="${OPENCLAW_MEMORY_DIR:-$HOME/.openclaw/smart-memory}"
MEMORIES_FILE="$MEMORY_DIR/memories.json"
ARCHIVE_FILE="$MEMORY_DIR/archive.json"
STATS_FILE="$MEMORY_DIR/stats.json"

die() { echo "ERROR: $*" >&2; exit 1; }

# Check dependencies
command -v jq >/dev/null 2>&1 || die "jq is required but not installed."

if [ ! -f "$MEMORIES_FILE" ]; then
    die "Memory store not found. Run 'memory-manager.sh init' first."
fi

# ─── Gather Data ─────────────────────────────────────────────────────────────

active_count=$(jq '.memories | length' "$MEMORIES_FILE")
forgotten_count=$(jq '[.memories[] | select(.forgotten == true)] | length' "$MEMORIES_FILE")
archive_count=$(jq '.archived | length' "$ARCHIVE_FILE" 2>/dev/null || echo 0)

# Category breakdown
categories=$(jq -r '
    .memories
    | group_by(.category)
    | map({category: .[0].category, count: length})
    | sort_by(-.count)
    | .[]
    | "    \(.category): \(.count)"
' "$MEMORIES_FILE" 2>/dev/null || echo "    (none)")

# Confidence breakdown
confidence_high=$(jq '[.memories[] | select(.confidence == "high")] | length' "$MEMORIES_FILE")
confidence_med=$(jq '[.memories[] | select(.confidence == "medium")] | length' "$MEMORIES_FILE")
confidence_low=$(jq '[.memories[] | select(.confidence == "low")] | length' "$MEMORIES_FILE")

# Source breakdown
source_explicit=$(jq '[.memories[] | select(.source == "user_explicit")] | length' "$MEMORIES_FILE")
source_convo=$(jq '[.memories[] | select(.source == "conversation")] | length' "$MEMORIES_FILE")
source_inferred=$(jq '[.memories[] | select(.source == "inferred")] | length' "$MEMORIES_FILE")

# Access patterns
most_accessed=$(jq '
    [.memories[] | select(.access_count > 0)]
    | sort_by(-.access_count)
    | .[:5][]
    | "    [\(.access_count)x] \(.key): \(.value[:60])"
' "$MEMORIES_FILE" 2>/dev/null || echo "    (none accessed yet)")

never_accessed=$(jq '[.memories[] | select(.access_count == 0 and .forgotten == false)] | length' "$MEMORIES_FILE")

# Date range
oldest=$(jq -r '[.memories[].created] | sort | first // "N/A"' "$MEMORIES_FILE" 2>/dev/null || echo "N/A")
newest=$(jq -r '[.memories[].created] | sort | last // "N/A"' "$MEMORIES_FILE" 2>/dev/null || echo "N/A")

# File sizes
memories_size=$(du -h "$MEMORIES_FILE" 2>/dev/null | cut -f1 || echo "N/A")
archive_size=$(du -h "$ARCHIVE_FILE" 2>/dev/null | cut -f1 || echo "N/A")
total_size=$(du -sh "$MEMORY_DIR" 2>/dev/null | cut -f1 || echo "N/A")

# Stats from stats.json
total_stores=$(jq '.total_stores // 0' "$STATS_FILE" 2>/dev/null || echo 0)
total_retrievals=$(jq '.total_retrievals // 0' "$STATS_FILE" 2>/dev/null || echo 0)
total_updates=$(jq '.total_updates // 0' "$STATS_FILE" 2>/dev/null || echo 0)
total_deletes=$(jq '.total_deletes // 0' "$STATS_FILE" 2>/dev/null || echo 0)
total_tokens_saved=$(jq '.total_tokens_saved // 0' "$STATS_FILE" 2>/dev/null || echo 0)
last_maintenance=$(jq -r '.last_maintenance // "never"' "$STATS_FILE" 2>/dev/null || echo "never")

# Token savings to dollar estimate
# Approximate: 1M tokens ~ $3 (input) for Claude, varies by model
# Using a conservative $2/1M tokens average
dollars_saved=$(echo "scale=4; $total_tokens_saved * 2 / 1000000" | bc 2>/dev/null || echo "N/A")

# ─── Output Report ───────────────────────────────────────────────────────────

cat <<REPORT

╔══════════════════════════════════════════════════════════╗
║           smart-memory  -  Status Report                ║
╚══════════════════════════════════════════════════════════╝

  MEMORY STORE
  ─────────────────────────────────────
  Active memories:     $active_count
  Forgotten (pending): $forgotten_count
  Archived:            $archive_count
  Total ever stored:   $total_stores

  CATEGORIES
  ─────────────────────────────────────
$categories

  CONFIDENCE LEVELS
  ─────────────────────────────────────
    high:   $confidence_high
    medium: $confidence_med
    low:    $confidence_low

  SOURCES
  ─────────────────────────────────────
    user_explicit: $source_explicit
    conversation:  $source_convo
    inferred:      $source_inferred

  USAGE ACTIVITY
  ─────────────────────────────────────
  Total retrievals:    $total_retrievals
  Total updates:       $total_updates
  Total deletes:       $total_deletes
  Never accessed:      $never_accessed

  MOST ACCESSED MEMORIES
  ─────────────────────────────────────
$most_accessed

  TOKEN SAVINGS
  ─────────────────────────────────────
  Tokens saved:        $total_tokens_saved
  Est. cost saved:     \$$dollars_saved

  STORAGE
  ─────────────────────────────────────
  Memories file:       $memories_size
  Archive file:        $archive_size
  Total disk usage:    $total_size

  TIMELINE
  ─────────────────────────────────────
  Oldest memory:       $oldest
  Newest memory:       $newest
  Last maintenance:    $last_maintenance

  PATH: $MEMORY_DIR

REPORT
