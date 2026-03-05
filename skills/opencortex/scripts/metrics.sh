#!/bin/bash
# OpenCortex — Metrics Collection & Reporting
#
# READ-ONLY: This script only counts files and greps for patterns.
# It does not modify any workspace files (except appending to metrics.log in --collect mode).
# No network access. No sensitive data captured — only counts, never content.
#
# Usage:
#   metrics.sh --collect          # Append today's snapshot to memory/metrics.log
#   metrics.sh --report           # Show trends from collected data
#   metrics.sh --report --weeks 8 # Show last 8 weeks (default: 12)
#   metrics.sh --json             # Output today's snapshot as JSON (for programmatic use)
#   metrics.sh --help             # Show this help
set -euo pipefail

WORKSPACE="${CLAWD_WORKSPACE:-$(cd "$(dirname "$0")/.." && pwd)}"
METRICS_LOG="$WORKSPACE/memory/metrics.log"
TODAY=$(date '+%Y-%m-%d')

# --- Helpers ---

# Trim whitespace from a number
trimnum() { echo "${1:-0}" | tr -dc '0-9'; }

# Safe grep -c wrapper (returns 0 on no match)
grepcount() { grep -c "$1" "$2" 2>/dev/null | tr -d ' ' || echo 0; }

count_files() {
  local dir="$1"
  local pattern="${2:-*.md}"
  local c
  c=$([ -d "$dir" ] && find "$dir" -name "$pattern" -type f 2>/dev/null | wc -l | tr -d ' ' || echo 0)
  echo "${c:-0}"
}

count_bytes() {
  local dir="$1"
  local pattern="${2:-*.md}"
  local c
  c=$([ -d "$dir" ] && find "$dir" -name "$pattern" -type f -exec cat {} + 2>/dev/null | wc -c | tr -d ' ' || echo 0)
  echo "${c:-0}"
}

count_grep() {
  local dir="$1"
  local pattern="$2"
  local c
  c=$([ -d "$dir" ] && grep -rl "$pattern" "$dir" --include="*.md" 2>/dev/null | wc -l | tr -d ' ' || echo 0)
  echo "${c:-0}"
}

count_grep_lines() {
  local dir="$1"
  local pattern="$2"
  if [ ! -d "$dir" ]; then echo 0; return; fi
  local c
  c=$(grep -r "$pattern" "$dir" --include="*.md" 2>/dev/null | wc -l | tr -d ' ')
  echo "${c:-0}"
}

# --- Snapshot: collect all metrics into variables ---

# Sets global vars: m_knowledge_files m_knowledge_kb m_decisions m_runbooks
# m_tools m_failures m_debriefs m_projects m_archive m_principles m_core_files
# m_cron_jobs m_infra_entries
snapshot_metrics() {
  m_knowledge_files=$(( $(count_files "$WORKSPACE/memory/projects") + $(count_files "$WORKSPACE/memory/contacts") + $(count_files "$WORKSPACE/memory/workflows") + $(count_files "$WORKSPACE/memory/runbooks") ))
  if [ -d "$WORKSPACE/memory" ]; then
    m_knowledge_files=$(( m_knowledge_files + $(trimnum "$(find "$WORKSPACE/memory" -maxdepth 1 -name "*.md" -type f 2>/dev/null | wc -l)") ))
  fi

  local kb=0
  for kdir in projects contacts workflows runbooks; do
    if [ -d "$WORKSPACE/memory/$kdir" ]; then
      kb=$(( kb + $(trimnum "$(find "$WORKSPACE/memory/$kdir" -name "*.md" -type f -exec cat {} + 2>/dev/null | wc -c)") ))
    fi
  done
  kb=$(( kb + $(trimnum "$(find "$WORKSPACE/memory" -maxdepth 1 -name "*.md" -type f -exec cat {} + 2>/dev/null | wc -c)") ))
  m_knowledge_kb=$(( kb / 1024 ))

  m_decisions=$(count_grep_lines "$WORKSPACE/memory" "\*\*Decision:\*\*")
  if [ -f "$WORKSPACE/MEMORY.md" ]; then
    m_decisions=$(( m_decisions + $(trimnum "$(grepcount '\*\*Decision:\*\*' "$WORKSPACE/MEMORY.md")") ))
  fi
  if [ -f "$WORKSPACE/USER.md" ]; then
    m_decisions=$(( m_decisions + $(trimnum "$(grepcount '\*\*Decision:\*\*' "$WORKSPACE/USER.md")") ))
  fi

  m_runbooks=$(count_files "$WORKSPACE/memory/runbooks")

  m_tools=0
  if [ -f "$WORKSPACE/TOOLS.md" ]; then
    m_tools=$(trimnum "$(grep -cE '^#{2,3} ' "$WORKSPACE/TOOLS.md" 2>/dev/null || echo 0)")
  fi

  local fail=$(count_grep_lines "$WORKSPACE/memory" "❌ FAILURE:")
  local corr=$(count_grep_lines "$WORKSPACE/memory" "🔧 CORRECTION:")
  m_failures=$(( fail + corr ))

  m_debriefs=$(count_grep_lines "$WORKSPACE/memory" "[Dd]ebrief")
  m_projects=$(count_files "$WORKSPACE/memory/projects")
  m_contacts=$(count_files "$WORKSPACE/memory/contacts")
  m_workflows=$(count_files "$WORKSPACE/memory/workflows")
  m_preferences=0
  if [ -f "$WORKSPACE/memory/preferences.md" ]; then
    m_preferences=$(trimnum "$(grep -c '\*\*Preference:\*\*' "$WORKSPACE/memory/preferences.md" 2>/dev/null || echo 0)")
  fi
  m_archive=$(count_files "$WORKSPACE/memory/archive")

  m_principles=0
  if [ -f "$WORKSPACE/MEMORY.md" ]; then
    m_principles=$(trimnum "$(grep -cE '^### P[0-9]' "$WORKSPACE/MEMORY.md" 2>/dev/null || echo 0)")
  fi

  m_core_files=0
  for f in SOUL.md AGENTS.md MEMORY.md TOOLS.md INFRA.md USER.md BOOTSTRAP.md; do
    if [ -f "$WORKSPACE/$f" ]; then
      m_core_files=$(( m_core_files + 1 ))
    fi
  done

  m_cron_jobs=0
  if command -v openclaw &>/dev/null; then
    m_cron_jobs=$(trimnum "$(openclaw cron list --json 2>/dev/null | grep -c '"name"' || echo 0)")
  fi

  m_infra_entries=0
  if [ -f "$WORKSPACE/INFRA.md" ]; then
    m_infra_entries=$(trimnum "$(grep -cE '^#{2,3} ' "$WORKSPACE/INFRA.md" 2>/dev/null || echo 0)")
  fi
}

