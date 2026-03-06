#!/bin/bash
# benchmark.sh — Performance benchmark for Agent Brain v3
# Tests operation latency at 100, 1000, 5000, and 10000 entries
# Compares SQLite vs JSON backends side by side

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MEMORY_SH="$SCRIPT_DIR/memory.sh"
MEMORY_DIR="$SCRIPT_DIR/../memory"

# Backup existing data
BACKUP_DB="$MEMORY_DIR/memory.benchmark.db"
BACKUP_JSON="$MEMORY_DIR/memory.benchmark.json"
[[ -f "$MEMORY_DIR/memory.db" ]] && cp "$MEMORY_DIR/memory.db" "$BACKUP_DB"
[[ -f "$MEMORY_DIR/memory.json" ]] && cp "$MEMORY_DIR/memory.json" "$BACKUP_JSON"

cleanup() {
  rm -f "$MEMORY_DIR/memory.db" "$MEMORY_DIR/memory.json" "$MEMORY_DIR/memory.json.bak"
  [[ -f "$BACKUP_DB" ]] && mv "$BACKUP_DB" "$MEMORY_DIR/memory.db"
  [[ -f "$BACKUP_JSON" ]] && mv "$BACKUP_JSON" "$MEMORY_DIR/memory.json"
}
trap cleanup EXIT

TAGS=("code.python" "code.javascript" "code.react" "code.database" "style.code"
      "workflow.git" "workflow.deploy" "testing" "identity" "project"
      "tools" "frontend" "backend" "performance" "security")

TYPES=("fact" "preference" "procedure")

random_tags() {
  local n=$(( RANDOM % 3 + 1 ))
  local result=""
  for ((i=0; i<n; i++)); do
    local idx=$(( RANDOM % ${#TAGS[@]} ))
    if [[ -n "$result" ]]; then
      result="$result,${TAGS[$idx]}"
    else
      result="${TAGS[$idx]}"
    fi
  done
  echo "$result"
}

random_type() {
  local idx=$(( RANDOM % ${#TYPES[@]} ))
  echo "${TYPES[$idx]}"
}

time_cmd() {
  local start end elapsed
  start=$(python3 -c "import time; print(time.time())")
  eval "$@" >/dev/null 2>&1
  end=$(python3 -c "import time; print(time.time())")
  elapsed=$(python3 -c "print(f'{($end - $start) * 1000:.1f}')")
  echo "$elapsed"
}

run_benchmark() {
  local backend="$1"
  local count="$2"

  echo "  Backend: $backend | Entries: $count"

  export AGENT_BRAIN_BACKEND="$backend"
  rm -f "$MEMORY_DIR/memory.db" "$MEMORY_DIR/memory.json" "$MEMORY_DIR/memory.json.bak"

  # Init
  "$MEMORY_SH" init >/dev/null 2>&1

  # Bulk insert
  local start end
  start=$(python3 -c "import time; print(time.time())")
  for ((i=1; i<=count; i++)); do
    local t=$(random_type)
    local tags=$(random_tags)
    "$MEMORY_SH" add "$t" "Benchmark entry number $i about ${TAGS[$(( RANDOM % ${#TAGS[@]} ))]}" user "$tags" >/dev/null 2>&1
  done
  end=$(python3 -c "import time; print(time.time())")
  local total_insert=$(python3 -c "print(f'{($end - $start) * 1000:.0f}')")
  local avg_insert=$(python3 -c "print(f'{($end - $start) / $count * 1000:.1f}')")

  # Benchmark operations
  local t_get=$(time_cmd "\"$MEMORY_SH\" get \"python code\"")
  local t_similar=$(time_cmd "\"$MEMORY_SH\" similar \"javascript react frontend\"")
  local t_conflicts=$(time_cmd "\"$MEMORY_SH\" conflicts \"Python is better than JavaScript for data science\"")
  local t_list=$(time_cmd "\"$MEMORY_SH\" list")
  local t_reflect=$(time_cmd "\"$MEMORY_SH\" reflect")
  local t_export=$(time_cmd "\"$MEMORY_SH\" export")

  printf "    Insert:     %s ms total (%s ms/entry)\n" "$total_insert" "$avg_insert"
  printf "    Get:        %s ms\n" "$t_get"
  printf "    Similar:    %s ms\n" "$t_similar"
  printf "    Conflicts:  %s ms\n" "$t_conflicts"
  printf "    List:       %s ms\n" "$t_list"
  printf "    Reflect:    %s ms\n" "$t_reflect"
  printf "    Export:     %s ms\n" "$t_export"
  echo ""

  unset AGENT_BRAIN_BACKEND
}

echo "========================================="
echo " Agent Brain v3 — Performance Benchmark"
echo "========================================="
echo ""

for count in 100 1000; do
  echo "--- $count entries ---"
  run_benchmark "sqlite" "$count"
  run_benchmark "json" "$count"
done

echo "--- 5000 entries (sqlite only) ---"
run_benchmark "sqlite" 5000

echo "========================================="
echo " Benchmark complete"
echo "========================================="
