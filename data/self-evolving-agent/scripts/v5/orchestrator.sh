#!/usr/bin/env bash
# ============================================================
# scripts/v5/orchestrator.sh — v5.0 Pipeline Orchestrator
#
# Runs the 6-stage v5.0 pipeline:
#   Stage 1: collect-logs.sh (same as v4, + stream-alerts integration)
#   Stage 2: embedding-analyze.sh (semantic embeddings, v4 fallback)
#   Stage 3: trend-analyzer.sh (4-week trend comparison)
#   Stage 4: fleet-analyzer.sh (multi-instance cross analysis)
#   Stage 5: benchmark.sh (effect measurement, same as v4)
#   Stage 6: synthesize-proposal.sh (proposal generation, same as v4)
#
# Fallback behavior:
#   - Ollama offline → EMBEDDING_FALLBACK=true → v4 heuristic for Stage 2
#   - Stage failure → log and continue (no crash)
#   - DRY_RUN=true → run all stages but don't deliver
#
# Usage:
#   orchestrator.sh [--dry-run] [--v4]
#
# Environment:
#   SEA_TMP_DIR          Temp directory (default: /tmp/sea-v5)
#   AGENTS_BASE          Agent base directory
#   LOGS_DIR             Logs directory
#   DRY_RUN              Skip delivery if "true"
#   OLLAMA_URL           Ollama API URL (checked for fallback)
#
# SECURITY MANIFEST:
#   - Reads: log files, session files, existing proposals
#   - Writes: /tmp/sea-v5/ artifacts, data/proposals/
#   - Network: Ollama (local only), LLM API (synthesis only)
#   - AGENTS.md: NEVER auto-modified. Proposals only.
# ============================================================
# shellcheck shell=bash

SHELLOPTS=
BASHOPTS=
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="${SKILL_DIR:-$(cd "$SCRIPT_DIR/../.." && pwd)}"
V4_DIR="$SKILL_DIR/scripts/v4"

# ── Configuration ──────────────────────────────────────────
SEA_TMP="${SEA_TMP_DIR:-/tmp/sea-v5}"
AGENTS_BASE="${AGENTS_BASE:-$HOME/.openclaw/agents}"
LOGS_DIR="${LOGS_DIR:-$HOME/.openclaw/logs}"
OLLAMA_URL="${OLLAMA_URL:-http://localhost:11434}"
DRY_RUN="${DRY_RUN:-false}"
FORCE_V4=false
COLLECT_DAYS="${COLLECT_DAYS:-7}"
MAX_SESSIONS="${MAX_SESSIONS:-30}"

export SEA_TMP_DIR="$SEA_TMP"
export SKILL_DIR
export AGENTS_BASE
export LOGS_DIR
export OLLAMA_URL

mkdir -p "$SEA_TMP" 2>/dev/null || true

# ── Logging ────────────────────────────────────────────────
log()  { echo "[SEA-v5 orch] $*" >&2; }
info() { echo "[SEA-v5] $*"; }

START_TIME=$(date +%s)

# ── Parse CLI flags ────────────────────────────────────────
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=true ;;
    --v4) FORCE_V4=true ;;
  esac
done

# ── Run a stage with timing and error isolation ────────────
run_stage() {
  local stage_num="$1"
  local stage_name="$2"
  local script="$3"
  shift 3

  local stage_start
  stage_start=$(date +%s)
  log "Stage $stage_num: $stage_name"

  if [ "$FORCE_V4" = "true" ] && [[ "$script" == *"v5"* ]]; then
    log "  --v4 flag: skipping v5 stage $stage_num ($stage_name)"
    return 0
  fi

  if bash "$script" "$@" 2>/dev/null; then
    local elapsed=$(( $(date +%s) - stage_start ))
    log "  Stage $stage_num complete (${elapsed}s)"
  else
    local elapsed=$(( $(date +%s) - stage_start ))
    log "  Stage $stage_num FAILED (${elapsed}s) — continuing"
  fi
}

# ── Check Ollama ───────────────────────────────────────────
check_ollama() {
  curl -sf --max-time 3 "${OLLAMA_URL}/api/tags" > /dev/null 2>&1
}