# --- Collect ---

do_collect() {
  mkdir -p "$WORKSPACE/memory"
  snapshot_metrics

  cat >> "$METRICS_LOG" <<EOF
---
date: $TODAY
knowledge_files: $m_knowledge_files
knowledge_kb: $m_knowledge_kb
decisions: $m_decisions
runbooks: $m_runbooks
tools: $m_tools
failures_logged: $m_failures
debriefs: $m_debriefs
projects: $m_projects
contacts: $m_contacts
workflows: $m_workflows
preferences: $m_preferences
archive_files: $m_archive
principles: $m_principles
core_files: $m_core_files
cron_jobs: $m_cron_jobs
infra_entries: $m_infra_entries
EOF

  echo "✅ Metrics collected for $TODAY → memory/metrics.log"
}

# --- JSON output ---

do_json() {
  mkdir -p "$WORKSPACE/memory"
  snapshot_metrics

  cat <<EOF
{
  "date": "$TODAY",
  "knowledge_files": $m_knowledge_files,
  "knowledge_kb": $m_knowledge_kb,
  "decisions": $m_decisions,
  "runbooks": $m_runbooks,
  "tools": $m_tools,
  "failures_logged": $m_failures,
  "debriefs": $m_debriefs,
  "projects": $m_projects,
  "contacts": $m_contacts,
  "workflows": $m_workflows,
  "preferences": $m_preferences,
  "archive_files": $m_archive,
  "principles": $m_principles
}
EOF
}

# --- Report ---

