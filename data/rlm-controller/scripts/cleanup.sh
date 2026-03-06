#!/usr/bin/env bash
set -euo pipefail

# Cleanup temporary RLM artifacts
# Defaults:
#   CLEAN_ROOT=. (current directory or workspace root)
#   CLEAN_RETENTION=0 (delete all)
#   CLEAN_IGNORE_FILE=./docs/cleanup_ignore.txt

ROOT_DIR="${CLEAN_ROOT:-.}"
RLM_SCRATCH="$ROOT_DIR/scratch/rlm_prototype"
CTX_DIR="$RLM_SCRATCH/ctx"
LOG_DIR="$RLM_SCRATCH/logs"
RETENTION="${CLEAN_RETENTION:-0}"
IGNORE_FILE="${CLEAN_IGNORE_FILE:-./docs/cleanup_ignore.txt}"

read_ignore() {
  if [[ -f "$IGNORE_FILE" ]]; then
    grep -v '^#' "$IGNORE_FILE" | sed '/^$/d'
  fi
}

should_ignore() {
  local f="$1"
  while IFS= read -r rule; do
    [[ "$f" == *"$rule"* ]] && return 0
  done < <(read_ignore)
  return 1
}

prune_dir() {
  local dir="$1"
  [[ -d "$dir" ]] || return 0

  # If retention is 0, delete all files except ignored
  if [[ "$RETENTION" -eq 0 ]]; then
    while IFS= read -r f; do
      if should_ignore "$f"; then
        echo "[skip] $f"
      else
        echo "[delete] $f"
        rm -f "$f"
      fi
    done < <(find "$dir" -maxdepth 1 -type f)
    return 0
  fi

  # Retain last N by mtime
  mapfile -t files < <(ls -t "$dir" 2>/dev/null || true)
  local count=0
  for f in "${files[@]}"; do
    local path="$dir/$f"
    [[ -f "$path" ]] || continue
    if should_ignore "$path"; then
      echo "[skip] $path"
      continue
    fi
    count=$((count+1))
    if [[ "$count" -le "$RETENTION" ]]; then
      echo "[keep] $path"
    else
      echo "[delete] $path"
      rm -f "$path"
    fi
  done
}

prune_dir "$CTX_DIR"
prune_dir "$LOG_DIR"

echo "Cleanup complete."