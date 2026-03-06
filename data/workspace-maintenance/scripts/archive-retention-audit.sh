#!/usr/bin/env bash
set -euo pipefail

ROOT="/Users/ineluxx/.openclaw/workspace/docs/archive"
OUT="$ROOT/DELETE-DRYRUN-$(date +%F).txt"

echo "# Dry-run deletion candidates (NO DELETE EXECUTED)" > "$OUT"
echo "# Generated: $(date '+%F %T %Z')" >> "$OUT"
echo >> "$OUT"

# legacy paths
echo "# Legacy skill paths (review)" >> "$OUT"
echo "/Users/ineluxx/.openclaw/workspace/attachments-skill/" >> "$OUT"
echo "/Users/ineluxx/.openclaw/workspace/qmd/" >> "$OUT"
echo "/Users/ineluxx/.openclaw/workspace/camofox/" >> "$OUT"
echo >> "$OUT"

# age-based candidate scan (example: >30 days)
echo "# Archived files older than 30 days (candidate review)" >> "$OUT"
find "$ROOT" -type f -name '*.md' -mtime +30 | sort >> "$OUT" || true

echo "Wrote $OUT"