do_report() {
  local weeks="${1:-12}"

  if [ ! -f "$METRICS_LOG" ]; then
    echo "No metrics data yet. Run: metrics.sh --collect"
    exit 0
  fi

  # Parse all entries from the log
  local dates=()
  local kf=() kb=() dec=() rb=() tools=() fail=() deb=() proj=() cont=() wflow=() pref=() arch=()
  local cur_date="" cur_kf="" cur_kb="" cur_dec="" cur_rb="" cur_tools="" cur_fail="" cur_deb="" cur_proj="" cur_cont="" cur_wflow="" cur_pref="" cur_arch=""

  while IFS= read -r line; do
    case "$line" in
      "---") 
        if [ -n "$cur_date" ]; then
          dates+=("$cur_date")
          kf+=("${cur_kf:-0}"); kb+=("${cur_kb:-0}"); dec+=("${cur_dec:-0}")
          rb+=("${cur_rb:-0}"); tools+=("${cur_tools:-0}"); fail+=("${cur_fail:-0}")
          deb+=("${cur_deb:-0}"); proj+=("${cur_proj:-0}"); cont+=("${cur_cont:-0}")
          wflow+=("${cur_wflow:-0}"); pref+=("${cur_pref:-0}"); arch+=("${cur_arch:-0}")
        fi
        cur_date="" cur_kf="" cur_kb="" cur_dec="" cur_rb="" cur_tools="" cur_fail="" cur_deb="" cur_proj="" cur_cont="" cur_wflow="" cur_pref="" cur_arch=""
        ;;
      date:*) cur_date="${line#date: }" ;;
      knowledge_files:*) cur_kf="${line#knowledge_files: }" ;;
      knowledge_kb:*) cur_kb="${line#knowledge_kb: }" ;;
      decisions:*) cur_dec="${line#decisions: }" ;;
      runbooks:*) cur_rb="${line#runbooks: }" ;;
      tools:*) cur_tools="${line#tools: }" ;;
      failures_logged:*) cur_fail="${line#failures_logged: }" ;;
      debriefs:*) cur_deb="${line#debriefs: }" ;;
      projects:*) cur_proj="${line#projects: }" ;;
      contacts:*) cur_cont="${line#contacts: }" ;;
      workflows:*) cur_wflow="${line#workflows: }" ;;
      preferences:*) cur_pref="${line#preferences: }" ;;
      archive_files:*) cur_arch="${line#archive_files: }" ;;
    esac
  done < "$METRICS_LOG"
  # Flush last entry
  if [ -n "$cur_date" ]; then
    dates+=("$cur_date")
    kf+=("${cur_kf:-0}"); kb+=("${cur_kb:-0}"); dec+=("${cur_dec:-0}")
    rb+=("${cur_rb:-0}"); tools+=("${cur_tools:-0}"); fail+=("${cur_fail:-0}")
    deb+=("${cur_deb:-0}"); proj+=("${cur_proj:-0}"); cont+=("${cur_cont:-0}")
    wflow+=("${cur_wflow:-0}"); pref+=("${cur_pref:-0}"); arch+=("${cur_arch:-0}")
  fi

  local total=${#dates[@]}
  if [ "$total" -eq 0 ]; then
    echo "No metrics entries found."
    exit 0
  fi

  # Limit to last N days (weeks * 7)
  local limit=$(( weeks * 7 ))
  local start=0
  [ "$total" -gt "$limit" ] && start=$(( total - limit ))

  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "  🧠 OpenCortex Metrics Report"
  echo "  Period: ${dates[$start]} → ${dates[$((total-1))]}"
  echo "  Data points: $(( total - start ))"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""

  # Summary: first vs latest
  local first=$start
  local last=$(( total - 1 ))

  printf "  %-24s %8s %8s %8s\n" "Metric" "Start" "Current" "Change"
  printf "  %-24s %8s %8s %8s\n" "────────────────────────" "────────" "────────" "────────"

  print_row() {
    local label="$1" v1="$2" v2="$3"
    local diff=$(( v2 - v1 ))
    local sign=""
    [ "$diff" -gt 0 ] && sign="+"
    printf "  %-24s %8d %8d %7s%d\n" "$label" "$v1" "$v2" "$sign" "$diff"
  }

  print_row "Knowledge files" "${kf[$first]}" "${kf[$last]}"
  print_row "Knowledge size (KB)" "${kb[$first]}" "${kb[$last]}"
  print_row "Decisions captured" "${dec[$first]}" "${dec[$last]}"
  print_row "Runbooks" "${rb[$first]}" "${rb[$last]}"
  print_row "Tools documented" "${tools[$first]}" "${tools[$last]}"
  print_row "Failures logged" "${fail[$first]}" "${fail[$last]}"
  print_row "Debriefs" "${deb[$first]}" "${deb[$last]}"
  print_row "Projects" "${proj[$first]}" "${proj[$last]}"
  print_row "Contacts" "${cont[$first]}" "${cont[$last]}"
  print_row "Workflows" "${wflow[$first]}" "${wflow[$last]}"
  print_row "Preferences" "${pref[$first]}" "${pref[$last]}"
  print_row "Archive files" "${arch[$first]}" "${arch[$last]}"

  echo ""

  # ASCII sparkline for knowledge KB
  echo "  📈 Knowledge Growth (KB):"
  draw_chart "kb" "$start" "$total"
  echo ""

  echo "  📈 Decisions Captured:"
  draw_chart "dec" "$start" "$total"
  echo ""

  echo "  📈 Tools Documented:"
  draw_chart "tools" "$start" "$total"
  echo ""

  # Health score
  local score=0
  local max_score=100

  # Score components (each out of ~12-13 points)
  [ "${kf[$last]}" -ge 5 ] && score=$(( score + 10 ))
  [ "${kf[$last]}" -ge 15 ] && score=$(( score + 5 ))
  [ "${dec[$last]}" -ge 5 ] && score=$(( score + 10 ))
  [ "${dec[$last]}" -ge 20 ] && score=$(( score + 5 ))
  [ "${rb[$last]}" -ge 1 ] && score=$(( score + 5 ))
  [ "${rb[$last]}" -ge 3 ] && score=$(( score + 5 ))
  [ "${tools[$last]}" -ge 3 ] && score=$(( score + 8 ))
  [ "${tools[$last]}" -ge 10 ] && score=$(( score + 4 ))
  [ "${proj[$last]}" -ge 2 ] && score=$(( score + 8 ))
  [ "${cont[$last]}" -ge 1 ] && score=$(( score + 3 ))
  [ "${cont[$last]}" -ge 5 ] && score=$(( score + 3 ))
  [ "${wflow[$last]}" -ge 1 ] && score=$(( score + 3 ))
  [ "${pref[$last]}" -ge 3 ] && score=$(( score + 4 ))
  [ "${pref[$last]}" -ge 10 ] && score=$(( score + 3 ))
  [ "${arch[$last]}" -ge 7 ] && score=$(( score + 7 ))
  [ "${arch[$last]}" -ge 30 ] && score=$(( score + 4 ))

  # Growth bonus (if any metric grew)
  local grew=0
  [ "${kf[$last]}" -gt "${kf[$first]}" ] && grew=1
  [ "${dec[$last]}" -gt "${dec[$first]}" ] && grew=1
  [ "${tools[$last]}" -gt "${tools[$first]}" ] && grew=1
  [ "${pref[$last]}" -gt "${pref[$first]}" ] && grew=1
  [ "$grew" -eq 1 ] && score=$(( score + 7 ))

  # Consistency bonus (more than 7 data points = at least a week of tracking)
  [ "$(( total - start ))" -ge 7 ] && score=$(( score + 7 ))

  [ "$score" -gt "$max_score" ] && score=$max_score

  echo "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  printf "  🏆 Compound Score: %d/%d" "$score" "$max_score"
  if [ "$score" -ge 80 ]; then
    echo "  — Thriving"
  elif [ "$score" -ge 60 ]; then
    echo "  — Growing"
  elif [ "$score" -ge 40 ]; then
    echo "  — Developing"
  elif [ "$score" -ge 20 ]; then
    echo "  — Getting started"
  else
    echo "  — Just installed"
  fi
  echo ""
  echo "  Score reflects knowledge depth, growth rate, and tracking consistency."
  echo "  A healthy OpenCortex installation trends upward over weeks."
  echo ""
}

