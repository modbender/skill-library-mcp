#!/bin/bash
# Track changes to documentation over time
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${SCRIPT_DIR}/_common.sh"

ensure_cache_dir

do_snapshot() {
  local datestamp=$(date +%Y-%m-%d_%H%M%S)
  local snapshot_file="${CACHE_SNAPSHOTS}/${datestamp}.txt"

  echo "Creating snapshot: ${datestamp}"
  parse_llms_entries | cut -f4 | sort > "$snapshot_file"
  local count=$(wc -l < "$snapshot_file")
  echo "Saved ${count} page paths to ${snapshot_file}"
}

do_list() {
  echo "Documentation snapshots"
  echo "================================"
  local count=0
  for f in "${CACHE_SNAPSHOTS}"/*.txt; do
    [[ -f "$f" ]] || continue
    local name=$(basename "$f" .txt)
    local pages=$(wc -l < "$f")
    printf "  %-25s %d pages\n" "$name" "$pages"
    count=$(( count + 1 ))
  done
  if (( count == 0 )); then
    echo "  (no snapshots — run: track-changes.sh snapshot)"
  else
    echo
    echo "Total: ${count} snapshots"
  fi
}

do_since() {
  local since_date="$1"
  if [[ -z "$since_date" ]]; then
    echo "Usage: track-changes.sh since <date>"
    echo "Example: track-changes.sh since 2026-02-01"
    exit 1
  fi

  # Find nearest snapshot on or before the given date
  local best_snapshot=""
  for f in "${CACHE_SNAPSHOTS}"/*.txt; do
    [[ -f "$f" ]] || continue
    local snap_date=$(basename "$f" .txt | cut -d_ -f1)
    if [[ "$snap_date" < "$since_date" ]] || [[ "$snap_date" == "$since_date" ]]; then
      best_snapshot="$f"
    fi
  done

  if [[ -z "$best_snapshot" ]]; then
    echo "[error] No snapshot found on or before ${since_date}"
    echo "Available snapshots:"
    do_list
    exit 1
  fi

  echo "Comparing current state against snapshot: $(basename "$best_snapshot" .txt)"
  echo "================================"
  echo

  # Get current state
  local current=$(mktemp)
  parse_llms_entries | cut -f4 | sort > "$current"

  # Compare
  local added=$(comm -13 "$best_snapshot" "$current")
  local removed=$(comm -23 "$best_snapshot" "$current")

  if [[ -n "$added" ]]; then
    echo "++ Added pages:"
    echo "$added" | while read -r path; do
      echo "  + /${path}"
    done
    echo
  fi

  if [[ -n "$removed" ]]; then
    echo "-- Removed pages:"
    echo "$removed" | while read -r path; do
      echo "  - /${path}"
    done
    echo
  fi

  if [[ -z "$added" ]] && [[ -z "$removed" ]]; then
    echo "No page additions or removals detected."
  fi

  local added_count=$(echo "$added" | grep -c . 2>/dev/null || echo 0)
  local removed_count=$(echo "$removed" | grep -c . 2>/dev/null || echo 0)
  echo "Summary: +${added_count} added, -${removed_count} removed"

  rm -f "$current"
}

case "$1" in
  snapshot) do_snapshot ;;
  list)     do_list ;;
  since)
    shift
    do_since "$@"
    ;;
  *)
    echo "Usage: track-changes.sh {snapshot|list|since <date>}"
    echo
    echo "  snapshot   Save current page list as a timestamped snapshot"
    echo "  list       Show all saved snapshots"
    echo "  since      Compare current state against a snapshot date"
    exit 1
    ;;
esac
