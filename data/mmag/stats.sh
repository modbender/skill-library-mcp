#!/usr/bin/env bash
# stats.sh – Display MMAG memory usage statistics per layer
# Usage: bash stats.sh [--root <memory-root>]

set -euo pipefail

ROOT="memory"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --root)
      ROOT="$2"
      shift 2
      ;;
    *)
      shift
      ;;
  esac
done

LAYERS=(
  "conversational:Conversational Memory"
  "long-term:Long-Term User Memory"
  "episodic:Episodic & Event-Linked Memory"
  "sensory:Sensory & Context-Aware Memory"
  "working:Short-Term Working Memory"
)

echo ""
echo "🧠 MMAG Memory Statistics"
echo "   Root: $ROOT"
echo "   Generated: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""
echo "─────────────────────────────────────────────────────────"

TOTAL_FILES=0
TOTAL_SIZE_BYTES=0

for entry in "${LAYERS[@]}"; do
  IFS=':' read -r layer label <<< "$entry"
  dir="$ROOT/$layer"

  if [ ! -d "$dir" ]; then
    echo "  ⬜ $label: not initialized"
    continue
  fi

  file_count=$(find "$dir" -name "*.md" ! -name "README.md" 2>/dev/null | wc -l | tr -d ' ')
  dir_size_human=$(du -sh "$dir" 2>/dev/null | cut -f1)
  dir_size_bytes=$(du -sb "$dir" 2>/dev/null | cut -f1 || echo "0")
  latest_file=$(find "$dir" -name "*.md" ! -name "README.md" 2>/dev/null | sort -r | head -1)
  latest_date=""
  if [ -n "$latest_file" ]; then
    latest_date=$(date -r "$latest_file" '+%Y-%m-%d %H:%M' 2>/dev/null || echo "unknown")
  fi

  TOTAL_FILES=$((TOTAL_FILES + file_count))
  TOTAL_SIZE_BYTES=$((TOTAL_SIZE_BYTES + dir_size_bytes))

  echo "  📂 $label"
  echo "     Files     : $file_count"
  echo "     Size      : $dir_size_human"
  if [ -n "$latest_date" ]; then
    echo "     Last entry: $latest_date"
  fi
  echo ""
done

# Snapshots
SNAPSHOTS_DIR="$ROOT/working/snapshots"
if [ -d "$SNAPSHOTS_DIR" ]; then
  snap_count=$(find "$SNAPSHOTS_DIR" -name "*.tar.gz" 2>/dev/null | wc -l | tr -d ' ')
  snap_size=$(du -sh "$SNAPSHOTS_DIR" 2>/dev/null | cut -f1)
  echo "  📸 Snapshots: $snap_count files ($snap_size)"
  echo ""
fi

echo "─────────────────────────────────────────────────────────"
# Convert total bytes to human-readable
if command -v numfmt &>/dev/null; then
  total_human=$(numfmt --to=iec-i --suffix=B "$TOTAL_SIZE_BYTES" 2>/dev/null || echo "${TOTAL_SIZE_BYTES}B")
else
  total_human="${TOTAL_SIZE_BYTES}B"
fi
echo "  Total files : $TOTAL_FILES"
echo "  Total size  : $total_human"
echo ""