draw_chart() {
  local var_name="$1"
  local start="$2"
  local total="$3"
  local -n arr="$var_name"

  # Find min/max
  local min=999999 max=0
  for (( i=start; i<total; i++ )); do
    local v="${arr[$i]}"
    [ "$v" -lt "$min" ] && min=$v
    [ "$v" -gt "$max" ] && max=$v
  done

  local range=$(( max - min ))
  [ "$range" -eq 0 ] && range=1

  local bar_chars="▁▂▃▄▅▆▇█"
  local chart=""

  # Sample up to 40 points for display width
  local count=$(( total - start ))
  local step=1
  [ "$count" -gt 40 ] && step=$(( count / 40 ))

  for (( i=start; i<total; i+=step )); do
    local v="${arr[$i]}"
    local idx=$(( (v - min) * 7 / range ))
    [ "$idx" -gt 7 ] && idx=7
    [ "$idx" -lt 0 ] && idx=0
    chart="${chart}${bar_chars:$idx:1}"
  done

  echo "     ${arr[$start]} ${chart} ${arr[$((total-1))]}"
}

# --- Main ---

case "${1:---help}" in
  --collect) do_collect ;;
  --report)  do_report "${3:-12}" ;;
  --json)    do_json ;;
  --help)
    echo "OpenCortex Metrics — track your agent's knowledge growth over time"
    echo ""
    echo "Usage:"
    echo "  metrics.sh --collect            Snapshot today's metrics → memory/metrics.log"
    echo "  metrics.sh --report             Show trends (default: last 12 weeks)"
    echo "  metrics.sh --report --weeks 8   Show last 8 weeks"
    echo "  metrics.sh --json               Today's snapshot as JSON"
    echo ""
    echo "This script is READ-ONLY (except appending to metrics.log in --collect mode)."
    echo "No network access. No sensitive data — only file counts and pattern matches."
    ;;
  *) echo "Unknown option: $1 (try --help)"; exit 1 ;;
esac