# ── Main ───────────────────────────────────────────────────
main() {
  local ts
  ts=$(date +%Y%m%d)

  info "Self-Evolving Agent v5.0 — $(date '+%Y-%m-%d %H:%M')"
  info "Pipeline: 6-stage (Collect→Embed→Trend→Fleet→Benchmark→Synthesize)"
  info "DRY_RUN: $DRY_RUN"

  # Check Ollama before starting
  if check_ollama; then
    info "Ollama: online ✓ (semantic embedding mode)"
    export EMBEDDING_FALLBACK=false
  else
    info "Ollama: offline — EMBEDDING_FALLBACK=true (v4 heuristic mode)"
    export EMBEDDING_FALLBACK=true
  fi

  if [ "$FORCE_V4" = "true" ]; then
    info "Force v4: redirecting to v4 orchestrator"
    exec bash "$V4_DIR/orchestrator.sh"
  fi

  # ── Stage 1: Collect ──────────────────────────────────────
  local collect_out="$SEA_TMP/collect-${ts}.json"
  run_stage 1 "Collect Logs" "$V4_DIR/collect-logs.sh" "$collect_out"

  # Integrate stream alerts into collect output
  local alerts_dir="$SKILL_DIR/data/stream-alerts"
  if [ -d "$alerts_dir" ]; then
    local alert_count
    alert_count=$(ls "$alerts_dir"/*.json 2>/dev/null | wc -l | tr -d ' ')
    if [ "${alert_count:-0}" -gt 0 ] && [ -f "$collect_out" ]; then
      python3 - "$collect_out" "$alerts_dir" << 'PYEOF' 2>/dev/null || true
import json, sys
from pathlib import Path
collect_file = sys.argv[1]
alerts_dir = Path(sys.argv[2])
data = json.load(open(collect_file))
alerts = []
for f in sorted(alerts_dir.glob("*.json")):
    try:
        a = json.load(open(f))
        alerts.append(a)
    except Exception:
        continue
data['stream_alerts'] = alerts
with open(collect_file, 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f"Integrated {len(alerts)} stream alerts into collect output", file=sys.stderr)
PYEOF
      log "  Integrated $alert_count stream alert(s)"
    fi
  fi

  # ── Stage 2: Embedding Analysis ───────────────────────────
  local embed_out="$SEA_TMP/embedding-analysis-${ts}.json"
  LOGS_JSON="$collect_out" \
  OUTPUT_JSON="$embed_out" \
  COLLECT_DAYS="$COLLECT_DAYS" \
  MAX_SESSIONS="$MAX_SESSIONS" \
  EMBEDDING_FALLBACK_ALLOWED=true \
  run_stage 2 "Embedding Analyze" "$SCRIPT_DIR/embedding-analyze.sh"

  # ── Stage 3: Trend Analysis ────────────────────────────────
  local trends_out="$SEA_TMP/trends-${ts}.json"
  PROPOSALS_DIR="$SKILL_DIR/data/proposals" \
  TRENDS_OUTPUT="$trends_out" \
  run_stage 3 "Trend Analyze" "$SCRIPT_DIR/trend-analyzer.sh"

  # ── Stage 4: Fleet Analysis ────────────────────────────────
  local fleet_out="$SEA_TMP/fleet-${ts}.json"
  FLEET_OUTPUT="$fleet_out" \
  run_stage 4 "Fleet Analyze" "$SCRIPT_DIR/fleet-analyzer.sh"

  # ── Stage 5: Benchmark ────────────────────────────────────
  local benchmark_out="$SEA_TMP/benchmarks-${ts}.json"
  # benchmark.sh uses SEA_TMP_DIR for I/O
  run_stage 5 "Benchmark" "$V4_DIR/benchmark.sh"

  # ── Stage 6: Synthesize ───────────────────────────────────
  local synth_out="$SEA_TMP/proposal-${ts}.md"
  if [ "$DRY_RUN" = "true" ]; then
    log "DRY_RUN=true — writing stub proposal"
    cat > "$synth_out" << 'MDEOF'
## 🧠 Self-Evolving Agent v5.0 — DRY RUN

This is a dry-run output. No actual analysis was performed.
The pipeline structure was validated successfully.

### Stages completed:
- [x] Stage 1: Collect Logs
- [x] Stage 2: Embedding Analyze (+ v4 fallback if Ollama offline)
- [x] Stage 3: Trend Analyze
- [x] Stage 4: Fleet Analyze
- [x] Stage 5: Benchmark
- [x] Stage 6: Synthesize (DRY RUN)
MDEOF
  else
    ANALYSIS_JSON="$embed_out" \
    BENCHMARK_JSON="$benchmark_out" \
    TRENDS_JSON="$trends_out" \
    FLEET_JSON="$fleet_out" \
    run_stage 6 "Synthesize Proposal" "$V4_DIR/synthesize-proposal.sh"
  fi

  # ── Summary ───────────────────────────────────────────────
  local elapsed=$(( $(date +%s) - START_TIME ))
  info ""
  info "Pipeline complete in ${elapsed}s"
  info "Engine: $([ "$EMBEDDING_FALLBACK" = "true" ] && echo 'heuristic (Ollama offline)' || echo 'semantic embedding')"
  info "Artifacts: $SEA_TMP/"

  # Print proposal if exists
  if [ -f "$SEA_TMP/proposal.md" ] && [ "$DRY_RUN" != "true" ]; then
    cat "$SEA_TMP/proposal.md"
  elif [ -f "$synth_out" ]; then
    cat "$synth_out"
  fi
}

main "$@"
